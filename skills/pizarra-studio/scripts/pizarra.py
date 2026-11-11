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
  render DIR                                render + mezcla + master a -14 LUFS + auditoría + copia ligera
  cierre DIR                                tabla de gastado y restante por proveedor
  aprender "TEXTO" [--espacio E] / aprendizajes [--espacio E]

Usa las mismas llaves que Vox Studio (ElevenLabs, Kie, Apify): en la nube las inyecta el proxy.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ.parent / "vox-studio" / "scripts"))
sys.path.insert(0, str(RAIZ / "scripts" / "comun"))  # paquete autocontenido: copia de los módulos compartidos
import vox  # noqa: E402  (voz, saldos, niveles, espacios y aprendizajes: una sola implementación)

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
    "personaje": "¿Lleva personaje? ¿Mascota, una persona dibujada que te represente, tu foto, o ninguno?",
    "voz": "¿Con voz narrada (la del espacio), con tu propia voz grabada, o solo texto en pantalla?",
    "musica": "¿Música: qué ánimo (tension, energia, serio, ironia, motivacion) o sin música?",
    "efectos": "¿Con efectos de sonido del dibujo (plumón, gis, golpes) o solo voz y música?",
    "gancho": "¿Cuál de los 2 o 3 ganchos propuestos para ESTE tema eliges?",
    "cta": "¿Con qué cierra: pregunta para comentar, seguir, link, WhatsApp, nada?",
    "marca": "¿Lleva nombre, @ o logo del espacio en pantalla, o explícitamente no?",
    "referencias": "¿Tienes una imagen o video de referencia de cómo quieres que se vea? (o «ninguna»)",
}
APROBACIONES = {
    "resumen": "Emi aprobó el resumen: lo que respondió frente a lo que se decidió por defecto",
    "storyboard": "Emi aprobó el storyboard (una línea por escena) antes de animar",
}


def dir_motor() -> Path:
    return Path(os.environ.get("PIZARRA_MOTOR") or Path.home() / ".claude" / "skills" / "video-pizarra")


def navegador() -> str:
    """Chromium ya instalado en la máquina; evita descargar otro."""
    if os.environ.get("CHROME_PATH"):
        return os.environ["CHROME_PATH"]
    for patron in ("chromium-*/chrome-linux*/chrome", "chromium/chrome-linux*/chrome"):
        hallados = sorted(Path("/opt/pw-browsers").glob(patron)) if Path("/opt/pw-browsers").is_dir() else []
        if hallados:
            return str(hallados[-1])
    return ""


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
    if commit_instalado() != MOTOR_COMMIT:
        raise ErrorVox("no se pudo dejar el motor en el commit revisado")
    faltan = [p for p in ("node", "npm", "ffmpeg", "ffprobe") if not shutil.which(p)]
    for mod in ("numpy", "PIL"):
        if subprocess.run([sys.executable, "-c", f"import {mod}"], capture_output=True).returncode != 0:
            faltan.append(f"python:{mod}")
    if not navegador():
        faltan.append("chromium (define CHROME_PATH o instala el de Playwright)")
    return faltan


# ---------- marca del espacio -> configuración del motor ----------

def marca_para_motor(perfil: dict, modo: str) -> dict:
    """Traduce el perfil del espacio a lo que entiende cada motor. No inventa colores."""
    c = perfil["colores"]
    if modo == "pizarron":
        return {"palette": {"ink": c["tinta"], "orange": c["acento"], "cream": c["papel"], "paper": c["papel"]},
                "hatches": {"marca": [c["acento"], c["tinta"]], "apoyo": [c["apoyo"], c["tinta"]]},
                "mascotTheme": "marca"}
    serif = perfil.get("titular") == "Gelasio"
    return {"palette": {"accent": c["acento"], "bg": c["papel"]},
            "font": {"display": "Gelasio" if serif else "Anton", "body": "Montserrat" if serif else "Poppins"},
            "mascotColor": c["acento"]}


# ---------- entrevista ----------

