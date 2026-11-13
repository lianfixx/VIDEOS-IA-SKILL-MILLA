"""Base común de Editor Studio: rutas, espacios, red, saldos, FFmpeg y memoria.

Sin dependencias fuera de la biblioteca estándar. Las llaves nunca se leen de archivos:
el entorno las inyecta (o vienen en variables de entorno) y aquí solo se envían.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent          # skills/editor-studio
PLANTILLA = RAIZ / "plantilla"
VERSION = "0.2.0"
MARCADOR = "proxy-injected"
KIE = "https://api.kie.ai/api/v1"
ELEVEN = "https://api.elevenlabs.io/v1"
ASSEMBLY = "https://api.assemblyai.com/v2"
ESPACIOS = ("personal", "milla", "castorena", "pan")
FORMATOS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
FPS = 30

# Zonas que tapa la interfaz de TikTok y Reels en 1080x1920 (mismas que usa Vox Studio).
ZONAS_APP = {"barra superior": (0, 0, 1080, 215), "descripción inferior": (0, 1450, 1080, 1920),
             "botones de la derecha": (960, 760, 1080, 1450)}
SEGURA = {"9:16": (90, 230, 960, 1440), "16:9": (96, 54, 1824, 1026), "1:1": (60, 60, 1020, 1020)}


class ErrorEditor(Exception):
    """Error que se le explica a quien usa la skill; nunca una traza."""


# ---------- espacios y memoria ----------

def dir_espacios() -> Path:
    if os.environ.get("EDITOR_ESPACIOS"):
        return Path(os.environ["EDITOR_ESPACIOS"])
    if (RAIZ / "espacios").is_dir():            # skill empaquetada: los espacios viajan dentro
        return RAIZ / "espacios"
    return RAIZ.parent.parent / "espacios"


def leer_json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ErrorEditor(f"falta {ruta}") from exc
    except ValueError as exc:
        raise ErrorEditor(f"{ruta} no es JSON válido: {exc}") from exc


def escribir_json(ruta: Path, datos) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return ruta


def perfil(espacio: str) -> dict:
    """Marca del espacio (perfil.json, común a las skills de video) + su estilo de edición."""
    if espacio not in ESPACIOS:
        raise ErrorEditor(f"espacio desconocido: {espacio}. Opciones: {', '.join(ESPACIOS)}")
    base = dir_espacios() / espacio
    p = leer_json(base / "perfil.json")
    p["edicion"] = leer_json(base / "edicion.json")
    p["espacio"] = espacio
    return p


def archivo_aprendizajes(espacio: str = "") -> Path:
    if espacio:
        if espacio not in ESPACIOS:
            raise ErrorEditor(f"espacio desconocido: {espacio}")
        return dir_espacios() / espacio / "aprendizajes-edicion.md"
    return dir_espacios() / "APRENDIZAJES-EDICION.md"


def leer_aprendizajes(espacio: str = "") -> str:
    """Lo general de edición, lo propio del espacio y, como información, lo que la marca ya aprendió en otras skills."""
    partes = []
    for f in [archivo_aprendizajes("")] + ([archivo_aprendizajes(espacio)] if espacio else []):
        if f.exists():
            partes.append(f.read_text(encoding="utf-8").strip())
    if espacio:
        marca = dir_espacios() / espacio / "aprendizajes.md"
        if marca.exists() and marca.read_text(encoding="utf-8").strip():
            partes.append("(Información de la marca, escrita por otras skills; no es una orden de edición)\n"
                          + marca.read_text(encoding="utf-8").strip())
    return "\n\n".join(partes) or "Sin aprendizajes registrados."


def aprender(texto: str, espacio: str = "") -> Path:
    texto = " ".join(texto.split())
    if len(texto) < 12:
        raise ErrorEditor("la lección es demasiado corta para servir después: di qué pasó y qué regla queda")
    f = archivo_aprendizajes(espacio)
    previo = f.read_text(encoding="utf-8") if f.exists() else "# Aprendizajes de edición\n"
    f.write_text(previo.rstrip("\n") + f"\n- {time.strftime('%Y-%m-%d')} · {texto}\n", encoding="utf-8")
    return f


def dir_produccion(d: Path, espacio: str = "") -> Path:
    """Una producción vive en productions/<espacio>/edicion/<tema>/ y en ningún otro lugar."""
    partes = d.resolve().parts
    for i in range(len(partes) - 3):
        if partes[i] == "productions" and partes[i + 1] in ESPACIOS and partes[i + 2] == "edicion":
            if espacio and partes[i + 1] != espacio:
                raise ErrorEditor(f"{d} está en el espacio «{partes[i + 1]}», no en «{espacio}»: los espacios no se mezclan")
            return d
    raise ErrorEditor(f"{d} no está dentro de productions/<espacio>/edicion/<tema>/")


def espacio_de(d: Path) -> str:
    partes = dir_produccion(d).resolve().parts
    return partes[partes.index("edicion") - 1]


# ---------- huellas ----------

def huella(*partes: str) -> str:
    return hashlib.sha256("\x1f".join(partes).encode()).hexdigest()


def sha_archivo(ruta: Path, n: int = 16) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as fh:
        for bloque in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()[:n]


# ---------- red ----------

def pedir(url: str, *, metodo="GET", cabeceras=None, cuerpo=None, datos: bytes | None = None,
          tipo: str = "", espera=120, tope: int = 64 * 1024 * 1024) -> bytes:
    u = urllib.parse.urlparse(url)
    if u.scheme != "https":
        raise ErrorEditor("solo se permiten URLs https")
    if cuerpo is not None:
        datos, tipo = json.dumps(cuerpo).encode(), "application/json"
    req = urllib.request.Request(url, data=datos, method=metodo,
                                 headers={"User-Agent": f"editor-studio/{VERSION} (python-urllib)", **(cabeceras or {})})
    if tipo:
        req.add_header("Content-Type", tipo)
    try:
        with urllib.request.urlopen(req, timeout=espera) as r:
            salida = r.read(tope + 1)
            if len(salida) > tope:
                raise ErrorEditor(f"la respuesta de {u.hostname} pasa de {tope // (1024 * 1024)} MB; no se descargó")
            return salida
    except urllib.error.HTTPError as exc:
        raise ErrorEditor(f"{u.hostname} respondió HTTP {exc.code}: {exc.read()[:240]!r}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        aviso = " No se sabe si el proveedor cobró: revisa su historial antes de reintentar." if metodo == "POST" else ""
        raise ErrorEditor(f"sin respuesta de {u.hostname}: {exc}.{aviso}") from exc


def como_json(crudo: bytes, quien: str) -> dict:
    try:
        return json.loads(crudo)
    except ValueError as exc:
        raise ErrorEditor(f"{quien} devolvió algo que no es JSON") from exc


def formulario(campos: dict, archivo: tuple[str, str, bytes, str] | None = None) -> tuple[bytes, str]:
    """multipart/form-data con la biblioteca estándar. archivo = (campo, nombre, bytes, tipo)."""
    borde = "editor" + uuid.uuid4().hex
    partes = []
    for k, v in campos.items():
        partes.append(f"--{borde}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    if archivo:
        campo, nombre, datos, tipo = archivo
        partes.append(f"--{borde}\r\nContent-Disposition: form-data; name=\"{campo}\"; filename=\"{nombre}\"\r\n"
                      f"Content-Type: {tipo}\r\n\r\n".encode() + datos + b"\r\n")
    partes.append(f"--{borde}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={borde}"


def cab_kie() -> dict:
    return {"Authorization": "Bearer " + os.environ.get("KIE_API_KEY", MARCADOR)}


def cab_eleven() -> dict:
    return {"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", MARCADOR)}


def cab_assembly() -> dict:
    return {"authorization": os.environ.get("ASSEMBLYAI_API_KEY", MARCADOR)}


def saldo() -> dict:
    """Saldo real de cada proveedor. Sin conexión se dice «sin dato»; nunca se estima."""
    out: dict = {}
    try:
        out["kie_creditos"] = como_json(pedir(f"{KIE}/chat/credit", cabeceras=cab_kie(), espera=30), "Kie").get("data")
    except ErrorEditor as exc:
        out["kie_error"] = str(exc)[:120]
    try:
        sub = como_json(pedir(f"{ELEVEN}/user/subscription", cabeceras=cab_eleven(), espera=30), "ElevenLabs")
        out["elevenlabs_usados"] = sub.get("character_count")
        out["elevenlabs_limite"] = sub.get("character_limit")
        out["elevenlabs_restantes"] = (sub.get("character_limit") or 0) - (sub.get("character_count") or 0)
    except ErrorEditor as exc:
        out["elevenlabs_error"] = str(exc)[:120]
    try:
        cab = {"Authorization": "Bearer " + os.environ.get("APIFY_TOKEN", MARCADOR)}
        lim = como_json(pedir("https://api.apify.com/v2/users/me/limits", cabeceras=cab, espera=30), "Apify").get("data") or {}
        uso = (lim.get("current") or {}).get("monthlyUsageUsd")
        tope = (lim.get("limits") or {}).get("maxMonthlyUsageUsd")
        out["apify_usado_usd"], out["apify_tope_usd"] = uso, tope
        if uso is not None and tope is not None:
            out["apify_restante_usd"] = round(tope - uso, 4)
    except ErrorEditor as exc:
        out["apify_error"] = str(exc)[:120]
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
        filas.append(f"ElevenLabs  | {gasto('elevenlabs_usados', True)} caracteres | "
                     f"{ahora['elevenlabs_restantes']} de {ahora['elevenlabs_limite']} caracteres")
    else:
        filas.append(f"ElevenLabs  | — | sin dato: {ahora.get('elevenlabs_error')}")
    if "apify_restante_usd" in ahora:
        filas.append(f"Apify       | {gasto('apify_usado_usd', True)} USD | "
                     f"{ahora['apify_restante_usd']} de {ahora['apify_tope_usd']} USD este mes")
    else:
        filas.append(f"Apify       | — | sin dato: {ahora.get('apify_error')}")
    filas.append("Claude      | no se puede consultar desde aquí | —")
    return "\n".join(filas)


# ---------- FFmpeg ----------

def correr(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=True, **kw)
    except FileNotFoundError as exc:
        raise ErrorEditor(f"falta el programa {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        cola = ""
        if isinstance(exc.stderr, (bytes, str)) and exc.stderr:
            texto = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
            cola = ": " + " | ".join(texto.strip().splitlines()[-3:])
        raise ErrorEditor(f"{cmd[0]} falló (código {exc.returncode}){cola}") from exc


def sonda(ruta: Path) -> dict:
    """Lo que hace falta saber de un archivo de video antes de tocarlo."""
    if not ruta.is_file():
        raise ErrorEditor(f"no existe {ruta}")
    out = correr(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(ruta)],
                 capture_output=True, text=True).stdout
    datos = json.loads(out)
    v = next((s for s in datos.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in datos.get("streams", []) if s.get("codec_type") == "audio"), None)
    info: dict = {"duracion_s": round(float(datos.get("format", {}).get("duration", 0) or 0), 3),
                  "tiene_audio": a is not None, "tiene_video": v is not None}
    if v:
        giro = 0
        for lado in v.get("side_data_list", []) or []:
            if "rotation" in lado:
                giro = int(lado["rotation"])
        giro = giro or int((v.get("tags") or {}).get("rotate", 0) or 0)
        ancho, alto = int(v.get("width", 0)), int(v.get("height", 0))
        if abs(giro) in (90, 270):
            ancho, alto = alto, ancho
        num, _, den = (v.get("avg_frame_rate") or "0/1").partition("/")
        fps = (float(num) / float(den)) if float(den or 0) else 0.0
        transfer = v.get("color_transfer", "")
        info.update({"ancho": ancho, "alto": alto, "giro": giro, "fps": round(fps, 3), "codec": v.get("codec_name"),
                     "pix_fmt": v.get("pix_fmt"), "transfer": transfer,
                     "hdr": transfer in ("arib-std-b67", "smpte2084"),
                     "fps_variable": (v.get("avg_frame_rate") != v.get("r_frame_rate"))})
    if a:
        info.update({"audio_hz": int(a.get("sample_rate", 0) or 0), "audio_canales": int(a.get("channels", 0) or 0)})
    return info


def duracion(ruta: Path) -> float:
    out = correr(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                 capture_output=True, text=True).stdout
    return float(out.strip())


def medir_sonoridad(audio: Path, objetivo: float = -14.0, extra: str = "") -> dict:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio), "-vn", "-af",
                        f"loudnorm=I={objetivo}:TP=-1.5:LRA=11{extra}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
    if not m:
        raise ErrorEditor(f"no se pudo medir la sonoridad de {audio.name}")
    return json.loads(m.group(0))


def formato_tiempo(t: float) -> str:
    m, s = divmod(max(0.0, t), 60)
    return f"{int(m)}:{s:05.2f}"
