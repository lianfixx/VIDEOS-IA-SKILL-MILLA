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
COLA = 1.5       # segundos tras la voz: ahí cae el llamado a comentar
ESCENA_LARGA = 7.0  # segundos; más que esto sin cambio de plano se siente lento
LIMITES = {"kicker": 18, "nota": 38, "fuente": 46, "dato": 6, "remate": 14}
# Planos: lo que se ve dentro de una escena. Cada uno entra cuando la voz dice su palabra ancla (`en`).
PLANOS = ("imagen", "cita", "lista", "calendario", "dato", "duo", "flujo", "barras", "linea")
PLANO_VIVO = {"cita", "lista", "calendario", "flujo", "barras", "linea"}  # se mueven solos mientras duran
PLANO_QUIETO = 4.5  # segundos; un recorte o una cifra sin nada nuevo se siente detenido
MAX_PLANOS = 5
# Estilo del video: «collage» (recortes sobre papel) o «pizarra» (motion: casi todo dibujado con código sobre cuadrícula).
ESTILOS_VIDEO = ("collage", "pizarra")
PAPEL_PIZARRA = "#FBFBF7"
MIN_PLANO = 18  # frames; con menos no da tiempo de leerlo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sonido as SON  # noqa: E402  (música y efectos hechos con código)


class ErrorVox(Exception):
    pass


# ---------- espacios y memoria ----------

def dir_espacios() -> Path:
    """Cada espacio (marca) vive en su propia carpeta: espacios/<nombre>/perfil.json."""
    if os.environ.get("VOX_ESPACIOS"):
        return Path(os.environ["VOX_ESPACIOS"])
    if (RAIZ / "espacios").is_dir():  # skill empaquetada para claude.ai: los espacios viajan dentro
        return RAIZ / "espacios"
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


# Marcas de voz dentro de la narración: no se leen ni salen en subtítulos; le dicen a la voz cómo decirlo.
PAUSAS = {"pausa": 0.5, "pausa larga": 1.0}
EXPRESIONES = {"ríe": "laughs", "suspira": "sighs", "carraspea": "clears throat", "susurra": "whispers", "irónica": "sarcastic",
               "sorprendida": "surprised", "seria": "serious", "emocionada": "excited", "lento": "slow", "duda": "hesitates"}
MODELOS_CON_EXPRESION = ("eleven_v3", "eleven_v4")  # entienden etiquetas entre corchetes; los demás, solo pausas
MARCA = re.compile(r"\[([^\[\]]{1,24})\]")
CAMBIO_TEMA = {"silencio": 0.55, "velocidad": 0.9}  # al cambiar de tema: respiro y la escena se dice más despacio
SILENCIO_ENTRE_VOCES = 0.18


def narracion_limpia(s: dict) -> str:
    """La narración sin marcas de voz: lo que se oye como palabras y sale en subtítulos."""
    return " ".join(MARCA.sub(" ", str(s.get("narracion", ""))).split())


def marcas_de(s: dict) -> list[str]:
    return [m.strip().lower() for m in MARCA.findall(str(s.get("narracion", "")))]


def texto_para_voz(s: dict, modelo: str) -> str:
    """Convierte las marcas a lo que entiende el modelo: `<break>` en los clásicos, etiquetas en los expresivos."""
    expresivo = modelo.startswith(MODELOS_CON_EXPRESION)
    def cambia(m: re.Match) -> str:
        k = m.group(1).strip().lower()
        if k in PAUSAS:
            return ("[long pause]" if k == "pausa larga" else "[pause]") if expresivo else f'<break time="{PAUSAS[k]}s" />'
        return f"[{EXPRESIONES[k]}]" if expresivo and k in EXPRESIONES else " "
    return " ".join(MARCA.sub(cambia, str(s.get("narracion", ""))).split())


def sin_etiquetas(palabras: list[dict]) -> list[dict]:
    """Quita de la alineación lo que no es palabra dicha: `<break time="0.5s" />` y `[laughs]`."""
    out, dentro = [], ""
    for w in palabras:
        t = w["t"]
        if not dentro and t.startswith("<break"):
            dentro = "/>"
        elif not dentro and t.startswith("[") and "]" not in t[1:]:
            dentro = "]"
        elif not dentro and re.fullmatch(r"\[[^\[\]]*\][.,;:!?…]*", t):
            continue
        if dentro:
            if dentro in t:
                dentro = ""
            continue
        out.append(w)
    return out


def plan_de_voz(g: dict, perfil: dict) -> list[dict]:
    """Tramos de narración: cada uno es una petición con su voz y velocidad. Sin marcas ni segunda voz, hay uno solo."""
    base = perfil["voz"]
    vel = velocidad_voz(g, base)
    tramos: list[dict] = []
    for i, s in enumerate(g["escenas"]):
        coment = s.get("voz") == "comentario"
        voz = perfil.get("voz_comentario") if coment else base
        if coment and not voz:
            raise ErrorVox(f"la escena {s.get('id')} pide la voz de comentario y el espacio no tiene `voz_comentario` en su perfil")
        cambio = bool(s.get("cambio_tema")) and i > 0
        v = velocidad_voz({}, voz) if coment else vel
        if cambio:
            v = round(max(VELOCIDAD_VOZ[0], v * CAMBIO_TEMA["velocidad"]), 3)
        clave = (voz["voice_id"], voz.get("modelo", "eleven_multilingual_v2"), v)
        nuevo = not tramos or cambio or tramos[-1]["cambio"] or tramos[-1]["clave"] != clave
        if nuevo:
            silencio = 0.0 if not tramos else CAMBIO_TEMA["silencio"] if cambio else SILENCIO_ENTRE_VOCES if tramos[-1]["clave"][0] != clave[0] else 0.0
            tramos.append({"voz": voz, "velocidad": v, "clave": clave, "cambio": cambio, "comentario": coment, "silencio": silencio, "textos": [], "palabras": 0})
        t = tramos[-1]
        t["textos"].append(texto_para_voz(s, clave[1]))
        t["palabras"] += len(narracion_limpia(s).split())
    for t in tramos:
        t["texto"] = " ".join(t.pop("textos"))
    return tramos


def firma_de_voz(g: dict, tramos: list[dict]) -> str:
    """Huella de lo que se narró. Con un solo tramo sin marcas es la de siempre: las voces ya pagadas siguen vigentes."""
    if len(tramos) == 1 and tramos[0]["texto"] == texto_completo(g):
        t = tramos[0]
        return huella(t["texto"], t["voz"]["voice_id"], t["voz"].get("modelo", ""), *([f"vel={t['velocidad']}"] if t["velocidad"] != 1.0 else []))
    return huella("tramos", json.dumps([[t["texto"], *t["clave"], t["silencio"]] for t in tramos], ensure_ascii=False))


def _tramo_narrado(t: dict, previo: str, siguiente: str, pagados: Path | None) -> tuple[bytes, list[dict]]:
    """Narra un tramo, o lo recupera si ya se pagó: un fallo a media narración no vuelve a cobrar lo anterior."""
    clave = huella("tramo", t["texto"], *map(str, t["clave"]), previo, siguiente)
    mp3, js = (pagados / f"{clave}.mp3", pagados / f"{clave}.json") if pagados else (None, None)
    if mp3 and mp3.is_file() and js.is_file():
        return mp3.read_bytes(), json.loads(js.read_text())
    audio, palabras = narrar(t["texto"], t["voz"], t["velocidad"], previo=previo, siguiente=siguiente)
    if pagados:
        pagados.mkdir(parents=True, exist_ok=True)
        mp3.write_bytes(audio)
        js.write_text(json.dumps(palabras))
    return audio, palabras


