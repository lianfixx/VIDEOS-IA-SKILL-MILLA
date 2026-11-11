#!/usr/bin/env python3
"""Pizarra Studio: videos dibujados a mano (pizarrón, acuarela, cuaderno, minimal) para los espacios de Emi.

Orquesta el motor público `santmun/video-pizarra` (SVG + GSAP y canvas, render cuadro por cuadro).
Ese motor NO vive en este repositorio: no tiene licencia de redistribución, así que se instala
aparte, fijado al commit revisado. Aquí están las reglas, la entrevista, la voz, la música, la
mezcla, las auditorías y el registro.

Subcomandos (sin --execute nada llama a un proveedor de pago):
  instalar                                  clona el motor en el commit revisado y comprueba dependencias
  motor                                     commit instalado y si el autor publicó algo nuevo
  proyecto productions/E/TEMA --perfil E --modo pizarron|estilos [--estilo acuarela|acuarela-viva|cuaderno|minimal]
  entrevista DIR                            qué falta preguntarle a Emi antes de producir (brief.json)
  voz DIR [--execute]                       narra con la voz del espacio; deja audio/vo.wav, words.json y tiempos.json
  musica DIR --animo A [--segundos N]       música original por código + rejilla de beats exacta
  qa DIR [--cada 1.2]                       cuadros de prueba de todo el video + hoja con guía de TikTok
  render DIR [--prueba]                     render + mezcla + master a -14 LUFS + auditoría + copia ligera
  revisar DIR [--prueba]                    hojas de transiciones y de tamaño teléfono + informe de revisión (obligatorio antes de `cierre`)
  cierre DIR                                tabla de gastado y restante por proveedor
  aprender "TEXTO" [--espacio E] / aprendizajes [--espacio E]

Usa las mismas llaves que Vox Studio (ElevenLabs, Kie, Apify): en la nube las inyecta el proxy.
Necesita la carpeta hermana `skills/vox-studio/scripts` (voz, saldos, niveles, espacios).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ.parent / "vox-studio" / "scripts"))
try:
    import vox  # voz, saldos, niveles, espacios y aprendizajes: una sola implementación
except ModuleNotFoundError as exc:  # pragma: no cover - mensaje para quien copie la skill suelta
    raise SystemExit(f"Pizarra Studio necesita skills/vox-studio/scripts junto a ella ({exc}). Usa el repositorio completo.") from exc

SON = vox.SON
ErrorVox = vox.ErrorVox

MOTOR_REPO = "https://github.com/santmun/video-pizarra"
MOTOR_COMMIT = "dc6adc4198027f26c60f5980c956e0a678e05aed"  # revisado el 2026-11-11; cambiarlo exige revisar el código nuevo
MODOS = {"pizarron": "template", "estilos": "template-estilos"}
ESTILOS = ["acuarela", "acuarela-viva", "cuaderno", "minimal"]
FORMATOS = {"9:16": (1080, 1920), "16:9": (1920, 1080)}

# Lo que hay que saber antes de producir. Cada campo es una pregunta para Emi; ninguno se inventa.
PREGUNTAS = {
    "tema": "¿De qué trata el video y cuál es la UNA idea que debe quedarse el espectador?",
    "opinion_emi": "¿Cuál es tu postura? ¿Qué quieres criticar, defender o provocar? ¿Algún chiste o referencia tuya?",
    "publico": "¿Para quién es exactamente (edad, qué le duele, qué sabe del tema)?",
    "objetivo": "¿Qué debe lograr: educar, vender, agendar citas, ganar seguidores, abrir debate?",
    "fuentes": "¿Qué datos, links o documentos debe usar? (o «investiga tú y enséñame las fuentes»)",
    "formato": "¿Vertical 9:16 (TikTok/Reels/Shorts) u horizontal 16:9 (YouTube)?",
    "duracion_s": "¿Cuánto dura: 30, 45, 60 o 75 segundos?",
    "tono": "¿Qué tono: divertido y cercano, serio, salseante, épico? ¿Qué tanto humor?",
    "estilo": "¿Pizarrón clásico, acuarela, acuarela viva, cuaderno o minimal? (se le muestra el catálogo)",
    "personaje": "¿Lleva personaje? ¿Una persona dibujada, tu foto, una mascota propia, o ninguno?",
    "voz": "¿Con voz narrada (la del espacio), con tu propia voz grabada, o solo texto en pantalla?",
    "musica": "¿Música: qué ánimo (tension, energia, serio, ironia, motivacion) o sin música?",
    "efectos": "¿Con efectos de sonido del dibujo (plumón, gis, golpes) o sin efectos?",
    "gancho": "¿Cuál de los 2 o 3 ganchos propuestos para ESTE tema eliges?",
    "cta": "¿Con qué cierra: pregunta para comentar, seguir, link, WhatsApp, nada?",
    "marca": "¿Lleva nombre, @ o logo del espacio en pantalla, o explícitamente no?",
    "referencias": "¿Tienes una imagen o video de referencia de cómo quieres que se vea? (o «ninguna»)",
}
APROBACIONES = {
    "resumen": "Emi aprobó el resumen: lo que respondió frente a lo que se decidió por defecto",
    "storyboard": "Emi aprobó el storyboard (una línea por escena) antes de animar",
}
TEMPORALES = ("out/_mudo.mp4", "out/_bruto.mp4", "out/_m2.mp4", "audio/_cama.wav", "audio/_cama-l.wav", "audio/_music.wav")


# ---------- motor ----------

def dir_motor() -> Path:
    """Carpeta propia: no se comparte con la skill original para que nadie la actualice por su cuenta."""
    return Path(os.environ.get("PIZARRA_MOTOR") or Path.home() / ".cache" / "pizarra-studio" / "motor")


def navegador() -> str:
    """Chromium ya instalado, si existe de verdad. Vacío = que Playwright use el suyo."""
    env = os.environ.get("CHROME_PATH", "")
    if env and Path(env).is_file():
        return env
    raices = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), "/opt/pw-browsers",
              str(Path.home() / ".cache" / "ms-playwright"), str(Path.home() / "Library" / "Caches" / "ms-playwright")]
    hallados = []
    for r in raices:
        if r and Path(r).is_dir():
            for patron in ("chromium-*/chrome-linux*/chrome", "chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"):
                hallados += [p for p in Path(r).glob(patron) if p.is_file()]
    if not hallados:
        return ""
    numero = lambda p: int(re.sub(r"\D", "", p.parts[-3 if "linux" in p.parts[-2] else -5]) or 0)
    return str(max(hallados, key=numero))


def _git(*args: str, cwd: Path | None = None) -> str:
    return vox._correr(["git", *args], cwd=cwd, capture_output=True, text=True).stdout.strip()


def commit_instalado() -> str:
    m = dir_motor()
    if not (m / ".git").is_dir():
        return ""
    try:
        return _git("rev-parse", "HEAD", cwd=m)
    except ErrorVox:
        return ""


def exigir_motor() -> Path:
    c = commit_instalado()
    if not c:
        raise ErrorVox("el motor no está instalado: ejecuta `pizarra.py instalar`")
    if c != MOTOR_COMMIT:
        raise ErrorVox(f"el motor instalado ({c[:7]}) no es el commit revisado ({MOTOR_COMMIT[:7]}): ejecuta `pizarra.py instalar`")
    if _git("status", "--porcelain", "--", "template", "template-estilos", cwd=dir_motor()):
        raise ErrorVox(f"el motor en {dir_motor()} tiene archivos modificados respecto al commit revisado: bórralo y ejecuta `pizarra.py instalar`")
    return dir_motor()


def instalar() -> list[str]:
    m = dir_motor()
    if commit_instalado() != MOTOR_COMMIT:
        if m.exists() and any(m.iterdir()) and not (m / ".git").is_dir():
            raise ErrorVox(f"{m} existe y no es un clon del motor; revísalo antes de continuar")
        m.mkdir(parents=True, exist_ok=True)
        if not (m / ".git").is_dir():
            _git("init", "-q", cwd=m)
            _git("remote", "add", "origin", MOTOR_REPO, cwd=m)
        _git("fetch", "-q", "--depth", "1", "origin", MOTOR_COMMIT, cwd=m)
        _git("checkout", "-q", "FETCH_HEAD", cwd=m)
    exigir_motor()
    faltan = [p for p in ("node", "npm", "ffmpeg", "ffprobe") if not shutil.which(p)]
    for mod in ("numpy", "PIL", "scipy"):
        if subprocess.run([sys.executable, "-c", f"import {mod}"], capture_output=True).returncode != 0:
            faltan.append(f"python:{mod}")
    if not navegador():
        faltan.append("chromium (instala el de Playwright con `npx playwright install chromium` o define CHROME_PATH)")
    return faltan


# ---------- marca del espacio -> configuración del motor ----------

def marca_para_motor(perfil: dict, modo: str, estilo: str = "") -> dict:
    """Traduce el perfil del espacio a lo que entiende cada motor. No inventa colores."""
    c = perfil["colores"]
    if modo == "pizarron":  # este motor trae sus tipografías de trazo a mano; la marca entra por el color
        return {"palette": {"ink": c["tinta"], "orange": c["acento"], "cream": c["papel"], "paper": c["papel"]},
                "hatches": {"marca": [c["acento"], c["tinta"]], "apoyo": [c["apoyo"], c["tinta"]]},
                "mascotTheme": "marca"}
    serif = perfil.get("titular") == "Gelasio"
    return {"style": estilo or "minimal", "palette": {"accent": c["acento"], "bg": c["papel"]},
            "font": {"display": "Gelasio" if serif else "Anton", "body": "Montserrat" if serif else "Poppins"},
            "mascotColor": c["acento"], "mascot": "none", "person": False,  # sin personaje: preferencia de Emi
            "words": "audio/words.json"}  # subtítulos con los tiempos reales de la voz (si no existe, el motor usa `say`)


# ---------- entrevista ----------

def faltantes(brief: dict) -> dict:
    """Preguntas sin responder y aprobaciones pendientes. Solo cuenta un texto real; la aprobación, solo `true`."""
    r, ap = brief.get("respuestas"), brief.get("aprobaciones")
    if not isinstance(r, dict) or not isinstance(ap, dict):
        raise ErrorVox("brief.json debe traer `respuestas` y `aprobaciones` como objetos")
    sin = {k: q for k, q in PREGUNTAS.items() if not (isinstance(r.get(k), str) and r[k].strip())}
    if "opinion_emi" not in sin and len(r["opinion_emi"].strip()) < 20:
        sin["opinion_emi"] = PREGUNTAS["opinion_emi"] + " (hace falta su postura real, no una frase de relleno)"
    return {"preguntas": sin, "aprobaciones": {k: v for k, v in APROBACIONES.items() if ap.get(k) is not True}}


def preferencias() -> dict:
    """Lo que Emi ya decidió para todos sus videos estilo pizarra; no se le vuelve a preguntar."""
    f = vox.dir_espacios() / "PREFERENCIAS-PIZARRA.json"
    if not f.is_file():
        return {}
    r = json.loads(f.read_text(encoding="utf-8")).get("respuestas") or {}
    return {k: v for k, v in r.items() if k in PREGUNTAS and isinstance(v, str) and v.strip()}


def leer_brief(d: Path) -> dict:
    f = d / "brief.json"
    if not f.is_file():
        raise ErrorVox(f"no existe {f}: crea la producción con `proyecto`")
    return json.loads(f.read_text(encoding="utf-8"))


def exigir_aprobado(d: Path) -> dict:
    b = leer_brief(d)
    f = faltantes(b)
    if f["preguntas"] or f["aprobaciones"]:
        pend = list(f["preguntas"]) + [f"aprobación: {k}" for k in f["aprobaciones"]]
        raise ErrorVox("falta completar la entrevista con Emi antes de producir: " + ", ".join(pend))
    return b


def leer_formato(texto: str) -> tuple[int, int]:
    t = str(texto).lower()
    return FORMATOS["16:9"] if ("16:9" in t or "horizontal" in t) else FORMATOS["9:16"]


def leer_duracion(texto: str) -> tuple[float, float] | None:
    """Rango pedido en segundos: «60», «45 a 60», «1:00», «1 minuto». None si no se entiende."""
    t = str(texto).lower()
    m = re.fullmatch(r"\s*(\d+):(\d{2})\s*", t)
    if m:
        v = int(m.group(1)) * 60 + int(m.group(2))
        return (v, v)
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", t)]
    if not nums:
        return None
    if "min" in t:
        nums = [n * 60 for n in nums]
    return (min(nums[:2]), max(nums[:2]))


def sin_efectos(texto: str) -> bool:
    t = str(texto).strip().lower()
    return t.startswith(("no", "sin")) or "solo voz" in t


TECHOS_LIMITADOR = (0.75, 0.68, 0.62, 0.56)  # del más abierto al más cerrado; se usa el primero que deja el pico en rango


# ---------- sincronía ----------

def desfase_ms(a, b, paso_ms: float = 1.0, maximo: int = 300) -> int:
    """Cuánto hay que retrasar `a` para que coincida con `b` (envolventes al mismo paso). Positivo: `b` va tarde."""
    import numpy as np
    n = min(len(a), len(b))
    a = np.asarray(a[:n], dtype=float) - float(np.mean(a[:n])); b = np.asarray(b[:n], dtype=float) - float(np.mean(b[:n]))
    k = max(range(-maximo, maximo + 1), key=lambda k: float((a[max(0, -k):n - max(0, k)] * b[max(0, k):n - max(0, -k)]).sum()))
    return round(k * paso_ms)


def _envolvente(ruta: Path, paso_ms: int):
    import numpy as np
    sr = 8000
    crudo = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"],
                           capture_output=True, check=True).stdout
    x = np.frombuffer(crudo, dtype=np.int16).astype(np.float32)
    h = sr * paso_ms // 1000
    n = len(x) // h
    return np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1))


def medir_sincronia(d: Path) -> dict:
    """Mide, sobre el archivo rendido: (1) el desfase de la voz dentro del MP4 y (2) cuánto se adelanta o atrasa
    el subtítulo respecto al arranque real de la voz en cada inicio de frase. No juzga si la animación acompaña:
    eso se mira en cuadros antes y después de cada palabra."""
    import numpy as np
    final, voz, palabras = d / "out" / "final.mp4", d / "audio" / "vo.wav", d / "audio" / "words.json"
    for f in (final, voz, palabras):
        if not f.is_file():
            raise ErrorVox(f"falta {f}: la sincronía se mide con voz y con un render hecho")
    desfase = desfase_ms(_envolvente(voz, 1), _envolvente(final, 1))
    w = json.loads(palabras.read_text(encoding="utf-8"))
    e = _envolvente(voz, 10)
    umbral = 0.08 * float(np.percentile(e, 95))
    errores = []
    for i, x in enumerate(w):
        if i and w[i - 1]["w"][-1] not in ".:!?":
            continue
        i0 = int(x["s"] * 100)
        arranques = [j for j in range(max(8, i0 - 40), min(len(e), i0 + 40)) if e[j] > umbral and e[j - 8:j].max() < umbral]
        if arranques:
            errores.append({"palabra": x["w"], "s": x["s"], "ms": round((min(arranques, key=lambda j: abs(j - i0)) - i0) * 10)})
    ms = sorted(v["ms"] for v in errores[1:]) or [0]  # la primera palabra arranca con el silencio inicial de la toma
    avisos = []
    if abs(desfase) > 40:
        avisos.append(f"la voz va {desfase} ms desfasada dentro del video (máximo 40)")
    if max(abs(ms[0]), abs(ms[-1])) > 200:
        avisos.append(f"un subtítulo se separa {max(abs(ms[0]), abs(ms[-1]))} ms de la voz (máximo 200)")
    info = {"render": vox.huella(final.read_bytes().hex()[:4096], str(final.stat().st_size))[:16], "desfase_voz_ms": desfase,
            "subtitulos_ms": {"min": ms[0], "mediana": ms[len(ms) // 2], "max": ms[-1], "frases": len(errores)},
            "detalle": errores, "avisos": avisos}
    (d / "out" / "sincronia.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


# ---------- voz ----------

def narrar_guion(d: Path, ejecutar: bool, prueba: bool = False) -> dict:
    """Una sola toma para toda la narración; reparte los tiempos reales entre escenas contando palabras."""
    b = leer_brief(d)
    g = json.loads((d / "guion.json").read_text(encoding="utf-8"))
    escenas = g.get("escenas") or []
    if not escenas or any(not str(s.get("narracion", "")).strip() for s in escenas):
        raise ErrorVox("guion.json necesita `escenas` con `id` y `narracion` en cada una")
    voz = vox.perfiles()[b["espacio"]]["voz"]
    texto = " ".join(" ".join(str(s["narracion"]).split()) for s in escenas)
    firma = vox.firma_voz(texto, voz)
    cache = d / "estados" / "voz.json"
    guardado = json.loads(cache.read_text()) if cache.is_file() else {}
    cruda = d / "audio" / "vo-cruda.mp3"
    if guardado.get("firma") == firma and cruda.is_file():
        palabras = guardado["palabras"]
    elif not ejecutar:
        return {"en_seco": True, "caracteres": len(texto), "voz": voz["nombre"]}
    else:
        if not prueba:  # narrar cuesta: antes, la entrevista completa y que Emi haya pedido la voz del espacio
            bb = exigir_aprobado(d)
            if "espacio" not in bb["respuestas"]["voz"].lower():
                raise ErrorVox(f"Emi respondió sobre la voz: «{bb['respuestas']['voz']}». No se narra con la voz del espacio.")
        audio, palabras = vox.narrar(texto, voz)
        cruda.parent.mkdir(parents=True, exist_ok=True)
        cruda.write_bytes(audio)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"firma": firma, "palabras": palabras}))
    conteos = [len(str(s["narracion"]).split()) for s in escenas]
    if sum(conteos) != len(palabras):
        raise ErrorVox(f"la alineación trae {len(palabras)} palabras y el guion {sum(conteos)}; no se inventan tiempos")
    vox.normalizar(cruda, d / "audio" / "vo.wav", vox.VOZ_LUFS)
    (d / "audio" / "words.json").write_text(json.dumps(
        [{"w": p["t"], "s": round(p["a"], 3), "e": round(p["b"], 3)} for p in palabras], ensure_ascii=False))
    tiempos, pos = [], 0
    total = round(vox.duracion_audio(d / "audio" / "vo.wav"), 3)
    for i, (s, n) in enumerate(zip(escenas, conteos)):
        # la primera escena empieza en 0 aunque la voz tarde unas décimas: así el video y el audio comparten reloj
        tiempos.append({"id": s["id"], "inicio": 0.0 if i == 0 else round(palabras[pos]["a"], 3),
                        "fin": round(palabras[pos + n - 1]["b"], 3), "palabras": n})
        pos += n
    for i, t in enumerate(tiempos):  # la escena dura hasta que empieza la siguiente
        t["hasta"] = tiempos[i + 1]["inicio"] if i + 1 < len(tiempos) else total
        t["dur"] = round(t["hasta"] - t["inicio"], 3)
    (d / "tiempos.json").write_text(json.dumps({"total": total, "escenas": tiempos}, ensure_ascii=False, indent=1))
    return {"en_seco": False, "caracteres": len(texto), "voz": voz["nombre"], "total": total, "escenas": tiempos}


# ---------- motor: dibujar ----------

def modo_de(d: Path) -> str:
    return "estilos" if (d / "video.js").is_file() and (d / "engine").is_dir() else "pizarron"


def args_modo(d: Path) -> list[str]:
    """Con voz las escenas siguen a la narración y las transiciones no se mueven al beat (modo B).

    Se usa igual en la medición, en los cuadros de prueba y en el render: lo que se revisa es lo que se entrega.
    """
    if modo_de(d) != "pizarron":
        return []
    return ["--mode", "B" if (d / "audio" / "vo.wav").is_file() else "A"]


def _node(d: Path, *args: str, espera: int = 3600) -> str:
    env = {**os.environ}
    if navegador():
        env["CHROME_PATH"] = navegador()
    try:
        r = subprocess.run(["node", "render.mjs", *args], cwd=d, env=env, capture_output=True, text=True, timeout=espera)
    except subprocess.TimeoutExpired as exc:
        raise ErrorVox(f"el motor no terminó en {espera} s") from exc
    except FileNotFoundError as exc:
        raise ErrorVox("falta Node.js") from exc
    if r.returncode != 0 or "PAGE ERROR" in r.stderr:
        raise ErrorVox("el motor falló al dibujar: " + (r.stderr or r.stdout)[-600:])
    return r.stdout


def duracion_del_video(d: Path) -> float:
    """Duración real que calcula el motor al construir las escenas (los dos motores la imprimen distinto)."""
    if modo_de(d) == "estilos":
        salida = _node(d, "--stills", "0.3", "--outdir", "_medir", espera=300)
        shutil.rmtree(d / "_medir", ignore_errors=True)
    else:
        habia = (d / "stills" / "s_000.30.jpg").exists()
        salida = _node(d, "--stills", "0.3", *args_modo(d), espera=300)
        if not habia:
            (d / "stills" / "s_000.30.jpg").unlink(missing_ok=True)
    m = re.search(r"(?:duration|duración)\s*([0-9]+(?:\.[0-9]+)?)\s*s", salida)
    if not m:
        raise ErrorVox("no se pudo medir la duración del video: indica --segundos")
    return float(m.group(1))


# ---------- música y beats ----------

def rejilla_beats(plan: dict, segundos: float, cortes: list[float]) -> dict:
    """Rejilla exacta para el motor: como la música se compuso aquí, el tempo no se estima, se sabe."""
    paso = 60.0 / plan["bpm"]
    beats = [round(i * paso, 3) for i in range(int(segundos / paso) + 1)]
    return {"tempo": float(plan["bpm"]), "beats": beats,
            "strength": [1.5 if i % 4 == 0 else 0.5 for i in range(len(beats))],  # el primer tiempo de cada compás es el golpe fuerte
            "sections": [0.0] + [round(c, 2) for c in cortes]}


def componer_musica(d: Path, animo: str, segundos: float | None) -> dict:
    tf = d / "tiempos.json"
    tiempos = json.loads(tf.read_text()) if tf.is_file() else None
    if segundos is None:
        segundos = duracion_del_video(d) + 0.6
    cortes = [t["inicio"] for t in tiempos["escenas"][1:]] if tiempos else []
    g = d / "guion.json"
    semilla = int(vox.huella(g.read_text(encoding="utf-8") if g.is_file() else d.name, animo)[:8], 16)
    plan = SON.plan_musica(animo, semilla)
    wav = d / "audio" / "_music.wav"
    try:
        SON.guardar(wav, SON.componer(animo, segundos, semilla, cortes), nivel=-20.0)
        vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-b:a", "192k", str(d / "audio" / "music.mp3")])
    finally:
        wav.unlink(missing_ok=True)
    (d / "audio" / "beats.json").write_text(json.dumps(rejilla_beats(plan, segundos, cortes)))
    (d / "estados").mkdir(exist_ok=True)
    (d / "estados" / "musica.json").write_text(json.dumps({**plan, "segundos": round(segundos, 2)}))
    return plan


# ---------- cuadros de prueba ----------

ZONAS = {"9:16": [(0, 0, 1080, 215), (0, 1450, 1080, 1920), (960, 760, 1080, 1450)], "16:9": []}


def hoja(d: Path, salida: Path, cols: int = 8) -> int:
    """Hoja de contacto con las zonas que tapa TikTok sombreadas (solo en vertical)."""
    from PIL import Image, ImageDraw
    archivos = sorted((d / "stills").glob("*.jpg"))
    if not archivos:
        raise ErrorVox("no hay cuadros de prueba: ejecuta `qa`")
    with Image.open(archivos[0]) as im0:
        w0, h0 = im0.size
    formato = "9:16" if h0 > w0 else "16:9"
    ancho = 220 if formato == "9:16" else 400
    alto = int(ancho * h0 / w0)
    filas = -(-len(archivos) // cols)
    lienzo = Image.new("RGB", (ancho * cols, alto * filas), "white")
    for i, f in enumerate(archivos):
        with Image.open(f) as im:
            im = im.convert("RGBA")
            capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
            dib = ImageDraw.Draw(capa)
            for x0, y0, x1, y1 in ZONAS[formato]:
                dib.rectangle([x0 * w0 / 1080, y0 * h0 / 1920, x1 * w0 / 1080, y1 * h0 / 1920], fill=(255, 0, 0, 38))
            im = Image.alpha_composite(im, capa).convert("RGB").resize((ancho, alto))
        lienzo.paste(im, ((i % cols) * ancho, (i // cols) * alto))
    salida.parent.mkdir(parents=True, exist_ok=True)
    lienzo.save(salida, quality=85)
    return len(archivos)


def cuadros_de_prueba(d: Path, cada: float) -> int:
    if not 0.2 <= cada <= 30:
        raise ErrorVox("--cada debe estar entre 0.2 y 30 segundos")
    shutil.rmtree(d / "stills", ignore_errors=True)
    _node(d, "--every", str(cada), *args_modo(d), espera=1200)
    return hoja(d, d / "out" / "hoja.jpg")


# ---------- render, mezcla y auditoría ----------

def _lufs(audio: Path) -> float:
    try:
        return float(vox._loudnorm(audio)["input_i"])
    except (ErrorVox, ValueError):
        return float("-inf")


def rendir(d: Path, prueba: bool = False) -> dict:
    """Con `prueba` rinde un borrador técnico (out/prueba.mp4) sin exigir la entrevista: nunca es un entregable."""
    b = leer_brief(d) if prueba else exigir_aprobado(d)
    resp = b.get("respuestas") or {}
    esperado = leer_formato(resp.get("formato", ""))      # el brief se interpreta ANTES de gastar minutos de render
    pedido = leer_duracion(resp.get("duracion_s", ""))
    modo = modo_de(d)
    marca = json.loads((d / "marca.json").read_text(encoding="utf-8")) if (d / "marca.json").is_file() else {}
    (d / "out").mkdir(exist_ok=True)
    final = d / "out" / ("prueba.mp4" if prueba else "final.mp4")
    movil = final.with_name(final.stem + "-movil.mp4")
    for viejo in (final, movil, d / "out" / "auditoria.json"):  # nada de una corrida anterior puede parecer vigente
        viejo.unlink(missing_ok=True)
    mudo, bruto = d / "out" / "_mudo.mp4", d / "out" / "_bruto.mp4"
    cama, cama_l = d / "audio" / "_cama.wav", d / "audio" / "_cama-l.wav"
    voz = d / "audio" / "vo.wav"
    hay_voz, hay_musica = voz.is_file(), (d / "audio" / "music.mp3").is_file()
    avisos: list[str] = []
    try:
        _node(d, "out/_mudo.mp4", *args_modo(d))
        dur = vox.duracion_audio(mudo)
        env = {**os.environ, "SWELL": "1"}
        if sin_efectos(resp.get("efectos", "")):
            env["SFX_GAIN"] = "0"  # Emi pidió no llevar efectos
        if modo == "pizarron":
            cmd = [sys.executable, "sfx_mix.py", f"{dur:.3f}", "audio/_cama.wav"] + (["audio/music.mp3"] if hay_musica else [])
        else:
            cmd = [sys.executable, "sfx_mix.py", "audio/_cama.wav"] + (["--music", "audio/music.mp3"] if hay_musica else [])
        r = subprocess.run(cmd, cwd=d, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            raise ErrorVox("falló la mezcla de efectos del motor: " + r.stderr[-400:])
        # Los golpes del dibujo (sellos, impactos) tienen picos muy altos: se limitan y recién entonces se mide.
        vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(cama), "-af", "alimiter=limit=0.4:level=false:attack=2:release=40", str(cama_l)])
        nivel_cama = _lufs(cama_l)
        hay_cama = math.isfinite(nivel_cama) and nivel_cama > -60
        base = ["ffmpeg", "-y", "-v", "error", "-i", str(mudo)]
        salida_av = ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", str(bruto)]
        if hay_voz and hay_cama:  # la voz manda: la cama (efectos + música) queda 12 LU por debajo
            ganancia = (vox.VOZ_LUFS - 12.0) - nivel_cama
            mezcla = f"[1:a]volume={ganancia:.2f}dB[c];[2:a][c]amix=inputs=2:normalize=0:duration=longest[a]"
            vox._correr(base + ["-i", str(cama_l), "-i", str(voz), "-filter_complex", mezcla, "-map", "0:v", "-map", "[a]"] + salida_av)
        elif hay_voz:
            vox._correr(base + ["-i", str(voz), "-map", "0:v", "-map", "1:a"] + salida_av)
        elif hay_cama:
            vox._correr(base + ["-i", str(cama_l), "-map", "0:v", "-map", "1:a"] + salida_av)
        else:  # ni voz ni música ni efectos: pista en silencio, sin master
            vox._correr(base + ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a"] + salida_av)
            avisos.append("el video no tiene voz, música ni efectos: sale en silencio")
        ganancia_master = 0.0
        if hay_voz or hay_cama:
            # El limitador se come parte de la ganancia: se parte siempre del bruto y se ajusta midiendo (una sola codificación final).
            # Una voz muy expresiva deja picos que la codificación AAC empuja por encima del techo:
            # si el pico real pasa de PICO_MAX se baja el techo del limitador y se repite.
            for techo in TECHOS_LIMITADOR:
                ganancia_master = round(-14.0 - _lufs(bruto), 2)
                for _ in range(4):
                    vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(bruto), "-c:v", "copy", "-af",
                                 f"volume={ganancia_master:.2f}dB,alimiter=limit={techo}:level=false:attack=3:release=60", "-ar", "48000",
                                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)])
                    falta = -14.0 - _lufs(final)
                    if abs(falta) <= 0.5:
                        break
                    ganancia_master = round(ganancia_master + falta * 1.2, 2)
                pico = vox.medir(final)["pico_dbtp"]
                if pico is None or float(pico) <= vox.PICO_MAX:
                    break
        else:
            shutil.copyfile(bruto, final)
        m = vox.medir(final) if (hay_voz or hay_cama) else {"lufs": None, "pico_dbtp": None}
        kbps = max(1200, min(6000, int(25 * 8 * 1000 / max(dur, 1) - 160)))  # copia ligera para mandar por chat (< 30 MB)
        vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(final), "-c:v", "libx264", "-preset", "medium", "-b:v", f"{kbps}k",
                     "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(movil)])
    finally:
        for tmp in TEMPORALES:
            (d / tmp).unlink(missing_ok=True)
    sonda = json.loads(vox._correr(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(final)], capture_output=True, text=True).stdout)
    v = next(x for x in sonda["streams"] if x["codec_type"] == "video")
    if (v["width"], v["height"]) != esperado:
        avisos.append(f"el video mide {v['width']}x{v['height']} y el formato pedido es {esperado[0]}x{esperado[1]}")
    if v["codec_name"] != "h264" or v["pix_fmt"] != "yuv420p":
        avisos.append(f"códec o formato de pixel inesperado: {v['codec_name']} {v['pix_fmt']}")
    if m["lufs"] is not None:
        if not vox.LUFS_FINAL[0] <= float(m["lufs"]) <= vox.LUFS_FINAL[1]:
            avisos.append(f"sonoridad final {m['lufs']} LUFS fuera de -14 ± 1")
        if float(m["pico_dbtp"]) > vox.PICO_MAX:
            avisos.append(f"pico {m['pico_dbtp']} dBTP por encima de {vox.PICO_MAX}")
    if pedido and not (pedido[0] * 0.8 - 5 <= dur <= pedido[1] * 1.2 + 5):
        avisos.append(f"dura {dur:.0f} s y Emi pidió {resp.get('duracion_s')}")
    if hay_voz:
        dv = vox.duracion_audio(voz)
        if dv > dur + 0.1:
            avisos.append(f"la voz dura {dv:.1f} s y el video {dur:.1f} s: la narración se corta al final")
        elif dur - dv > 4:
            avisos.append(f"el video sigue {dur - dv:.1f} s después de la voz: revisa las duraciones de las escenas")
    if hay_musica and vox.duracion_audio(d / "audio" / "music.mp3") < dur - 0.5:
        avisos.append("la música dura menos que el video: vuelve a ejecutar `musica` (sin --segundos mide el video)")
    if m["lufs"] is not None:
        silencio = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(final), "-af", "silencedetect=n=-45dB:d=1.5", "-f", "null", "-"],
                                  capture_output=True, text=True).stderr.count("silence_start")
        if silencio:
            avisos.append(f"{silencio} silencio(s) de más de 1.5 s")
    informe = {"archivo": final.name, "prueba": prueba, "modo": modo, "duracion_s": round(dur, 2), "ancho": v["width"], "alto": v["height"],
               "lufs": m["lufs"], "pico_dbtp": m["pico_dbtp"], "voz": hay_voz, "musica": hay_musica, "efectos": env.get("SFX_GAIN") != "0",
               "ganancia_master_db": ganancia_master, "motor": str(marca.get("motor") or commit_instalado())[:7],
               "mb": round(final.stat().st_size / 1e6, 1), "avisos": avisos}
    (d / "out" / "auditoria.json").write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    vox.escribir_manifiesto(d, final, {"skill_md": str(RAIZ / "SKILL.md"), "motor": f"santmun/video-pizarra@{informe['motor']} ({modo})",
                            "render": {"codec": "h264", "audio": "aac 192k 48 kHz", "voz": hay_voz, "musica": hay_musica, "efectos": informe["efectos"]},
                            "medido": {"lufs": m["lufs"], "pico_dbtp": m["pico_dbtp"], "duracion_s": informe["duracion_s"]}})
    return informe


def cortes_del_video(d: Path) -> list[float]:
    """Dónde cambia cada escena: de la voz si la hay; si no, de los golpes de transición que anotó el motor."""
    tf = d / "tiempos.json"
    if tf.is_file() and (d / "audio" / "vo.wav").is_file():
        return [t["inicio"] for t in json.loads(tf.read_text())["escenas"][1:]]
    hf = d / "hits.json"
    if hf.is_file():
        try:
            return sorted(float(h["t"] if isinstance(h, dict) else h) for h in json.loads(hf.read_text()))
        except (ValueError, KeyError, TypeError):
            return []
    return []


# ---------- producción ----------

BRIEF_BASE = {"espacio": "", "modo": "", "estilo": "", "respuestas": {k: "" for k in PREGUNTAS},
              "decidido_por_defecto": [], "aprobaciones": {k: False for k in APROBACIONES}}


def crear_proyecto(d: Path, espacio: str, modo: str, estilo: str) -> None:
    perfiles = vox.perfiles()
    if espacio not in perfiles:
        raise ErrorVox(f"espacio desconocido: {espacio}; opciones {sorted(perfiles)}")
    if modo == "estilos" and not estilo:
        raise ErrorVox("en modo estilos indica --estilo")
    if d.parent.name != espacio or d.parent.parent.name != "productions":
        raise ErrorVox(f"las producciones son privadas y van por espacio: usa productions/{espacio}/{d.name}")
    if d.exists():
        raise ErrorVox(f"{d} ya existe; no se sobrescribe una producción")
    motor = exigir_motor()
    tmp = d.with_name(d.name + ".creando")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.parent.mkdir(parents=True, exist_ok=True)
    try:  # se arma aparte y se renombra al final: un fallo a medias no deja una producción rota
        shutil.copytree(motor / MODOS[modo], tmp, ignore=shutil.ignore_patterns("node_modules", ".venv"))
        for carpeta in ("audio", "estados", "out", "assets"):
            (tmp / carpeta).mkdir(exist_ok=True)
        vox._correr(["npm", "install", "--no-audit", "--no-fund", "--silent"], cwd=tmp)
        p = perfiles[espacio]
        cfg = marca_para_motor(p, modo, estilo)
        (tmp / "marca.json").write_text(json.dumps({"espacio": espacio, "nombre": p["nombre"], "tono": p["tono"], "voz": p["voz"]["nombre"],
                                                    "cierre": p.get("cierre", ""), "motor": MOTOR_COMMIT, "config_motor": cfg}, ensure_ascii=False, indent=1))
        js = json.dumps(cfg, ensure_ascii=False)
        if modo == "pizarron":  # este motor carga scripts clásicos desde index.html
            (tmp / "marca.js").write_text(f"window.MARCA = {js};\n", encoding="utf-8")
            html = (tmp / "index.html").read_text(encoding="utf-8")
            nuevo = html.replace('<script src="scenes.js">', '<script src="marca.js"></script>\n<script src="scenes.js">')
            if nuevo == html:
                raise ErrorVox("el index.html del motor cambió y no se pudo inyectar la marca: revisa el motor antes de producir")
            (tmp / "index.html").write_text(nuevo, encoding="utf-8")
        else:  # el de estilos usa módulos: import marca from './marca.js'
            (tmp / "marca.js").write_text(f"export default {js};\n", encoding="utf-8")
        respuestas = {**BRIEF_BASE["respuestas"], **preferencias()}
        (tmp / "brief.json").write_text(json.dumps({**BRIEF_BASE, "espacio": espacio, "modo": modo, "estilo": estilo or "pizarron",
                                                    "respuestas": respuestas}, ensure_ascii=False, indent=1))
        (tmp / "estados" / "saldo-inicio.json").write_text(json.dumps(vox.saldo()))
        tmp.rename(d)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def archivo_aprendizajes_pizarra() -> Path:
    return vox.dir_espacios() / "APRENDIZAJES-PIZARRA.md"


def _aprendido(espacio: str) -> str:
    extra = archivo_aprendizajes_pizarra()
    return vox.leer_aprendizajes(espacio) + ("\n\n" + extra.read_text(encoding="utf-8").strip() if extra.is_file() else "")


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("instalar"); sub.add_parser("motor")
    p = sub.add_parser("proyecto"); p.add_argument("dir"); p.add_argument("--perfil", required=True)
    p.add_argument("--modo", choices=sorted(MODOS), required=True); p.add_argument("--estilo", choices=ESTILOS, default="")
    for nombre in ("entrevista", "cierre"):
        p = sub.add_parser(nombre); p.add_argument("dir")
    p = sub.add_parser("render"); p.add_argument("dir"); p.add_argument("--prueba", action="store_true")
    p = sub.add_parser("sincronia"); p.add_argument("dir")
    p = sub.add_parser("voz"); p.add_argument("dir"); p.add_argument("--execute", action="store_true"); p.add_argument("--prueba", action="store_true")
    p = sub.add_parser("musica"); p.add_argument("dir"); p.add_argument("--animo", choices=sorted(SON.ANIMOS), required=True)
    p.add_argument("--segundos", type=float, default=None)
    p = sub.add_parser("revisar"); p.add_argument("dir"); p.add_argument("--prueba", action="store_true")
    p = sub.add_parser("qa"); p.add_argument("dir"); p.add_argument("--cada", type=float, default=1.2)
    p = sub.add_parser("aprender"); p.add_argument("texto"); p.add_argument("--espacio", default="")
    p = sub.add_parser("aprendizajes"); p.add_argument("--espacio", default="")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "instalar":
            faltan = instalar()
            print(f"Motor en {dir_motor()} · commit {MOTOR_COMMIT[:7]} (revisado).")
            print("Falta instalar: " + ", ".join(faltan) if faltan else "Dependencias completas. Navegador: " + navegador())
            return 1 if faltan else 0
        elif a.cmd == "motor":
            print(f"Instalado: {commit_instalado()[:7] or 'no'} · Revisado y fijado: {MOTOR_COMMIT[:7]}")
            try:
                remoto = _git("ls-remote", MOTOR_REPO, "HEAD").split()[0]
                if remoto == MOTOR_COMMIT:
                    print("El autor no ha publicado nada nuevo.")
                else:
                    print(f"El autor publicó cambios ({remoto[:7]}). Para adoptarlos: leer el código nuevo, probar un render, "
                          "cambiar MOTOR_COMMIT y registrarlo en CHANGELOG.md. No se actualiza solo.")
            except (ErrorVox, IndexError) as exc:
                print(f"No se pudo consultar el repositorio del autor: {str(exc)[:80]}")
        elif a.cmd == "sincronia":
            i = medir_sincronia(Path(a.dir))
            t = i["subtitulos_ms"]
            print(f"Voz dentro del video: {i['desfase_voz_ms']} ms de desfase. Subtítulos frente a la voz en {t['frases']} inicios de frase: "
                  f"de {t['min']} a {t['max']} ms (mediana {t['mediana']}; positivo = el subtítulo entra antes).")
            print("\n".join("  ⚠ " + x for x in i["avisos"]) or "  Sin avisos. Falta mirar un cuadro antes y otro después de cada palabra ancla.")
            return 1 if i["avisos"] else 0
        elif a.cmd == "proyecto":
            d = Path(a.dir)
            crear_proyecto(d, a.perfil, a.modo, a.estilo)
            print(f"Producción creada en {d} (modo {a.modo}). Sigue: `entrevista {d}`.\n")
            print("Antes de escribir nada, aplica lo aprendido:\n" + _aprendido(a.perfil))
        elif a.cmd == "entrevista":
            f = faltantes(leer_brief(Path(a.dir)))
            if not f["preguntas"] and not f["aprobaciones"]:
                print("Entrevista completa y aprobada. Se puede producir.")
                return 0
            if f["preguntas"]:
                print(f"Faltan {len(f['preguntas'])} respuestas de Emi (pregúntalas en tandas de hasta 4, con una opción recomendada):")
                for k, q in f["preguntas"].items():
                    print(f"  · {k}: {q}")
            for k, q in f["aprobaciones"].items():
                print(f"  · pendiente — {q}")
            return 1
        elif a.cmd == "voz":
            r = narrar_guion(Path(a.dir), a.execute, a.prueba)
            if r["en_seco"]:
                print(f"En seco: {r['caracteres']} caracteres con la voz {r['voz']}. Añade --execute para narrar.")
            else:
                print(f"Voz lista ({r['voz']}): {r['total']} s. Duración real de cada escena, para construir la animación:")
                for t in r["escenas"]:
                    print(f"  {t['id']}: empieza {t['inicio']} s · dura {t['dur']} s")
        elif a.cmd == "musica":
            plan = componer_musica(Path(a.dir), a.animo, a.segundos)
            print(f"Música original: {plan['animo']} · {plan['bpm']} bpm · tónica {plan['tonica']}. Rejilla de beats exacta en audio/beats.json.")
        elif a.cmd == "qa":
            n = cuadros_de_prueba(Path(a.dir), a.cada)
            print(f"{n} cuadros en {a.dir}/out/hoja.jpg (rojo = zonas que tapa TikTok). Míralos todos antes de rendir.")
        elif a.cmd == "render":
            i = rendir(Path(a.dir), a.prueba)
            nivel = f"{i['lufs']} LUFS · pico {i['pico_dbtp']} dBTP" if i["lufs"] is not None else "sin audio"
            print(f"{'PRUEBA TÉCNICA (no entregable)' if a.prueba else 'Final'} en {a.dir}/out/{i['archivo']} · "
                  f"{i['duracion_s']} s · {i['ancho']}x{i['alto']} · {nivel} · {i['mb']} MB")
            for aviso in i["avisos"]:
                print(f"  ⚠ {aviso}")
            if not i["avisos"]:
                print("  Sin avisos automáticos.")
            print("Copia ligera junto al archivo (-movil). Pide a Emi que lo vea y lo escuche; termina con `cierre`.")
        elif a.cmd == "revisar":
            d = Path(a.dir)
            video = d / "out" / ("prueba.mp4" if a.prueba else "final.mp4")
            if not video.is_file():
                raise ErrorVox(f"no existe {video}: falta rendir")
            f = vox.crear_revision(d, video, cortes_del_video(d))
            print(f"Mira {d}/out/hoja-transiciones.png (cada cambio de escena: antes, durante y después) y {d}/out/hoja-telefono.png (tamaño real de un teléfono).")
            print(f"Luego llena {f}: `hallazgos` (segundo, problema, arreglo), `pendientes` y `revisado_por`. Corrige los 3 peores y vuelve a rendir.")
        elif a.cmd == "cierre":
            d = Path(a.dir)
            vox.exigir_revision(d, d / "out" / "final.mp4")
            ini = d / "estados" / "saldo-inicio.json"
            ahora = vox.saldo()
            (d / "estados").mkdir(exist_ok=True)
            (d / "estados" / "saldo-cierre.json").write_text(json.dumps(ahora))
            print(vox.tabla_saldo(json.loads(ini.read_text()) if ini.is_file() else None, ahora))
            print('\nRegistra lo aprendido en este video: pizarra.py aprender "..." [--espacio E]')
        elif a.cmd == "aprender":
            if a.espacio:
                return vox.main(["aprender", a.texto, "--espacio", a.espacio])
            destino = archivo_aprendizajes_pizarra()
            if not destino.exists():
                destino.write_text("# Aprendizajes de los videos estilo pizarra\n\n", encoding="utf-8")
            with destino.open("a", encoding="utf-8") as fh:
                fh.write(f"- {time.strftime('%Y-%m-%d')} · {' '.join(a.texto.split())}\n")
            print(f"Aprendizaje guardado en {destino}")
        elif a.cmd == "aprendizajes":
            print(_aprendido(a.espacio))
    except ErrorVox as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except (KeyError, ValueError, OSError, IndexError, TypeError, AttributeError, subprocess.SubprocessError) as exc:
        print(f"Error: dato inesperado ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
