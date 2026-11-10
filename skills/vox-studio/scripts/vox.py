#!/usr/bin/env python3
"""Vox Studio: shorts verticales estilo documental-collage con Remotion.

Subcomandos (sin --execute nada llama a un proveedor de pago):
  espacios                                 lista los espacios (marcas) y su perfil
  proyecto productions/E/TEMA --perfil E   crea la producción dentro de su espacio
  validar GUION                            comprueba el guion (exige la opinión de Emi)
  voz GUION --dir DIR [--execute]          narra con ElevenLabs y guarda la alineación real
  armar GUION --dir DIR                    reconstruye video.json sin volver a pagar la voz
  imagen --prompt-file F --out O --estado S [--estilo ilustracion|foto|sticker] [--modelo M] [--croma verde|magenta]
  recorte ENTRADA SALIDA                   quita el fondo uniforme conectado al borde -> PNG con alfa
  foto --consulta "..." --dir DIR [--execute]   busca fotos reales con Apify (candidatas, con su fuente)
  foto-bajar --dir DIR --indice N --out O  descarga una candidata ya verificada (derechos y fuente)
  catalogar DIR                            guarda en la biblioteca los recortes del video, con su descripción
  biblioteca [--buscar TEXTO] [--espacio E]  qué hay para reciclar
  reciclar ID --dir DIR                    copia un recurso de la biblioteca a una producción
  sonido GUION                             analiza el guion y propone música, efectos y remates
  render DIR                               render + portada + master a -14 LUFS + hoja de fotogramas para auditar
  cierre DIR                               tabla de gastado y restante del video (obligatoria al entregar)
  saldo                                    cuánto queda en Kie, ElevenLabs y Apify
  aprender "TEXTO" [--espacio E]           guarda una lección para los videos siguientes
  aprendizajes [--espacio E]               lo aprendido hasta hoy; leerlo antes de cada guion

Las claves nunca se escriben aquí. En la nube el proxy las inyecta (se envía un
marcador); en local se leen de KIE_API_KEY, ELEVENLABS_API_KEY y APIFY_TOKEN.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla"
FPS = 30
MARCADOR = "proxy-injected"
KIE = "https://api.kie.ai/api/v1"
ELEVEN = "https://api.elevenlabs.io/v1"
HOSTS_DESCARGA = {"tempfile.aiquickdraw.com", "file.aiquickdraw.com"}
# Modelo -> campos extra de input según su esquema oficial (docs.kie.ai, comprobado el 2026-11-10).
MODELOS_KIE = {
    "nano-banana-2-lite": {},
    "seedream/5-lite-text-to-image": {"quality": "basic", "output_format": "png"},
}
ENTRADAS = ["sello", "desliza-izq", "cae", "desliza-der", "desdobla", "mordidas"]
TRANSICIONES = ["viaje", "barrido", "viaje", "rasgado"]
ESTILOS = {
    # Natural: ilustración editorial con textura y proporciones reales. Es el estilo por defecto.
    "ilustracion": "hand-painted editorial magazine illustration, gouache and ink texture, natural realistic proportions, "
                   "expressive but believable, limited muted palette with one warm accent color, soft natural lighting",
    # Fotografía creíble para recortar; no usar para personas reales identificables.
    "foto": "realistic documentary photograph, natural light, true-to-life colors and textures, candid, shot on 50mm lens",
    "sticker": "flat 2D editorial cartoon illustration, bold thick black outlines, flat colors",
}
CROMAS = {"verde": "pure green (#00FF00)", "magenta": "pure magenta (#FF00FF)"}
SIGNOS = "¿¡?!.,;:"
MIN_ESCENA = 24  # frames; con menos, la cámara no alcanza a llegar
LIMITES = {"kicker": 18, "nota": 38, "fuente": 46, "dato": 6, "remate": 14}

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sonido as SON  # noqa: E402  (música y efectos hechos con código)


class ErrorVox(Exception):
    pass


# ---------- espacios y memoria ----------

def dir_espacios() -> Path:
    """Cada espacio (marca) vive en su propia carpeta: espacios/<nombre>/perfil.json."""
    if os.environ.get("VOX_ESPACIOS"):
        return Path(os.environ["VOX_ESPACIOS"])
    return RAIZ.parent.parent / "espacios"


def perfiles() -> dict:
    out = {}
    for f in sorted(dir_espacios().glob("*/perfil.json")):
        out[f.parent.name] = json.loads(f.read_text(encoding="utf-8"))
    if not out:
        raise ErrorVox(f"no hay espacios en {dir_espacios()}")
    return out


def archivo_aprendizajes(espacio: str = "") -> Path:
    """Sin espacio: lo que vale para todos los videos. Con espacio: lo propio de esa marca."""
    if espacio:
        if espacio not in perfiles():
            raise ErrorVox(f"espacio desconocido: {espacio}")
        return dir_espacios() / espacio / "aprendizajes.md"
    return dir_espacios() / "APRENDIZAJES.md"


def leer_aprendizajes(espacio: str = "") -> str:
    partes = []
    for f in [archivo_aprendizajes("")] + ([archivo_aprendizajes(espacio)] if espacio else []):
        if f.exists():
            partes.append(f.read_text(encoding="utf-8").strip())
    return "\n\n".join(partes) or "Sin aprendizajes registrados."


# ---------- guion ----------

def limpia(palabra: str) -> str:
    return palabra.strip(SIGNOS).upper()


def partir(texto: str) -> list[str]:
    """Mismo reparto en líneas que usa el compositor (Vox.tsx)."""
    lineas, actual = [], ""
    for p in texto.split():
        if actual and len(actual + " " + p) > 11:
            lineas.append(actual)
            actual = p
        else:
            actual = f"{actual} {p}" if actual else p
    if actual:
        lineas.append(actual)
    return lineas


def ruta_segura(rel: str) -> bool:
    p = Path(rel)
    return bool(rel) and not p.is_absolute() and ".." not in p.parts and "\\" not in rel


def validar_guion(g: dict) -> list[str]:
    e: list[str] = []
    try:
        conocidos = perfiles()
    except ErrorVox as exc:
        return [str(exc)]
    if g.get("perfil") not in conocidos:
        e.append(f"perfil desconocido: {g.get('perfil')!r}; usa uno de {sorted(conocidos)}")
    if len(str(g.get("opinion_emi", "")).strip()) < 20:
        e.append("falta opinion_emi: pregunta a Emi su postura sobre el tema antes de escribir (mínimo 20 caracteres)")
    if not str(g.get("titulo", "")).strip():
        e.append("falta titulo")
    if "?" not in str(g.get("cta_pregunta", "")):
        e.append("cta_pregunta debe ser una pregunta que invite a comentar")
    mus = g.get("musica") or {}
    if mus.get("animo") not in set(SON.ANIMOS) | {"ninguna"}:
        e.append(f"falta musica.animo: analiza de qué va el video (`vox.py sonido GUION`) y elige uno de {sorted(SON.ANIMOS)} o 'ninguna'")
    if mus.get("animo") == "ninguna" and len(str(mus.get("motivo", ""))) < 10:
        e.append("musica 'ninguna' exige musica.motivo")
    port = g.get("portada") or {}
    if len(str(port.get("texto", ""))) > 34 or len(partir(str(port.get("texto", "")))) > 3:
        e.append("portada.texto: máximo 34 caracteres y 3 líneas")
    if port.get("imagen_archivo") and not ruta_segura(port["imagen_archivo"]):
        e.append("portada.imagen_archivo debe ser relativa a public/")
    escenas = g.get("escenas") or []
    if not any(s.get("sonido") for s in escenas):
        e.append("ninguna escena tiene `sonido`: propone al menos un efecto que subraye el contenido")
    if not 4 <= len(escenas) <= 9:
        e.append(f"se esperan de 4 a 9 escenas; hay {len(escenas)}")
    vistos, ent_previa, tr_previa = set(), None, None
    for i, s in enumerate(escenas):
        p = f"escena {i + 1}"
        if s.get("id") in vistos or not s.get("id"):
            e.append(f"{p}: id ausente o repetido")
        vistos.add(s.get("id"))
        n = " ".join(str(s.get("narracion", "")).split())
        k = " ".join(str(s.get("keyword", "")).split())
        if not n:
            e.append(f"{p}: falta narracion")
        if not k or len(k) > 34:
            e.append(f"{p}: keyword vacío o de más de 34 caracteres")
        if k and n and k.lower() == n.lower():
            e.append(f"{p}: el keyword repite la narración; debe reforzarla")
        if any(len(w) > 16 for w in k.split()):
            e.append(f"{p}: una palabra del keyword pasa de 16 letras y no cabe en pantalla")
        if len(partir(k)) > 3:
            e.append(f"{p}: el keyword ocupa {len(partir(k))} líneas; el máximo es 3 (acórtalo)")
        r = s.get("resaltar")
        if r and limpia(r) not in {limpia(w) for w in k.split()}:
            e.append(f"{p}: resaltar {r!r} no es una palabra del keyword")
        for campo, tope in LIMITES.items():
            if len(str(s.get(campo, ""))) > tope:
                e.append(f"{p}: {campo} pasa de {tope} caracteres")
        if s.get("sonido") and s["sonido"] not in SON.EFECTOS:
            e.append(f"{p}: sonido {s['sonido']!r} no existe; opciones {sorted(SON.EFECTOS)}")
        img = s.get("imagen_archivo", "")
        if img and not ruta_segura(img):
            e.append(f"{p}: imagen_archivo debe ser una ruta relativa a public/, sin '..'")
        ent = s.get("entrada")
        if ent and ent not in ENTRADAS:
            e.append(f"{p}: entrada {ent!r} no existe; opciones {ENTRADAS}")
        ent = ent or ENTRADAS[i % len(ENTRADAS)]  # se compara la entrada efectiva, incluida la automática
        if ent == ent_previa:
            e.append(f"{p}: repite la entrada de la escena anterior ({ent})")
        ent_previa = ent
        tr = s.get("transicion")
        if tr and tr not in set(TRANSICIONES):
            e.append(f"{p}: transicion {tr!r} no existe; opciones {sorted(set(TRANSICIONES))}")
        tr = tr or TRANSICIONES[i % len(TRANSICIONES)]
        if i > 1 and tr == tr_previa:
            e.append(f"{p}: repite la transición de la escena anterior ({tr})")
        tr_previa = tr
    if escenas and "?" not in str(escenas[-1].get("narracion", "")):
        e.append("la última escena debe narrar la pregunta de cierre (cta_pregunta)")
    return e


def texto_completo(g: dict) -> str:
    return " ".join(" ".join(str(s["narracion"]).split()) for s in g["escenas"])


def palabras_desde_alineacion(chars: list[str], ini: list[float], fin: list[float]) -> list[dict]:
    """Agrupa la alineación por carácter del proveedor en palabras con tiempo real."""
    out, actual = [], None
    for i, ch in enumerate(chars):
        if ch.isspace():
            if actual:
                out.append(actual)
                actual = None
            continue
        if actual is None:
            actual = {"t": "", "a": float(ini[i]), "b": float(fin[i])}
        actual["t"] += ch
        actual["b"] = float(fin[i])
    if actual:
        out.append(actual)
    return out


def armar_video(g: dict, palabras: list[dict], duracion: float, perfil: dict, publico: Path | None = None) -> dict:
    """Convierte guion + tiempos reales de palabra en la línea de tiempo que lee Remotion.

    Las palabras se reparten entre escenas contando palabras, no caracteres: así un
    proveedor que normalice comillas o espacios no desplaza los límites en silencio.
    """
    conteos = [len(str(s["narracion"]).split()) for s in g["escenas"]]
    if sum(conteos) != len(palabras):
        raise ErrorVox(f"la alineación trae {len(palabras)} palabras y el guion {sum(conteos)}; no se inventan tiempos")
    inicios, pos = [], 0
    for c in conteos:
        if c == 0:
            raise ErrorVox("una escena quedó sin palabras; revisa la narración")
        inicios.append(palabras[pos]["a"])
        pos += c
    total = int(round((duracion + 0.7) * FPS))
    cortes = [0] + [max(0, int(round((t - 0.12) * FPS))) for t in inicios[1:]] + [total]
    escenas = []
    for i, s in enumerate(g["escenas"]):
        desde, dur = cortes[i], cortes[i + 1] - cortes[i]
        if dur < MIN_ESCENA:
            raise ErrorVox(f"la escena {s['id']} dura {dur} frames; el mínimo es {MIN_ESCENA}. Únela a otra o alarga su narración")
        img = s.get("imagen_archivo", "")
        if img and publico is not None and not (publico / img).is_file():
            raise ErrorVox(f"la escena {s['id']} pide {img} y no existe en {publico}")
        escenas.append({
            "id": s["id"], "desde": desde, "dur": dur,
            "keyword": " ".join(str(s["keyword"]).split()).upper(), "resaltar": limpia(s.get("resaltar") or ""),
            "kicker": s.get("kicker", ""), "nota": s.get("nota", ""), "dato": s.get("dato", ""),
            "fuente": s.get("fuente", ""), "imagen": img, "foto": bool(s.get("foto_real", False)),
            "entrada": s.get("entrada") or ENTRADAS[i % len(ENTRADAS)],
            "transicion": s.get("transicion") or TRANSICIONES[i % len(TRANSICIONES)],
            "sonido": s.get("sonido", ""), "remate": str(s.get("remate", "")).upper(),
        })
    port = g.get("portada") or {}
    con_imagen = next((x for x in escenas if x["imagen"]), None)
    portada = {
        "texto": " ".join(str(port.get("texto") or escenas[0]["keyword"]).split()).upper(),
        "resaltar": limpia(port.get("resaltar") or escenas[0]["resaltar"]),
        "imagen": port.get("imagen_archivo") or (con_imagen["imagen"] if con_imagen else ""),
    }
    if portada["imagen"] and publico is not None and not (publico / portada["imagen"]).is_file():
        raise ErrorVox(f"la portada pide {portada['imagen']} y no existe en {publico}")
    animo = (g.get("musica") or {}).get("animo", "ninguna")
    return {
        "fps": FPS, "ancho": 1080, "alto": 1920, "frames": total,
        "titulo": g["titulo"], "perfil": perfil, "voz": "audio/voz.mp3",
        "musica": "" if animo == "ninguna" else "audio/musica.wav", "animo": animo,
        "finVoz": round(palabras[-1]["b"], 3), "portada": portada, "sfx": True, "escenas": escenas,
        "palabras": [{"t": p["t"], "a": round(p["a"], 3), "b": round(p["b"], 3)} for p in palabras],
    }


# ---------- red ----------

def _pedir(url: str, *, metodo="GET", cabeceras=None, cuerpo=None, espera=120) -> bytes:
    if urllib.parse.urlparse(url).scheme != "https":
        raise ErrorVox("solo se permiten URLs https")
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo, headers={"User-Agent": "vox-studio/0.4 (video tool; python-urllib)", **(cabeceras or {})})
    if datos is not None:
        req.add_header("Content-Type", "application/json")
    host = urllib.parse.urlparse(url).hostname
    try:
        with urllib.request.urlopen(req, timeout=espera) as r:
            return r.read()
    except urllib.error.HTTPError as exc:
        raise ErrorVox(f"{host} respondió HTTP {exc.code}: {exc.read()[:200]!r}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        aviso = " No se sabe si el proveedor cobró: revisa su historial antes de reintentar." if metodo == "POST" else ""
        raise ErrorVox(f"sin respuesta de {host}: {exc}.{aviso}") from exc


def _json(crudo: bytes, quien: str) -> dict:
    try:
        return json.loads(crudo)
    except ValueError as exc:
        raise ErrorVox(f"{quien} devolvió algo que no es JSON") from exc


def _kie() -> dict:
    return {"Authorization": "Bearer " + os.environ.get("KIE_API_KEY", MARCADOR)}


def _eleven() -> dict:
    return {"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", MARCADOR)}


def saldo() -> dict:
    """Saldo real de cada proveedor. Un proveedor sin conexión se informa como tal, nunca se estima."""
    out: dict = {}
    try:
        out["kie_creditos"] = _json(_pedir(f"{KIE}/chat/credit", cabeceras=_kie(), espera=30), "Kie").get("data")
    except ErrorVox as exc:
        out["kie_error"] = str(exc)[:120]
    try:
        sub = _json(_pedir(f"{ELEVEN}/user/subscription", cabeceras=_eleven(), espera=30), "ElevenLabs")
        out["elevenlabs_usados"] = sub.get("character_count")
        out["elevenlabs_limite"] = sub.get("character_limit")
        out["elevenlabs_restantes"] = (sub.get("character_limit") or 0) - (sub.get("character_count") or 0)
    except ErrorVox as exc:
        out["elevenlabs_error"] = str(exc)[:120]
    try:
        cab = {"Authorization": "Bearer " + os.environ.get("APIFY_TOKEN", MARCADOR)}
        lim = _json(_pedir("https://api.apify.com/v2/users/me/limits", cabeceras=cab, espera=30), "Apify").get("data") or {}
        uso = (lim.get("current") or {}).get("monthlyUsageUsd")
        tope = (lim.get("limits") or {}).get("maxMonthlyUsageUsd")
        out["apify_usado_usd"], out["apify_tope_usd"] = uso, tope
        if uso is not None and tope is not None:
            out["apify_restante_usd"] = round(tope - uso, 4)
    except ErrorVox:
        out["apify"] = "no conectado (falta el token)"
    out["fecha"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return out


def tabla_saldo(antes: dict | None, ahora: dict) -> str:
    def gasto(clave, sube=False):
        if not antes or antes.get(clave) is None or ahora.get(clave) is None:
            return "—"
        return f"{(ahora[clave] - antes[clave]) if sube else (antes[clave] - ahora[clave]):g}"
    filas = ["Proveedor   | Gastado en este video | Queda"]
    if ahora.get("kie_creditos") is not None:
        filas.append(f"Kie         | {gasto('kie_creditos')} créditos | {ahora['kie_creditos']:g} créditos")
    else:
        filas.append(f"Kie         | — | sin dato: {ahora.get('kie_error')}")
    if "elevenlabs_restantes" in ahora:
        filas.append(f"ElevenLabs  | {gasto('elevenlabs_usados', True)} caracteres | {ahora['elevenlabs_restantes']} de {ahora['elevenlabs_limite']} caracteres")
    else:
        filas.append(f"ElevenLabs  | — | sin dato: {ahora.get('elevenlabs_error')}")
    if "apify_restante_usd" in ahora:
        filas.append(f"Apify       | {gasto('apify_usado_usd', True)} USD | {ahora['apify_restante_usd']} de {ahora['apify_tope_usd']} USD este mes")
    else:
        filas.append(f"Apify       | — | {ahora.get('apify', 'sin dato')}")
    return "\n".join(filas)


def huella(*partes: str) -> str:
    return hashlib.sha256("\x1f".join(partes).encode()).hexdigest()


def narrar(texto: str, voz: dict) -> tuple[bytes, list[dict]]:
    cuerpo = {"text": texto, "model_id": voz.get("modelo", "eleven_multilingual_v2"),
              "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}}
    r = _json(_pedir(f"{ELEVEN}/text-to-speech/{voz['voice_id']}/with-timestamps?output_format=mp3_44100_128",
                     metodo="POST", cabeceras=_eleven(), cuerpo=cuerpo, espera=240), "ElevenLabs")
    al = r.get("alignment") or {}
    if not al.get("characters") or not r.get("audio_base64"):
        raise ErrorVox("ElevenLabs no devolvió audio con alineación; no se inventan tiempos de subtítulos")
    return base64.b64decode(r["audio_base64"]), palabras_desde_alineacion(
        al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"])


def _correr(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=True, **kw)
    except FileNotFoundError as exc:
        raise ErrorVox(f"falta el programa {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise ErrorVox(f"{cmd[0]} falló (código {exc.returncode})") from exc


def duracion_audio(ruta: Path) -> float:
    out = _correr(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                  capture_output=True, text=True).stdout
    return float(out.strip())


def generar_imagen(prompt: str, salida: Path, estado: Path, aspecto="3:4", modelo="nano-banana-2-lite", espera=300) -> None:
    if modelo not in MODELOS_KIE:
        raise ErrorVox(f"modelo {modelo!r} sin esquema comprobado; añade su contrato antes de usarlo")
    firma = huella(prompt, aspecto, modelo)
    if estado.exists():
        est = json.loads(estado.read_text())
        if est.get("firma") != firma:
            raise ErrorVox(f"{estado} pertenece a otro prompt, aspecto o modelo; usa un archivo de estado nuevo")
        if est.get("fallo"):
            raise ErrorVox(f"esa tarea ya falló ({est['fallo']}); cambia el prompt y usa un estado nuevo")
    else:
        r = _json(_pedir(f"{KIE}/jobs/createTask", metodo="POST", cabeceras=_kie(),
                         cuerpo={"model": modelo, "input": {"prompt": prompt, "aspect_ratio": aspecto, **MODELOS_KIE[modelo]}}), "Kie")
        tid = (r.get("data") or {}).get("taskId")
        if not tid:
            raise ErrorVox(f"Kie no devolvió taskId: {str(r)[:200]}")
        est = {"taskId": tid, "modelo": modelo, "firma": firma}
        estado.parent.mkdir(parents=True, exist_ok=True)
        estado.write_text(json.dumps(est))
    limite = time.time() + espera
    while time.time() < limite:
        d = _json(_pedir(f"{KIE}/jobs/recordInfo?taskId={est['taskId']}", cabeceras=_kie()), "Kie").get("data") or {}
        st = str(d.get("state", "")).lower()
        if st == "success":
            rj = d.get("resultJson")
            urls = ((json.loads(rj) if isinstance(rj, str) else rj) or {}).get("resultUrls") or []
            if not urls:
                raise ErrorVox("Kie terminó sin URL de resultado")
            if urllib.parse.urlparse(urls[0]).hostname not in HOSTS_DESCARGA:
                raise ErrorVox(f"host de descarga no autorizado: {urllib.parse.urlparse(urls[0]).hostname}")
            salida.parent.mkdir(parents=True, exist_ok=True)
            salida.write_bytes(_pedir(urls[0]))
            return
        if st in {"fail", "failed", "error"}:
            est["fallo"] = str(d.get("failMsg"))[:200]
            estado.write_text(json.dumps(est))
            raise ErrorVox(f"Kie falló: {est['fallo']}")
        time.sleep(4)
    raise ErrorVox(f"Kie no terminó a tiempo; repite el mismo comando con {estado} para reconsultar sin crear otra tarea")


# ---------- imagen local ----------

def recortar_croma(entrada: Path, salida: Path, tolerancia: float = 95.0) -> tuple[int, int]:
    """Quita el fondo uniforme *conectado al borde* y recorta al contenido.

    Mide el color real del fondo en el marco de la imagen (no supone verde puro). Elimina lo
    que toca el borde y los huecos interiores casi idénticos al fondo; un verde distinto dentro
    del sujeto (una hoja, una prenda) se conserva. Para sujetos verdes, generar con --croma magenta.
    """
    import numpy as np
    from PIL import Image, ImageFilter
    from scipy import ndimage

    im = np.asarray(Image.open(entrada).convert("RGB")).astype(np.float32)
    alto, ancho = im.shape[:2]
    m = max(2, min(alto, ancho) // 60)
    marco = np.concatenate([im[:m].reshape(-1, 3), im[-m:].reshape(-1, 3), im[:, :m].reshape(-1, 3), im[:, -m:].reshape(-1, 3)])
    fondo = np.median(marco, axis=0)
    if float(np.mean(np.linalg.norm(marco - fondo, axis=1) < tolerancia)) < 0.9:
        raise ErrorVox("el fondo no es uniforme: genera la imagen de nuevo sobre un color plano")
    dist = np.linalg.norm(im - fondo, axis=2)
    etiquetas, _ = ndimage.label(dist < tolerancia)
    borde = np.unique(np.concatenate([etiquetas[0], etiquetas[-1], etiquetas[:, 0], etiquetas[:, -1]]))
    es_fondo = np.isin(etiquetas, borde[borde > 0])
    # Huecos encerrados (entre un brazo y el cuerpo, perforaciones): solo si son casi idénticos al fondo.
    es_fondo |= dist < tolerancia * 0.45
    if es_fondo.all():
        raise ErrorVox("el recorte quedó vacío: no hay sujeto distinto del fondo")
    # Borde suave: la transparencia sube con la distancia de color solo en la franja pegada al fondo.
    franja = ndimage.binary_dilation(es_fondo, iterations=3) & ~es_fondo
    alfa = np.where(es_fondo, 0.0, 1.0)
    alfa[franja] = np.clip((dist[franja] - tolerancia * 0.5) / (tolerancia * 0.9), 0.15, 1.0)
    # Quitar el derrame del color de fondo únicamente en esa franja.
    canal = int(np.argmax(fondo))
    otros = [c for c in range(3) if c != canal]
    rgb = im.copy()
    rgb[..., canal][franja] = np.minimum(im[..., canal], np.maximum(im[..., otros[0]], im[..., otros[1]]))[franja]
    out = Image.fromarray(np.dstack([rgb, alfa[..., None] * 255.0]).clip(0, 255).astype(np.uint8), "RGBA")
    a = out.getchannel("A").filter(ImageFilter.GaussianBlur(0.6))
    out.putalpha(a)
    caja = a.point(lambda v: 255 if v > 24 else 0).getbbox()
    if not caja:
        raise ErrorVox("el recorte quedó vacío")
    out = out.crop(caja)
    salida.parent.mkdir(parents=True, exist_ok=True)
    out.save(salida)
    return out.size


SFX = {
    "pop": "sine=f=880:d=0.09,afade=t=out:st=0.02:d=0.07,volume=0.7",
    "golpe": "sine=f=70:d=0.22,afade=t=out:st=0.03:d=0.19,volume=1.2",
    "papel": "anoisesrc=d=0.28:c=white:a=0.5,highpass=f=2500,afade=t=in:d=0.05,afade=t=out:st=0.1:d=0.18",
    "deslizar": "anoisesrc=d=0.4:c=pink:a=0.6,bandpass=f=1400:w=1200,afade=t=in:d=0.22,afade=t=out:st=0.24:d=0.16",
    "marcador": "anoisesrc=d=0.3:c=brown:a=0.9,highpass=f=900,afade=t=in:d=0.03,afade=t=out:st=0.18:d=0.12",
    "rasgar": "anoisesrc=d=0.45:c=white:a=0.7,bandpass=f=3200:w=2600,tremolo=f=38:d=0.8,afade=t=in:d=0.04,afade=t=out:st=0.25:d=0.2",
}


def sintetizar_sfx(destino: Path) -> list[str]:
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, filtro in SFX.items():
        _correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", filtro, "-ar", "48000", "-ac", "2",
                 str(destino / f"{nombre}.wav")])
    return sorted(SFX)


def _loudnorm(video: Path) -> dict:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-af", "loudnorm=I=-14:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
    if not m:
        raise ErrorVox("no se pudo medir la sonoridad del video")
    return json.loads(m.group(0))


def masterizar(entrada: Path, salida: Path) -> None:
    """Dos pasadas: se mide y luego se aplica una ganancia lineal exacta a -14 LUFS con pico <= -2 dBTP."""
    m = _loudnorm(entrada)
    filtro = (f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    salida.parent.mkdir(parents=True, exist_ok=True)
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(entrada), "-c:v", "copy", "-af", filtro, "-ar", "48000",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(salida)])


def medir(video: Path) -> dict:
    d = _loudnorm(video)
    return {"lufs": d.get("input_i"), "pico_dbtp": d.get("input_tp"), "duracion_s": round(duracion_audio(video), 2)}


def hoja_de_fotogramas(video: Path, datos: dict, salida: Path) -> None:
    """Un cuadro del inicio, el cambio y la mitad de cada escena, para auditar con los ojos."""
    cuadros = [0]
    for e in datos["escenas"]:
        cuadros += [e["desde"] + 2, e["desde"] + e["dur"] // 2]
    cuadros = sorted(set(min(c, datos["frames"] - 1) for c in cuadros))
    sel = "+".join(f"eq(n\\,{c})" for c in cuadros)
    cols = min(8, len(cuadros))
    filas = -(-len(cuadros) // cols)
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", f"select='{sel}',scale=250:-1,tile={cols}x{filas}",
             "-vsync", "0", "-frames:v", "1", str(salida)])


VOL_MUSICA = 0.09  # ganancia de la música bajo la voz en Vox.tsx


def auditar_audio(d: Path, datos: dict, final: dict) -> dict:
    """Revisión medible del sonido. No sustituye al oído de Emi: no juzga si la música gusta."""
    import math
    avisos = []
    voz = _loudnorm(d / "public" / "audio" / "voz.mp3")
    informe = {"voz_lufs": float(voz["input_i"]), "final_lufs": float(final["lufs"]), "final_pico_dbtp": float(final["pico_dbtp"])}
    if datos.get("musica"):
        mus = _loudnorm(d / "public" / datos["musica"])
        bajo_voz = float(voz["input_i"]) - (float(mus["input_i"]) + 20 * math.log10(VOL_MUSICA))
        informe["musica_bajo_voz_lu"] = round(bajo_voz, 1)
        if bajo_voz < 12:
            avisos.append(f"la música queda solo {bajo_voz:.1f} LU bajo la voz (mínimo 12): puede taparla")
        if bajo_voz > 30:
            avisos.append(f"la música queda {bajo_voz:.1f} LU bajo la voz: casi no se oirá")
    else:
        avisos.append("el video no lleva música")
    if not -15.5 <= informe["final_lufs"] <= -13:
        avisos.append(f"sonoridad final {informe['final_lufs']} LUFS fuera de -14 ± 1")
    if informe["final_pico_dbtp"] > -1.0:
        avisos.append(f"pico {informe['final_pico_dbtp']} dBTP por encima de -1")
    usados = {e["sonido"] for e in datos["escenas"] if e.get("sonido")}
    faltan = sorted(x for x in usados if not (d / "public" / "sfx" / f"{x}.wav").is_file())
    if faltan:
        avisos.append(f"faltan efectos en public/sfx: {faltan}")
    silencio = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(d / "out" / "final.mp4"), "-af", "silencedetect=n=-45dB:d=1.2", "-f", "null", "-"],
                              capture_output=True, text=True).stderr.count("silence_start")
    if silencio:
        avisos.append(f"{silencio} silencio(s) de más de 1.2 s")
    informe["efectos"] = sorted(usados)
    informe["avisos"] = avisos
    (d / "out" / "auditoria-audio.json").write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    return informe


def rendir(d: Path) -> dict:
    datos = json.loads((d / "src" / "data" / "video.json").read_text(encoding="utf-8"))
    cmd = ["npx", "remotion", "render", "src/index.ts", "Vox", "out/video.mp4", "--props=src/data/video.json",
           "--codec=h264", "--audio-codec=aac", "--pixel-format=yuv420p", "--log=error"]
    navegador = os.environ.get("VOX_NAVEGADOR", "/usr/local/bin/chrome-headless-shell")
    if Path(navegador).exists():
        cmd.append(f"--browser-executable={navegador}")
    _correr(cmd, cwd=d)
    foto = ["npx", "remotion", "still", "src/index.ts", "Portada", "out/portada.png", "--props=src/data/video.json", "--log=error"]
    _correr(foto + [c for c in cmd if c.startswith("--browser-executable")], cwd=d)
    masterizar(d / "out" / "video.mp4", d / "out" / "final.mp4")
    hoja_de_fotogramas(d / "out" / "final.mp4", datos, d / "out" / "hoja.png")
    m = medir(d / "out" / "final.mp4")
    m["audio"] = auditar_audio(d, datos, m)
    return m


# ---------- fotos reales (Apify) ----------

ACTOR_FOTOS = "automation-lab~google-images-scraper"


def buscar_fotos(consulta: str, maximo: int, tope_usd: float, derechos: str = "creative_commons") -> list[dict]:
    """Candidatas reales con su página de origen. Encontrar una foto no da derecho a usarla."""
    cab = {"Authorization": "Bearer " + os.environ.get("APIFY_TOKEN", MARCADOR)}
    entrada = {"queries": [consulta], "maxResultsPerQuery": maximo, "imageSize": "large", "imageType": "photo",
               "safeSearch": "strict", "language": "es", "country": "mx"}
    if derechos != "cualquiera":
        entrada["usageRights"] = derechos
    url = f"https://api.apify.com/v2/acts/{ACTOR_FOTOS}/run-sync-get-dataset-items?maxTotalChargeUsd={tope_usd}&restartOnError=false"
    datos = _json(_pedir(url, metodo="POST", cabeceras=cab, cuerpo=entrada, espera=280), "Apify")
    if not isinstance(datos, list):
        raise ErrorVox(f"Apify devolvió algo inesperado: {str(datos)[:160]}")
    return [{"imagen": x.get("imageUrl") or x.get("url"), "pagina": x.get("sourceUrl"), "dominio": x.get("sourceDomain"),
             "titulo": x.get("title"), "ancho": x.get("imageWidth") or x.get("width"), "alto": x.get("imageHeight") or x.get("height")}
            for x in datos if (x.get("imageUrl") or x.get("url"))][:maximo]


def licencia_commons(url_imagen: str) -> dict | None:
    """Autor y licencia de un archivo de Wikimedia Commons, leídos de su propia ficha."""
    u = urllib.parse.urlparse(url_imagen)
    if u.hostname != "upload.wikimedia.org":
        return None
    nombre = urllib.parse.unquote(u.path.rsplit("/", 1)[-1])
    api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=extmetadata&titles="
           + urllib.parse.quote("File:" + nombre))
    paginas = (_json(_pedir(api, espera=30), "Wikimedia Commons").get("query") or {}).get("pages") or {}
    info = next(iter(paginas.values()), {}).get("imageinfo") or [{}]
    meta = info[0].get("extmetadata") or {}
    limpio = lambda k: re.sub(r"<[^>]+>", "", str((meta.get(k) or {}).get("value", ""))).strip()
    if not limpio("LicenseShortName"):
        return None
    return {"licencia": limpio("LicenseShortName"), "autor": limpio("Artist"), "atribucion_requerida": limpio("AttributionRequired"),
            "ficha": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(nombre)}


# ---------- biblioteca para reciclar ----------

def dir_biblioteca() -> Path:
    return Path(os.environ.get("VOX_BIBLIOTECA") or RAIZ.parent.parent / "biblioteca")


def leer_catalogo() -> list[dict]:
    f = dir_biblioteca() / "catalogo.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def catalogar(d: Path) -> list[dict]:
    """Copia a la biblioteca los recortes que el video usó, con lo que muestran y cómo se hicieron."""
    g = json.loads((d / "guion.json").read_text(encoding="utf-8"))
    cat = leer_catalogo()
    conocidos = {x["sha256"] for x in cat}
    nuevos = []
    for s in g["escenas"]:
        img = s.get("imagen_archivo")
        origen = d / "public" / img if img else None
        if not origen or not origen.is_file():
            continue
        sha = hashlib.sha256(origen.read_bytes()).hexdigest()
        if sha in conocidos:
            continue
        prompt_f = d / "prompts" / (Path(img).stem + ".txt")
        ident = f"{g['perfil']}-{d.name}-{Path(img).stem}"
        destino = dir_biblioteca() / g["perfil"] / f"{ident}{origen.suffix}"
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origen, destino)
        try:  # copia ligera: basta para un video vertical y no engorda el repositorio
            from PIL import Image
            with Image.open(destino) as im:
                if max(im.size) > 1200:
                    im.thumbnail((1200, 1200))
                    im.save(destino, optimize=True)
        except ImportError:
            pass
        item = {"id": ident, "espacio": g["perfil"], "archivo": str(destino.relative_to(dir_biblioteca())), "sha256": sha,
                "muestra": prompt_f.read_text(encoding="utf-8").strip() if prompt_f.is_file() else "",
                "descripcion": s.get("descripcion_imagen", ""), "foto_real": bool(s.get("foto_real", False)),
                "origen": f"productions/{g['perfil']}/{d.name}", "fecha": time.strftime("%Y-%m-%d"), "usos": 1}
        cat.append(item)
        conocidos.add(sha)
        nuevos.append(item)
    (dir_biblioteca() / "catalogo.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return nuevos


def buscar_en_biblioteca(texto: str = "", espacio: str = "") -> list[dict]:
    terminos = [t for t in re.split(r"\W+", texto.lower()) if len(t) > 2]
    out = []
    for x in leer_catalogo():
        if espacio and x["espacio"] != espacio:
            continue
        donde = f"{x['muestra']} {x['descripcion']} {x['id']}".lower()
        if all(t in donde for t in terminos):
            out.append(x)
    return out


# ---------- CLI ----------

def _guion(ruta: str) -> dict:
    g = json.loads(Path(ruta).read_text(encoding="utf-8"))
    errores = validar_guion(g)
    if errores:
        raise ErrorVox("guion inválido: " + "; ".join(errores))
    return g


def _escribir_video(g: dict, d: Path, palabras: list[dict]) -> dict:
    video = armar_video(g, palabras, duracion_audio(d / "public" / "audio" / "voz.mp3"), perfiles()[g["perfil"]], d / "public")
    # Sonido nuevo para cada video: la semilla sale de su propio texto.
    semilla = int(huella(g["titulo"], texto_completo(g))[:8], 16)
    plan = SON.plan_musica(video["animo"], semilla) if video["musica"] else {"tonica": 48}
    SON.sintetizar_efectos(d / "public" / "sfx", semilla, plan["tonica"])
    if video["musica"]:  # pista original, a la medida exacta y siguiendo los cambios de escena
        cortes = [e["desde"] / FPS for e in video["escenas"][1:]]
        SON.guardar(d / "public" / video["musica"], SON.componer(video["animo"], video["frames"] / FPS, semilla, cortes), pico=0.5)
        (d / "estados").mkdir(exist_ok=True)
        (d / "estados" / "musica.json").write_text(json.dumps(plan))
    (d / "src" / "data").mkdir(parents=True, exist_ok=True)
    (d / "src" / "data" / "video.json").write_text(json.dumps(video, ensure_ascii=False, indent=1), encoding="utf-8")
    return video


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("espacios")
    sub.add_parser("saldo")
    p = sub.add_parser("proyecto"); p.add_argument("dir"); p.add_argument("--perfil", required=True)
    p = sub.add_parser("validar"); p.add_argument("guion")
    p = sub.add_parser("voz"); p.add_argument("guion"); p.add_argument("--dir", required=True); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("armar"); p.add_argument("guion"); p.add_argument("--dir", required=True)
    p = sub.add_parser("imagen"); p.add_argument("--prompt-file", required=True); p.add_argument("--out", required=True)
    p.add_argument("--estado", required=True); p.add_argument("--aspecto", default="3:4"); p.add_argument("--execute", action="store_true")
    p.add_argument("--estilo", choices=sorted(ESTILOS), default="ilustracion"); p.add_argument("--modelo", choices=sorted(MODELOS_KIE), default="nano-banana-2-lite")
    p.add_argument("--croma", choices=sorted(CROMAS) + ["ninguno"], default="verde")
    p = sub.add_parser("recorte"); p.add_argument("entrada"); p.add_argument("salida")
    p = sub.add_parser("render"); p.add_argument("dir")
    p = sub.add_parser("sonido"); p.add_argument("guion")
    p = sub.add_parser("foto"); p.add_argument("--consulta", required=True); p.add_argument("--dir", required=True)
    p.add_argument("--max", type=int, default=5); p.add_argument("--tope-usd", type=float, default=0.12)
    p.add_argument("--derechos", choices=["creative_commons", "commercial", "cualquiera"], default="creative_commons"); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("foto-bajar"); p.add_argument("--dir", required=True); p.add_argument("--indice", type=int, required=True)
    p.add_argument("--out", required=True); p.add_argument("--licencia", default=""); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("catalogar"); p.add_argument("dir")
    p = sub.add_parser("biblioteca"); p.add_argument("--buscar", default=""); p.add_argument("--espacio", default="")
    p = sub.add_parser("reciclar"); p.add_argument("id"); p.add_argument("--dir", required=True); p.add_argument("--como", default="")
    p = sub.add_parser("cierre"); p.add_argument("dir")
    p = sub.add_parser("aprender"); p.add_argument("texto"); p.add_argument("--espacio", default="")
    p = sub.add_parser("aprendizajes"); p.add_argument("--espacio", default="")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "espacios":
            for k, v in perfiles().items():
                print(f"{k:10} {v['nombre']:22} acento {v['colores']['acento']}  voz {v['voz']['nombre']}  [{v['estado']}]")
        elif a.cmd == "saldo":
            print(tabla_saldo(None, saldo()))
        elif a.cmd == "proyecto":
            if a.perfil not in perfiles():
                raise ErrorVox(f"espacio desconocido: {a.perfil}")
            d = Path(a.dir)
            if d.parent.name != a.perfil:
                raise ErrorVox(f"cada espacio va por separado: usa productions/{a.perfil}/{d.name}")
            if d.exists():
                raise ErrorVox(f"{d} ya existe; no se sobrescribe una producción")
            with tempfile.TemporaryDirectory() as tmp:  # los SFX se prueban antes de crear nada
                sintetizar_sfx(Path(tmp) / "sfx")
                SON.sintetizar_efectos(Path(tmp) / "sfx")
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(PLANTILLA, d, ignore=shutil.ignore_patterns("node_modules", "out"))
                shutil.copytree(Path(tmp) / "sfx", d / "public" / "sfx")
            (d / "estados").mkdir(exist_ok=True)
            (d / "estados" / "saldo-inicio.json").write_text(json.dumps(saldo()))
            print(f"Producción creada en {d}.\n\nAntes de escribir el guion, aplica esto:\n{leer_aprendizajes(a.perfil)}")
        elif a.cmd == "validar":
            g = json.loads(Path(a.guion).read_text(encoding="utf-8"))
            errores = validar_guion(g)
            for x in errores:
                print("✗", x)
            print("Guion válido." if not errores else f"{len(errores)} problema(s).")
            return 1 if errores else 0
        elif a.cmd in {"voz", "armar"}:
            g = _guion(a.guion)
            voz = perfiles()[g["perfil"]]["voz"]
            texto = texto_completo(g)
            d = Path(a.dir)
            cache = d / "estados" / "voz.json"
            firma = huella(texto, voz["voice_id"], voz.get("modelo", ""))
            guardado = json.loads(cache.read_text()) if cache.exists() else {}
            vigente = guardado.get("firma") == firma and (d / "public" / "audio" / "voz.mp3").is_file()
            if vigente:
                video = _escribir_video(g, d, guardado["palabras"])
                print(f"video.json reconstruido con la voz ya pagada: {video['frames'] / FPS:.1f} s. No se gastó nada.")
            elif a.cmd == "armar":
                raise ErrorVox("la narración cambió o no existe: ejecuta `voz --execute` (esto sí gasta caracteres)")
            elif not a.execute:
                print(f"En seco: {len(texto)} caracteres con la voz {voz['nombre']}. Añade --execute para narrar.")
            else:
                audio, palabras = narrar(texto, voz)
                destino = d / "public" / "audio" / "voz.mp3"
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(audio)
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({"firma": firma, "palabras": palabras}))  # antes de armar: lo pagado no se pierde
                video = _escribir_video(g, d, palabras)
                print(f"Voz lista: {len(texto)} caracteres, {video['frames'] / FPS:.1f} s, {len(palabras)} palabras con tiempo real.")
        elif a.cmd == "imagen":
            prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip() + ". " + ESTILOS[a.estilo]
            if a.croma != "ninguno":
                prompt += (f", single isolated subject, centered, full subject visible with margin, on a perfectly uniform solid "
                           f"{CROMAS[a.croma]} chroma key background, no cast shadow, no floor, no gradient")
            prompt += ", no text, no letters, no logos, no watermark"
            if not a.execute:
                print(f"En seco: 1 imagen {a.modelo} {a.aspecto}, estilo {a.estilo}. Añade --execute para generarla.")
                return 0
            generar_imagen(prompt, Path(a.out), Path(a.estado), a.aspecto, a.modelo)
            print(f"Imagen guardada en {a.out}")
        elif a.cmd == "recorte":
            print("Recorte", recortar_croma(Path(a.entrada), Path(a.salida)))
        elif a.cmd == "sonido":
            g = json.loads(Path(a.guion).read_text(encoding="utf-8"))
            pr = SON.proponer(g)
            m = pr["musica"]
            print(f"Música propuesta: {m['animo']} ({m['bpm']} bpm) — {m['porque']}")
            print("Opciones: " + "; ".join(f"{k}: {v[4]}" for k, v in SON.ANIMOS.items()))
            for x in pr["escenas"]:
                print(f"  escena {x['id']}: sonido={x['sonido'] or '—'}  remate={x['remate'] or '—'}")
            print("Efectos disponibles: " + "; ".join(f"{k} ({v[1]})" for k, v in SON.EFECTOS.items()))
            print("Es una propuesta: revísala contra el sentido de cada escena y escribe en el guion musica.animo, sonido y remate.")
        elif a.cmd == "foto":
            if not 1 <= a.max <= 10:
                raise ErrorVox("--max entre 1 y 10: se buscan pocas candidatas, no un banco de imágenes")
            # Precio del actor medido el 2026-11-10: 0.005 por arranque + 0.05 por página de resultados + 0.0023 por imagen.
            minimo = round(0.005 + 0.05 + 0.0023 * a.max + 0.005, 3)
            if a.tope_usd < minimo:
                raise ErrorVox(f"--tope-usd {a.tope_usd} no alcanza: una búsqueda de {a.max} fotos cuesta cerca de {minimo} USD y un tope menor la aborta cobrando igual")
            if not a.execute:
                print(f"En seco: hasta {a.max} fotos de «{a.consulta}», derechos {a.derechos}, tope {a.tope_usd} USD. Añade --execute.")
                return 0
            fotos = buscar_fotos(a.consulta, a.max, a.tope_usd, a.derechos)
            est = Path(a.dir) / "estados" / "fotos.json"
            est.parent.mkdir(parents=True, exist_ok=True)
            est.write_text(json.dumps({"consulta": a.consulta, "derechos": a.derechos, "candidatas": fotos}, ensure_ascii=False, indent=1))
            for i, f in enumerate(fotos):
                print(f"[{i}] {f['ancho']}x{f['alto']}  {f['dominio']}  {str(f['titulo'])[:60]}\n     página: {f['pagina']}")
            print("Antes de usar una: abre su página, confirma qué muestra y su licencia. El filtro de derechos solo orienta.")
        elif a.cmd == "foto-bajar":
            est = json.loads((Path(a.dir) / "estados" / "fotos.json").read_text())
            f = est["candidatas"][a.indice]
            try:
                oficial = licencia_commons(f["imagen"])  # en Commons la licencia se lee de la ficha
            except ErrorVox as exc:  # su API limita peticiones: se sigue con verificación manual de la ficha
                oficial = None
                print(f"No se pudo leer la ficha automáticamente ({str(exc)[:60]}); usa --licencia tras abrirla.")
            if oficial:
                f["commons"] = oficial
                a.licencia = f"{oficial['licencia']} · {oficial['autor']}"
                print(f"Wikimedia Commons: {a.licencia}\n  ficha: {oficial['ficha']}")
            if len(a.licencia.strip()) < 8:
                raise ErrorVox("--licencia: escribe la licencia y el autor comprobados en la página de origen")
            if not a.execute:
                print(f"En seco: bajaría {f['imagen']} (página {f['pagina']}). Añade --execute.")
                return 0
            destino = Path(a.out)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(_pedir(f["imagen"], espera=60))
            f.update(licencia=a.licencia, archivo=str(destino), sha256=hashlib.sha256(destino.read_bytes()).hexdigest())
            (Path(a.dir) / "estados" / "fotos.json").write_text(json.dumps(est, ensure_ascii=False, indent=1))
            print(f"Foto guardada en {destino}. Si el host está bloqueado por la red del entorno, pide a Emi autorizar ese dominio.")
        elif a.cmd == "catalogar":
            nuevos = catalogar(Path(a.dir))
            print(f"{len(nuevos)} recurso(s) nuevos en la biblioteca: " + ", ".join(x["id"] for x in nuevos))
        elif a.cmd == "biblioteca":
            for x in buscar_en_biblioteca(a.buscar, a.espacio):
                print(f"{x['id']}  [{x['espacio']}]  usos {x['usos']}  {x['archivo']}\n    {x['muestra'] or x['descripcion']}")
            print("Reciclar solo si la imagen dice exactamente lo que la escena necesita; mírala antes. Si no, genera una nueva.")
        elif a.cmd == "reciclar":
            cat = leer_catalogo()
            x = next((c for c in cat if c["id"] == a.id), None)
            if not x:
                raise ErrorVox(f"no existe {a.id} en la biblioteca")
            destino = Path(a.dir) / "public" / "img" / (a.como or Path(x["archivo"]).name)
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(dir_biblioteca() / x["archivo"], destino)
            x["usos"] += 1
            (dir_biblioteca() / "catalogo.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"Copiado a {destino} (uso número {x['usos']}).")
        elif a.cmd == "render":
            m = rendir(Path(a.dir))
            print(f"Final en {a.dir}/out/final.mp4 · {m['duracion_s']} s · {m['lufs']} LUFS · pico {m['pico_dbtp']} dBTP")
            au = m["audio"]
            print(f"Audio: voz {au['voz_lufs']} LUFS · música {au.get('musica_bajo_voz_lu', '—')} LU bajo la voz · efectos {au['efectos']}")
            for aviso in au["avisos"]:
                print(f"  ⚠ {aviso}")
            print(f"Audita {a.dir}/out/hoja.png y {a.dir}/out/portada.png antes de entregar y termina con `cierre` y `catalogar`.")
        elif a.cmd == "cierre":
            d = Path(a.dir)
            ini = d / "estados" / "saldo-inicio.json"
            ahora = saldo()
            (d / "estados").mkdir(exist_ok=True)
            (d / "estados" / "saldo-cierre.json").write_text(json.dumps(ahora))
            print(tabla_saldo(json.loads(ini.read_text()) if ini.exists() else None, ahora))
            print("\nRegistra lo aprendido en este video: vox.py aprender \"...\" [--espacio E]")
        elif a.cmd == "aprender":
            destino = archivo_aprendizajes(a.espacio)
            if not destino.exists():
                destino.write_text(f"# Aprendizajes · {a.espacio}\n\n", encoding="utf-8")
            with destino.open("a", encoding="utf-8") as fh:
                fh.write(f"- {time.strftime('%Y-%m-%d')} · {' '.join(a.texto.split())}\n")
            print(f"Aprendizaje guardado en {destino}")
        elif a.cmd == "aprendizajes":
            print(leer_aprendizajes(a.espacio))
    except ErrorVox as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except (KeyError, ValueError, OSError) as exc:
        print(f"Error: dato inesperado ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