def narrar_guion(g: dict, perfil: dict, destino: Path, pagados: Path | None = None) -> list[dict]:
    """Narra cada tramo, los une con sus silencios y devuelve las palabras con tiempo real sobre el audio final."""
    tramos = plan_de_voz(g, perfil)
    if len(tramos) == 1:
        audio, palabras = _tramo_narrado(tramos[0], "", "", pagados)
        palabras = sin_etiquetas(palabras)
        if len(palabras) != tramos[0]["palabras"]:
            raise ErrorVox(f"la voz volvió con {len(palabras)} palabras y el guion tiene {tramos[0]['palabras']}; revisa las marcas de voz. "
                           "El audio pagado quedó guardado: al corregir solo las marcas no se vuelve a cobrar si el texto enviado no cambia")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(audio)
        if tramos[0]["comentario"]:
            for w in palabras:
                w["c"] = True
        return palabras
    tmp = Path(tempfile.mkdtemp(prefix="vox-voz-"))
    try:
        return _unir_tramos(tramos, destino, tmp, pagados)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _unir_tramos(tramos: list[dict], destino: Path, tmp: Path, pagados: Path | None) -> list[dict]:
    todas, piezas, reloj = [], [], 0.0
    varias_voces = len({t["clave"][0] for t in tramos}) > 1
    for n, t in enumerate(tramos):
        clasico = not t["clave"][1].startswith(MODELOS_CON_EXPRESION)
        audio, palabras = _tramo_narrado(t, tramos[n - 1]["texto"][-300:] if n and clasico else "",
                                         tramos[n + 1]["texto"][:300] if n + 1 < len(tramos) and clasico else "", pagados)
        palabras = sin_etiquetas(palabras)
        if len(palabras) != t["palabras"]:
            raise ErrorVox(f"el tramo {n + 1} volvió con {len(palabras)} palabras y el guion tiene {t['palabras']}; no se inventan tiempos. "
                           "Los tramos ya pagados quedaron guardados y no se vuelven a cobrar")
        crudo, wav = tmp / f"{n}.mp3", tmp / f"{n}.wav"
        crudo.write_bytes(audio)
        if varias_voces and duracion_audio(crudo) >= 3.0:  # cada voz al mismo nivel antes de unirlas
            normalizar(crudo, wav, VOZ_LUFS)
        else:
            _correr(["ffmpeg", "-y", "-v", "error", "-i", str(crudo), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)])
        if t["silencio"]:
            sil = tmp / f"s{n}.wav"
            _correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(t["silencio"]), "-c:a", "pcm_s16le", str(sil)])
            piezas.append(sil)
            reloj += duracion_audio(sil)
        for w in palabras:
            todas.append({"t": w["t"], "a": w["a"] + reloj, "b": w["b"] + reloj, **({"c": True} if t["comentario"] else {})})
        piezas.append(wav)
        reloj += duracion_audio(wav)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{x}'\n" for x in piezas))
    destino.parent.mkdir(parents=True, exist_ok=True)
    _correr(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista), "-ac", "1", "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "160k", str(destino)])
    return todas


def imagenes_de(s: dict) -> list[str]:
    """Todas las imágenes que usa una escena: la suya y las de sus planos."""
    return list(fichas_de_imagenes(s))


def fichas_de_imagenes(s: dict) -> dict[str, dict]:
    """Cada imagen de la escena con lo que hay que saber de ella: si es foto real y su crédito.

    Solo cuentan la imagen de la escena y las de planos `imagen` y `duo`, y solo rutas dentro de public/.
    """
    out: dict[str, dict] = {}
    def suma(ruta, foto=False, credito=""):
        if isinstance(ruta, str) and ruta and ruta_segura(ruta) and ruta not in out:
            out[ruta] = {"foto_real": bool(foto), "credito": str(credito or "")}
    suma(s.get("imagen_archivo"), s.get("foto_real"), s.get("credito"))
    planos = s.get("planos")
    for pl in planos if isinstance(planos, list) else []:
        if not isinstance(pl, dict):
            continue
        if pl.get("tipo") == "imagen":
            suma(pl.get("imagen_archivo"), pl.get("foto_real"), pl.get("credito"))
        elif pl.get("tipo") == "duo" and isinstance(pl.get("imagenes"), list):
            for x in pl["imagenes"]:
                suma(x)
    return out


SIGNOS_ANCLA = SIGNOS + "«»()[]…%\"'“”‘’—-"


def clave_ancla(palabra: str) -> str:
    return str(palabra).strip(SIGNOS_ANCLA).lower()


def buscar_ancla(palabras: list[str], ancla: str, desde: int = 0) -> int:
    """Índice de la primera palabra de la narración igual al ancla (sin signos, comillas ni mayúsculas), o -1."""
    clave = clave_ancla(ancla)
    for j in range(desde, len(palabras)):
        if clave and clave_ancla(palabras[j]) == clave:
            return j
    return -1


