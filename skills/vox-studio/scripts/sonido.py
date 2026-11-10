#!/usr/bin/env python3
"""Música y efectos hechos con código (numpy): sin proveedor, sin costo y sin licencias de terceros.

- `componer(animo, segundos)` genera una pista instrumental original y determinista.
- `EFECTOS` son remates sonoros tipo meme sintetizados aquí (no son grabaciones ajenas).
- `proponer(guion)` lee de qué va el video y sugiere ánimo, tempo, efectos y remates por escena.
  Es una propuesta de partida: quien escribe el guion la revisa con criterio y la ajusta.
"""
from __future__ import annotations

import re
import wave
from pathlib import Path

import numpy as np

SR = 48000

# ánimo -> (bpm, tónica MIDI, modo, progresión en grados, descripción)
ANIMOS = {
    "tension": (92, 45, "menor", [0, 5, 3, 4], "pulso grave y contenido; denuncia, misterio, dato incómodo"),
    "energia": (122, 48, "mayor", [0, 4, 5, 3], "bombo a tierra y arpegio brillante; gym, retos, listas rápidas"),
    "serio": (78, 43, "menor", [0, 3, 5, 4], "colchón lento sin batería; jurídico, institucional, explicación sobria"),
    "ironia": (104, 50, "mayor", [0, 3, 4, 0], "pizzicato juguetón con bloque de madera; sarcasmo, absurdo, humor"),
    "motivacion": (110, 48, "mayor", [0, 3, 5, 4], "arpegio que crece; superación, cierre con llamado a la acción"),
}
ESCALAS = {"mayor": [0, 2, 4, 5, 7, 9, 11], "menor": [0, 2, 3, 5, 7, 8, 10]}


def _hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def _env(n: int, ataque: float, caida: float) -> np.ndarray:
    t = np.arange(n) / SR
    return np.minimum(1.0, t / max(ataque, 1e-4)) * np.exp(-t / max(caida, 1e-4))


def _tono(midi: float, dur: float, forma="sierra", ataque=0.005, caida=0.25) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = _hz(midi)
    if forma == "seno":
        o = np.sin(2 * np.pi * f * t)
    elif forma == "pluck":  # pocos armónicos: suena a cuerda pulsada
        o = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.6 for k in range(1, 6))
    else:  # sierra suave
        o = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))
    return o * _env(n, ataque, caida)


def _ruido(dur: float, rng: np.random.Generator, caida=0.05, agudo=True) -> np.ndarray:
    n = int(dur * SR)
    r = rng.standard_normal(n)
    if agudo:
        r = np.diff(r, prepend=0.0)
    else:
        r = np.convolve(r, np.ones(64) / 64, mode="same")
    return r * _env(n, 0.001, caida)


def _bombo(dur=0.3) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (48 * t + 60 * (1 - np.exp(-t * 28)) / 28)) * np.exp(-t / 0.11)


def _poner(mezcla: np.ndarray, sonido: np.ndarray, en: float, gan: float) -> None:
    i = int(en * SR)
    if i >= len(mezcla):
        return
    s = sonido[: len(mezcla) - i]
    mezcla[i:i + len(s)] += s * gan


