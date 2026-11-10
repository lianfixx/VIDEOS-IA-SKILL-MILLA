#!/usr/bin/env python3
"""Vox Studio: shorts verticales estilo documental-collage con Remotion.

Subcomandos (sin --execute nada llama a un proveedor ni gasta saldo):
  perfiles                         lista los perfiles de marca
  proyecto DIR --perfil P          copia la plantilla Remotion a una producción privada
  validar GUION                    comprueba el guion (exige la opinión de Emi)
  voz GUION --dir DIR [--execute]  narra con ElevenLabs y arma src/data/video.json
  imagen --prompt-file F --out O   genera una imagen con Kie (nano-banana-2-lite)
  recorte ENTRADA SALIDA           quita el fondo verde (croma) -> PNG con alfa
  sfx DIR                          sintetiza el kit de efectos con FFmpeg (sin proveedor)
  master ENTRADA SALIDA            normaliza el audio a -14 LUFS / -1.5 dBTP sin recodificar video
  saldo                            consulta créditos de Kie y caracteres de ElevenLabs

Las claves nunca se escriben aquí. En la nube el proxy las inyecta (se envía un
marcador); en local se leen de KIE_API_KEY y ELEVENLABS_API_KEY.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla"
FPS = 30
MARCADOR = "proxy-injected"
KIE = "https://api.kie.ai/api/v1"
ELEVEN = "https://api.elevenlabs.io/v1"
HOSTS_DESCARGA = {"tempfile.aiquickdraw.com", "file.aiquickdraw.com"}
MODELOS_KIE = {"nano-banana-2-lite"}  # ampliar solo con esquema comprobado
ENTRADAS = ["sello", "desliza-izq", "cae", "desliza-der", "desdobla", "mordidas"]
SUFIJO_CROMA = (
    "flat 2D editorial cartoon illustration, bold thick black outlines, flat colors, "
    "single isolated subject, centered, full subject visible with margin, "
    "on a perfectly uniform solid pure green (#00FF00) chroma key background, "
    "no shadow, no floor, no gradient, no text, no letters, no logos, no watermark"
)


class ErrorVox(Exception):
    pass


def perfiles() -> dict:
    datos = json.loads((RAIZ / "perfiles.json").read_text(encoding="utf-8"))
    return {k: v for k, v in datos.items() if not k.startswith("_")}


# ---------- guion ----------

def validar_guion(g: dict) -> list[str]:
    e: list[str] = []
    if g.get("perfil") not in perfiles():
        e.append(f"perfil desconocido: {g.get('perfil')!r}; usa uno de {sorted(perfiles())}")
    if len(str(g.get("opinion_emi", "")).strip()) < 20:
        e.append("falta opinion_emi: pregunta a Emi su postura sobre el tema antes de escribir (mínimo 20 caracteres)")
    if not str(g.get("titulo", "")).strip():
        e.append("falta titulo")
    if "?" not in str(g.get("cta_pregunta", "")):
        e.append("cta_pregunta debe ser una pregunta que invite a comentar")
    escenas = g.get("escenas") or []
    if not 4 <= len(escenas) <= 9:
        e.append(f"se esperan de 4 a 9 escenas; hay {len(escenas)}")
    vistos, previa = set(), None
    for i, s in enumerate(escenas, 1):
        p = f"escena {i}"
        if s.get("id") in vistos or not s.get("id"):
            e.append(f"{p}: id ausente o repetido")
        vistos.add(s.get("id"))
        n = str(s.get("narracion", "")).strip()
        k = str(s.get("keyword", "")).strip()
        if not n:
            e.append(f"{p}: falta narracion")
        if not k or len(k) > 34:
            e.append(f"{p}: keyword vacío o de más de 34 caracteres")
        if k and n and k.lower() == n.lower():
            e.append(f"{p}: el keyword repite la narración; debe reforzarla")
        r = s.get("resaltar")
        if r and r.upper() not in k.upper().split():
            e.append(f"{p}: resaltar {r!r} no es una palabra del keyword")
        ent = s.get("entrada")
        if ent and ent not in ENTRADAS:
            e.append(f"{p}: entrada {ent!r} no existe; opciones {ENTRADAS}")
        if ent and ent == previa:
            e.append(f"{p}: repite la entrada de la escena anterior")
        previa = ent or previa
    return e


def texto_completo(g: dict) -> tuple[str, list[tuple[int, int]]]:
    """Une las narraciones y devuelve el texto y el rango de caracteres de cada escena."""
    partes, rangos, pos = [], [], 0
    for s in g["escenas"]:
        t = " ".join(str(s["narracion"]).split())
        rangos.append((pos, pos + len(t)))
        partes.append(t)
        pos += len(t) + 1
    return " ".join(partes), rangos


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
            actual = {"t": "", "a": float(ini[i]), "b": float(fin[i]), "c": i}
        actual["t"] += ch
        actual["b"] = float(fin[i])
    if actual:
        out.append(actual)
    return out


def armar_video(g: dict, palabras: list[dict], duracion: float, perfil: dict) -> dict:
    """Convierte guion + tiempos reales de palabra en la línea de tiempo que lee Remotion."""
    _, rangos = texto_completo(g)
    escenas, n = [], len(g["escenas"])
    inicios = []
    for a, b in rangos:
        propias = [p for p in palabras if a <= p["c"] < b]
        if not propias:
            raise ErrorVox("una escena quedó sin palabras alineadas; revisa la narración")
        inicios.append(propias[0]["a"])
    total = int(round((duracion + 0.7) * FPS))
    for i, s in enumerate(g["escenas"]):
        desde = 0 if i == 0 else max(0, int(round((inicios[i] - 0.12) * FPS)))
        hasta = total if i == n - 1 else max(desde + 1, int(round((inicios[i + 1] - 0.12) * FPS)))
        escenas.append({
            "id": s["id"], "desde": desde, "dur": hasta - desde,
            "keyword": str(s["keyword"]).upper(), "resaltar": (s.get("resaltar") or "").upper(),
            "kicker": s.get("kicker", ""), "nota": s.get("nota", ""), "dato": s.get("dato", ""),
            "fuente": s.get("fuente", ""),
            "imagen": s.get("imagen_archivo", ""), "foto": bool(s.get("foto_real", False)),
            "entrada": s.get("entrada") or ENTRADAS[i % len(ENTRADAS)],
        })
    return {
        "fps": FPS, "ancho": 1080, "alto": 1920, "frames": total,
        "titulo": g["titulo"], "perfil": perfil, "voz": "audio/voz.mp3",
        "musica": g.get("musica_archivo", ""), "sfx": True, "escenas": escenas,
        "palabras": [{"t": p["t"], "a": round(p["a"], 3), "b": round(p["b"], 3)} for p in palabras],
    }


# ---------- red ----------

def _pedir(url: str, *, metodo="GET", cabeceras=None, cuerpo=None, espera=120) -> bytes:
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo, headers=cabeceras or {})
    if datos is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=espera) as r:
            return r.read()
    except urllib.error.HTTPError as exc:
        raise ErrorVox(f"{urllib.request.urlparse(url).hostname} respondió HTTP {exc.code}: {exc.read()[:200]!r}") from exc


def _kie() -> dict:
    return {"Authorization": "Bearer " + os.environ.get("KIE_API_KEY", MARCADOR)}


def _eleven() -> dict:
    return {"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", MARCADOR)}


def saldo() -> dict:
    kie = json.loads(_pedir(f"{KIE}/chat/credit", cabeceras=_kie())).get("data")
    sub = json.loads(_pedir(f"{ELEVEN}/user/subscription", cabeceras=_eleven()))
    return {"kie_creditos": kie, "elevenlabs_usados": sub.get("character_count"), "elevenlabs_limite": sub.get("character_limit")}


def narrar(texto: str, voz: dict) -> tuple[bytes, list[dict]]:
    cuerpo = {"text": texto, "model_id": voz.get("modelo", "eleven_multilingual_v2"),
              "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}}
    r = json.loads(_pedir(f"{ELEVEN}/text-to-speech/{voz['voice_id']}/with-timestamps?output_format=mp3_44100_128",
                          metodo="POST", cabeceras=_eleven(), cuerpo=cuerpo, espera=240))
    al = r.get("alignment") or {}
    if not al.get("characters"):
        raise ErrorVox("ElevenLabs no devolvió alineación; no se inventan tiempos de subtítulos")
    return base64.b64decode(r["audio_base64"]), palabras_desde_alineacion(
        al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"])


def duracion_audio(ruta: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def generar_imagen(prompt: str, salida: Path, estado: Path, aspecto="3:4", modelo="nano-banana-2-lite", espera=300) -> None:
    if modelo not in MODELOS_KIE:
        raise ErrorVox(f"modelo {modelo!r} sin esquema comprobado; añade su contrato antes de usarlo")
    if estado.exists():
        est = json.loads(estado.read_text())
    else:
        r = json.loads(_pedir(f"{KIE}/jobs/createTask", metodo="POST", cabeceras=_kie(),
                              cuerpo={"model": modelo, "input": {"prompt": prompt, "aspect_ratio": aspecto}}))
        tid = (r.get("data") or {}).get("taskId")
        if not tid:
            raise ErrorVox(f"Kie no devolvió taskId: {str(r)[:200]}")
        est = {"taskId": tid, "modelo": modelo}
        estado.parent.mkdir(parents=True, exist_ok=True)
        estado.write_text(json.dumps(est))
    limite = time.time() + espera
    while time.time() < limite:
        d = json.loads(_pedir(f"{KIE}/jobs/recordInfo?taskId={est['taskId']}", cabeceras=_kie())).get("data") or {}
        st = str(d.get("state", "")).lower()
        if st == "success":
            rj = d.get("resultJson")
            url = (json.loads(rj) if isinstance(rj, str) else rj)["resultUrls"][0]
            host = urllib.request.urlparse(url).hostname
            if host not in HOSTS_DESCARGA:
                raise ErrorVox(f"host de descarga no autorizado: {host}")
            salida.parent.mkdir(parents=True, exist_ok=True)
            salida.write_bytes(_pedir(url))
            return
        if st in {"fail", "failed", "error"}:
            raise ErrorVox(f"Kie falló: {d.get('failMsg')}")
        time.sleep(4)
    raise ErrorVox(f"Kie no terminó a tiempo; reconsulta la misma tarea con el estado {estado} (no crees otra)")


# ---------- imagen local ----------

def recortar_croma(entrada: Path, salida: Path) -> tuple[int, int]:
    """Quita un fondo verde uniforme, limpia el derrame y recorta al contenido."""
    import numpy as np
    from PIL import Image, ImageFilter

    im = np.asarray(Image.open(entrada).convert("RGB")).astype(np.float32)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    exceso = g - np.maximum(r, b)  # cuánto domina el verde
    alfa = np.clip(1.0 - (exceso - 18.0) / 50.0, 0.0, 1.0)
    g2 = np.where(exceso > 0, np.maximum(r, b) + exceso * 0.08, g)  # despill
    rgba = np.dstack([r, g2, b, alfa * 255.0]).clip(0, 255).astype(np.uint8)
    out = Image.fromarray(rgba, "RGBA")
    a = out.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    out.putalpha(a)
    caja = a.point(lambda v: 255 if v > 24 else 0).getbbox()
    if not caja:
        raise ErrorVox("el recorte quedó vacío: la imagen no tenía un sujeto sobre fondo verde")
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
}


def sintetizar_sfx(destino: Path) -> list[str]:
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, filtro in SFX.items():
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", filtro, "-ar", "48000", "-ac", "2",
                        str(destino / f"{nombre}.wav")], check=True)
    return sorted(SFX)


def masterizar(entrada: Path, salida: Path) -> None:
    salida.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(entrada), "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(salida)], check=True)


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("perfiles")
    sub.add_parser("saldo")
    p = sub.add_parser("proyecto"); p.add_argument("dir"); p.add_argument("--perfil", required=True)
    p = sub.add_parser("validar"); p.add_argument("guion")
    p = sub.add_parser("voz"); p.add_argument("guion"); p.add_argument("--dir", required=True); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("imagen"); p.add_argument("--prompt-file", required=True); p.add_argument("--out", required=True)
    p.add_argument("--estado", required=True); p.add_argument("--aspecto", default="3:4"); p.add_argument("--sin-croma", action="store_true"); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("recorte"); p.add_argument("entrada"); p.add_argument("salida")
    p = sub.add_parser("sfx"); p.add_argument("dir")
    p = sub.add_parser("master"); p.add_argument("entrada"); p.add_argument("salida")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "perfiles":
            for k, v in perfiles().items():
                print(f"{k:10} {v['nombre']:22} acento {v['colores']['acento']}  voz {v['voz']['nombre']}  [{v['estado']}]")
        elif a.cmd == "saldo":
            print(json.dumps(saldo()))
        elif a.cmd == "proyecto":
            if a.perfil not in perfiles():
                raise ErrorVox(f"perfil desconocido: {a.perfil}")
            d = Path(a.dir)
            if d.exists():
                raise ErrorVox(f"{d} ya existe; no se sobrescribe una producción")
            shutil.copytree(PLANTILLA, d, ignore=shutil.ignore_patterns("node_modules", "out"))
            sintetizar_sfx(d / "public" / "sfx")
            print(f"Producción creada en {d}. Sigue: npm ci, escribir guion.json, validar, voz.")
        elif a.cmd == "validar":
            errores = validar_guion(json.loads(Path(a.guion).read_text(encoding="utf-8")))
            for x in errores:
                print("✗", x)
            print("Guion válido." if not errores else f"{len(errores)} problema(s).")
            return 1 if errores else 0
        elif a.cmd == "voz":
            g = json.loads(Path(a.guion).read_text(encoding="utf-8"))
            errores = validar_guion(g)
            if errores:
                raise ErrorVox("guion inválido: " + "; ".join(errores))
            perfil = perfiles()[g["perfil"]]
            texto, _ = texto_completo(g)
            if not a.execute:
                print(f"En seco: {len(texto)} caracteres con la voz {perfil['voz']['nombre']}. Añade --execute para narrar.")
                return 0
            d = Path(a.dir)
            audio, palabras = narrar(texto, perfil["voz"])
            destino = d / "public" / "audio" / "voz.mp3"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(audio)
            video = armar_video(g, palabras, duracion_audio(destino), perfil)
            (d / "src" / "data").mkdir(parents=True, exist_ok=True)
            (d / "src" / "data" / "video.json").write_text(json.dumps(video, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"Voz lista: {len(texto)} caracteres, {video['frames'] / FPS:.1f} s, {len(palabras)} palabras con tiempo real.")
        elif a.cmd == "imagen":
            prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip()
            if not a.sin_croma:
                prompt = f"{prompt}. {SUFIJO_CROMA}"
            if not a.execute:
                print(f"En seco: 1 imagen nano-banana-2-lite {a.aspecto}. Añade --execute para generarla.")
                return 0
            generar_imagen(prompt, Path(a.out), Path(a.estado), a.aspecto)
            print(f"Imagen guardada en {a.out}")
        elif a.cmd == "recorte":
            print("Recorte", recortar_croma(Path(a.entrada), Path(a.salida)))
        elif a.cmd == "master":
            masterizar(Path(a.entrada), Path(a.salida))
            print(f"Master en {a.salida}")
        elif a.cmd == "sfx":
            print("SFX:", ", ".join(sintetizar_sfx(Path(a.dir))))
    except ErrorVox as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
