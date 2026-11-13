"""Corte: silencios por energía del audio, muletillas, tomas repetidas y aplicación al cuadro.

Método (ver OFICIO.md): se corta por lo que suena, no solo por los huecos del texto; las
tomas repetidas se proponen y decide quien edita; nada se aplica sin aprobación de Emi.
"""
from __future__ import annotations

import difflib
import re
import shutil
import time
import unicodedata
import wave
from pathlib import Path

from comun import ErrorEditor, correr, escribir_json, formato_tiempo, huella

try:  # numpy acelera la medición; sin él no se puede cortar por energía
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

VENTANA = 0.010           # segundos por ventana de energía
RUIDO_BREVE = 0.060       # un ruido más corto que esto no parte un silencio
BAJO_LA_VOZ = 16.0        # dB bajo la mediana de la voz: de ahí para abajo es silencio
MIN_CUADROS = 2           # un corte más corto que esto no vale la pena
FUNDIDO = 0.006           # segundos de fundido de audio en cada empalme

# Cada ritmo: silencio mínimo que se toca y aire que queda a cada lado del corte.
RITMOS = {
    "apretado": {"silencio": 0.30, "aire": 0.08},
    "natural": {"silencio": 0.55, "aire": 0.16},
    "minimo": {"silencio": 1.20, "aire": 0.30},
}
# Sonidos de relleno que no son palabras: se proponen siempre.
MULETILLAS_SEGURAS = {"eh", "ehh", "em", "emm", "mm", "mmm", "mhm", "ah", "ahh", "uh", "um", "hm", "hmm", "aa", "ee"}
# Palabras que a veces son muletilla y a veces dicen algo: se proponen solo si están aisladas por pausas.
MULETILLAS_DUDOSAS = {"este", "pues", "bueno", "osea", "digamos", "basicamente", "literal", "tipo", "ok", "okay", "entonces", "no"}
FRASES_MULETILLA = [("o", "sea"), ("es", "decir"), ("la", "verdad"), ("como", "que"), ("por", "asi", "decirlo")]
GROSERIAS = {"pendejo", "pendeja", "pendejos", "pendejada", "pendejadas", "chingar", "chingada", "chingado", "chingados",
             "chingon", "chingona", "chinga", "chingue", "chingas", "verga", "vergas", "puto", "puta", "putos", "putas",
             "putazo", "cabron", "cabrona", "cabrones", "culero", "culera", "culeros", "mierda", "mierdas", "joder",
             "pinche", "pinches", "mamada", "mamadas", "culo", "wey", "guey", "carajo", "coño", "cono", "marica", "maricon"}
# «wey», «güey» y «pinche» son modismo antes que grosería en el habla de Emi: se avisan, no se tapan solos.
MODISMOS = {"wey", "guey", "pinche", "pinches", "chingon", "chingona"}