def _acorde(tonica: int, modo: str, grado: int) -> list[int]:
    esc = ESCALAS[modo]
    return [tonica + esc[(grado + k) % 7] + 12 * ((grado + k) // 7) for k in (0, 2, 4)]


def componer(animo: str, segundos: float, semilla: int = 7) -> np.ndarray:
    """Pista instrumental original en mono, normalizada a un pico de -6 dBFS."""
    if animo not in ANIMOS:
        raise ValueError(f"ánimo desconocido: {animo}; opciones {sorted(ANIMOS)}")
    bpm, tonica, modo, prog, _ = ANIMOS[animo]
    rng = np.random.default_rng(semilla)
    negra = 60.0 / bpm
    n = int((segundos + 0.5) * SR)
    m = np.zeros(n)
    compas, t = 0, 0.0
    while t < segundos:
        notas = _acorde(tonica, modo, prog[compas % len(prog)])
        crece = min(1.0, 0.55 + 0.45 * t / max(segundos, 1))  # la pista crece hacia el cierre
        # colchón
        for nota in notas:
            _poner(m, _tono(nota + 12, negra * 4, "seno", ataque=0.4, caida=negra * 3), t, 0.10)
        for paso in range(8):  # corcheas
            tp = t + paso * negra / 2
            if animo in {"tension", "serio"}:
                if animo == "tension" or paso % 4 == 0:
                    _poner(m, _tono(notas[0] - 12, negra / 2, "sierra", caida=0.16), tp, 0.20 * crece)
            if animo in {"energia", "motivacion"}:
                _poner(m, _tono(notas[paso % 3] + 24, negra / 2, "pluck", caida=0.14), tp, 0.13 * crece)
                if paso % 2 == 0:
                    _poner(m, _tono(notas[0] - 12, negra, "sierra", caida=0.22), tp, 0.18)
            if animo == "ironia":
                swing = (negra / 6) if paso % 2 else 0.0
                _poner(m, _tono(notas[[0, 2, 1, 2][paso % 4]] + 12, 0.2, "pluck", caida=0.07), tp + swing, 0.22)
                if paso in (2, 6):
                    _poner(m, _tono(84, 0.08, "seno", caida=0.02), tp, 0.16)  # bloque de madera
            # batería
            if animo in {"energia", "motivacion"} and paso % 2 == 0:
                _poner(m, _bombo(), tp, 0.55 * crece)
            if animo == "tension" and paso in (0, 5):
                _poner(m, _bombo(), tp, 0.40)
            if animo in {"energia", "motivacion", "tension"} and paso % 2 == 1:
                _poner(m, _ruido(0.08, rng, caida=0.02), tp, 0.05)
            if animo == "energia" and paso in (2, 6):
                _poner(m, _ruido(0.2, rng, caida=0.06), tp, 0.10)  # palmada
        if animo == "serio" and compas % 2 == 0:  # nota de piano espaciada
            _poner(m, _tono(notas[2] + 24, negra * 3, "pluck", caida=0.9), t + negra, 0.14)
        t += negra * 4
        compas += 1
    m = m[: int(segundos * SR)]
    borde = int(0.6 * SR)
    m[:borde] *= np.linspace(0, 1, borde)
    m[-borde:] *= np.linspace(1, 0, borde)
    return m / (np.max(np.abs(m)) + 1e-9) * 0.5


# ---------- remates sonoros (memes) sintetizados ----------

def _boom(rng):
    n = int(0.9 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (38 * t + 70 * (1 - np.exp(-t * 9)) / 9)) * np.exp(-t / 0.32)


def _scratch(rng):
    n = int(0.45 * SR); t = np.arange(n) / SR
    barrido = np.sin(2 * np.pi * np.cumsum(900 - 1500 * t + 700 * np.sin(2 * np.pi * 9 * t)) / SR)
    return (barrido * 0.6 + rng.standard_normal(n) * 0.25) * _env(n, 0.005, 0.2)


def _trombon(rng):
    partes = []
    for midi, dur in [(58, 0.32), (57, 0.32), (56, 0.32), (55, 0.75)]:
        n = int(dur * SR); t = np.arange(n) / SR
        vib = 1 + 0.012 * np.sin(2 * np.pi * 5.5 * t)
        f = _hz(midi) * vib * (1 - (0.05 * t / dur if dur > 0.5 else 0))
        o = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k for k in range(1, 7))
        partes.append(o * np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06))
    return np.concatenate(partes)


def _ding(rng):
    return _tono(88, 1.0, "seno", caida=0.35) + 0.5 * _tono(100, 1.0, "seno", caida=0.2)


def _redoble(rng):
    m = np.zeros(int(1.1 * SR))
    _poner(m, _ruido(0.12, rng, caida=0.04, agudo=False) + _tono(50, 0.12, "seno", caida=0.05), 0.0, 1.0)
    _poner(m, _ruido(0.12, rng, caida=0.04, agudo=False) + _tono(47, 0.12, "seno", caida=0.05), 0.18, 1.0)
    _poner(m, _ruido(0.7, rng, caida=0.25), 0.42, 0.5)
    return m


def _suspenso(rng):
    m = np.zeros(int(1.5 * SR))
    for i, (midi, en) in enumerate([(50, 0.0), (50, 0.28), (46, 0.56)]):
        dur = 0.9 if i == 2 else 0.22
        _poner(m, _tono(midi, dur, "sierra", caida=0.5 if i == 2 else 0.12) + _tono(midi - 12, dur, "sierra", caida=0.5 if i == 2 else 0.12), en, 0.6)
    return m


def _caja(rng):
    m = np.zeros(int(0.9 * SR))
    _poner(m, _ruido(0.1, rng, caida=0.03), 0.0, 0.6)
    _poner(m, _tono(91, 0.8, "seno", caida=0.3) + 0.6 * _tono(96, 0.8, "seno", caida=0.25), 0.08, 0.7)
    return m


def _error(rng):
    return np.concatenate([_tono(52, 0.16, "sierra", caida=0.3), np.zeros(int(0.05 * SR)), _tono(47, 0.3, "sierra", caida=0.3)])