def faltantes(brief: dict) -> dict:
    """Preguntas sin responder y aprobaciones pendientes. Una respuesta vacía no cuenta."""
    r = brief.get("respuestas") or {}
    sin = {k: q for k, q in PREGUNTAS.items() if not str(r.get(k, "")).strip()}
    if "opinion_emi" not in sin and len(str(r.get("opinion_emi", "")).strip()) < 20:
        sin["opinion_emi"] = PREGUNTAS["opinion_emi"] + " (hace falta su postura real, no una frase de relleno)"
    ap = brief.get("aprobaciones") or {}
    return {"preguntas": sin, "aprobaciones": {k: v for k, v in APROBACIONES.items() if ap.get(k) is not True}}


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


# ---------- voz ----------

def narrar_guion(d: Path, ejecutar: bool) -> dict:
    """Una sola toma para toda la narración; reparte los tiempos reales entre escenas contando palabras."""
    b = leer_brief(d)
    g = json.loads((d / "guion.json").read_text(encoding="utf-8"))
    escenas = g.get("escenas") or []
    if not escenas or any(not str(s.get("narracion", "")).strip() for s in escenas):
        raise ErrorVox("guion.json necesita `escenas` con `id` y `narracion` en cada una")
    voz = vox.perfiles()[b["espacio"]]["voz"]
    texto = " ".join(" ".join(str(s["narracion"]).split()) for s in escenas)
    firma = vox.huella(texto, voz["voice_id"], voz.get("modelo", ""))
    cache = d / "estados" / "voz.json"
    guardado = json.loads(cache.read_text()) if cache.is_file() else {}
    cruda = d / "audio" / "vo-cruda.mp3"
    if guardado.get("firma") == firma and cruda.is_file():
        palabras = guardado["palabras"]
    elif not ejecutar:
        return {"en_seco": True, "caracteres": len(texto), "voz": voz["nombre"]}
    else:
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
    for s, n in zip(escenas, conteos):
        tiempos.append({"id": s["id"], "inicio": round(palabras[pos]["a"], 3), "fin": round(palabras[pos + n - 1]["b"], 3), "palabras": n})
        pos += n
    for i, t in enumerate(tiempos):  # la escena dura hasta que empieza la siguiente
        t["hasta"] = tiempos[i + 1]["inicio"] if i + 1 < len(tiempos) else total
        t["dur"] = round(t["hasta"] - t["inicio"], 3)
    (d / "tiempos.json").write_text(json.dumps({"total": total, "escenas": tiempos}, ensure_ascii=False, indent=1))
    return {"en_seco": False, "caracteres": len(texto), "voz": voz["nombre"], "total": total, "escenas": tiempos}


# ---------- música y beats ----------

def rejilla_beats(plan: dict, segundos: float, cortes: list[float]) -> dict:
    """Rejilla exacta para el motor: como la música se compuso aquí, el tempo no se estima, se sabe."""
    paso = 60.0 / plan["bpm"]
    beats = [round(i * paso, 3) for i in range(int(segundos / paso) + 1)]
    return {"tempo": float(plan["bpm"]), "beats": beats,
            "strength": [1.0 if i % 4 == 0 else 0.45 for i in range(len(beats))],
            "sections": [0.0] + [round(c, 2) for c in cortes]}


def componer_musica(d: Path, animo: str, segundos: float | None) -> dict:
    tf = d / "tiempos.json"
    tiempos = json.loads(tf.read_text()) if tf.is_file() else None
    if segundos is None:  # la duración real la da el propio motor al dibujar las escenas
        salida = _node(d, "--stills", "0.3")
        try:
            segundos = float(salida.split("duration")[-1].strip().rstrip("s").split()[0].rstrip("s")) + 0.6
        except (ValueError, IndexError) as exc:
            raise ErrorVox("no se pudo medir la duración del video: indica --segundos") from exc
    cortes = [t["inicio"] for t in tiempos["escenas"][1:]] if tiempos else []
    g = d / "guion.json"
    semilla = int(vox.huella(g.read_text(encoding="utf-8") if g.is_file() else d.name, animo)[:8], 16)
    plan = SON.plan_musica(animo, semilla)
    wav = d / "audio" / "_music.wav"
    SON.guardar(wav, SON.componer(animo, segundos, semilla, cortes), nivel=-20.0)
    vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-b:a", "192k", str(d / "audio" / "music.mp3")])
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