def validar_planos(s: dict, p: str) -> list[str]:
    """Reglas de los planos de una escena. El primero abre la escena; los demás entran con su ancla, en orden."""
    e: list[str] = []
    planos = s.get("planos")
    if planos is None:
        return e
    if not isinstance(planos, list) or not planos or len(planos) > MAX_PLANOS or not all(isinstance(x, dict) for x in planos):
        return [f"{p}: planos debe ser una lista de 1 a {MAX_PLANOS} objetos"]
    narr = narracion_limpia(s).split()
    pos = 0
    anclas: list[int] = []   # palabra con la que entra cada plano
    ultimas: list[int] = []  # última palabra a la que se ancla una pieza de cada plano
    for j, pl in enumerate(planos):
        q = f"{p}, plano {j + 1}"
        tipo = pl.get("tipo")
        anclas.append(-1); ultimas.append(-1)
        if tipo not in PLANOS:
            e.append(f"{q}: tipo {tipo!r} no existe; opciones {list(PLANOS)}")
            continue
        for campo in ("etiqueta", "dato", "origen", "texto", "resaltar", "entre", "credito", "en"):
            if campo in pl and not isinstance(pl[campo], str):
                e.append(f"{q}: `{campo}` debe ser texto")
                pl[campo] = ""
        if tipo not in ("imagen", "duo") and ("imagen_archivo" in pl or "imagenes" in pl):
            e.append(f"{q}: un plano `{tipo}` no lleva imágenes; usa un plano `imagen` o `duo`")
        if j == 0 and pl.get("en"):
            e.append(f"{q}: el primer plano abre la escena; no lleva `en`")
        if j > 0:
            k = buscar_ancla(narr, pl.get("en", ""), pos)
            if k < 0:
                e.append(f"{q}: `en` debe ser una palabra de la narración posterior al plano anterior (se recibió {pl.get('en')!r})")
            else:
                pos = k + 1
                anclas[j] = k
        if tipo == "imagen" and not (isinstance(pl.get("imagen_archivo"), str) and pl["imagen_archivo"] and ruta_segura(pl["imagen_archivo"])):
            e.append(f"{q}: imagen_archivo debe ser una ruta relativa a public/")
        if tipo == "imagen" and pl.get("foto_real") and not 5 <= len(str(pl.get("credito", ""))) <= 60:
            e.append(f"{q}: una foto real exige `credito` (autor y licencia, de 5 a 60 caracteres) a la vista")
        if tipo == "cita":
            texto, marca = " ".join(str(pl.get("texto", "")).split()), " ".join(str(pl.get("resaltar", "")).split())
            if not 12 <= len(texto) <= 150:
                e.append(f"{q}: la cita lleva de 12 a 150 caracteres, copiados de la fuente")
            if marca and marca not in texto:
                e.append(f"{q}: resaltar debe ser un fragmento literal de la cita")
            if not 3 <= len(str(pl.get("origen", ""))) <= 40:
                e.append(f"{q}: una cita exige `origen` (de dónde sale), de hasta 40 caracteres")
        if tipo == "lista":
            items = pl.get("items")
            if not isinstance(items, list) or not 2 <= len(items) <= 4 or not all(isinstance(x, dict) for x in items):
                e.append(f"{q}: la lista lleva de 2 a 4 items")
            else:
                ipos = max(0, pos - 1)  # la primera pieza puede compartir palabra con su plano; las demás van después
                for it in items:
                    if not isinstance(it.get("texto"), str) or not 1 <= len(it["texto"]) <= 16:
                        e.append(f"{q}: cada item lleva texto de hasta 16 caracteres")
                    if it.get("marca", "") not in ("", "si", "no"):
                        e.append(f"{q}: marca debe ser 'si', 'no' o vacía")
                    if it.get("en"):
                        k = buscar_ancla(narr, it["en"], ipos)
                        if k < 0:
                            e.append(f"{q}: el item {it.get('texto')!r} pide una palabra que la narración no dice después ({it['en']!r})")
                        else:
                            ipos = k + 1
                            ultimas[j] = max(ultimas[j], k)
        if tipo == "calendario":
            celdas, dias = pl.get("celdas"), pl.get("dias")
            if celdas is not None:
                if not isinstance(celdas, list) or not 2 <= len(celdas) <= 14 or not all(
                        isinstance(x, dict) and 1 <= len(str(x.get("t", ""))) <= 3 and x.get("estado", "") in ("", "tachado", "marcado") for x in celdas):
                    e.append(f"{q}: celdas lleva de 2 a 14 objetos {{t (hasta 3 letras), estado: '', 'tachado' o 'marcado'}}")
            elif not (isinstance(dias, int) and not isinstance(dias, bool) and 2 <= dias <= 31):
                e.append(f"{q}: el calendario pide `dias` (2 a 31) o `celdas`")
            if len(str(pl.get("etiqueta", ""))) > 30:
                e.append(f"{q}: etiqueta de hasta 30 caracteres")
        if tipo == "dato":
            if not 1 <= len(str(pl.get("dato", ""))) <= LIMITES["dato"]:
                e.append(f"{q}: dato de 1 a {LIMITES['dato']} caracteres")
            if len(str(pl.get("etiqueta", ""))) > 30:
                e.append(f"{q}: etiqueta de hasta 30 caracteres")
        def piezas(nombre: str, campo: str, minimo: int, maximo: int, tope: int) -> list[dict]:
            """Lista de piezas (pasos, hitos, barras, etiquetas) con texto corto y ancla opcional, en orden."""
            xs = pl.get(nombre)
            if not isinstance(xs, list) or not minimo <= len(xs) <= maximo or not all(isinstance(x, dict) for x in xs):
                e.append(f"{q}: `{nombre}` lleva de {minimo} a {maximo} objetos")
                return []
            ipos = max(0, pos - 1)
            for x in xs:
                if not isinstance(x.get(campo), str) or not 1 <= len(x[campo]) <= tope:
                    e.append(f"{q}: cada elemento de `{nombre}` lleva `{campo}` (texto) de hasta {tope} caracteres")
                if x.get("en"):
                    k = buscar_ancla(narr, x["en"], ipos)
                    if k < 0:
                        e.append(f"{q}: `{nombre}` pide una palabra que la narración no dice después ({x['en']!r})")
                    else:
                        ipos = k + 1
                        ultimas[j] = max(ultimas[j], k)
            return xs
        if tipo == "flujo":
            for x in piezas("pasos", "texto", 2, 4, 14):
                if len(str(x.get("nota", ""))) > 22:
                    e.append(f"{q}: la nota de un paso lleva hasta 22 caracteres")
        if tipo == "linea":
            for x in piezas("hitos", "texto", 2, 4, 24):
                if not 1 <= len(str(x.get("fecha", ""))) <= 10:
                    e.append(f"{q}: cada hito lleva `fecha` de hasta 10 caracteres")
        if tipo == "barras":
            for x in piezas("barras", "etiqueta", 2, 4, 16):
                v = x.get("valor")
                if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
                    e.append(f"{q}: cada barra lleva `valor` numérico mayor que cero")
                if len(str(x.get("texto", ""))) > 9:
                    e.append(f"{q}: el texto de una barra lleva hasta 9 caracteres")
            if not 3 <= len(str(pl.get("origen", ""))) <= 40:
                e.append(f"{q}: una gráfica exige `origen` (de dónde salen las cifras), de hasta 40 caracteres")
        if pl.get("etiquetas") is not None:
            if tipo != "imagen":
                e.append(f"{q}: `etiquetas` solo va en planos de imagen")
            for x in piezas("etiquetas", "texto", 1, 3, 16):
                if not all(isinstance(x.get(c), (int, float)) and not isinstance(x.get(c), bool) and 0 <= x[c] <= 1 for c in ("x", "y")):
                    e.append(f"{q}: cada etiqueta lleva `x` e `y` entre 0 y 1 (dónde señala dentro de la imagen)")
        ap = pl.get("apunte")
        if ap is not None:
            if not isinstance(ap, dict) or not 1 <= len(str(ap.get("texto", ""))) <= LIMITES["nota"]:
                e.append(f"{q}: `apunte` lleva `texto` de hasta {LIMITES['nota']} caracteres")
            elif ap.get("en"):
                k = buscar_ancla(narr, ap["en"], max(0, pos - 1))
                if k < 0:
                    e.append(f"{q}: el apunte pide una palabra que la narración no dice después ({ap['en']!r})")
                else:
                    ultimas[j] = max(ultimas[j], k)
            if s.get("nota"):
                e.append(f"{q}: la escena ya lleva `nota`; usa una u otra, no las dos")
        if tipo == "duo":
            imgs = pl.get("imagenes")
            if not isinstance(imgs, list) or len(imgs) != 2 or not all(isinstance(x, str) and x and ruta_segura(x) for x in imgs):
                e.append(f"{q}: un duo lleva dos imágenes (rutas relativas a public/)")
            if len(str(pl.get("entre", ""))) > 3:
                e.append(f"{q}: `entre` lleva hasta 3 letras (O, VS, +)")
    for j in range(len(planos) - 1):  # una pieza anclada después del plano siguiente nunca se vería
        if ultimas[j] >= 0 and anclas[j + 1] >= 0 and ultimas[j] >= anclas[j + 1]:
            e.append(f"{p}, plano {j + 1}: una de sus piezas se ancla a «{narr[ultimas[j]]}», que se dice cuando ya entró el plano {j + 2}; ánclala antes o muévela a ese plano")
    ancla = s.get("remate_en")
    if ancla and buscar_ancla(narr, ancla) < 0:
        e.append(f"{p}: remate_en debe ser una palabra de la narración (se toma su primera aparición)")
    return e


def planos_en_tiempo(s: dict, palabras: list[dict], desde: int, dur: int) -> list[dict]:
    """Planos con su frame de entrada (relativo a la escena), tomado del tiempo real de la palabra ancla."""
    narr = [w["t"] for w in palabras]
    def cuadro(k: int) -> int:
        return max(0, int(round(palabras[k]["a"] * FPS)) - desde - 4)  # entra 4 frames antes de la palabra
    out, pos, previo = [], 0, -MIN_PLANO
    for j, pl in enumerate(s.get("planos") or []):
        en = 0
        if j > 0:
            k = buscar_ancla(narr, pl.get("en", ""), pos)
            if k < 0:
                raise ErrorVox(f"la escena {s['id']} no dice {pl.get('en')!r} después del plano anterior")
            pos = k + 1
            en = max(cuadro(k), previo + MIN_PLANO)
            if en > dur - MIN_PLANO:
                raise ErrorVox(f"el plano {j + 1} de la escena {s['id']} entraría a {dur - en} frames del final; ánclalo antes")
        previo = en
        n: dict = {"tipo": pl["tipo"], "desde": en}
        if pl["tipo"] == "imagen":
            n["imagen"] = pl["imagen_archivo"]
            if pl.get("foto_real"):
                n.update(foto=True, credito=str(pl.get("credito", "")))
        elif pl["tipo"] == "cita":
            n.update(texto=" ".join(str(pl["texto"]).split()), resaltar=" ".join(str(pl.get("resaltar", "")).split()), origen=str(pl["origen"]))
        elif pl["tipo"] == "lista":
            items, ipos = [], max(0, pos - 1)
            for m, it in enumerate(pl["items"]):
                t = en + 8 + 9 * m
                if it.get("en"):
                    k = buscar_ancla(narr, it["en"], ipos)
                    if k >= 0:
                        ipos, t = k + 1, max(cuadro(k), en + 4)
                if items:
                    t = max(t, items[-1]["desde"] + 5)
                items.append({"texto": str(it["texto"]).upper(), "marca": it.get("marca", ""), "desde": t})
            n["items"] = items
        elif pl["tipo"] == "calendario":
            n["celdas"] = pl.get("celdas") or [{"t": str(x + 1), "estado": "tachado"} for x in range(pl["dias"])]
            n["etiqueta"] = str(pl.get("etiqueta", ""))
        elif pl["tipo"] == "dato":
            n.update(dato=str(pl["dato"]), etiqueta=str(pl.get("etiqueta", "")), tachar=bool(pl.get("tachar", False)))
        elif pl["tipo"] == "duo":
            n.update(imagenes=list(pl["imagenes"]), entre=str(pl.get("entre", "")).upper())

        def con_tiempo(xs: list[dict], campos: tuple, paso: int, mayus: tuple = ()) -> list[dict]:
            """Cada pieza entra con su ancla (tiempo real) o, sin ancla, a ritmo fijo tras la anterior."""
            hechos, ipos = [], max(0, pos - 1)
            for m, x in enumerate(xs):
                t = en + 8 + paso * m
                if x.get("en"):
                    k = buscar_ancla(narr, x["en"], ipos)
                    if k >= 0:
                        ipos, t = k + 1, max(cuadro(k), en + 4)
                if hechos:
                    t = max(t, hechos[-1]["desde"] + 6)
                d = {c: (str(x.get(c, "")).upper() if c in mayus else x.get(c, "")) for c in campos}
                hechos.append({**d, "desde": t})
            return hechos
        if pl["tipo"] == "flujo":
            n["pasos"] = con_tiempo(pl["pasos"], ("texto", "nota"), 14, ("texto",))
        elif pl["tipo"] == "linea":
            n["hitos"] = con_tiempo(pl["hitos"], ("fecha", "texto"), 16, ("fecha",))
        elif pl["tipo"] == "barras":
            n["barras"] = con_tiempo(pl["barras"], ("etiqueta", "valor", "texto"), 10, ("etiqueta",))
            n["origen"] = str(pl["origen"])
        if pl.get("etiquetas"):
            n["etiquetas"] = con_tiempo(pl["etiquetas"], ("texto", "x", "y"), 12, ("texto",))
        if pl.get("apunte"):
            n["apunte"] = con_tiempo([pl["apunte"]], ("texto",), 0)[0]
            if not pl["apunte"].get("en"):
                n["apunte"]["desde"] = en + 22
        out.append(n)
    for j, n in enumerate(out):
        n["dur"] = (out[j + 1]["desde"] if j + 1 < len(out) else dur) - n["desde"]
        fin = n["desde"] + n["dur"]
        # Ninguna pieza entra cuando su plano ya se fue: las últimas se adelantan lo justo para verse.
        for clave in ("items", "pasos", "hitos", "barras", "etiquetas"):
            piezas = n.get(clave) or []
            for m in range(len(piezas) - 1, -1, -1):
                tope = fin - 12 - 5 * (len(piezas) - 1 - m)
                piezas[m]["desde"] = max(n["desde"], min(piezas[m]["desde"], tope))
        if n.get("apunte"):
            n["apunte"]["desde"] = max(n["desde"], min(n["apunte"]["desde"], fin - 20))
    return out


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


