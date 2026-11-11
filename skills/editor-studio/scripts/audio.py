"""Sonido: efectos sintetizados aquí (sin grabaciones ajenas), tapado de groserías, mezcla y auditoría.

La voz manda. Se lleva a -16 LUFS, los efectos quedan por debajo de ella y la mezcla final
sale a -14 LUFS con pico máximo de -1.5 dBTP, que es lo que piden TikTok, Reels y YouTube.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from comun import ErrorEditor, correr, duracion, medir_sonoridad

VOZ_LUFS = -16.0
EFECTO_BAJO_VOZ = 8.0       # dB que un efecto queda bajo la voz, salvo que el plan diga otra cosa (6 a 14)
MUSICA_BAJO_VOZ = 18.0      # LU que la música queda bajo la voz
LUFS_FINAL = (-15.0, -13.0)
PICO_MAX = -1.5

# Efectos hechos con osciladores y ruido filtrado. Uno por idea: repetido pierde la gracia.
EFECTOS = {
    "pop": "sine=f=880:d=0.09,afade=t=out:st=0.02:d=0.07",
    "clic": "sine=f=1900:d=0.03,afade=t=out:st=0.005:d=0.025",
    "deslizar": "anoisesrc=d=0.4:c=pink:a=0.6,bandpass=f=1400:w=1200,afade=t=in:d=0.22,afade=t=out:st=0.24:d=0.16",
    "golpe": "sine=f=64:d=0.26,afade=t=out:st=0.03:d=0.23",
    "subida": "anoisesrc=d=0.9:c=white:a=0.5,highpass=f=600,bandpass=f=2600:w=2200,afade=t=in:d=0.85:curve=exp,afade=t=out:st=0.86:d=0.04",
    "ding": "sine=f=1318:d=0.5,afade=t=out:st=0.02:d=0.48",
    "papel": "anoisesrc=d=0.28:c=white:a=0.5,highpass=f=2500,afade=t=in:d=0.05,afade=t=out:st=0.1:d=0.18",
    "teclas": "anoisesrc=d=0.5:c=white:a=0.6,highpass=f=3000,tremolo=f=13:d=0.95,afade=t=out:st=0.4:d=0.1",
    "bip": "sine=f=1000:d=6.0",          # largo de sobra: se recorta a lo que dure la palabra
}
# Cuándo conviene cada uno (lo usa `sonido` para proponer; decide quien edita)
PARA_PIEZA = {"titulo": "deslizar", "rotulo": "clic", "sello": "golpe", "dato": "ding", "cierre": "pop",
              "foto": "papel", "panel": "deslizar", "barrido": "deslizar", "detras": "golpe", "inserto": "deslizar",
              "particulas": "pop"}
ADELANTO = {"deslizar": 0.12, "subida": 0.9}     # segundos que el efecto arranca antes de la pieza


def sintetizar(destino: Path) -> list[str]:
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, filtro in EFECTOS.items():
        correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", filtro, "-ar", "48000", "-ac", "2",
                "-af", "alimiter=limit=0.7", str(destino / f"{nombre}.wav")], capture_output=True)
    return sorted(EFECTOS)


def proponer(piezas: list[dict], densidad: str) -> list[dict]:
    """Punto de partida: un efecto en las piezas que más pesan, según la densidad. Se revisa con criterio."""
    orden = {"ninguna": [], "minima": ["sello", "dato", "cierre"],
             "media": ["sello", "dato", "cierre", "titulo", "panel", "detras", "inserto"],
             "alta": list(PARA_PIEZA)}.get(densidad)
    if orden is None:
        raise ErrorEditor("densidad debe ser ninguna, minima, media o alta")
    out, previo = [], None
    for p in piezas:
        if p["tipo"] in orden:
            sonido = PARA_PIEZA[p["tipo"]]
            if sonido == previo and p["tipo"] not in ("sello", "dato"):
                continue                       # no repetir el mismo sonido dos piezas seguidas
            out.append({"en": p["id"], "sonido": sonido})
            previo = sonido
    return out


def _pico_db(ruta: Path) -> float:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(ruta), "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"max_volume:\s*(-?[\d.]+) dB", r.stderr)
    if not m:
        raise ErrorEditor(f"no se pudo medir {ruta.name}")
    return float(m.group(1))


def mezclar(voz: Path, salida: Path, efectos: list[dict], dir_efectos: Path, total: float,
            censura: list[dict] | None = None, musica: Path | None = None) -> dict:
    """Voz nivelada + efectos colocados + (música) → una sola pista WAV de 48 kHz.

    efectos: [{"t": segundos, "sonido": nombre, "db": dB bajo la voz}]
    censura: [{"t0", "t1"}] tramos donde la voz se apaga y suena un tono.
    """
    m = medir_sonoridad(voz, VOZ_LUFS)
    try:
        medida = float(m["input_i"])
    except (KeyError, ValueError) as exc:
        raise ErrorEditor("la voz no se pudo medir: ¿el video trae audio?") from exc
    if medida < -60:
        raise ErrorEditor("la pista de voz está en silencio")
    ganancia_voz = VOZ_LUFS - medida
    pico_voz = _pico_db(voz) + ganancia_voz
    entradas, grafo, mezcla = ["-i", str(voz)], [], []
    filtro_voz = f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={ganancia_voz:.2f}dB"
    for c in censura or []:
        filtro_voz += f",volume=enable='between(t,{c['t0']:.3f},{c['t1']:.3f})':volume=0"
    grafo.append(filtro_voz + ",alimiter=limit=0.85:level=false[voz]")
    mezcla.append("[voz]")
    n, niveles = 1, []
    for e in list(efectos) + [{"t": c["t0"], "sonido": "bip", "db": 10.0, "dura": c["t1"] - c["t0"]} for c in (censura or [])]:
        archivo = dir_efectos / f"{e['sonido']}.wav"
        if not archivo.exists():
            raise ErrorEditor(f"falta el efecto {e['sonido']}: corre `sonido` primero")
        bajo = min(14.0, max(6.0, float(e.get("db", EFECTO_BAJO_VOZ))))
        ganancia = (pico_voz - bajo) - _pico_db(archivo)          # el pico del efecto queda `bajo` dB bajo el de la voz
        t = max(0.0, float(e["t"]) - ADELANTO.get(e["sonido"], 0.0))
        recorte = f"atrim=0:{e['dura']:.3f},afade=t=out:st={max(0.0, e['dura'] - 0.01):.3f}:d=0.01," if e.get("dura") else ""
        entradas += ["-i", str(archivo)]
        grafo.append(f"[{n}:a]{recorte}volume={ganancia:.2f}dB,adelay={int(t * 1000)}|{int(t * 1000)}[e{n}]")
        mezcla.append(f"[e{n}]")
        niveles.append({"sonido": e["sonido"], "t": round(t, 3), "bajo_la_voz_db": bajo})
        n += 1
    info_musica = None
    if musica:
        mm = float(medir_sonoridad(musica, VOZ_LUFS)["input_i"])
        gan = (VOZ_LUFS - MUSICA_BAJO_VOZ) - mm
        entradas += ["-stream_loop", "-1", "-i", str(musica)]
        grafo.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gan:.2f}dB,atrim=0:{total:.3f},"
                     f"afade=t=in:d=0.6,afade=t=out:st={max(0.0, total - 1.2):.3f}:d=1.2[mus]")
        mezcla.append("[mus]")
        info_musica = {"archivo": musica.name, "bajo_la_voz_lu": MUSICA_BAJO_VOZ}
    grafo.append(f"{''.join(mezcla)}amix=inputs={len(mezcla)}:normalize=0:duration=first,atrim=0:{total:.3f}[m]")
    salida.parent.mkdir(parents=True, exist_ok=True)
    guion = salida.with_suffix(".filtro.txt")
    guion.write_text(";\n".join(grafo), encoding="utf-8")
    correr(["ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex_script", str(guion), "-map", "[m]",
            "-ar", "48000", "-c:a", "pcm_s16le", str(salida)], capture_output=True)
    guion.unlink(missing_ok=True)
    return {"ganancia_voz_db": round(ganancia_voz, 2), "efectos": niveles, "musica": info_musica,
            "censuras": len(censura or [])}


def masterizar(video_mudo: Path, mezcla: Path, salida: Path) -> float:
    """Une imagen y mezcla, lleva a -14 LUFS con ganancia fija y limita los picos. Devuelve la ganancia aplicada."""
    ganancia = round(-14.0 - float(medir_sonoridad(mezcla)["input_i"]), 2)
    salida.parent.mkdir(parents=True, exist_ok=True)
    correr(["ffmpeg", "-y", "-v", "error", "-i", str(video_mudo), "-i", str(mezcla), "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-af", f"volume={ganancia}dB,alimiter=limit=0.8:level=false:attack=3:release=60",
            "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(salida)],
           capture_output=True)
    return ganancia


def auditar(final: Path, mezcla_info: dict, ganancia_master: float, esperado_s: float) -> dict:
    """Números del archivo entregable y avisos. Sin avisos significa en rango, no aprobado: falta el oído de Emi."""
    m = medir_sonoridad(final)
    lufs, pico, rango = float(m["input_i"]), float(m["input_tp"]), float(m["input_lra"])
    real = duracion(final)
    avisos = []
    if not LUFS_FINAL[0] <= lufs <= LUFS_FINAL[1]:
        avisos.append(f"sonoridad final {lufs:.1f} LUFS; debe quedar en -14 ± 1")
    if pico > PICO_MAX:
        avisos.append(f"pico de {pico:.1f} dBTP; el tope es {PICO_MAX}")
    if abs(ganancia_master) > 4:
        avisos.append(f"el master movió {ganancia_master:+.1f} dB: la mezcla venía desbalanceada")
    if abs(real - esperado_s) > 0.15:
        avisos.append(f"el archivo dura {real:.2f} s y la edición {esperado_s:.2f} s")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final), "-af", "silencedetect=noise=-50dB:d=1.5",
                        "-f", "null", "-"], capture_output=True, text=True)
    mudos = re.findall(r"silence_start: ([\d.]+)", r.stderr)
    if mudos:
        avisos.append("hay silencio total de más de 1.5 s en: " + ", ".join(f"{float(x):.1f} s" for x in mudos[:5]))
    return {"lufs": round(lufs, 2), "pico_dbtp": round(pico, 2), "rango_lu": round(rango, 2), "duracion_s": round(real, 2),
            "ganancia_master_db": ganancia_master, "mezcla": mezcla_info, "avisos": avisos,
            "nota": "Una IA no puede oír: cómo suena la voz, el ritmo y si un efecto molesta lo decide Emi escuchando."}