def _node(d: Path, *args: str) -> str:
    env = {**os.environ}
    if navegador():
        env["CHROME_PATH"] = navegador()
    r = subprocess.run(["node", "render.mjs", *args], cwd=d, env=env, capture_output=True, text=True)
    if r.returncode != 0 or "PAGE ERROR" in r.stderr:
        raise ErrorVox("el motor falló al dibujar: " + (r.stderr or r.stdout)[-600:])
    return r.stdout


def cuadros_de_prueba(d: Path, cada: float) -> int:
    shutil.rmtree(d / "stills", ignore_errors=True)
    _node(d, "--every", str(cada))
    return hoja(d, d / "out" / "hoja.jpg")


# ---------- render, mezcla y auditoría ----------

def modo_de(d: Path) -> str:
    return "estilos" if (d / "video.js").is_file() and (d / "engine").is_dir() else "pizarron"


def rendir(d: Path, prueba: bool = False) -> dict:
    """Con `prueba` rinde un borrador técnico (out/prueba.mp4) sin exigir la entrevista: nunca es un entregable."""
    if not prueba:
        exigir_aprobado(d)
    modo = modo_de(d)
    (d / "out").mkdir(exist_ok=True)
    mudo = d / "out" / "_mudo.mp4"
    voz = d / "audio" / "vo.wav"
    hay_voz, hay_musica = voz.is_file(), (d / "audio" / "music.mp3").is_file()
    # Con voz, las escenas siguen a la narración: las transiciones no se mueven al beat (modo B).
    _node(d, "out/_mudo.mp4", *(["--mode", "B" if hay_voz else "A"] if modo == "pizarron" else []))
    dur = vox.duracion_audio(mudo)
    cama = d / "audio" / "_cama.wav"  # efectos del motor + música, sin la voz
    env = {**os.environ, "SWELL": "1"}
    if modo == "pizarron":
        cmd = [sys.executable, "sfx_mix.py", f"{dur:.3f}", "audio/_cama.wav"] + (["audio/music.mp3"] if hay_musica else [])
    else:
        cmd = [sys.executable, "sfx_mix.py", "audio/_cama.wav"] + (["--music", "audio/music.mp3"] if hay_musica else [])
    r = subprocess.run(cmd, cwd=d, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise ErrorVox("falló la mezcla de efectos del motor: " + r.stderr[-400:])
    bruto = d / "out" / "_bruto.mp4"
    # Los golpes del dibujo (sellos, impactos) tienen picos muy altos: se limitan antes de mezclar
    # para que el master pueda llegar a -14 LUFS sin aplastar la voz.
    doma = "alimiter=limit=0.4:level=false:attack=2:release=40"
    if hay_voz:  # la voz manda: la cama (efectos + música) queda 12 LU por debajo
        ganancia = (vox.VOZ_LUFS - 12.0) - float(vox._loudnorm(cama)["input_i"])
        mezcla = f"[1:a]{doma},volume={ganancia:.2f}dB[c];[2:a][c]amix=inputs=2:normalize=0:duration=longest[a]"
        vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(mudo), "-i", str(cama), "-i", str(voz), "-filter_complex", mezcla,
                     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(bruto)])
    else:
        vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(mudo), "-i", str(cama), "-map", "0:v", "-map", "1:a", "-af", doma,
                     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(bruto)])
    final = d / "out" / ("prueba.mp4" if prueba else "final.mp4")
    ganancia_master = vox.masterizar(bruto, final)
    for _ in range(3):  # el limitador se come parte de la ganancia: se repone lo que falte, con medida real cada vez
        falta = round(-14.0 - float(vox.medir(final)["lufs"]), 2)
        if abs(falta) <= 0.5:
            break
        tmp = final.with_name("_m2.mp4")
        vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(final), "-c:v", "copy", "-af",
                     f"volume={falta * 1.25:.2f}dB,alimiter=limit=0.75:level=false:attack=3:release=60", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                     "-movflags", "+faststart", str(tmp)])
        tmp.replace(final)
        ganancia_master = round(ganancia_master + falta * 1.25, 2)
    m = vox.medir(final)
    # copia ligera para mandar por chat (< 30 MB)
    kbps = max(1200, min(6000, int(25 * 8 * 1000 / max(dur, 1) - 160)))
    vox._correr(["ffmpeg", "-y", "-v", "error", "-i", str(final), "-c:v", "libx264", "-preset", "medium", "-b:v", f"{kbps}k",
                 "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(final.with_name(final.stem + "-movil.mp4"))])
    for tmp in (mudo, bruto, cama):
        tmp.unlink(missing_ok=True)
    avisos = []
    sonda = json.loads(vox._correr(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(final)], capture_output=True, text=True).stdout)
    v = next(x for x in sonda["streams"] if x["codec_type"] == "video")
    b = leer_brief(d)
    esperado = FORMATOS.get(str(b["respuestas"].get("formato", "9:16")).strip()[:4].strip(), (1080, 1920))
    if (v["width"], v["height"]) != esperado:
        avisos.append(f"el video mide {v['width']}x{v['height']} y el formato pedido es {esperado[0]}x{esperado[1]}")
    if v["codec_name"] != "h264" or v["pix_fmt"] != "yuv420p":
        avisos.append(f"códec o formato de pixel inesperado: {v['codec_name']} {v['pix_fmt']}")
    if not vox.LUFS_FINAL[0] <= float(m["lufs"]) <= vox.LUFS_FINAL[1]:
        avisos.append(f"sonoridad final {m['lufs']} LUFS fuera de -14 ± 1")
    if float(m["pico_dbtp"]) > vox.PICO_MAX:
        avisos.append(f"pico {m['pico_dbtp']} dBTP por encima de {vox.PICO_MAX}")
    pedido = float(str(b["respuestas"].get("duracion_s", "0")).split()[0] or 0) if str(b["respuestas"].get("duracion_s", "")).strip()[:1].isdigit() else 0
    if pedido and abs(dur - pedido) > max(8.0, pedido * 0.2):
        avisos.append(f"dura {dur:.0f} s y Emi pidió {pedido:.0f} s")
    if hay_musica and vox.duracion_audio(d / "audio" / "music.mp3") < dur - 0.5:
        avisos.append(f"la música dura menos que el video ({dur:.1f} s): vuelve a ejecutar `musica` (sin --segundos mide el video)")
    silencio = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(final), "-af", "silencedetect=n=-45dB:d=1.5", "-f", "null", "-"],
                              capture_output=True, text=True).stderr.count("silence_start")
    if silencio:
        avisos.append(f"{silencio} silencio(s) de más de 1.5 s")
    informe = {"archivo": final.name, "prueba": prueba, "modo": modo, "duracion_s": round(dur, 2), "ancho": v["width"], "alto": v["height"], "lufs": m["lufs"], "pico_dbtp": m["pico_dbtp"],
               "voz": hay_voz, "musica": hay_musica, "ganancia_master_db": ganancia_master, "motor": MOTOR_COMMIT[:7],
               "mb": round(final.stat().st_size / 1e6, 1), "avisos": avisos}
    (d / "out" / "auditoria.json").write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    return informe