def efectivas(escenas: list[dict], campo: str, ciclo: list[str]) -> list[str]:
    """Valor final de `entrada` o `transicion` por escena.

    Lo que el guion fija se respeta; lo automático sigue el ciclo y, si coincidiría con la
    escena anterior o con la que el guion fijó para la siguiente, salta a otra opción. Así elegir una a mano nunca
    provoca una repetición con las automáticas de alrededor.
    """
    out: list[str] = []
    for i, s in enumerate(escenas):
        v = s.get(campo)
        if not v:
            vecinas = {out[-1] if out else None, escenas[i + 1].get(campo) if i + 1 < len(escenas) else None}
            v = next((ciclo[(i + k) % len(ciclo)] for k in range(len(ciclo)) if ciclo[(i + k) % len(ciclo)] not in vecinas), ciclo[i % len(ciclo)])
        out.append(v)
    return out


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
    if not isinstance(g.get("cierre", ""), str) or len(g.get("cierre", "")) > 16:
        e.append("cierre: texto de hasta 16 caracteres (sustituye al llamado del espacio solo en este video)")
    if g.get("estilo", "collage") not in ESTILOS_VIDEO:
        e.append(f"estilo {g.get('estilo')!r} no existe; opciones {list(ESTILOS_VIDEO)}")
    bucle = g.get("bucle")
    if bucle is not None:
        ids = [x.get("id") for x in (g.get("escenas") or []) if isinstance(x, dict)]
        if not isinstance(bucle, dict) or len(str(bucle.get("pregunta", ""))) < 8 or bucle.get("cierra") not in ids:
            e.append("bucle: lleva `pregunta` (lo que el gancho deja abierto) y `cierra` (id de la escena que lo responde)")
        elif ids.index(bucle["cierra"]) < 1 or ids.index(bucle["cierra"]) > len(ids) - 2:
            e.append("bucle.cierra: la respuesta llega después del gancho y antes de la pregunta final")
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
    vistos = set()
    if not isinstance(escenas, list) or not all(isinstance(x, dict) for x in escenas):
        return e + ["escenas debe ser una lista de objetos"]
    limpias = [{k: (v if isinstance(v, str) else "") for k, v in x.items() if k in ("entrada", "transicion")} for x in escenas]
    ents, trs = efectivas(limpias, "entrada", ENTRADAS), efectivas(limpias, "transicion", TRANSICIONES)
    for i, s in enumerate(escenas):
        p = f"escena {i + 1}"
        if s.get("id") in vistos or not s.get("id"):
            e.append(f"{p}: id ausente o repetido")
        vistos.add(s.get("id"))
        n = narracion_limpia(s)
        k = " ".join(str(s.get("keyword", "")).split())
        desconocidas = [m for m in marcas_de(s) if m not in PAUSAS and m not in EXPRESIONES]
        if desconocidas:
            e.append(f"{p}: marcas de voz desconocidas {desconocidas}; opciones {sorted(PAUSAS) + sorted(EXPRESIONES)}")
        cruda = str(s.get("narracion", ""))
        if "[" in MARCA.sub(" ", cruda) or "]" in MARCA.sub(" ", cruda) or "<" in cruda or ">" in cruda:
            e.append(f"{p}: los corchetes son solo para marcas de voz como [pausa]; quita corchetes sueltos y los signos < >")
        elif any((m.start() > 0 and not cruda[m.start() - 1].isspace()) or (m.end() < len(cruda) and not cruda[m.end()].isspace()) for m in MARCA.finditer(cruda)):
            e.append(f"{p}: cada marca de voz va separada por espacios y después del signo de puntuación («cheque. [pausa] En pleno…»)")
        if s.get("voz") not in (None, "", "comentario"):
            e.append(f"{p}: `voz` solo admite 'comentario' (la segunda voz del espacio)")
        elif s.get("voz") == "comentario" and g.get("perfil") in conocidos and not conocidos[g["perfil"]].get("voz_comentario"):
            e.append(f"{p}: el espacio {g['perfil']} no tiene `voz_comentario` en su perfil")
        if not isinstance(s.get("cambio_tema", False), bool) or (s.get("cambio_tema") and i == 0):
            e.append(f"{p}: cambio_tema es verdadero o falso y no va en la primera escena")
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
        for campo in ("entrada", "transicion", "sonido", "remate", "kicker", "nota", "dato", "fuente", "resaltar", "imagen_archivo"):
            if not isinstance(s.get(campo, ""), str):
                e.append(f"{p}: {campo} debe ser texto")
                s[campo] = ""
        if s.get("remate") and not s.get("sonido"):
            e.append(f"{p}: un remate cae con su sonido; elige `sonido` para esta escena")
        if s.get("remate") and i == 0:
            e.append(f"{p}: la primera escena ya abre con el gancho; el remate va de la segunda en adelante")
        if s.get("sonido") and s["sonido"] not in SON.EFECTOS:
            e.append(f"{p}: sonido {s['sonido']!r} no existe; opciones {sorted(SON.EFECTOS)}")
        img = s.get("imagen_archivo", "")
        if img and not ruta_segura(img):
            e.append(f"{p}: imagen_archivo debe ser una ruta relativa a public/, sin '..'")
        e.extend(validar_planos(s, p))
        ent = s.get("entrada")
        if ent and ent not in ENTRADAS:
            e.append(f"{p}: entrada {ent!r} no existe; opciones {ENTRADAS}")
        if i > 0 and ents[i] == ents[i - 1]:  # solo puede pasar si el guion fijó las dos
            e.append(f"{p}: repite la entrada de la escena anterior ({ents[i]})")
        tr = s.get("transicion")
        if tr and tr not in set(TRANSICIONES):
            e.append(f"{p}: transicion {tr!r} no existe; opciones {sorted(set(TRANSICIONES))}")
        if i > 1 and trs[i] == trs[i - 1]:
            e.append(f"{p}: repite la transición de la escena anterior ({trs[i]})")
    if escenas and "?" not in str(escenas[-1].get("narracion", "")):
        e.append("la última escena debe narrar la pregunta de cierre (cta_pregunta)")
    return e


