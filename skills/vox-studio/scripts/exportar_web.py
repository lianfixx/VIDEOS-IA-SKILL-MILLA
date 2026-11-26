#!/usr/bin/env python3
"""Versión web de un video ya aprobado, para usarlo en una página (de venta o de un espacio).

Uso:
  python3 exportar_web.py VIDEO.mp4 --out CARPETA [--con-audio] [--scrub]
                          [--tope-mb 3] [--lado-corto 720] [--poster-en SEG]

Tres usos:
  sin opciones   fondo del hero: sin audio, en loop; la compresión sube hasta caber en --tope-mb (3 MB)
  --con-audio    video explicativo con controles: conserva la voz; sin tope salvo que se pida --tope-mb
  --scrub        añade scrub.mp4, un cuadro clave en cada cuadro, para video que avanza con el scroll

Deja en CARPETA:
  web.mp4      H.264, faststart, para cualquier navegador
  web.webm     VP9 (y Opus con --con-audio), normalmente más ligero
  poster.webp  el cuadro elegido con --poster-en (por defecto el primero): lo que se ve mientras carga
               y con movimiento reducido
  poster.jpg   el mismo cuadro, para quien no lee WebP
  scrub.mp4    solo con --scrub
  web.json     pesos, compresión usada, si cabe en el tope y si el loop cierra sin salto (orienta; se mira a ojo)

No toca el original, no sube nada y no gasta saldo. Requiere ffmpeg y ffprobe (con libx264, libvpx-vp9,
libwebp y libopus, como el ffmpeg de Homebrew). El mismo archivo vive en vox-studio, editor-studio y
milla-video-studio; las pruebas de Vox Studio comprueban que las tres copias sean idénticas.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

TOPE_LOOP_MB = 3.0


def correr(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Falló: {' '.join(args)}\n{r.stderr[-800:]}")
    return r


def mb(ruta):
    return round(os.path.getsize(ruta) / 1_048_576, 2)


def datos(ruta):
    r = correr(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                "-of", "json", ruta])
    j = json.loads(r.stdout)
    video = [s for s in j.get("streams", []) if s.get("codec_type") == "video"]
    if not video:
        sys.exit(f"{ruta} no tiene pista de video.")
    audio = any(s.get("codec_type") == "audio" for s in j.get("streams", []))
    return video[0]["width"], video[0]["height"], float(j["format"]["duration"]), audio


def escala(corto):
    """El lado corto queda en `corto` px: 1280x720 si es horizontal, 720x1280 si es vertical."""
    return f"scale='if(gt(iw,ih),-2,{corto})':'if(gt(iw,ih),{corto},-2)':flags=lanczos"


def h264(src, dst, crf, corto, audio, keyint=None):
    aud = ["-c:a", "aac", "-b:a", "128k"] if (audio and not keyint) else ["-an"]
    x264 = ["-x264-params", f"keyint={keyint}:min-keyint={keyint}:scenecut=0"] if keyint else []
    correr(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, *aud, "-vf", escala(corto),
            "-c:v", "libx264", "-preset", "veryfast", "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-crf", str(crf), *x264, "-movflags", "+faststart", dst])


def vp9(src, dst, crf, corto, audio):
    aud = ["-c:a", "libopus", "-b:a", "96k"] if audio else ["-an"]
    correr(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, *aud, "-vf", escala(corto),
            "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", str(crf), "-row-mt", "1", "-deadline", "good",
            "-cpu-used", "4", "-pix_fmt", "yuv420p", dst])


def con_tope(fn, src, dst, crf, tope, paso, maximo, *args):
    while True:
        fn(src, dst, crf, *args)
        if tope is None or mb(dst) <= tope or crf >= maximo:
            return crf
        crf = min(crf + paso, maximo)


def _ssim(a, b):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", a, "-i", b, "-lavfi",
                        "[0:v]format=gray[a];[1:v]format=gray[b];[a][b]ssim", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"All:([0-9.]+)", r.stderr)
    return float(m.group(1)) if m else None


def revisar_loop(src, tmp):
    """Compara el salto del último cuadro al primero con el paso normal entre dos cuadros seguidos."""
    ini = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    c = os.path.join(tmp, "c%d.png")
    correr(ini + ["-i", src, "-vf", "select=lt(n\\,2)", "-fps_mode", "passthrough", c])
    correr(ini + ["-sseof", "-0.2", "-i", src, "-update", "1", os.path.join(tmp, "z.png")])
    paso = _ssim(os.path.join(tmp, "c1.png"), os.path.join(tmp, "c2.png"))
    salto = _ssim(os.path.join(tmp, "z.png"), os.path.join(tmp, "c1.png"))
    if paso is None or salto is None:
        return {"sin_salto": None}
    return {"parecido_entre_cuadros_seguidos": round(paso, 4), "parecido_ultimo_vs_primero": round(salto, 4),
            "sin_salto": salto >= paso - 0.02}


def main(argv=None):
    p = argparse.ArgumentParser(description="Versión web de un video aprobado.")
    p.add_argument("video")
    p.add_argument("--out", required=True)
    p.add_argument("--con-audio", action="store_true")
    p.add_argument("--scrub", action="store_true")
    p.add_argument("--tope-mb", type=float, default=None)
    p.add_argument("--lado-corto", type=int, default=720)
    p.add_argument("--poster-en", type=float, default=0.0)
    a = p.parse_args(argv)

    w, h, dur, tiene_audio = datos(a.video)
    if a.con_audio and not tiene_audio:
        sys.exit("Se pidió --con-audio y el video no tiene audio.")
    if not 0 <= a.poster_en < dur:
        sys.exit(f"--poster-en debe estar entre 0 y {dur:.2f} s.")
    tope = a.tope_mb if a.tope_mb is not None else (None if a.con_audio else TOPE_LOOP_MB)
    os.makedirs(a.out, exist_ok=True)
    o = lambda n: os.path.join(a.out, n)

    crf_mp4 = con_tope(h264, a.video, o("web.mp4"), 26, tope, 2, 36, a.lado_corto, a.con_audio)
    crf_webm = con_tope(vp9, a.video, o("web.webm"), 36, tope, 3, 48, a.lado_corto, a.con_audio)
    cuadro = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(a.poster_en), "-i", a.video,
              "-frames:v", "1", "-vf", escala(a.lado_corto)]
    correr(cuadro + ["-c:v", "libwebp", "-quality", "80", o("poster.webp")])
    correr(cuadro + ["-q:v", "3", o("poster.jpg")])
    if a.scrub:
        h264(a.video, o("scrub.mp4"), crf_mp4, a.lado_corto, False, keyint=1)
    with tempfile.TemporaryDirectory() as tmp:
        loop = None if a.con_audio else revisar_loop(a.video, tmp)

    informe = {
        "origen": os.path.basename(a.video), "origen_px": f"{w}x{h}", "duracion_s": round(dur, 2),
        "uso": "explicativo con audio" if a.con_audio else "fondo en loop",
        "lado_corto_px": a.lado_corto, "tope_mb": tope, "poster_en_s": a.poster_en,
        "mp4": {"mb": mb(o("web.mp4")), "crf": crf_mp4},
        "webm": {"mb": mb(o("web.webm")), "crf": crf_webm},
        "poster_webp_kb": round(os.path.getsize(o("poster.webp")) / 1024),
        "poster_jpg_kb": round(os.path.getsize(o("poster.jpg")) / 1024),
        "scrub_mb": mb(o("scrub.mp4")) if a.scrub else None,
        "loop": loop,
        "avisos": [],
    }
    if tope is not None:
        for k in ("mp4", "webm"):
            informe[k]["cabe_en_tope"] = informe[k]["mb"] <= tope
            if not informe[k]["cabe_en_tope"]:
                informe["avisos"].append(f"{k} no cabe en {tope} MB ni con la compresión máxima: acortar el tramo "
                                         "o bajar --lado-corto.")
    if not a.con_audio and dur > 10:
        informe["avisos"].append(f"Dura {dur:.1f} s; para fondo del hero conviene un tramo de 6 a 8 s.")
    if loop and loop.get("sin_salto") is False:
        informe["avisos"].append("El final no se parece al inicio: el loop puede brincar. Mirarlo a ojo.")
    with open(o("web.json"), "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    return informe


if __name__ == "__main__":
    main()
