"""Transcripción con tiempo por palabra, en crudo (con muletillas): ElevenLabs Scribe, AssemblyAI o un archivo.

Todas las vías entregan el mismo formato: {"motor", "idioma", "aproximado", "palabras": [{i, t0, t1, txt, conf, hablante}]}.
`aproximado` es verdadero cuando los tiempos por palabra se repartieron dentro de una frase (SRT/VTT):
con eso se pueden poner subtítulos por frase, pero no cortar muletillas ni anclar piezas a una palabra.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from comun import ASSEMBLY, ELEVEN, ErrorEditor, cab_assembly, cab_eleven, como_json, formulario, pedir

MOTORES = ("scribe", "assemblyai", "archivo")
MAX_AUDIO = 60 * 1024 * 1024


def _salida(motor: str, idioma: str, palabras: list[dict], aproximado: bool = False, extra: dict | None = None) -> dict:
    limpias = []
    try:
        palabras = sorted(palabras, key=lambda p: (float(p["t0"]), float(p["t1"])))      # siempre en orden de tiempo
    except (KeyError, TypeError, ValueError) as exc:
        raise ErrorEditor(f"{motor}: hay palabras sin tiempos legibles") from exc
    for p in palabras:
        txt = str(p.get("txt") or "").strip()
        if not txt or float(p["t1"]) <= float(p["t0"]):
            continue
        limpias.append({"i": len(limpias), "t0": round(float(p["t0"]), 3), "t1": round(float(p["t1"]), 3), "txt": txt,
                        "conf": p.get("conf"), "hablante": p.get("hablante")})
    for a, b in zip(limpias, limpias[1:]):     # dos palabras nunca se enciman
        if b["t0"] < a["t1"]:
            medio = round(min(max((a["t1"] + b["t0"]) / 2, a["t0"] + 0.01), b["t1"] - 0.01), 3)
            a["t1"], b["t0"] = medio, medio
    limpias = [p for p in limpias if p["t1"] > p["t0"]]          # una palabra tragada por otra no se conserva
    for k, p in enumerate(limpias):
        p["i"] = k
    if not limpias:
        raise ErrorEditor(f"{motor} no devolvió ninguna palabra: revisa que el video tenga voz")
    return {"motor": motor, "idioma": idioma, "aproximado": aproximado, "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
            "hablantes": sorted({p["hablante"] for p in limpias if p["hablante"] is not None}, key=str),
            "palabras": limpias, **(extra or {})}


def con_scribe(audio: Path, idioma: str = "es", hablantes: bool = False, modelo: str = "scribe_v1") -> dict:
    """ElevenLabs Scribe: una llamada, tiempos por palabra y eventos de audio (risas, música) marcados aparte."""
    datos = audio.read_bytes()
    if len(datos) > MAX_AUDIO:
        raise ErrorEditor("el audio pasa de 60 MB: transcribe el WAV mono de 16 kHz que deja `ingerir`")
    campos = {"model_id": modelo, "language_code": idioma, "timestamps_granularity": "word",
              "tag_audio_events": "true", "diarize": "true" if hablantes else "false"}
    cuerpo, tipo = formulario(campos, ("file", audio.name, datos, "audio/wav"))
    r = como_json(pedir(f"{ELEVEN}/speech-to-text", metodo="POST", cabeceras=cab_eleven(), datos=cuerpo, tipo=tipo,
                        espera=600), "ElevenLabs")
    palabras, eventos = [], []
    for w in r.get("words") or []:
        if w.get("type") == "audio_event":
            eventos.append({"t0": w.get("start"), "t1": w.get("end"), "txt": w.get("text")})
        elif w.get("type", "word") == "word" and w.get("start") is not None:
            palabras.append({"t0": w["start"], "t1": w["end"], "txt": w.get("text", ""), "conf": w.get("logprob"),
                             "hablante": w.get("speaker_id")})
    return _salida("scribe", r.get("language_code") or idioma, palabras, extra={"eventos": eventos, "modelo": modelo})


def con_assemblyai(audio: Path, idioma: str = "es", hablantes: bool = False, espera_max: int = 900) -> dict:
    """AssemblyAI: sube, pide la transcripción con muletillas y espera el resultado."""
    datos = audio.read_bytes()
    subida = como_json(pedir(f"{ASSEMBLY}/upload", metodo="POST", cabeceras=cab_assembly(), datos=datos,
                             tipo="application/octet-stream", espera=600), "AssemblyAI")
    if not subida.get("upload_url"):
        raise ErrorEditor("AssemblyAI no aceptó el audio")
    cuerpo = {"audio_url": subida["upload_url"], "language_code": idioma, "punctuate": True, "format_text": True,
              "disfluencies": True, "speaker_labels": bool(hablantes)}
    trabajo = como_json(pedir(f"{ASSEMBLY}/transcript", metodo="POST", cabeceras=cab_assembly(), cuerpo=cuerpo), "AssemblyAI")
    ident, limite = trabajo.get("id"), time.time() + espera_max
    if not ident:
        raise ErrorEditor(f"AssemblyAI no creó el trabajo: {str(trabajo)[:200]}")
    while True:
        r = como_json(pedir(f"{ASSEMBLY}/transcript/{ident}", cabeceras=cab_assembly()), "AssemblyAI")
        if r.get("status") == "completed":
            break
        if r.get("status") == "error":
            raise ErrorEditor(f"AssemblyAI falló: {r.get('error')}")
        if time.time() > limite:
            raise ErrorEditor(f"AssemblyAI no terminó en {espera_max} s (trabajo {ident}); no se reintenta solo para no cobrar doble")
        time.sleep(3)
    palabras = [{"t0": w["start"] / 1000, "t1": w["end"] / 1000, "txt": w.get("text", ""), "conf": w.get("confidence"),
                 "hablante": w.get("speaker")} for w in r.get("words") or []]
    return _salida("assemblyai", idioma, palabras, extra={"trabajo": ident})


# ---------- importar un archivo (Whisper Mate u otra app) ----------

_MARCA = re.compile(r"(\d+):(\d{2}):(\d{2})[.,](\d{1,3})|(\d{1,2}):(\d{2})[.,](\d{1,3})")


def _segundos(txt: str) -> float:
    m = _MARCA.search(txt)
    if not m:
        raise ErrorEditor(f"marca de tiempo ilegible: {txt!r}")
    if m.group(1) is not None:
        h, mi, s, ms = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    else:
        h, mi, s, ms = 0, int(m.group(5)), int(m.group(6)), m.group(7)
    return h * 3600 + mi * 60 + s + int(ms.ljust(3, "0")) / 1000


def _repartir(texto: str, t0: float, t1: float) -> list[dict]:
    """Sin tiempo por palabra, se reparte la frase según el largo de cada palabra. Es una aproximación."""
    piezas = texto.split()
    peso = [max(1, len(re.sub(r"\W", "", w))) for w in piezas]
    total, t, out = sum(peso) or 1, t0, []
    for w, k in zip(piezas, peso):
        d = (t1 - t0) * k / total
        out.append({"t0": t, "t1": t + d, "txt": w})
        t += d
    return out


def de_subtitulos(texto: str) -> list[dict]:
    """SRT o VTT a palabras con tiempos repartidos por frase."""
    palabras = []
    for bloque in re.split(r"\n\s*\n", texto.replace("\r", "").strip()):
        lineas = [x for x in bloque.split("\n") if x.strip()]
        pos = next((k for k, x in enumerate(lineas) if "-->" in x), None)
        if pos is None:
            continue
        a, _, b = lineas[pos].partition("-->")
        dicho = re.sub(r"<[^>]+>", "", " ".join(lineas[pos + 1:])).strip()
        if dicho:
            palabras += _repartir(dicho, _segundos(a), _segundos(b))
    return palabras


def _buscar_palabras(obj) -> list[dict] | None:
    """Encuentra, en cualquier JSON de transcripción, la lista de palabras con inicio y fin."""
    if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
        claves = set().union(*(x.keys() for x in obj[:20]))
        anidadas = next((k for k in ("words", "palabras", "word_segments") if k in claves), None)
        if anidadas:                           # frases que traen dentro sus palabras: valen las palabras
            juntas = []
            for x in obj:
                juntas += _buscar_palabras(x.get(anidadas) or []) or []
            if juntas:
                return juntas
        texto = next((k for k in ("txt", "text", "word", "punctuated_word", "value") if k in claves), None)
        ini = next((k for k in ("t0", "start", "startTime", "start_time", "begin", "from") if k in claves), None)
        fin = next((k for k in ("t1", "end", "endTime", "end_time", "to") if k in claves), None)
        if texto and ini and fin:
            # ¿son palabras o frases? más de una palabra por elemento, en promedio, es frase
            medio = sum(len(str(x.get(texto, "")).split()) for x in obj) / len(obj)
            if medio <= 1.6:
                return [{"t0": x[ini], "t1": x[fin], "txt": x.get(texto, ""), "conf": x.get("confidence") or x.get("probability"),
                         "hablante": x.get("speaker")} for x in obj if x.get(ini) is not None and x.get(fin) is not None]
        for x in obj:
            hallado = _buscar_palabras(x)
            if hallado:
                juntas = []
                for y in obj:
                    juntas += _buscar_palabras(y) or []
                return juntas
    elif isinstance(obj, dict):
        for clave in ("words", "palabras", "word_segments"):
            if clave in obj:
                hallado = _buscar_palabras(obj[clave])
                if hallado:
                    return hallado
        for v in obj.values():
            if isinstance(v, (list, dict)):
                hallado = _buscar_palabras(v)
                if hallado:
                    return hallado
    return None


def _buscar_frases(obj) -> list[dict]:
    if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
        claves = set().union(*(x.keys() for x in obj[:20]))
        texto = next((k for k in ("text", "txt", "transcript") if k in claves), None)
        ini = next((k for k in ("start", "t0", "startTime", "start_time", "from") if k in claves), None)
        fin = next((k for k in ("end", "t1", "endTime", "end_time", "to") if k in claves), None)
        if texto and ini and fin:
            return [x | {"_t": texto, "_i": ini, "_f": fin} for x in obj]
    if isinstance(obj, dict):
        for v in obj.values():
            hallado = _buscar_frases(v) if isinstance(v, (list, dict)) else []
            if hallado:
                return hallado
    return []


def _num(v) -> float:
    return _segundos(v) if isinstance(v, str) and ":" in v else float(v)


def _escala(maximo: float, duracion: float | None) -> float:
    """¿Los tiempos vienen en milisegundos? Con la duración real del audio se sabe; sin ella, solo si es evidente."""
    if duracion:
        return 0.001 if maximo > duracion * 1.5 + 2 else 1.0
    return 0.001 if maximo > 36000 else 1.0


def de_archivo(ruta: Path, idioma: str = "es", duracion: float | None = None) -> dict:
    """Importa la exportación de otra app: JSON con palabras, JSON con frases, SRT o VTT.

    `duracion` es la del audio real: permite distinguir segundos de milisegundos en clips cortos.
    """
    texto = ruta.read_text(encoding="utf-8-sig", errors="replace")
    if ruta.suffix.lower() == ".json":
        try:
            obj = json.loads(texto)
        except ValueError as exc:
            raise ErrorEditor(f"{ruta.name} no es JSON válido") from exc
        palabras = _buscar_palabras(obj)
        if palabras:
            escala = _escala(max(_num(p["t1"]) for p in palabras), duracion)
            for p in palabras:
                p["t0"], p["t1"] = _num(p["t0"]) * escala, _num(p["t1"]) * escala
            return _salida("archivo", idioma, palabras, extra={"origen": ruta.name})
        frases = _buscar_frases(obj)
        if not frases:
            raise ErrorEditor(f"{ruta.name} no trae palabras ni frases con tiempos")
        escala = _escala(max(_num(f[f["_f"]]) for f in frases), duracion)
        palabras = []
        for f in frases:
            palabras += _repartir(str(f[f["_t"]]), _num(f[f["_i"]]) * escala, _num(f[f["_f"]]) * escala)
        return _salida("archivo", idioma, palabras, aproximado=True, extra={"origen": ruta.name})
    if ruta.suffix.lower() in (".srt", ".vtt"):
        return _salida("archivo", idioma, de_subtitulos(texto), aproximado=True, extra={"origen": ruta.name})
    raise ErrorEditor("formato no admitido: usa JSON, SRT o VTT")


def texto_legible(t: dict, pausa: float = 0.7) -> str:
    """La transcripción para leerla completa antes de editar, con la hora de cada párrafo."""
    from comun import formato_tiempo
    lineas, actual, inicio = [], [], None
    palabras = t["palabras"]
    for i, p in enumerate(palabras):
        if inicio is None:
            inicio = p["t0"]
        actual.append(p["txt"])
        sig = palabras[i + 1]["t0"] if i + 1 < len(palabras) else None
        if sig is None or sig - p["t1"] >= pausa:
            lineas.append(f"[{formato_tiempo(inicio)}] " + " ".join(actual))
            actual, inicio = [], None
    return "\n".join(lineas) + "\n"


def comparar(a: dict, b: dict) -> dict:
    """Dos motores sobre el mismo audio: en qué coinciden y en qué no. No dice cuál es mejor: eso se escucha."""
    import difflib
    from corte import MULETILLAS_SEGURAS, normal
    na, nb = (a["motor"], b["motor"]) if a["motor"] != b["motor"] else (a["motor"] + "-1", b["motor"] + "-2")
    a, b = {**a, "motor": na}, {**b, "motor": nb}
    wa, wb = [normal(p["txt"]) for p in a["palabras"]], [normal(p["txt"]) for p in b["palabras"]]
    sm = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
    difs, desfases = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            desfases += [abs(a["palabras"][i1 + k]["t0"] - b["palabras"][j1 + k]["t0"]) for k in range(i2 - i1)]
        else:
            difs.append({"t": a["palabras"][min(i1, len(wa) - 1)]["t0"] if wa else 0.0,
                         a["motor"]: " ".join(p["txt"] for p in a["palabras"][i1:i2]),
                         b["motor"]: " ".join(p["txt"] for p in b["palabras"][j1:j2])})
    desfases.sort()
    return {"palabras": {a["motor"]: len(wa), b["motor"]: len(wb)},
            "muletillas": {a["motor"]: sum(w in MULETILLAS_SEGURAS for w in wa), b["motor"]: sum(w in MULETILLAS_SEGURAS for w in wb)},
            "coincidencia": round(sm.ratio(), 3),
            "desfase_mediano_s": round(desfases[len(desfases) // 2], 3) if desfases else None,
            "desfase_p90_s": round(desfases[int(len(desfases) * 0.9)], 3) if desfases else None,
            "diferencias": difs[:60]}