def avisos_guion(g: dict) -> list[str]:
    """Oficio del guion: no bloquea, pero un video que ignora estos avisos rara vez queda bien."""
    a: list[str] = []
    escenas = [s for s in (g.get("escenas") or []) if isinstance(s, dict)]
    cuenta = [len(narracion_limpia(s).split()) for s in escenas]
    if not cuenta:
        return a
    if cuenta[0] > 14:
        a.append(f"el gancho tiene {cuenta[0]} palabras; con 14 o menos detiene mejor el scroll")
    try:
        modelo = perfiles()[g.get("perfil")]["voz"].get("modelo", "")
    except (ErrorVox, KeyError):
        modelo = ""
    for i, s in enumerate(escenas):
        mudas = [m for m in marcas_de(s) if m in EXPRESIONES]
        m_esc = (perfiles()[g["perfil"]].get("voz_comentario") or {}).get("modelo", "") if s.get("voz") == "comentario" and modelo else modelo
        if mudas and not m_esc.startswith(MODELOS_CON_EXPRESION):
            a.append(f"escena {i + 1}: las expresiones {mudas} solo las dice un modelo expresivo ({', '.join(MODELOS_CON_EXPRESION)}); con {m_esc or 'esta voz'} se omiten")
    if g.get("estilo") == "pizarra":
        todos = [pl for s in escenas for pl in (s.get("planos") or []) if isinstance(pl, dict)]
        fotos = [pl for pl in todos if pl.get("tipo") in ("imagen", "duo") and not pl.get("foto_real")]
        if not todos:
            a.append("estilo pizarra sin `planos`: en pizarra la historia se dibuja con cita, lista, flujo, línea, barras, calendario y cifras")
        elif len(fotos) * 3 > len(todos):
            a.append(f"estilo pizarra con {len(fotos)} de {len(todos)} planos de imagen generada: en pizarra casi todo se dibuja con código")
    if not g.get("bucle"):
        a.append("falta `bucle`: escribe qué pregunta deja abierta el gancho y en qué escena se responde (NARRATIVA.md)")
    for i, s in enumerate(escenas):
        if s.get("dato") and isinstance(s.get("planos"), list) and s["planos"]:
            a.append(f"escena {i + 1}: lleva `planos`, así que su `dato` de escena no se dibuja; ponlo como plano `dato`")
    primero = (escenas[0].get("planos") or [{}])[0] if isinstance(escenas[0].get("planos"), list) else {}
    if isinstance(primero, dict) and primero.get("tipo") in ("lista", "flujo", "barras", "linea"):
        a.append(f"el video abre con un plano `{primero['tipo']}`, cuyas piezas entran después: el primer cuadro quedaría solo con el titular. Abre con imagen, cita o dato")
    if cuenta[0] > 6 and len(escenas[0].get("planos") or []) < 2:
        a.append("el gancho se queda con una sola imagen: dale un segundo plano para que algo cambie en los primeros 2 s")
    total = sum(cuenta)
    if total < 55:
        a.append(f"{total} palabras en total (~{total / 2.7:.0f} s): muy corto para desarrollar una idea")
    if total > 200:
        a.append(f"{total} palabras en total (~{total / 2.7:.0f} s): pasa de 75 s; recorta o divide en dos videos")
    def n_planos(s: dict) -> int:
        return len(s["planos"]) if isinstance(s.get("planos"), list) else 0
    for i, n in enumerate(cuenta):
        if n > 22 and n_planos(escenas[i]) < 2:
            a.append(f"escena {i + 1}: {n} palabras (~{n / 2.7:.0f} s) sin cambio de plano; divídela en dos o dale `planos`")
        elif n > 12 and n_planos(escenas[i]) < 2:
            a.append(f"escena {i + 1}: {n} palabras con una sola imagen quieta; cuéntala con `planos` (cita, lista, calendario, dato, duo u otra imagen)")
    sin_imagen = [i + 1 for i, s in enumerate(escenas) if not s.get("imagen_archivo") and not s.get("dato") and not n_planos(s)]
    if sin_imagen:
        a.append(f"escenas {sin_imagen} sin imagen ni dato: quedan solo con texto")
    if sum(1 for s in escenas if imagenes_de(s)) < max(2, len(escenas) // 2):
        a.append("menos de la mitad de las escenas lleva imagen; el estilo pide algo que ver casi siempre")
    if not any(s.get("fuente") for s in escenas) and any(ch.isdigit() for s in escenas for ch in str(s.get("narracion", ""))):
        a.append("hay cifras en la narración y ninguna escena muestra `fuente`")
    primeras = [str(s.get("keyword", "")).split()[:1] for s in escenas]
    if len({tuple(x) for x in primeras}) < len(primeras) - 1:
        a.append("varios keywords empiezan igual; varía el arranque")
    return a


def texto_completo(g: dict) -> str:
    return " ".join(narracion_limpia(s) for s in g["escenas"])


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
    conteos = [len(narracion_limpia(s).split()) for s in g["escenas"]]
    if sum(conteos) != len(palabras):
        raise ErrorVox(f"la alineación trae {len(palabras)} palabras y el guion {sum(conteos)}; no se inventan tiempos")
    inicios, pos = [], 0
    for c in conteos:
        if c == 0:
            raise ErrorVox("una escena quedó sin palabras; revisa la narración")
        inicios.append(palabras[pos]["a"])
        pos += c
    total = int(round((duracion + COLA) * FPS))
    cortes = [0] + [max(0, int(round((t - 0.12) * FPS))) for t in inicios[1:]] + [total]
    escenas = []
    ents, trs = efectivas(g["escenas"], "entrada", ENTRADAS), efectivas(g["escenas"], "transicion", TRANSICIONES)
    for i, s in enumerate(g["escenas"]):
        desde, dur = cortes[i], cortes[i + 1] - cortes[i]
        if dur < MIN_ESCENA:
            raise ErrorVox(f"la escena {s['id']} dura {dur} frames; el mínimo es {MIN_ESCENA}. Únela a otra o alarga su narración")
        img = s.get("imagen_archivo", "")
        for x in imagenes_de(s):
            if publico is not None and not (publico / x).is_file():
                raise ErrorVox(f"la escena {s['id']} pide {x} y no existe en {publico}")
        suyas = palabras[sum(conteos[:i]):sum(conteos[:i + 1])]
        planos = planos_en_tiempo(s, suyas, desde, dur)
        remate_en = None
        if s.get("remate") and s.get("remate_en"):
            k = buscar_ancla([w["t"] for w in suyas], s["remate_en"])
            if k >= 0:
                remate_en = max(0, min(int(round(suyas[k]["a"] * FPS)) - desde - 2, dur - 30))  # con tiempo de verse antes del corte
        escenas.append({
            "planos": planos, "remateEn": remate_en, "comentario": s.get("voz") == "comentario",
            "id": s["id"], "desde": desde, "dur": dur,
            "keyword": " ".join(str(s["keyword"]).split()).upper(), "resaltar": limpia(s.get("resaltar") or ""),
            "kicker": s.get("kicker", ""), "nota": s.get("nota", ""), "dato": s.get("dato", ""),
            "fuente": s.get("fuente", ""), "imagen": img, "foto": bool(s.get("foto_real", False)),
            "entrada": ents[i], "transicion": trs[i],
            "sonido": s.get("sonido", ""), "remate": str(s.get("remate", "")).upper(),
        })
    port = g.get("portada") or {}
    con_imagen = next((x for x in escenas if x["imagen"]), None)
    de_plano = next((ruta for s in g["escenas"] for ruta, f in fichas_de_imagenes(s).items() if not f["foto_real"]), "")
    portada = {
        "texto": " ".join(str(port.get("texto") or escenas[0]["keyword"]).split()).upper(),
        "resaltar": limpia(port.get("resaltar") or escenas[0]["resaltar"]),
        "imagen": port.get("imagen_archivo") or (con_imagen["imagen"] if con_imagen else de_plano),
    }
    if portada["imagen"] and publico is not None and not (publico / portada["imagen"]).is_file():
        raise ErrorVox(f"la portada pide {portada['imagen']} y no existe en {publico}")
    animo = (g.get("musica") or {}).get("animo", "ninguna")
    if g.get("estilo") == "pizarra":  # misma marca, sobre pizarra blanca cuadriculada
        perfil = {**perfil, "cuadricula": True, "colores": {**perfil["colores"], "papel": PAPEL_PIZARRA}}
    return {
        "fps": FPS, "ancho": 1080, "alto": 1920, "frames": total,
        "titulo": g["titulo"], "perfil": perfil, "voz": "audio/voz.mp3",
        "musica": "" if animo == "ninguna" else "audio/musica.wav", "animo": animo,
        "finVoz": round(palabras[-1]["b"], 3), "portada": portada, "sfx": True, "escenas": escenas,
        "cierre": str(g.get("cierre") or perfil.get("cierre") or "COMENTA")[:16].upper(),
        "palabras": [{"t": p["t"], "a": round(p["a"], 3), "b": round(p["b"], 3), **({"c": True} if p.get("c") else {})} for p in palabras],
        "etiquetaComentario": str(perfil.get("etiqueta_comentario") or "OPINIÓN")[:14].upper(),
    }


# ---------- red ----------

def _pedir(url: str, *, metodo="GET", cabeceras=None, cuerpo=None, espera=120, tope: int = 64 * 1024 * 1024) -> bytes:
    if urllib.parse.urlparse(url).scheme != "https":
        raise ErrorVox("solo se permiten URLs https")
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo, headers={"User-Agent": "vox-studio/0.4 (video tool; python-urllib)", **(cabeceras or {})})
    if datos is not None:
        req.add_header("Content-Type", "application/json")
    host = urllib.parse.urlparse(url).hostname
    try:
        with urllib.request.urlopen(req, timeout=espera) as r:
            datos_r = r.read(tope + 1)
            if len(datos_r) > tope:
                raise ErrorVox(f"la respuesta de {host} pasa de {tope // (1024 * 1024)} MB; no se descargó")
            return datos_r
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


