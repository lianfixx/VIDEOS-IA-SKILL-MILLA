#!/usr/bin/env python3
"""Regla de Emi (13/11/2026): «jamás en nada digas que lo armó una IA».

Una sola implementación para Vox Studio, Pizarra Studio y Editor Studio. Revisa los textos que se ven o se oyen
en un video (narración, titulares, notas, remates, portada, cierre). Hablar de IA como TEMA está permitido;
lo prohibido es atribuirle a una IA, a una máquina o a «nadie» la autoría del propio video.
Sin dependencias: se puede importar desde cualquier skill.
"""
from __future__ import annotations

import re
import unicodedata

_AGENTE = r"(?:una |la |el |un )?(?:ia|i\.a\.|inteligencia artificial|chat ?gpt|claude|gemini|maquina|robot)\b"
_AUTORIA_IA = [
    # «lo hizo una IA», «esto lo armó la IA», «todo lo editó una máquina»
    r"\b(?:lo|la|los|las|esto|todo esto|todo|lo que (?:ves|escuchas|oyes))\s+(?:lo\s+|la\s+)?"
    r"(?:hizo|hicieron|armo|armaron|edito|editaron|creo|crearon|genero|generaron|produjo|narro|escribio|animo|monto|diseno)\s+" + _AGENTE,
    # «este video fue hecho con IA», «este cierre lo generó una IA»
    r"\b(?:este|esta|estos|estas)\s+(?:video|short|clip|cierre|guion|voz|reel|animacion|edicion|portada|imagen|imagenes|musica)\b[^.!?]{0,30}?"
    r"\b(?:hech|cread|generad|editad|armad|producid|narrad|escrit|animad|disenad)[oa]s?\s+(?:con|por)\s+" + _AGENTE,
    r"\b(?:este|esta)\s+(?:video|short|clip|cierre|guion|voz|reel|animacion|edicion)\s+(?:lo|la)\s+"
    r"(?:hizo|armo|edito|creo|genero|produjo|narro|escribio|animo|monto)\s+" + _AGENTE,
    # «hecho con IA» como etiqueta del propio video («HECHO 100 % CON IA»)
    r"^\s*(?:video\s+)?(?:hech|cread|generad|editad|armad|producid|narrad)[oa]s?\s+(?:100\s*%\s*)?(?:con|por)\s+" + _AGENTE + r"\s*[.!]*\s*$",
    # «nadie lo editó», «nadie abrió CapCut», «sin editor», «$0 de editor»
    r"\bnadie\s+(?:lo\s+|la\s+)?(?:edito|grabo|narro|armo|animo|monto|abrio (?:capcut|premiere|el editor))\b(?![^.!?]{0,12}\b(?:mas que|sino|excepto|salvo|aparte de))",
    r"\b(?:no\s+)?(?:lo|la)\s+(?:edito|grabo|narro|armo|animo|monto|hizo)\s+nadie\b(?![^.!?]{0,12}\b(?:mas que|sino|excepto|salvo|aparte de))",
    r"\bsin\s+(?:un\s+)?editor(?:es)?\b", r"\b\$?\s?0 de editor\b", r"\bni (?:un|una)\s+(?:editor|editora)\b",
    # la voz: «voz de IA», «esta voz no es real», «te habla una IA»
    r"\bvoz\s+(?:de|con|por|hecha con|generada (?:con|por))\s+" + _AGENTE, r"\bvoz\s+(?:artificial|sintetica|clonada)\b",
    r"\besta voz no es (?:real|mia|humana)\b", r"\b(?:te habla|les habla|aqui habla|soy)\s+" + _AGENTE,
]


def _plano(texto: str) -> str:
    t = unicodedata.normalize("NFD", str(texto).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[«»“”\"'¡¿,;:()\[\]]", " ", t).split())


def dice_que_lo_hizo_una_ia(texto: str) -> str:
    """Devuelve el fragmento que atribuye el video a una IA (o a «nadie»), o "" si no hay."""
    t = _plano(texto)
    for patron in _AUTORIA_IA:
        m = re.search(patron, t)
        if m:
            return m.group(0).strip()
    return ""


def revisar_autoria(textos: list[tuple[str, str]]) -> list[str]:
    errores = []
    for lugar, texto in textos:
        frase = dice_que_lo_hizo_una_ia(texto)
        if frase:
            errores.append(f"{lugar}: «{frase}» dice que el video lo hizo una IA (o nadie). Regla de Emi: jamás se dice. Reescríbelo")
    return errores



def textos_de(obj, lugar: str = "", omitir: frozenset = frozenset({"porque", "_doc", "origen", "motivo", "opinion_emi", "notas_internas", "fuente_url", "archivo", "carpeta", "imagen", "imagen_archivo", "src", "url", "id"})) -> list[tuple[str, str]]:
    """Todas las cadenas de un JSON (guion, storyboard, plan), con su ruta, salvo las claves que no se ven en pantalla."""
    out = []
    if isinstance(obj, str):
        if obj.strip():
            out.append((lugar or "texto", obj))
    elif isinstance(obj, dict):
        for c, v in obj.items():
            if c not in omitir:
                out += textos_de(v, f"{lugar}.{c}" if lugar else str(c), omitir)
    elif isinstance(obj, list):
        for n, v in enumerate(obj):
            out += textos_de(v, f"{lugar}[{n}]", omitir)
    return out