# ---------- CLI ----------

BRIEF_BASE = {"espacio": "", "modo": "", "estilo": "", "respuestas": {k: "" for k in PREGUNTAS},
              "decidido_por_defecto": [], "aprobaciones": {k: False for k in APROBACIONES}}


def archivo_aprendizajes_pizarra() -> Path:
    return vox.dir_espacios() / "APRENDIZAJES-PIZARRA.md"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("instalar"); sub.add_parser("motor")
    p = sub.add_parser("proyecto"); p.add_argument("dir"); p.add_argument("--perfil", required=True)
    p.add_argument("--modo", choices=sorted(MODOS), required=True); p.add_argument("--estilo", choices=ESTILOS, default="")
    for nombre in ("entrevista", "cierre"):
        p = sub.add_parser(nombre); p.add_argument("dir")
    p = sub.add_parser("render"); p.add_argument("dir"); p.add_argument("--prueba", action="store_true")
    p = sub.add_parser("voz"); p.add_argument("dir"); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("musica"); p.add_argument("dir"); p.add_argument("--animo", choices=sorted(SON.ANIMOS), required=True)
    p.add_argument("--segundos", type=float, default=None)
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
            except ErrorVox as exc:
                print(f"No se pudo consultar el repositorio del autor: {str(exc)[:80]}")
        elif a.cmd == "proyecto":
            perfiles = vox.perfiles()
            if a.perfil not in perfiles:
                raise ErrorVox(f"espacio desconocido: {a.perfil}; opciones {sorted(perfiles)}")
            if a.modo == "estilos" and not a.estilo:
                raise ErrorVox("en modo estilos indica --estilo")
            d = Path(a.dir)
            if d.parent.name != a.perfil:
                raise ErrorVox(f"cada espacio va por separado: usa productions/{a.perfil}/{d.name}")
            if d.exists():
                raise ErrorVox(f"{d} ya existe; no se sobrescribe una producción")
            motor = exigir_motor()
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(motor / MODOS[a.modo], d, ignore=shutil.ignore_patterns("node_modules", ".venv"))
            for carpeta in ("audio", "estados", "out", "assets"):
                (d / carpeta).mkdir(exist_ok=True)
            vox._correr(["npm", "install", "--no-audit", "--no-fund", "--silent"], cwd=d)
            (d / "marca.json").write_text(json.dumps({"espacio": a.perfil, "nombre": perfiles[a.perfil]["nombre"],
                                                      "tono": perfiles[a.perfil]["tono"], "voz": perfiles[a.perfil]["voz"]["nombre"],
                                                      "cierre": perfiles[a.perfil].get("cierre", ""),
                                                      "config_motor": marca_para_motor(perfiles[a.perfil], a.modo)}, ensure_ascii=False, indent=1))
            cfg = json.dumps(marca_para_motor(perfiles[a.perfil], a.modo), ensure_ascii=False)
            if a.modo == "pizarron":  # el motor de pizarrón carga scripts clásicos desde index.html
                (d / "marca.js").write_text(f"window.MARCA = {cfg};\n", encoding="utf-8")
                html = (d / "index.html").read_text(encoding="utf-8")
                (d / "index.html").write_text(html.replace('<script src="scenes.js">', '<script src="marca.js"></script>\n<script src="scenes.js">'), encoding="utf-8")
            else:  # el de estilos usa módulos: import marca from './marca.js'
                (d / "marca.js").write_text(f"export default {cfg};\n", encoding="utf-8")
            (d / "brief.json").write_text(json.dumps({**BRIEF_BASE, "espacio": a.perfil, "modo": a.modo, "estilo": a.estilo or "pizarron"}, ensure_ascii=False, indent=1))
            (d / "estados" / "saldo-inicio.json").write_text(json.dumps(vox.saldo()))
            print(f"Producción creada en {d} (modo {a.modo}). Sigue: `entrevista {d}`.\n")
            print("Antes de escribir nada, aplica lo aprendido:\n" + vox.leer_aprendizajes(a.perfil))
            if archivo_aprendizajes_pizarra().is_file():
                print("\n" + archivo_aprendizajes_pizarra().read_text(encoding="utf-8").strip())
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
            r = narrar_guion(Path(a.dir), a.execute)
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
            print(f"{'PRUEBA TÉCNICA (no entregable)' if a.prueba else 'Final'} en {a.dir}/out/{i['archivo']} · {i['duracion_s']} s · {i['ancho']}x{i['alto']} · {i['lufs']} LUFS · pico {i['pico_dbtp']} dBTP · {i['mb']} MB")
            for aviso in i["avisos"]:
                print(f"  ⚠ {aviso}")
            print("  Sin avisos automáticos." if not i["avisos"] else "", end="")
            print(f"\nCopia ligera junto al archivo (-movil). Pide a Emi que lo vea y lo escuche; termina con `cierre`.")
        elif a.cmd == "cierre":
            return vox.main(["cierre", a.dir])
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
            print(vox.leer_aprendizajes(a.espacio))
            if archivo_aprendizajes_pizarra().is_file():
                print("\n" + archivo_aprendizajes_pizarra().read_text(encoding="utf-8").strip())
    except ErrorVox as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except (KeyError, ValueError, OSError, IndexError, TypeError) as exc:
        print(f"Error: dato inesperado ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