VELOCIDAD_VOZ = (0.7, 1.2)  # rango que acepta ElevenLabs; 1.0 es la voz tal cual


def velocidad_voz(g: dict, voz: dict) -> float:
    """Velocidad de la narración: `voz_velocidad` del guion o `velocidad` del perfil; 1.0 si no se pide."""
    v = g.get("voz_velocidad", voz.get("velocidad", 1.0))
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not VELOCIDAD_VOZ[0] <= v <= VELOCIDAD_VOZ[1]:
        raise ErrorVox(f"velocidad de voz {v!r} fuera de rango: usa un número entre {VELOCIDAD_VOZ[0]} y {VELOCIDAD_VOZ[1]}")
    return float(v)


def ajustes_voz(velocidad: float = 1.0) -> dict:
    a = {"stability": 0.4, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}
    if velocidad != 1.0:
        a["speed"] = velocidad
    return a


def narrar(texto: str, voz: dict, velocidad: float = 1.0, previo: str = "", siguiente: str = "") -> tuple[bytes, list[dict]]:
    cuerpo = {"text": texto, "model_id": voz.get("modelo", "eleven_multilingual_v2"),
              "voice_settings": ajustes_voz(velocidad)}
    if previo:  # contexto para que la entonación continúe entre tramos
        cuerpo["previous_text"] = previo
    if siguiente:
        cuerpo["next_text"] = siguiente
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


def _loudnorm(audio: Path, objetivo: float = -14.0, extra: str = "") -> dict:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(audio), "-af", f"loudnorm=I={objetivo}:TP=-2:LRA=11{extra}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
    if not m:
        raise ErrorVox(f"no se pudo medir la sonoridad de {audio.name}")
    return json.loads(m.group(0))


def normalizar(entrada: Path, salida: Path, objetivo: float, video: bool = False) -> str:
    """Dos pasadas: se mide y se aplica una ganancia. Devuelve 'linear' si no hubo compresión."""
    m = _loudnorm(entrada, objetivo)
    medido = (f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    tipo = _loudnorm(entrada, objetivo, medido).get("normalization_type", "")
    salida.parent.mkdir(parents=True, exist_ok=True)
    codec = ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"] if video else ["-c:a", "pcm_s16le"]
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(entrada), "-af", f"loudnorm=I={objetivo}:TP=-2:LRA=11{medido}", "-ar", "48000", *codec, str(salida)])
    return tipo


def masterizar(entrada: Path, salida: Path) -> float:
    """Lleva la mezcla a -14 LUFS con una ganancia fija y un limitador de picos; devuelve la ganancia en dB.

    La voz ya entra nivelada, así que la ganancia debe ser pequeña. Una ganancia grande
    significa que la mezcla venía mal balanceada y la auditoría lo avisa.
    """
    ganancia = round(-14.0 - float(_loudnorm(entrada)["input_i"]), 2)
    salida.parent.mkdir(parents=True, exist_ok=True)
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(entrada), "-c:v", "copy",
             "-af", f"volume={ganancia}dB,alimiter=limit=0.75:level=false:attack=3:release=60", "-ar", "48000",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(salida)])
    return ganancia


def medir(video: Path) -> dict:
    d = _loudnorm(video)
    return {"lufs": d.get("input_i"), "pico_dbtp": d.get("input_tp"), "duracion_s": round(duracion_audio(video), 2)}


def hoja_de_fotogramas(video: Path, datos: dict, salida: Path, guia: bool = False) -> None:
    """Un cuadro del inicio, el cambio y la mitad de cada escena, para auditar con los ojos.

    Con `guia` se sombrean las zonas que tapa la interfaz de TikTok (barra superior, botones
    de la derecha y descripción inferior): nada importante debe caer ahí.
    """
    cuadros = [0]
    for e in datos["escenas"]:
        cuadros += [e["desde"] + 2, e["desde"] + e["dur"] // 2]
    cuadros = sorted(set(min(c, datos["frames"] - 1) for c in cuadros + [datos["frames"] - 8]))
    sel = "+".join(f"eq(n\\,{c})" for c in cuadros)
    cols = min(8, len(cuadros))
    filas = -(-len(cuadros) // cols)
    zonas = ""
    if guia:
        zonas = ("drawbox=x=0:y=0:w=1080:h=215:color=red@0.28:t=fill,drawbox=x=0:y=1450:w=1080:h=470:color=red@0.28:t=fill,"
                 "drawbox=x=960:y=760:w=120:h=690:color=red@0.28:t=fill,")
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", f"select='{sel}',{zonas}scale=250:-1,tile={cols}x{filas}",
             "-vsync", "0", "-frames:v", "1", str(salida)])


VOZ_LUFS = -16.0        # la narración se normaliza a este nivel antes del montaje
MUSICA_BAJO_VOZ = 17.0  # LU que la música queda por debajo de la voz
VOL_EFECTO = 0.8        # ganancia de los remates sonoros (salen a -20 dBFS RMS)
LUFS_FINAL = (-15.0, -13.0)
PICO_MAX = -1.5


def auditar_audio(d: Path, datos: dict, final: dict, ganancia_master: float = 0.0) -> dict:
    """Revisión medible del sonido. No sustituye al oído de Emi: no juzga si la música gusta."""
    import math
    avisos = []
    voz = float(_loudnorm(d / "public" / datos["voz"])["input_i"])
    informe = {"voz_lufs": voz, "final_lufs": float(final["lufs"]), "final_pico_dbtp": float(final["pico_dbtp"]), "ganancia_master_db": ganancia_master}
    if abs(voz - VOZ_LUFS) > 1.5:
        avisos.append(f"la voz mide {voz} LUFS y debía quedar en {VOZ_LUFS}: vuelve a ejecutar `armar`")
    if datos.get("musica"):
        mus = float(_loudnorm(d / "public" / datos["musica"])["input_i"])
        bajo_voz = voz - (mus + 20 * math.log10(datos.get("volMusica", 0.09)))
        informe["musica_bajo_voz_lu"] = round(bajo_voz, 1)
        if bajo_voz < 12:
            avisos.append(f"la música queda solo {bajo_voz:.1f} LU bajo la voz (mínimo 12): puede taparla")
        if bajo_voz > 26:
            avisos.append(f"la música queda {bajo_voz:.1f} LU bajo la voz: casi no se oirá")
    elif datos.get("animo") != "ninguna":
        avisos.append("el video no lleva música")
    if not LUFS_FINAL[0] <= informe["final_lufs"] <= LUFS_FINAL[1]:
        avisos.append(f"sonoridad final {informe['final_lufs']} LUFS fuera de -14 ± 1")
    if informe["final_pico_dbtp"] > PICO_MAX:
        avisos.append(f"pico {informe['final_pico_dbtp']} dBTP por encima de {PICO_MAX}")
    if abs(ganancia_master) > 4:
        avisos.append(f"el master tuvo que mover {ganancia_master:+.1f} dB: la mezcla venía desbalanceada respecto a la voz")
    niveles = {}
    for nombre in sorted({e["sonido"] for e in datos["escenas"] if e.get("sonido")}):
        f = d / "public" / "sfx" / f"{nombre}.wav"
        if not f.is_file():
            avisos.append(f"falta el efecto {nombre} en public/sfx")
            continue
        sobre_voz = SON.leer_nivel(f) + 20 * math.log10(datos.get("volEfecto", VOL_EFECTO)) - voz
        niveles[nombre] = round(sobre_voz, 1)
        if sobre_voz > 0:
            avisos.append(f"el efecto {nombre} suena {sobre_voz:.1f} dB por encima de la voz")
        if sobre_voz < -16:
            avisos.append(f"el efecto {nombre} queda {-sobre_voz:.1f} dB bajo la voz: apenas se oirá")
    informe["efectos_respecto_a_voz_db"] = niveles
    silencio = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(d / "out" / "final.mp4"), "-af", "silencedetect=n=-45dB:d=1.2", "-f", "null", "-"],
                              capture_output=True, text=True).stderr.count("silence_start")
    if silencio:
        avisos.append(f"{silencio} silencio(s) de más de 1.2 s")
    informe["avisos"] = avisos
    (d / "out" / "auditoria-audio.json").write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    return informe