EFECTOS = {
    "boom": (_boom, "golpe grave: gancho, revelación fuerte"),
    "scratch": (_scratch, "disco rayado: «un momento», contradicción, mentira"),
    "trombon": (_trombon, "trombón triste: fracaso, decepción, chiste a costa propia"),
    "ding": (_ding, "campanita: dato correcto, idea, respuesta"),
    "redoble": (_redoble, "ba dum tss: remate de chiste"),
    "suspenso": (_suspenso, "tan tan taaan: giro, pregunta incómoda"),
    "caja": (_caja, "caja registradora: dinero, costos, multas"),
    "error": (_error, "error: dato falso, lo que no hay que hacer"),
}


def guardar(ruta: Path, onda: np.ndarray, pico: float = 0.7) -> None:
    onda = onda / (np.max(np.abs(onda)) + 1e-9) * pico
    datos = (np.clip(onda, -1, 1) * 32767).astype("<i2")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.repeat(datos, 2).tobytes())


def sintetizar_efectos(destino: Path) -> list[str]:
    for i, (nombre, (fn, _)) in enumerate(EFECTOS.items()):
        guardar(destino / f"{nombre}.wav", fn(np.random.default_rng(100 + i)))
    return sorted(EFECTOS)


# ---------- análisis del guion ----------

PISTAS_ANIMO = {
    "tension": r"mentir|mintier|engañ|fraude|robo|corrup|peligro|nadie te dice|oculta|verdad|trampa|estafa|miedo|crisis",
    "energia": r"gym|entren|músculo|rutina|reto|rápido|hack|truco|energ|cardio|proteína|levant",
    "serio": r"ley|contrato|demanda|juicio|derecho|tribunal|amparo|fiscal|laboral|despido|finiquito|pensión|artículo|código",
    "ironia": r"obvio|claro que|spoiler|plot twist|sorpresa|ajá|según|supuestamente|qué raro|casualidad",
    "motivacion": r"puedes|lograr|empieza|cambia|disciplina|sueño|meta|hazlo|vale la pena|crece",
}
PISTAS_EFECTO = [
    ("caja", r"dinero|pesos|\$|pagar|multa|costo|precio|quincena|sueldo|cobr|deuda|impuesto"),
    ("scratch", r"\bpero\b|mentira|falso|no es cierto|en realidad|espera|un momento|te mintieron"),
    ("error", r"error|nunca hagas|no hagas|prohibido|ilegal|cuidado"),
    ("trombon", r"fracas|perdi|nadie|ni modo|triste|quebr|reprob"),
    ("suspenso", r"\?$|secreto|nadie sabe|lo peor|adivina"),
    ("ding", r"\d|dato|según|estudio|resulta que|la clave|solución|respuesta"),
]
ANIMO_POR_ESPACIO = {"milla": "serio", "castorena": "serio", "pan": "tension", "personal": "energia"}


def proponer(g: dict) -> dict:
    """Propuesta de música, efectos y remates a partir del contenido del guion."""
    texto = " ".join([str(g.get("titulo", "")), str(g.get("opinion_emi", ""))] + [str(s.get("narracion", "")) for s in g.get("escenas", [])]).lower()
    votos = {a: len(re.findall(p, texto)) for a, p in PISTAS_ANIMO.items()}
    animo = max(votos, key=votos.get)
    if votos[animo] == 0:
        animo = ANIMO_POR_ESPACIO.get(g.get("perfil", ""), "tension")
    sobrio = g.get("perfil") in {"castorena", "milla"}
    if sobrio and animo in {"ironia", "energia"}:
        animo = "serio"  # los espacios jurídicos no llevan música de chiste
    escenas, usados = [], set()
    for i, s in enumerate(g.get("escenas", [])):
        n = str(s.get("narracion", "")).lower().strip()
        efecto = "boom" if i == 0 else None
        for nombre, patron in PISTAS_EFECTO:
            if efecto is None and re.search(patron, n):
                efecto = nombre
        if sobrio and efecto in {"trombon", "redoble", "scratch"}:
            efecto = "ding"
        if efecto in usados and efecto not in {"ding"}:
            efecto = None  # un remate repetido deja de tener gracia
        if efecto:
            usados.add(efecto)
        remate = ""
        if not sobrio:
            if efecto == "scratch":
                remate = "PLOT TWIST"
            elif efecto == "error":
                remate = "ASÍ NO"
            elif efecto == "caja":
                remate = "$$$"
        escenas.append({"id": s.get("id"), "sonido": efecto or "", "remate": remate})
    bpm = ANIMOS[animo][0]
    return {"musica": {"animo": animo, "bpm": bpm, "porque": ANIMOS[animo][4], "votos": votos}, "escenas": escenas}