def normal(txt: str) -> str:
    """minúsculas, sin acentos ni signos: para comparar palabras."""
    t = unicodedata.normalize("NFD", txt.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", t)


def fin_de_frase(txt: str) -> bool:
    return txt.rstrip().endswith((".", "?", "!", "…"))


# ---------- energía ----------

def leer_wav(ruta: Path):
    """WAV PCM de 16 bits a un arreglo mono en [-1, 1] y su frecuencia."""
    if np is None:
        raise ErrorEditor("falta numpy: python3 -m pip install numpy")
    try:
        with wave.open(str(ruta), "rb") as w:
            if w.getsampwidth() != 2:
                raise ErrorEditor(f"{ruta.name} no es PCM de 16 bits; conviértelo con `ingerir`")
            hz, canales = w.getframerate(), w.getnchannels()
            crudo = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
    except (wave.Error, EOFError) as exc:
        raise ErrorEditor(f"{ruta.name} no es un WAV legible: {exc}") from exc
    if canales > 1:
        crudo = crudo.reshape(-1, canales).mean(axis=1)
    return crudo, hz


def energia_db(muestras, hz: int):
    """Energía RMS en dB por ventana de 10 ms."""
    n = max(1, int(hz * VENTANA))
    total = (len(muestras) // n) * n
    if total == 0:
        return np.zeros(0, dtype=np.float32)
    rms = np.sqrt((muestras[:total].reshape(-1, n) ** 2).mean(axis=1) + 1e-12)
    return (20 * np.log10(rms + 1e-9)).astype(np.float32)


def nivel_de_voz(db, palabras: list[dict] | None) -> float:
    """Mediana de la energía donde hay voz. Con palabras: dentro de ellas; sin ellas: el tercio más sonoro."""
    if len(db) == 0:
        raise ErrorEditor("el audio está vacío")
    if palabras:
        mascara = np.zeros(len(db), dtype=bool)
        for p in palabras:
            mascara[int(p["t0"] / VENTANA):int(p["t1"] / VENTANA) + 1] = True
        if mascara.sum() >= 20:
            return float(np.median(db[mascara]))
    return float(np.median(np.sort(db)[-max(1, len(db) // 3):]))


def silencios(db, umbral_db: float, minimo: float) -> list[tuple[float, float]]:
    """Tramos por debajo del umbral que duran al menos `minimo`. Un ruido breve no parte un silencio."""
    callado = db < umbral_db
    breve = int(round(RUIDO_BREVE / VENTANA))
    i, n = 0, len(callado)
    while i < n:                         # tapar los ruidos breves entre dos silencios
        if not callado[i]:
            j = i
            while j < n and not callado[j]:
                j += 1
            if 0 < i and j < n and (j - i) <= breve:
                callado[i:j] = True
            i = j
        else:
            i += 1
    out, i = [], 0
    while i < n:
        if callado[i]:
            j = i
            while j < n and callado[j]:
                j += 1
            if (j - i) * VENTANA >= minimo:
                out.append((round(i * VENTANA, 3), round(j * VENTANA, 3)))
            i = j
        else:
            i += 1
    return out


# ---------- propuestas ----------

def _al_cuadro(t: float, fps: int, arriba: bool = False) -> float:
    c = t * fps
    c = int(c + 0.999999) if arriba else int(c + 1e-6)
    return round(c / fps, 6)


def _palabra_en(palabras: list[dict], t: float) -> dict | None:
    for p in palabras:
        if p["t0"] < t < p["t1"]:
            return p
    return None


def umbral_de_silencio(db, palabras: list[dict] | None) -> tuple[float, float, float]:
    """(umbral, nivel de voz, piso de ruido). Con ruido o música de fondo el umbral sube con el piso:
    16 dB bajo la voz quedaría por debajo del ruido y nunca habría silencio."""
    voz = nivel_de_voz(db, palabras)
    piso = float(np.percentile(db, 10))
    return max(voz - BAJO_LA_VOZ, min(voz - 6.0, piso + 6.0)), voz, piso


def huecos_de_texto(palabras: list[dict], minimo: float, total: float) -> list[tuple[float, float]]:
    """Pausas según la transcripción: sirven cuando el fondo no deja medir el silencio en el audio."""
    out, previo = [], 0.0
    for p in sorted(palabras, key=lambda p: p["t0"]):
        if p["t0"] - previo >= minimo:
            out.append((round(previo, 3), round(p["t0"], 3)))
        previo = max(previo, p["t1"])
    if total - previo >= minimo:
        out.append((round(previo, 3), round(total, 3)))
    return out


def proponer_silencios(db, palabras: list[dict], ritmo: str, fps: int, total: float) -> list[dict]:
    if ritmo not in RITMOS:
        raise ErrorEditor(f"ritmo desconocido: {ritmo}. Opciones: {', '.join(RITMOS)}")
    r = RITMOS[ritmo]
    umbral, voz, piso = umbral_de_silencio(db, palabras)
    medidos = silencios(db, umbral, r["silencio"])
    if palabras and voz - piso < 12.0:
        # fondo fuerte: se suman las pausas que marca la transcripción y que el audio no dejó ver
        medidos = sorted(set(medidos) | {h for h in huecos_de_texto(palabras, r["silencio"], total)
                                         if not any(a < h[1] and h[0] < b for a, b in medidos)})
    cortes = []
    for a, b in medidos:
        antes = max((p for p in palabras if p["t1"] <= a + 0.05), key=lambda p: p["t1"], default=None)
        aire_izq = r["aire"] * (1.5 if antes and fin_de_frase(antes["txt"]) else 1.0)
        t0, t1 = a + aire_izq, b - r["aire"]
        if a <= 0.02:                     # silencio inicial: el video arranca casi pegado a la voz
            t0 = 0.0
        if b >= total - 0.02:             # silencio final: queda media segundo de cola
            t1, t0 = total, min(total, a + 0.5)
        # nunca dentro de una palabra: la transcripción manda sobre la energía
        dentro = _palabra_en(palabras, t0)
        if dentro:
            t0 = dentro["t1"] + 0.03
        dentro = _palabra_en(palabras, t1)
        if dentro:
            t1 = dentro["t0"] - 0.03
        # una palabra dicha en voz baja dentro del «silencio» no se corta: el corte se parte a sus lados
        tramos, inicio = [], t0
        for w in sorted((w for w in palabras if t0 < (w["t0"] + w["t1"]) / 2 < t1), key=lambda w: w["t0"]):
            tramos.append((inicio, w["t0"] - r["aire"]))
            inicio = w["t1"] + r["aire"]
        tramos.append((inicio, t1))
        for x0, x1 in tramos:
            x0, x1 = _al_cuadro(x0, fps, arriba=True), (total if x1 >= total - 0.02 else _al_cuadro(x1, fps))
            if x1 - x0 >= max(MIN_CUADROS / fps, 0.12 if len(tramos) > 1 else 0):
                cortes.append({"t0": x0, "t1": x1, "tipo": "silencio",
                               "motivo": f"pausa de {b - a:.2f} s; queda de {(b - a) - (x1 - x0):.2f} s"})
    return cortes


def proponer_muletillas(palabras: list[dict], fps: int) -> list[dict]:
    cortes, n = [], len(palabras)
    for i, p in enumerate(palabras):
        w = normal(p["txt"])
        antes = p["t0"] - (palabras[i - 1]["t1"] if i else 0.0)
        despues = (palabras[i + 1]["t0"] if i + 1 < n else p["t1"] + 9) - p["t1"]
        segura = w in MULETILLAS_SEGURAS
        dudosa = w in MULETILLAS_DUDOSAS and antes >= 0.18 and despues >= 0.18 and not fin_de_frase(p["txt"])
        if not (segura or dudosa):
            continue
        t0 = _al_cuadro(p["t0"] - min(antes, 0.30) / 2, fps, arriba=True)
        t1 = _al_cuadro(p["t1"] + min(despues, 0.30) / 2, fps)
        if t1 - t0 >= MIN_CUADROS / fps:
            cortes.append({"t0": t0, "t1": t1, "tipo": "muletilla", "texto": p["txt"],
                           "motivo": "sonido de relleno" if segura else "muletilla aislada por pausas: confirmar leyendo la frase"})
    for frase in FRASES_MULETILLA:
        k = len(frase)
        for i in range(n - k + 1):
            if tuple(normal(q["txt"]) for q in palabras[i:i + k]) == frase:
                a, b = palabras[i], palabras[i + k - 1]
                antes = a["t0"] - (palabras[i - 1]["t1"] if i else 0.0)
                despues = (palabras[i + k]["t0"] if i + k < n else b["t1"] + 9) - b["t1"]
                if antes >= 0.15 or despues >= 0.15:
                    cortes.append({"t0": _al_cuadro(a["t0"], fps, arriba=True), "t1": _al_cuadro(b["t1"], fps),
                                   "tipo": "muletilla", "texto": " ".join(frase),
                                   "motivo": "frase de relleno: confirmar leyendo la frase", "estado": "dudoso"})
    return cortes


def frases(palabras: list[dict], pausa: float = 0.6) -> list[list[dict]]:
    """Parte la transcripción en frases por pausa larga o punto final."""
    out, actual = [], []
    for i, p in enumerate(palabras):
        actual.append(p)
        sig = palabras[i + 1]["t0"] if i + 1 < len(palabras) else None
        if sig is None or sig - p["t1"] >= pausa or fin_de_frase(p["txt"]):
            out.append(actual)
            actual = []
    return [f for f in out if f]


def proponer_tomas(palabras: list[dict], fps: int) -> list[dict]:
    """Tomas repetidas y arranques en falso: gana la última completa. Son propuestas: decide quien edita."""
    fr, cortes, quitadas = frases(palabras), [], set()
    for i in range(len(fr)):
        if i in quitadas:
            continue
        a = [normal(p["txt"]) for p in fr[i] if normal(p["txt"])]
        if not a:
            continue
        for j in range(i + 1, min(i + 4, len(fr))):
            b = [normal(p["txt"]) for p in fr[j] if normal(p["txt"])]
            if not b:
                continue
            comun = 0
            while comun < min(len(a), len(b)) and a[comun] == b[comun]:
                comun += 1
            parecido = difflib.SequenceMatcher(None, a, b[:max(len(a), 1) + 2]).ratio()
            en_falso = len(a) <= 4 and comun >= min(2, len(a)) and len(b) >= len(a)
            repetida = len(a) >= 3 and (comun >= 3 or parecido >= 0.72) and len(b) >= len(a) * 0.6
            if en_falso or repetida:
                # se quita desde esta toma hasta donde empieza la que gana (incluye tomas intermedias fallidas)
                antes = max((w["t1"] for w in palabras if w["t1"] <= fr[i][0]["t0"] + 1e-6), default=0.0)
                t0 = _al_cuadro(max(antes + 0.02, fr[i][0]["t0"] - 0.05), fps, arriba=True)      # sin comerse la cola de la palabra anterior
                t1 = _al_cuadro(fr[j][0]["t0"] - 0.08, fps)
                if t1 - t0 >= MIN_CUADROS / fps:
                    corte = {"t0": t0, "t1": t1, "tipo": "toma",
                             "texto": " ".join(p["txt"] for p in fr[i])[:120],
                             "motivo": ("arranque en falso" if en_falso and not repetida else "toma repetida")
                             + f"; gana la de {formato_tiempo(fr[j][0]['t0'])}: «"
                             + " ".join(p["txt"] for p in fr[j])[:80] + "»"}
                    if j > i + 1:       # entre las dos hay frases distintas: puede ser una repetición a propósito
                        medio = " / ".join(" ".join(p["txt"] for p in fr[k])[:50] for k in range(i + 1, j))
                        corte["estado"] = "dudoso"
                        corte["motivo"] += f". OJO: se irían también {j - i - 1} frases de en medio («{medio}»); puede ser énfasis y no una toma repetida"
                    cortes.append(corte)
                    quitadas.update(range(i, j))
                break
    return cortes


def proponer_censura(palabras: list[dict]) -> list[dict]:
    """Groserías: no se cortan, se tapan con un sonido. Los modismos solo se avisan."""
    out = []
    for i, p in enumerate(palabras):
        w = normal(p["txt"])
        if w in GROSERIAS:
            out.append({"i": i, "t0": round(p["t0"], 3), "t1": round(p["t1"], 3), "texto": p["txt"],
                        "accion": "avisar" if w in MODISMOS else "tapar"})
    return out


PEGADOS = 0.25            # dos cortes separados por menos que esto, sin palabra en medio, son uno solo


def unir(cortes: list[dict], fps: int, palabras: list[dict] | None = None) -> list[dict]:
    """Ordena, funde los que se tocan y numera. Una toma absorbe los silencios y muletillas que contiene.

    Dos cortes separados por una rebanada de aire (sin ninguna palabra) se funden: dejar 0.1 s de
    ambiente entre dos cortes suena a tropiezo.
    """
    orden = sorted((dict(c) for c in cortes), key=lambda c: (c["t0"], -c["t1"]))
    out: list[dict] = []

    def hay_palabra(a: float, b: float) -> bool:
        return any(a - 0.02 <= (p["t0"] + p["t1"]) / 2 <= b + 0.02 for p in palabras or [])

    peso = {"silencio": 0, "muletilla": 1, "manual": 2, "toma": 3}
    for c in orden:
        c.setdefault("estado", "propuesto")
        pegado = bool(out) and c["t0"] - out[-1]["t1"] < PEGADOS and not hay_palabra(out[-1]["t1"], c["t0"])
        if out and (c["t0"] <= out[-1]["t1"] + 1 / fps or pegado) and c["estado"] == out[-1]["estado"]:
            prev = out[-1]
            prev["t1"] = max(prev["t1"], c["t1"])
            if peso.get(c["tipo"], 0) > peso.get(prev["tipo"], 0):      # manda el motivo que más pesa
                prev.update({"tipo": c["tipo"], "motivo": c["motivo"], "texto": c.get("texto", "")})
            if "con su pausa" not in prev["motivo"] and prev["tipo"] != "silencio":
                prev["motivo"] += " (con su pausa)"
        else:
            out.append(c)
    for k, c in enumerate(out, 1):
        c["id"] = f"c{k:03d}"
        c["t0"], c["t1"] = round(c["t0"], 6), round(c["t1"], 6)
    return out


def plan(wav: Path, palabras: list[dict], ritmo: str, fps: int, muletillas: str = "seguras") -> dict:
    muestras, hz = leer_wav(wav)
    db = energia_db(muestras, hz)
    total = len(muestras) / hz
    umbral, voz, piso = umbral_de_silencio(db, palabras)
    avisos = []
    if voz < -60:
        avisos.append("el audio está prácticamente en silencio: revisa que el video traiga voz")
    elif voz - piso < 12.0:
        avisos.append(f"hay ruido o música de fondo fuerte (solo {voz - piso:.0f} dB bajo la voz): los silencios se apoyan en las pausas "
                      "de la transcripción; escucha la vista previa con más cuidado")
    fuera = [p for p in palabras if p["t0"] >= total]
    if fuera:
        avisos.append(f"{len(fuera)} palabras de la transcripción caen después del final del audio: ¿es la transcripción de este video?")
    cortes = proponer_silencios(db, palabras, ritmo, fps, total)
    if palabras and muletillas != "ninguna":
        m = proponer_muletillas(palabras, fps)
        if muletillas == "seguras":
            for c in m:
                if c["motivo"] != "sonido de relleno":
                    c["estado"] = "dudoso"
        cortes += m
        cortes += proponer_tomas(palabras, fps)
    return {"version": 1, "fps": fps, "ritmo": ritmo, "duracion_crudo_s": round(total, 3),
            "voz_db": round(voz, 1), "piso_db": round(piso, 1), "umbral_db": round(umbral, 1), "muletillas": muletillas,
            "avisos": avisos,
            "cortes": unir(cortes, fps, palabras), "censura": proponer_censura(palabras), "aprobacion": None,
            "creado": time.strftime("%Y-%m-%d %H:%M:%S")}


# ---------- aplicar ----------

def vigentes(p: dict, incluir_propuestos: bool = False) -> list[dict]:
    ok = {"aprobado"} | ({"propuesto"} if incluir_propuestos else set())
    return [c for c in p["cortes"] if c.get("estado") in ok]


def tramos_que_quedan(p: dict, incluir_propuestos: bool = False) -> list[tuple[float, float]]:
    total, t, out = p["duracion_crudo_s"], 0.0, []
    for c in sorted(vigentes(p, incluir_propuestos), key=lambda c: c["t0"]):
        if c["t0"] > t + 1e-6:
            out.append((round(t, 6), round(c["t0"], 6)))
        t = max(t, c["t1"])
    if total > t + 1e-6:
        out.append((round(t, 6), round(total, 6)))
    return [(x, y) for x, y in out if y - x >= MIN_CUADROS / p["fps"]]      # una rebanada de menos de dos cuadros no se conserva


def huella_plan(p: dict) -> str:
    """Cambia si cambia cualquier corte vigente: la aprobación vale solo para este plan."""
    return huella(*(f"{c['t0']:.5f}-{c['t1']:.5f}-{c['estado']}" for c in p["cortes"]),
                  *(f"censura-{x.get('i')}-{x.get('accion')}" for x in p.get("censura") or []), str(p["fps"]))[:16]


def exigir_aprobacion(p: dict) -> None:
    ap = p.get("aprobacion")
    if not ap or not ap.get("por"):
        raise ErrorEditor("los cortes no están aprobados: enséñale a Emi la tabla y la vista previa, y registra su respuesta con `aprobar`")
    if ap.get("huella") != huella_plan(p):
        raise ErrorEditor("los cortes cambiaron después de la aprobación: vuelve a enseñarlos y a aprobar")
    if any(c.get("estado") in ("propuesto", "dudoso") for c in p["cortes"]):
        raise ErrorEditor("quedan cortes sin decidir (propuesto o dudoso): cada uno debe quedar aprobado o descartado")


def remapear(palabras: list[dict], quedan: list[tuple[float, float]]) -> list[dict]:
    """Tiempos de cada palabra en el video ya cortado. Una palabra que cae en lo quitado desaparece."""
    out, corrido = [], 0.0
    for a, b in quedan:
        for p in palabras:
            centro = (p["t0"] + p["t1"]) / 2
            if a <= centro < b:
                q = dict(p)
                q["i_crudo"] = p.get("i")
                q["t0"] = round(max(p["t0"], a) - a + corrido, 3)
                q["t1"] = round(min(p["t1"], b) - a + corrido, 3)
                out.append(q)
        corrido += b - a
    for i, q in enumerate(out):
        q["i"] = i
    return out


def empalmes(quedan: list[tuple[float, float]]) -> list[float]:
    """Segundos del video cortado donde hay un empalme."""
    out, t = [], 0.0
    for a, b in quedan[:-1]:
        t += b - a
        out.append(round(t, 3))
    return out


def tiempo_limpio(t: float, quedan: list[tuple[float, float]]) -> float | None:
    """Un segundo del crudo, en el video cortado; None si cayó en lo quitado."""
    corrido = 0.0
    for a, b in quedan:
        if a <= t < b:
            return round(t - a + corrido, 3)
        corrido += b - a
    return None


def aplicar(entrada: Path, salida: Path, quedan: list[tuple[float, float]], fps: int, previa: bool = False,
            con_audio: bool = True) -> None:
    """Corta tramo por tramo y los une. Memoria constante: sirve igual para 30 segundos que para 30 minutos.

    (Un solo grafo con una rama por tramo guarda en memoria los cuadros de todas las ramas: con un clip
    vertical de unos minutos agotaba la memoria.) El audio de cada tramo va sin comprimir hasta la unión,
    para que no se acumule desfase, con 6 ms de fundido en cada empalme.
    """
    if not quedan:
        raise ErrorEditor("no queda nada después de cortar")
    salida.parent.mkdir(parents=True, exist_ok=True)
    tmp = salida.parent / (salida.stem + ".tramos")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    calidad = ["-preset", "ultrafast", "-crf", "30"] if previa else ["-preset", "medium", "-crf", "16"]
    try:
        lista, n = [], len(quedan)
        for k, (a, b) in enumerate(quedan):
            d, f = b - a, tmp / f"{k:04d}.mkv"
            cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.6f}", "-i", str(entrada), "-t", f"{d:.6f}",
                   "-vf", ("scale=-2:640," if previa else "") + f"fps={fps}", "-r", str(fps), "-g", str(fps),
                   "-c:v", "libx264", *calidad, "-pix_fmt", "yuv420p"]
            if con_audio:
                fundidos = [x for x in ((f"afade=t=in:st=0:d={FUNDIDO}" if k else ""),
                                        (f"afade=t=out:st={max(0.0, d - FUNDIDO):.4f}:d={FUNDIDO}" if k < n - 1 else "")) if x]
                cmd += ["-af", ",".join(["aresample=48000"] + fundidos), "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2"]
            else:
                cmd += ["-an"]
            correr(cmd + [str(f)], capture_output=True)
            lista.append(f"file '{f.name}'")
        (tmp / "lista.txt").write_text("\n".join(lista) + "\n", encoding="utf-8")
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-c:v", "copy"]
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"] if con_audio else ["-an"]
        correr(cmd + ["-movflags", "+faststart", str(salida)], capture_output=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def verificar(wav_limpio: Path, quedan: list[tuple[float, float]], palabras_limpias: list[dict], umbral_db: float,
              esperado_s: float, real_s: float, fps: int, video_s: float | None = None, audio_s: float | None = None) -> list[str]:
    """Avisos sobre el video ya cortado: duración, empalmes en plena voz y palabras partidas."""
    avisos = []
    if video_s is not None and audio_s is not None and abs(video_s - audio_s) > 2.5 / fps:
        avisos.append(f"la imagen dura {video_s:.2f} s y el sonido {audio_s:.2f} s: quedaron desfasados")
    if abs(esperado_s - real_s) > 2.5 / fps:
        avisos.append(f"la duración salió {real_s:.2f} s y se esperaban {esperado_s:.2f} s: voz e imagen pueden estar desfasadas")
    muestras, hz = leer_wav(wav_limpio)
    db = energia_db(muestras, hz)
    for t in empalmes(quedan):
        i = int(t / VENTANA)
        antes, despues = db[max(0, i - 3):i], db[i:i + 3]
        if len(antes) and len(despues) and min(float(antes.mean()), float(despues.mean())) > umbral_db + 10:
            avisos.append(f"empalme en plena voz en {formato_tiempo(t)}: escúchalo; puede haber cortado una palabra")
        for p in palabras_limpias:
            if p["t0"] + 0.04 < t < p["t1"] - 0.04:
                avisos.append(f"el empalme de {formato_tiempo(t)} cae dentro de «{p['txt']}»")
    return avisos


def tabla(p: dict) -> str:
    """La tabla que se le enseña a Emi."""
    quita = p["duracion_crudo_s"] - sum(b - a for a, b in tramos_que_quedan(p, incluir_propuestos=True))    # unión: sin contar dos veces lo encimado
    filas = [f"Crudo: {formato_tiempo(p['duracion_crudo_s'])} · se quitarían {quita:.1f} s · quedaría en "
             f"{formato_tiempo(p['duracion_crudo_s'] - quita)} · ritmo {p['ritmo']}", "",
             "| # | De | A | Dura | Qué es | Por qué | Estado |", "|---|---|---|---|---|---|---|"]
    for c in p["cortes"]:
        texto = f" «{c['texto']}»" if c.get("texto") else ""
        filas.append(f"| {c['id']} | {formato_tiempo(c['t0'])} | {formato_tiempo(c['t1'])} | {c['t1'] - c['t0']:.2f} s | "
                     f"{c['tipo']}{texto} | {c['motivo']} | {c['estado']} |")
    if p.get("censura"):
        filas += ["", "Palabras fuertes (no se cortan; «tapar» les pone un sonido encima):", ""]
        filas += [f"- {formato_tiempo(x['t0'])} «{x['texto']}» → {x['accion']}" for x in p["censura"]]
    return "\n".join(filas)


def guardar(p: dict, ruta: Path) -> Path:
    return escribir_json(ruta, p)