ZONAS_TIKTOK = {"barra superior": (0, 0, 1080, 215), "descripción inferior": (0, 1450, 1080, 1920), "botones de la derecha": (960, 760, 1080, 1450)}


def auditar_video(d: Path, datos: dict) -> dict:
    """Revisión medible de la imagen: formato del archivo, contenido en zonas tapadas y cuadros vacíos."""
    import numpy as np
    from PIL import Image
    final = d / "out" / "final.mp4"
    avisos = []
    sonda = json.loads(_correr(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(final)],
                               capture_output=True, text=True).stdout)
    v = next(x for x in sonda["streams"] if x["codec_type"] == "video")
    au = next((x for x in sonda["streams"] if x["codec_type"] == "audio"), {})
    formato = {"codec": v["codec_name"], "ancho": v["width"], "alto": v["height"], "fps": v["r_frame_rate"], "pix_fmt": v["pix_fmt"],
               "audio": au.get("codec_name"), "audio_hz": au.get("sample_rate"), "kbps": round(int(sonda["format"]["bit_rate"]) / 1000),
               "duracion_s": round(float(sonda["format"]["duration"]), 2)}
    esperado = {"codec": "h264", "ancho": 1080, "alto": 1920, "fps": "30/1", "pix_fmt": "yuv420p", "audio": "aac", "audio_hz": "48000"}
    for k, val in esperado.items():
        if formato[k] != val:
            avisos.append(f"formato: {k} es {formato[k]} y debía ser {val}")
    if abs(formato["duracion_s"] - datos["frames"] / FPS) > 0.15:
        avisos.append(f"el archivo dura {formato['duracion_s']} s y la línea de tiempo {datos['frames'] / FPS:.2f} s")
    papel = np.array([int(datos["perfil"]["colores"]["papel"][i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32)

    def cuadro(n: int):
        tmp = d / "out" / "_cuadro.png"
        _correr(["ffmpeg", "-y", "-v", "error", "-i", str(final), "-vf", f"select='eq(n\\,{n})'", "-vsync", "0", "-frames:v", "1", str(tmp)])
        with Image.open(tmp) as im:
            a = np.asarray(im.convert("RGB")).astype(np.float32)
        tmp.unlink(missing_ok=True)
        return np.linalg.norm(a - papel, axis=2) > 90  # tinta: lo que no es papel (el grano y la viñeta no llegan a 90)

    ocupacion = {}
    for e in datos["escenas"]:  # a tres cuartos de cada escena ya entró todo y no hay transición encima
        tinta = cuadro(min(datos["frames"] - 1, e["desde"] + int(e["dur"] * 0.75)))
        for nombre, (x0, y0, x1, y1) in ZONAS_TIKTOK.items():
            frac = float(tinta[y0:y1, x0:x1].mean())
            ocupacion[f"{e['id']} · {nombre}"] = round(frac * 100, 2)
            if frac > 0.004:
                avisos.append(f"escena {e['id']}: hay contenido bajo la {nombre} de TikTok ({frac * 100:.1f} % de esa zona)")
        util = float(tinta[230:1440, 90:960].mean())
        if util < 0.06:
            avisos.append(f"escena {e['id']}: el cuadro está casi vacío ({util * 100:.0f} % de tinta en la zona útil)")
    if float(cuadro(0)[230:1440, 90:960].mean()) < 0.06:
        avisos.append("el primer cuadro está casi vacío: no detiene el scroll")
    informe = {"formato": formato, "ocupacion_zonas_tapadas_pct": ocupacion, "avisos": avisos}
    (d / "out" / "auditoria-video.json").write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    return informe


def rendir(d: Path) -> dict:
    datos = json.loads((d / "src" / "data" / "video.json").read_text(encoding="utf-8"))
    cmd = ["npx", "remotion", "render", "src/index.ts", "Vox", "out/video.mp4", "--props=src/data/video.json",
           "--codec=h264", "--audio-codec=aac", "--pixel-format=yuv420p", "--log=error",
           "--crf=16", "--jpeg-quality=95", "--color-space=bt709"]  # fuente limpia: TikTok vuelve a comprimir
    navegador = os.environ.get("VOX_NAVEGADOR", "/usr/local/bin/chrome-headless-shell")
    if Path(navegador).exists():
        cmd.append(f"--browser-executable={navegador}")
    _correr(cmd, cwd=d)
    foto = ["npx", "remotion", "still", "src/index.ts", "Portada", "out/portada.png", "--props=src/data/video.json", "--log=error"]
    _correr(foto + [c for c in cmd if c.startswith("--browser-executable")], cwd=d)
    tipo = masterizar(d / "out" / "video.mp4", d / "out" / "final.mp4")
    hoja_de_fotogramas(d / "out" / "final.mp4", datos, d / "out" / "hoja.png")
    hoja_de_fotogramas(d / "out" / "final.mp4", datos, d / "out" / "hoja-tiktok.png", guia=True)
    m = medir(d / "out" / "final.mp4")
    m["audio"] = auditar_audio(d, datos, m, tipo)
    m["video"] = auditar_video(d, datos)
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


def miniatura_commons(url_imagen: str, ancho: int = 960) -> str:
    """URL de la versión reducida estándar de un original de Wikimedia Commons; cadena vacía si no lo es."""
    m = re.match(r"https://upload\.wikimedia\.org/wikipedia/commons/([0-9a-f])/([0-9a-f]{2})/([^/?#]+)(?:[?#].*)?$", url_imagen)
    if not m:
        return ""
    nombre = m.group(3)
    extra = ".jpg" if nombre.lower().endswith((".tif", ".tiff")) else ".png" if nombre.lower().endswith(".svg") else ""
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{m.group(1)}/{m.group(2)}/{nombre}/{ancho}px-{nombre}{extra}"


def licencia_commons(url_imagen: str) -> dict | None:
    """Autor y licencia de un archivo de Wikimedia Commons, leídos de su propia ficha."""
    u = urllib.parse.urlparse(url_imagen)
    if u.hostname != "upload.wikimedia.org" or not u.path.startswith("/wikipedia/commons/"):
        return None  # los archivos locales de cada Wikipedia (uso legítimo) no son de Commons
    partes = u.path.split("/")
    # En una miniatura (/thumb/a/ab/Nombre.jpg/1200px-Nombre.jpg) el archivo real es el penúltimo segmento.
    nombre = urllib.parse.unquote(partes[-2] if "thumb" in partes else partes[-1])
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
    g = _guion(str(d / "guion.json"))
    dir_biblioteca().mkdir(parents=True, exist_ok=True)
    cat = leer_catalogo()
    conocidos = {x["sha256"] for x in cat}
    nuevos = []
    for s, img, ficha in [(s, x, f) for s in g["escenas"] for x, f in fichas_de_imagenes(s).items()]:
        origen = d / "public" / img
        if not origen.is_file():
            continue
        sha = hashlib.sha256(origen.read_bytes()).hexdigest()
        if sha in conocidos:
            continue
        prompt_f = d / "prompts" / (Path(img).stem + ".txt")
        ident = f"{g['perfil']}-{d.name}-{Path(img).stem}-{sha[:8]}"  # el sha evita choques si la imagen se regenera
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
                "descripcion": s.get("descripcion_imagen", ""), "foto_real": ficha["foto_real"], "credito": ficha["credito"],
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
    import math
    cruda = d / "public" / "audio" / "voz.mp3"
    video = armar_video(g, palabras, duracion_audio(cruda), perfiles()[g["perfil"]], d / "public")
    # La voz manda: se lleva a un nivel fijo y todo lo demás se coloca respecto a ella.
    normalizar(cruda, d / "public" / "audio" / "voz-n.wav", VOZ_LUFS)
    video["voz"] = "audio/voz-n.wav"
    # Sonido nuevo para cada video: la semilla sale de su propio texto.
    semilla = int(huella(g["titulo"], texto_completo(g))[:8], 16)
    plan = SON.plan_musica(video["animo"], semilla) if video["musica"] else {"tonica": 48}
    SON.sintetizar_efectos(d / "public" / "sfx", semilla, plan["tonica"])
    video["volEfecto"] = VOL_EFECTO
    pista, receta = d / "public" / "audio" / "musica.wav", d / "estados" / "musica.json"
    if video["musica"]:  # pista original, a la medida exacta y siguiendo los cambios de escena
        cortes = [e["desde"] / FPS for e in video["escenas"][1:]]
        SON.guardar(pista, SON.componer(video["animo"], video["frames"] / FPS, semilla, cortes), nivel=-20.0)
        mus = float(_loudnorm(pista)["input_i"])
        video["volMusica"] = round(min(1.0, 10 ** ((VOZ_LUFS - MUSICA_BAJO_VOZ - mus) / 20)), 4)
        receta.parent.mkdir(exist_ok=True)
        receta.write_text(json.dumps(plan))
    else:  # sin música: no dejar restos de un armado anterior
        pista.unlink(missing_ok=True)
        receta.unlink(missing_ok=True)
    for e in video["escenas"]:  # ritmo real, medido en la voz
        for j, pl in enumerate(e.get("planos") or []):
            extra = len(pl.get("etiquetas") or []) + (1 if pl.get("apunte") else 0)
            if pl["tipo"] not in PLANO_VIVO and not extra and pl["dur"] / FPS > PLANO_QUIETO and not (j == len(e["planos"]) - 1 and e is video["escenas"][-1]):
                print(f"⚠ escena {e['id']}, plano {j + 1} ({pl['tipo']}): {pl['dur'] / FPS:.1f} s sin nada nuevo; añade otro plano, un apunte o etiquetas")
        if e["dur"] / FPS > ESCENA_LARGA and len(e.get("planos") or []) < 2:
            print(f"⚠ la escena {e['id']} dura {e['dur'] / FPS:.1f} s: divídela o acepta el pulso automático a media escena")
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
    p.add_argument("--estilo", choices=sorted(ESTILOS), default=None); p.add_argument("--perfil", default=""); p.add_argument("--modelo", choices=sorted(MODELOS_KIE), default="nano-banana-2-lite")
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
            for x in avisos_guion(g):
                print("⚠", x)
            return 1 if errores else 0
        elif a.cmd in {"voz", "armar"}:
            g = _guion(a.guion)
            perfil = perfiles()[g["perfil"]]
            d = Path(a.dir)
            cache = d / "estados" / "voz.json"
            tramos = plan_de_voz(g, perfil)
            firma = firma_de_voz(g, tramos)  # un solo tramo sin marcas conserva la huella de siempre
            letras = sum(len(t["texto"]) for t in tramos)
            guardado = json.loads(cache.read_text()) if cache.exists() else {}
            vigente = guardado.get("firma") == firma and (d / "public" / "audio" / "voz.mp3").is_file()
            if vigente:
                video = _escribir_video(g, d, guardado["palabras"])
                print(f"video.json reconstruido con la voz ya pagada: {video['frames'] / FPS:.1f} s. No se gastó nada.")
            elif a.cmd == "armar":
                raise ErrorVox("la narración cambió o no existe: ejecuta `voz --execute` (esto sí gasta caracteres)")
            elif not a.execute:
                print(f"En seco: {letras} caracteres en {len(tramos)} tramo(s). Añade --execute para narrar.")
                for n, t in enumerate(tramos):
                    print(f"  tramo {n + 1}: {t['voz']['nombre']} · velocidad {t['velocidad']} · {len(t['texto'])} caracteres"
                          + (" · cambio de tema (respiro y más despacio)" if t["cambio"] else "") + (" · comentario" if t["comentario"] else ""))
            else:
                palabras = narrar_guion(g, perfil, d / "public" / "audio" / "voz.mp3", d / "estados" / "tramos")
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({"firma": firma, "palabras": palabras}))  # antes de armar: lo pagado no se pierde
                video = _escribir_video(g, d, palabras)
                print(f"Voz lista: {letras} caracteres en {len(tramos)} tramo(s), {video['frames'] / FPS:.1f} s, {len(palabras)} palabras con tiempo real.")
        elif a.cmd == "imagen":
            if a.perfil and a.perfil not in perfiles():
                raise ErrorVox(f"espacio desconocido: {a.perfil}")
            a.estilo = a.estilo or (perfiles()[a.perfil].get("estilo_imagen") if a.perfil else None) or "ilustracion"
            if a.estilo not in ESTILOS:
                raise ErrorVox(f"estilo_imagen {a.estilo!r} del espacio no existe")
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
            if not 0 <= a.indice < len(est["candidatas"]):
                raise ErrorVox(f"--indice entre 0 y {len(est['candidatas']) - 1}")
            f = est["candidatas"][a.indice]
            destino = Path(a.out)
            if Path(a.dir).resolve() not in destino.resolve().parents:
                raise ErrorVox("--out debe quedar dentro de la producción (--dir)")
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
            try:
                datos_img = _pedir(f["imagen"], espera=60, tope=15 * 1024 * 1024)
            except ErrorVox as exc:
                reducida = miniatura_commons(f["imagen"])
                if "429" not in str(exc) or not reducida:
                    raise
                # Wikimedia limita los originales; sus tamaños estándar sí se sirven y bastan para un video vertical.
                print("Wikimedia limitó el original; se baja la versión de 960 px de la misma foto.")
                datos_img = _pedir(reducida, espera=60, tope=15 * 1024 * 1024)
                f["imagen_bajada"] = reducida
            try:
                import io
                from PIL import Image
                Image.open(io.BytesIO(datos_img)).verify()
            except Exception as exc:  # noqa: BLE001 - lo bajado no es una imagen
                raise ErrorVox("lo descargado no es una imagen válida; no se guardó") from exc
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(datos_img)
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
            destino = Path(a.dir) / "public" / "img" / Path(a.como or x["archivo"]).name  # solo el nombre: nunca fuera de la producción
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(dir_biblioteca() / x["archivo"], destino)
            x["usos"] += 1
            (dir_biblioteca() / "catalogo.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"Copiado a {destino} (uso número {x['usos']}).")
        elif a.cmd == "render":
            m = rendir(Path(a.dir))
            print(f"Final en {a.dir}/out/final.mp4 · {m['duracion_s']} s · {m['lufs']} LUFS · pico {m['pico_dbtp']} dBTP")
            au = m["audio"]
            print(f"Audio: voz {au['voz_lufs']} LUFS · música {au.get('musica_bajo_voz_lu', '—')} LU bajo la voz · efectos respecto a la voz (dB) {au['efectos_respecto_a_voz_db']} · master {au['ganancia_master_db']:+.1f} dB")
            fm = m["video"]["formato"]
            print(f"Imagen: {fm['codec']} {fm['ancho']}x{fm['alto']} {fm['fps']} {fm['pix_fmt']} · {fm['kbps']} kbps")
            for aviso in au["avisos"] + m["video"]["avisos"]:
                print(f"  ⚠ {aviso}")
            if not au["avisos"] and not m["video"]["avisos"]:
                print("  Sin avisos automáticos de audio ni de imagen.")
            print(f"Audita {a.dir}/out/hoja.png, {a.dir}/out/hoja-tiktok.png (zonas que tapa TikTok en rojo) y {a.dir}/out/portada.png antes de entregar y termina con `cierre` y `catalogar`.")
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
            if a.espacio:
                print(f"Quedó solo para «{a.espacio}»: úsalo únicamente para el espíritu de esa marca (tono, público, voz, límites, aprobaciones). "
                      "Lo técnico, de oficio o de proceso vale para todos los espacios: guárdalo sin --espacio.")
        elif a.cmd == "aprendizajes":
            print(leer_aprendizajes(a.espacio))
    except ErrorVox as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except (KeyError, ValueError, OSError, IndexError, TypeError) as exc:
        print(f"Error: dato inesperado ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
