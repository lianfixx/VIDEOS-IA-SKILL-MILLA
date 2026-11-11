#!/usr/bin/env python3
"""Vox Studio: shorts verticales estilo documental-collage con Remotion.

Subcomandos (sin --execute nada llama a un proveedor de pago):
  espacios                                 lista los espacios (marcas) y su perfil
  proyecto productions/E/TEMA --perfil E   crea la producción dentro de su espacio
  validar GUION                            comprueba el guion (exige la opinión de Emi)
  voz GUION --dir DIR [--execute]          narra con ElevenLabs y guarda la alineación real
  armar GUION --dir DIR                    reconstruye video.json sin volver a pagar la voz
  imagen --prompt-file F --out O --estado S [--estilo ilustracion|foto|sticker] [--modelo M] [--croma verde|magenta]
  recorte ENTRADA SALIDA                   quita el fondo uniforme conectado al borde -> PNG con alfa
  foto --consulta "..." --dir DIR [--execute]   busca fotos reales con Apify (candidatas, con su fuente)
  foto-bajar --dir DIR --indice N --out O  descarga una candidata ya verificada (derechos y fuente)
  catalogar DIR                            guarda en la biblioteca los recortes del video, con su descripción
  biblioteca [--buscar TEXTO] [--espacio E]  qué hay para reciclar
  reciclar ID --dir DIR                    copia un recurso de la biblioteca a una producción
  sonido GUION                             analiza el guion y propone música, efectos y remates
  blender --dir D --perfil E --tipo texto|moneda|caja|modelo --out RUTA --porque "..." [--acabado plano|real] [--giro N]
                                           objeto 3D rendido con Blender (PNG transparente o secuencia que gira)
  blender-instalar                         instala Blender como módulo de Python (solo cuando haga falta)
  comfy --dir D --flujo F.json --out RUTA --porque "..." [--execute]   imagen desde el servidor ComfyUI de Emi (COMFY_URL)
  revisar DIR                              hojas de transiciones y de tamaño teléfono + informe de revisión (obligatorio antes de `cierre`)
  referencia ARCHIVO --dir DIR             convierte una imagen o video de referencia de Emi en una hoja para mirarla
  render DIR                               render + portada + master a -14 LUFS + hoja de fotogramas para auditar
  cierre DIR                               tabla de gastado y restante del video (obligatoria al entregar)
  saldo                                    cuánto queda en Kie, ElevenLabs y Apify
  aprender "TEXTO" [--espacio E]           guarda una lección para los videos siguientes
  aprendizajes [--espacio E]               lo aprendido hasta hoy; leerlo antes de cada guion

Las claves nunca se escriben aquí. En la nube el proxy las inyecta (se envía un
marcador); en local se leen de KIE_API_KEY, ELEVENLABS_API_KEY y APIFY_TOKEN.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla"
FPS = 30
MARCADOR = "proxy-injected"
KIE = "https://api.kie.ai/api/v1"
ELEVEN = "https://api.elevenlabs.io/v1"
HOSTS_DESCARGA = {"tempfile.aiquickdraw.com", "file.aiquickdraw.com"}
# Modelo -> campos extra de input según su esquema oficial (docs.kie.ai, comprobado el 2026-11-10).
MODELOS_KIE = {
    "nano-banana-2-lite": {},
    "seedream/5-lite-text-to-image": {"quality": "basic", "output_format": "png"},
}
ENTRADAS = ["sello", "desliza-izq", "cae", "desliza-der", "desdobla", "mordidas"]
TRANSICIONES = ["viaje", "barrido", "viaje", "rasgado"]
ESTILOS = {
    # Natural: ilustración editorial con textura y proporciones reales. Es el estilo por defecto.
    "ilustracion": "hand-painted editorial magazine illustration, gouache and ink texture, natural realistic proportions, "
                   "expressive but believable, limited muted palette with one warm accent color, soft natural lighting",
    # Fotografía creíble para recortar; no usar para personas reales identificables.
    "foto": "realistic documentary photograph, natural light, true-to-life colors and textures, candid, shot on 50mm lens",
    "sticker": "flat 2D editorial cartoon illustration, bold thick black outlines, flat colors",
}
CROMAS = {"verde": "pure green (#00FF00)", "magenta": "pure magenta (#FF00FF)"}
SIGNOS = "¿¡?!.,;:"
MIN_ESCENA = 24  # frames; con menos, la cámara no alcanza a llegar
COLA = 1.5       # segundos tras la voz: ahí cae el llamado a comentar
LADO_HORNO = 720        # px del lienzo donde se hornea un objeto 3D
ADELANTO_PRIMERA = 60   # cuadros que el compositor adelanta la primera escena (Vox.tsx: `k === 0 ? frame + 60`)
LISTO = ".listo"        # marca de secuencia horneada completa
ESCENA_LARGA = 7.0  # segundos; más que esto sin cambio de plano se siente lento
# Recursos de más costo o riesgo de «verse a IA»: cada uno exige decir por qué hace falta en esa escena.
OBJETOS_3D = ["moneda", "monedas", "barras", "caja", "globo"]   # Three.js dentro del compositor, colores planos + contorno
TRATAMIENTOS = ["semitono", "duotono"]                             # sombreadores de imprenta para fotos y recortes
BLENDER_TIPOS = ["texto", "moneda", "caja", "modelo"]             # render fuera del compositor: PNG o secuencia con transparencia
MODELOS_3D = {".glb", ".gltf", ".obj", ".stl"}                    # formatos de modelo que Blender importa aquí
# Para qué existe cada escena. Si no se puede decir, la escena sobra.
FUNCIONES = ["gancho", "contexto", "dato", "giro", "prueba", "opinion", "remate", "cierre"]
CIFRA = re.compile(r"\d+\s*%|\$\s*\d|\d[\d.,]*\s*(?:mil|millones|pesos|dólares|años|veces|por ciento)\b|\b\d{2,}[\d.,]*\b", re.I)
LIMITES = {"kicker": 18, "nota": 38, "fuente": 46, "dato": 6, "remate": 14}

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sonido as SON  # noqa: E402  (música y efectos hechos con código)


class ErrorVox(Exception):
    pass


# ---------- espacios y memoria ----------

def dir_espacios() -> Path:
    """Cada espacio (marca) vive en su propia carpeta: espacios/<nombre>/perfil.json."""
    if os.environ.get("VOX_ESPACIOS"):
        return Path(os.environ["VOX_ESPACIOS"])
    if (RAIZ / "espacios").is_dir():  # skill empaquetada para claude.ai: los espacios viajan dentro
        return RAIZ / "espacios"
    return RAIZ.parent.parent / "espacios"


def perfiles() -> dict:
    out = {}
    for f in sorted(dir_espacios().glob("*/perfil.json")):
        out[f.parent.name] = json.loads(f.read_text(encoding="utf-8"))
    if not out:
        raise ErrorVox(f"no hay espacios en {dir_espacios()}")
    return out


def archivo_aprendizajes(espacio: str = "") -> Path:
    """Sin espacio: lo que vale para todos los videos. Con espacio: lo propio de esa marca."""
    if espacio:
        if espacio not in perfiles():
            raise ErrorVox(f"espacio desconocido: {espacio}")
        return dir_espacios() / espacio / "aprendizajes.md"
    return dir_espacios() / "APRENDIZAJES.md"


def leer_aprendizajes(espacio: str = "") -> str:
    partes = []
    for f in [archivo_aprendizajes("")] + ([archivo_aprendizajes(espacio)] if espacio else []):
        if f.exists():
            partes.append(f.read_text(encoding="utf-8").strip())
    return "\n\n".join(partes) or "Sin aprendizajes registrados."


# ---------- guion ----------

def limpia(palabra: str) -> str:
    return palabra.strip(SIGNOS).upper()


def partir(texto: str) -> list[str]:
    """Mismo reparto en líneas que usa el compositor (Vox.tsx)."""
    lineas, actual = [], ""
    for p in texto.split():
        if actual and len(actual + " " + p) > 11:
            lineas.append(actual)
            actual = p
        else:
            actual = f"{actual} {p}" if actual else p
    if actual:
        lineas.append(actual)
    return lineas


def ruta_segura(rel: str) -> bool:
    p = Path(rel)
    return bool(rel) and not p.is_absolute() and ".." not in p.parts and "\\" not in rel


def efectivas(escenas: list[dict], campo: str, ciclo: list[str]) -> list[str]:
    """Valor final de `entrada` o `transicion` por escena.

    Lo que el guion fija se respeta; lo automático sigue el ciclo y, si coincidiría con la
    escena anterior o con la que el guion fijó para la siguiente, salta a otra opción. Así elegir una a mano nunca
    provoca una repetición con las automáticas de alrededor.
    """
    out: list[str] = []
    for i, s in enumerate(escenas):
        v = s.get(campo)
        if not v:
            vecinas = {out[-1] if out else None, escenas[i + 1].get(campo) if i + 1 < len(escenas) else None}
            v = next((ciclo[(i + k) % len(ciclo)] for k in range(len(ciclo)) if ciclo[(i + k) % len(ciclo)] not in vecinas), ciclo[i % len(ciclo)])
        out.append(v)
    return out


def validar_guion(g: dict) -> list[str]:
    e: list[str] = []
    try:
        conocidos = perfiles()
    except ErrorVox as exc:
        return [str(exc)]
    if g.get("perfil") not in conocidos:
        e.append(f"perfil desconocido: {g.get('perfil')!r}; usa uno de {sorted(conocidos)}")
    if len(str(g.get("opinion_emi", "")).strip()) < 20:
        e.append("falta opinion_emi: pregunta a Emi su postura sobre el tema antes de escribir (mínimo 20 caracteres)")
    if not str(g.get("titulo", "")).strip():
        e.append("falta titulo")
    if "?" not in str(g.get("cta_pregunta", "")):
        e.append("cta_pregunta debe ser una pregunta que invite a comentar")
    mus = g.get("musica") or {}
    if mus.get("animo") not in set(SON.ANIMOS) | {"ninguna"}:
        e.append(f"falta musica.animo: analiza de qué va el video (`vox.py sonido GUION`) y elige uno de {sorted(SON.ANIMOS)} o 'ninguna'")
    if mus.get("animo") == "ninguna" and len(str(mus.get("motivo", ""))) < 10:
        e.append("musica 'ninguna' exige musica.motivo")
    port = g.get("portada") or {}
    if len(str(port.get("texto", ""))) > 34 or len(partir(str(port.get("texto", "")))) > 3:
        e.append("portada.texto: máximo 34 caracteres y 3 líneas")
    if port.get("imagen_archivo") and not ruta_segura(port["imagen_archivo"]):
        e.append("portada.imagen_archivo debe ser relativa a public/")
    ganchos = g.get("ganchos_propuestos")
    if not (isinstance(ganchos, list) and len(ganchos) >= 2 and all(isinstance(x, str) and x.strip() for x in ganchos)):
        e.append("faltan ganchos_propuestos: al menos 2 aperturas distintas para que Emi elija")
    elif not (isinstance(g.get("gancho_elegido"), int) and not isinstance(g.get("gancho_elegido"), bool) and 0 <= g["gancho_elegido"] < len(ganchos)):
        e.append("falta gancho_elegido: el número (desde 0) del gancho que eligió Emi")
    escenas = g.get("escenas") or []
    if not any(s.get("sonido") for s in escenas):
        e.append("ninguna escena tiene `sonido`: propone al menos un efecto que subraye el contenido")
    if not 4 <= len(escenas) <= 9:
        e.append(f"se esperan de 4 a 9 escenas; hay {len(escenas)}")
    vistos = set()
    if not isinstance(escenas, list) or not all(isinstance(x, dict) for x in escenas):
        return e + ["escenas debe ser una lista de objetos"]
    limpias = [{k: (v if isinstance(v, str) else "") for k, v in x.items() if k in ("entrada", "transicion")} for x in escenas]
    ents, trs = efectivas(limpias, "entrada", ENTRADAS), efectivas(limpias, "transicion", TRANSICIONES)
    for i, s in enumerate(escenas):
        p = f"escena {i + 1}"
        if s.get("id") in vistos or not s.get("id"):
            e.append(f"{p}: id ausente o repetido")
        vistos.add(s.get("id"))
        n = " ".join(str(s.get("narracion", "")).split())
        k = " ".join(str(s.get("keyword", "")).split())
        if not n:
            e.append(f"{p}: falta narracion")
        if not k or len(k) > 34:
            e.append(f"{p}: keyword vacío o de más de 34 caracteres")
        if k and n and k.lower() == n.lower():
            e.append(f"{p}: el keyword repite la narración; debe reforzarla")
        if any(len(w) > 16 for w in k.split()):
            e.append(f"{p}: una palabra del keyword pasa de 16 letras y no cabe en pantalla")
        if len(partir(k)) > 3:
            e.append(f"{p}: el keyword ocupa {len(partir(k))} líneas; el máximo es 3 (acórtalo)")
        r = s.get("resaltar")
        if r and limpia(r) not in {limpia(w) for w in k.split()}:
            e.append(f"{p}: resaltar {r!r} no es una palabra del keyword")
        for campo, tope in LIMITES.items():
            if len(str(s.get(campo, ""))) > tope:
                e.append(f"{p}: {campo} pasa de {tope} caracteres")
        for campo in ("entrada", "transicion", "sonido", "remate", "kicker", "nota", "dato", "fuente", "resaltar", "imagen_archivo"):
            if not isinstance(s.get(campo, ""), str):
                e.append(f"{p}: {campo} debe ser texto")
                s[campo] = ""
        if s.get("funcion") not in FUNCIONES:
            e.append(f"{p}: falta `funcion` (para qué existe la escena); opciones {FUNCIONES}")
        if CIFRA.search(n) and not str(s.get("fuente", "")).strip() and len(str(g.get("cifras_sin_fuente", "")).strip()) < 10:
            e.append(f"{p}: la narración trae una cifra y la escena no muestra `fuente`. Un dato sin fuente no se publica")
        o3 = s.get("objeto3d")
        if o3 is not None:
            if not (isinstance(o3, dict) and o3.get("tipo") in OBJETOS_3D):
                e.append(f"{p}: objeto3d.tipo debe ser uno de {OBJETOS_3D}")
            else:
                vals = o3.get("valores", [])
                if not (isinstance(vals, list) and len(vals) <= 5 and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0 for v in vals)):
                    e.append(f"{p}: objeto3d.valores debe ser una lista de hasta 5 números finitos no negativos")
                elif o3["tipo"] == "barras" and len(vals) < 2:
                    e.append(f"{p}: unas barras necesitan al menos 2 valores reales")
                elif o3["tipo"] == "barras" and max(vals) <= 0:
                    e.append(f"{p}: unas barras con todos los valores en cero no muestran nada")
                elif o3["tipo"] == "monedas" and vals and not (isinstance(vals[0], int) and 2 <= vals[0] <= 8):
                    e.append(f"{p}: en monedas, valores[0] es cuántas se apilan: un entero de 2 a 8")
                elif "resaltar" in o3:
                    r = o3["resaltar"]
                    if o3["tipo"] != "barras":
                        e.append(f"{p}: objeto3d.resaltar solo existe en barras")
                    elif not (isinstance(r, int) and not isinstance(r, bool) and 0 <= r < len(vals)):
                        e.append(f"{p}: objeto3d.resaltar debe ser el índice (desde 0) de una de las {len(vals)} barras")
                if len(str(o3.get("porque", "")).strip()) < 15:
                    e.append(f"{p}: objeto3d.porque: di en una frase qué explica mejor en 3D que en plano; si no hay respuesta, no va en 3D")
                if o3["tipo"] == "barras" and not str(s.get("fuente", "")).strip():
                    e.append(f"{p}: unas barras son datos: la escena necesita `fuente`")
            if s.get("imagen_archivo") or s.get("dato"):
                e.append(f"{p}: objeto3d ocupa el lugar del recorte; quita imagen_archivo o dato")
        sec = s.get("secuencia")
        if sec is not None:
            if not (isinstance(sec, dict) and isinstance(sec.get("carpeta"), str) and ruta_segura(sec["carpeta"])
                    and isinstance(sec.get("cuadros"), int) and not isinstance(sec.get("cuadros"), bool) and 2 <= sec["cuadros"] <= 240):
                e.append(f"{p}: secuencia necesita `carpeta` (relativa a public/) y `cuadros` (2 a 240)")
            if s.get("imagen_archivo") or s.get("dato") or s.get("objeto3d"):
                e.append(f"{p}: secuencia ocupa el lugar del recorte; quita imagen_archivo, dato u objeto3d")
        tr3 = s.get("tratamiento")
        if tr3:
            if tr3 not in TRATAMIENTOS:
                e.append(f"{p}: tratamiento {tr3!r} no existe; opciones {TRATAMIENTOS}")
            elif not s.get("imagen_archivo"):
                e.append(f"{p}: tratamiento solo aplica a una escena con imagen_archivo")
        if s.get("remate") and not s.get("sonido"):
            e.append(f"{p}: un remate cae con su sonido; elige `sonido` para esta escena")
        if s.get("remate") and i == 0:
            e.append(f"{p}: la primera escena ya abre con el gancho; el remate va de la segunda en adelante")
        if s.get("sonido") and s["sonido"] not in SON.EFECTOS:
            e.append(f"{p}: sonido {s['sonido']!r} no existe; opciones {sorted(SON.EFECTOS)}")
        img = s.get("imagen_archivo", "")
        if img and not ruta_segura(img):
            e.append(f"{p}: imagen_archivo debe ser una ruta relativa a public/, sin '..'")
        ent = s.get("entrada")
        if ent and ent not in ENTRADAS:
            e.append(f"{p}: entrada {ent!r} no existe; opciones {ENTRADAS}")
        if i > 0 and ents[i] == ents[i - 1]:  # solo puede pasar si el guion fijó las dos
            e.append(f"{p}: repite la entrada de la escena anterior ({ents[i]})")
        tr = s.get("transicion")
        if tr and tr not in set(TRANSICIONES):
            e.append(f"{p}: transicion {tr!r} no existe; opciones {sorted(set(TRANSICIONES))}")
        if i > 1 and trs[i] == trs[i - 1]:
            e.append(f"{p}: repite la transición de la escena anterior ({trs[i]})")
    funs = [s.get("funcion") for s in escenas]
    if escenas and all(f in FUNCIONES for f in funs):
        if funs[0] != "gancho":
            e.append("la primera escena debe ser el `gancho`")
        if funs[-1] != "cierre":
            e.append("la última escena debe ser el `cierre`")
        if "opinion" not in funs:
            e.append("ninguna escena tiene funcion `opinion`: la postura de Emi debe oírse en el video, no solo guiarlo")
    if escenas and "?" not in str(escenas[-1].get("narracion", "")):
        e.append("la última escena debe narrar la pregunta de cierre (cta_pregunta)")
    return e


def avisos_guion(g: dict) -> list[str]:
    """Oficio del guion: no bloquea, pero un video que ignora estos avisos rara vez queda bien."""
    a: list[str] = []
    escenas = [s for s in (g.get("escenas") or []) if isinstance(s, dict)]
    cuenta = [len(str(s.get("narracion", "")).split()) for s in escenas]
    if not cuenta:
        return a
    if cuenta[0] > 14:
        a.append(f"el gancho tiene {cuenta[0]} palabras; con 14 o menos detiene mejor el scroll")
    total = sum(cuenta)
    if total < 55:
        a.append(f"{total} palabras en total (~{total / 2.7:.0f} s): muy corto para desarrollar una idea")
    if total > 200:
        a.append(f"{total} palabras en total (~{total / 2.7:.0f} s): pasa de 75 s; recorta o divide en dos videos")
    for i, n in enumerate(cuenta):
        if n > 22:
            a.append(f"escena {i + 1}: {n} palabras (~{n / 2.7:.0f} s) sin cambio de plano; divídela en dos")
    sin_imagen = [i + 1 for i, s in enumerate(escenas) if not s.get("imagen_archivo") and not s.get("dato") and not s.get("objeto3d") and not s.get("secuencia")]
    n3d = sum(1 for s in escenas if s.get("objeto3d") or s.get("secuencia"))
    if n3d > max(1, len(escenas) // 3):
        a.append(f"{n3d} escenas en 3D de {len(escenas)}: el 3D es un acento, no el estilo; deja solo las que de verdad lo necesitan")
    if sin_imagen:
        a.append(f"escenas {sin_imagen} sin imagen ni dato: quedan solo con texto")
    if sum(1 for s in escenas if s.get("imagen_archivo") or s.get("objeto3d") or s.get("secuencia")) < max(2, len(escenas) // 2):
        a.append("menos de la mitad de las escenas lleva imagen; el estilo pide algo que ver casi siempre")
    primeras = [str(s.get("keyword", "")).split()[:1] for s in escenas]
    if len({tuple(x) for x in primeras}) < len(primeras) - 1:
        a.append("varios keywords empiezan igual; varía el arranque")
    return a


def texto_completo(g: dict) -> str:
    return " ".join(" ".join(str(s["narracion"]).split()) for s in g["escenas"])


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
            actual = {"t": "", "a": float(ini[i]), "b": float(fin[i])}
        actual["t"] += ch
        actual["b"] = float(fin[i])
    if actual:
        out.append(actual)
    return out


def armar_video(g: dict, palabras: list[dict], duracion: float, perfil: dict, publico: Path | None = None) -> dict:
    """Convierte guion + tiempos reales de palabra en la línea de tiempo que lee Remotion.

    Las palabras se reparten entre escenas contando palabras, no caracteres: así un
    proveedor que normalice comillas o espacios no desplaza los límites en silencio.
    """
    conteos = [len(str(s["narracion"]).split()) for s in g["escenas"]]
    if sum(conteos) != len(palabras):
        raise ErrorVox(f"la alineación trae {len(palabras)} palabras y el guion {sum(conteos)}; no se inventan tiempos")
    inicios, pos = [], 0
    for c in conteos:
        if c == 0:
            raise ErrorVox("una escena quedó sin palabras; revisa la narración")
        inicios.append(palabras[pos]["a"])
        pos += c
    total = int(round((duracion + COLA) * FPS))
    cortes = [0] + [max(0, int(round((t - 0.12) * FPS))) for t in inicios[1:]] + [total]
    escenas = []
    ents, trs = efectivas(g["escenas"], "entrada", ENTRADAS), efectivas(g["escenas"], "transicion", TRANSICIONES)
    for i, s in enumerate(g["escenas"]):
        desde, dur = cortes[i], cortes[i + 1] - cortes[i]
        if dur < MIN_ESCENA:
            raise ErrorVox(f"la escena {s['id']} dura {dur} frames; el mínimo es {MIN_ESCENA}. Únela a otra o alarga su narración")
        img = s.get("imagen_archivo", "")
        if img and publico is not None and not (publico / img).is_file():
            raise ErrorVox(f"la escena {s['id']} pide {img} y no existe en {publico}")
        sec = s.get("secuencia") if isinstance(s.get("secuencia"), dict) else None
        if sec and publico is not None:
            faltan = [n for n in range(sec["cuadros"]) if not (publico / sec["carpeta"] / f"{n:04d}.png").is_file()]
            if faltan:
                raise ErrorVox(f"la escena {s['id']} pide {sec['cuadros']} cuadros en {sec['carpeta']} y faltan {len(faltan)} (el primero, {faltan[0]:04d}.png)")
        escenas.append({
            "id": s["id"], "desde": desde, "dur": dur,
            "keyword": " ".join(str(s["keyword"]).split()).upper(), "resaltar": limpia(s.get("resaltar") or ""),
            "kicker": s.get("kicker", ""), "nota": s.get("nota", ""), "dato": s.get("dato", ""),
            "fuente": s.get("fuente", ""), "imagen": img, "foto": bool(s.get("foto_real", False)),
            "entrada": ents[i], "transicion": trs[i],
            "sonido": s.get("sonido", ""), "remate": str(s.get("remate", "")).upper(),
            "objeto3d": ({k: v for k, v in s["objeto3d"].items() if k in ("tipo", "valores", "resaltar")} if isinstance(s.get("objeto3d"), dict) else None),
            "tratamiento": s.get("tratamiento", ""),
            "secuencia": ({"carpeta": s["secuencia"]["carpeta"].strip("/"), "cuadros": s["secuencia"]["cuadros"]} if isinstance(s.get("secuencia"), dict) else None),
        })
    port = g.get("portada") or {}
    con_imagen = next((x for x in escenas if x["imagen"]), None)
    portada = {
        "texto": " ".join(str(port.get("texto") or escenas[0]["keyword"]).split()).upper(),
        "resaltar": limpia(port.get("resaltar") or escenas[0]["resaltar"]),
        "imagen": port.get("imagen_archivo") or (con_imagen["imagen"] if con_imagen else ""),
    }
    if portada["imagen"] and publico is not None and not (publico / portada["imagen"]).is_file():
        raise ErrorVox(f"la portada pide {portada['imagen']} y no existe en {publico}")
    animo = (g.get("musica") or {}).get("animo", "ninguna")
    return {
        "fps": FPS, "ancho": 1080, "alto": 1920, "frames": total,
        "titulo": g["titulo"], "perfil": perfil, "voz": "audio/voz.mp3",
        "musica": "" if animo == "ninguna" else "audio/musica.wav", "animo": animo,
        "finVoz": round(palabras[-1]["b"], 3), "portada": portada, "sfx": True, "escenas": escenas,
        "cierre": str(perfil.get("cierre") or "COMENTA")[:16].upper(),
        "palabras": [{"t": p["t"], "a": round(p["a"], 3), "b": round(p["b"], 3)} for p in palabras],
    }


# ---------- red ----------

LOCALES = {"127.0.0.1", "localhost", "::1"}


def _pedir(url: str, *, metodo="GET", cabeceras=None, cuerpo=None, espera=120, tope: int = 64 * 1024 * 1024, http_local: bool = False) -> bytes:
    u = urllib.parse.urlparse(url)
    if u.scheme != "https" and not (http_local and u.scheme == "http" and u.hostname in LOCALES):
        raise ErrorVox("solo se permiten URLs https")
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo, headers={"User-Agent": "vox-studio/0.4 (video tool; python-urllib)", **(cabeceras or {})})
    if datos is not None:
        req.add_header("Content-Type", "application/json")
    host = urllib.parse.urlparse(url).hostname
    try:
        with urllib.request.urlopen(req, timeout=espera) as r:
            datos_r = r.read(tope + 1)
            if len(datos_r) > tope:
                raise ErrorVox(f"la respuesta de {host} pasa de {tope // (1024 * 1024)} MB; no se descargó")
            return datos_r
    except urllib.error.HTTPError as exc:
        raise ErrorVox(f"{host} respondió HTTP {exc.code}: {exc.read()[:200]!r}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        aviso = " No se sabe si el proveedor cobró: revisa su historial antes de reintentar." if metodo == "POST" else ""
        raise ErrorVox(f"sin respuesta de {host}: {exc}.{aviso}") from exc


def _json(crudo: bytes, quien: str) -> dict:
    try:
        return json.loads(crudo)
    except ValueError as exc:
        raise ErrorVox(f"{quien} devolvió algo que no es JSON") from exc


def _kie() -> dict:
    return {"Authorization": "Bearer " + os.environ.get("KIE_API_KEY", MARCADOR)}


def _eleven() -> dict:
    return {"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", MARCADOR)}


def saldo() -> dict:
    """Saldo real de cada proveedor. Un proveedor sin conexión se informa como tal, nunca se estima."""
    out: dict = {}
    try:
        out["kie_creditos"] = _json(_pedir(f"{KIE}/chat/credit", cabeceras=_kie(), espera=30), "Kie").get("data")
    except ErrorVox as exc:
        out["kie_error"] = str(exc)[:120]
    try:
        sub = _json(_pedir(f"{ELEVEN}/user/subscription", cabeceras=_eleven(), espera=30), "ElevenLabs")
        out["elevenlabs_usados"] = sub.get("character_count")
        out["elevenlabs_limite"] = sub.get("character_limit")
        out["elevenlabs_restantes"] = (sub.get("character_limit") or 0) - (sub.get("character_count") or 0)
    except ErrorVox as exc:
        out["elevenlabs_error"] = str(exc)[:120]
    try:
        cab = {"Authorization": "Bearer " + os.environ.get("APIFY_TOKEN", MARCADOR)}
        lim = _json(_pedir("https://api.apify.com/v2/users/me/limits", cabeceras=cab, espera=30), "Apify").get("data") or {}
        uso = (lim.get("current") or {}).get("monthlyUsageUsd")
        tope = (lim.get("limits") or {}).get("maxMonthlyUsageUsd")
        out["apify_usado_usd"], out["apify_tope_usd"] = uso, tope
        if uso is not None and tope is not None:
            out["apify_restante_usd"] = round(tope - uso, 4)
    except ErrorVox:
        out["apify"] = "no conectado (falta el token)"
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
        filas.append(f"ElevenLabs  | {gasto('elevenlabs_usados', True)} caracteres | {ahora['elevenlabs_restantes']} de {ahora['elevenlabs_limite']} caracteres")
    else:
        filas.append(f"ElevenLabs  | — | sin dato: {ahora.get('elevenlabs_error')}")
    if "apify_restante_usd" in ahora:
        filas.append(f"Apify       | {gasto('apify_usado_usd', True)} USD | {ahora['apify_restante_usd']} de {ahora['apify_tope_usd']} USD este mes")
    else:
        filas.append(f"Apify       | — | {ahora.get('apify', 'sin dato')}")
    return "\n".join(filas)


def huella(*partes: str) -> str:
    return hashlib.sha256("\x1f".join(partes).encode()).hexdigest()


def narrar(texto: str, voz: dict) -> tuple[bytes, list[dict]]:
    cuerpo = {"text": texto, "model_id": voz.get("modelo", "eleven_multilingual_v2"),
              "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}}
    r = _json(_pedir(f"{ELEVEN}/text-to-speech/{voz['voice_id']}/with-timestamps?output_format=mp3_44100_128",
                     metodo="POST", cabeceras=_eleven(), cuerpo=cuerpo, espera=240), "ElevenLabs")
    al = r.get("alignment") or {}
    if not al.get("characters") or not r.get("audio_base64"):
        raise ErrorVox("ElevenLabs no devolvió audio con alineación; no se inventan tiempos de subtítulos")
    return base64.b64decode(r["audio_base64"]), palabras_desde_alineacion(
        al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"])


def _correr(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=True, **kw)
    except FileNotFoundError as exc:
        raise ErrorVox(f"falta el programa {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise ErrorVox(f"{cmd[0]} falló (código {exc.returncode})") from exc


def duracion_audio(ruta: Path) -> float:
    out = _correr(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                  capture_output=True, text=True).stdout
    return float(out.strip())


def generar_imagen(prompt: str, salida: Path, estado: Path, aspecto="3:4", modelo="nano-banana-2-lite", espera=300) -> None:
    if modelo not in MODELOS_KIE:
        raise ErrorVox(f"modelo {modelo!r} sin esquema comprobado; añade su contrato antes de usarlo")
    firma = huella(prompt, aspecto, modelo)
    if estado.exists():
        est = json.loads(estado.read_text())
        if est.get("firma") != firma:
            raise ErrorVox(f"{estado} pertenece a otro prompt, aspecto o modelo; usa un archivo de estado nuevo")
        if est.get("fallo"):
            raise ErrorVox(f"esa tarea ya falló ({est['fallo']}); cambia el prompt y usa un estado nuevo")
    else:
        r = _json(_pedir(f"{KIE}/jobs/createTask", metodo="POST", cabeceras=_kie(),
                         cuerpo={"model": modelo, "input": {"prompt": prompt, "aspect_ratio": aspecto, **MODELOS_KIE[modelo]}}), "Kie")
        tid = (r.get("data") or {}).get("taskId")
        if not tid:
            raise ErrorVox(f"Kie no devolvió taskId: {str(r)[:200]}")
        est = {"taskId": tid, "modelo": modelo, "firma": firma}
        estado.parent.mkdir(parents=True, exist_ok=True)
        estado.write_text(json.dumps(est))
    limite = time.time() + espera
    while time.time() < limite:
        d = _json(_pedir(f"{KIE}/jobs/recordInfo?taskId={est['taskId']}", cabeceras=_kie()), "Kie").get("data") or {}
        st = str(d.get("state", "")).lower()
        if st == "success":
            rj = d.get("resultJson")
            urls = ((json.loads(rj) if isinstance(rj, str) else rj) or {}).get("resultUrls") or []
            if not urls:
                raise ErrorVox("Kie terminó sin URL de resultado")
            if urllib.parse.urlparse(urls[0]).hostname not in HOSTS_DESCARGA:
                raise ErrorVox(f"host de descarga no autorizado: {urllib.parse.urlparse(urls[0]).hostname}")
            salida.parent.mkdir(parents=True, exist_ok=True)
            salida.write_bytes(_pedir(urls[0]))
            return
        if st in {"fail", "failed", "error"}:
            est["fallo"] = str(d.get("failMsg"))[:200]
            estado.write_text(json.dumps(est))
            raise ErrorVox(f"Kie falló: {est['fallo']}")
        time.sleep(4)
    raise ErrorVox(f"Kie no terminó a tiempo; repite el mismo comando con {estado} para reconsultar sin crear otra tarea")


# ---------- imagen local ----------

def recortar_croma(entrada: Path, salida: Path, tolerancia: float = 95.0) -> tuple[int, int]:
    """Quita el fondo uniforme *conectado al borde* y recorta al contenido.

    Mide el color real del fondo en el marco de la imagen (no supone verde puro). Elimina lo
    que toca el borde y los huecos interiores casi idénticos al fondo; un verde distinto dentro
    del sujeto (una hoja, una prenda) se conserva. Para sujetos verdes, generar con --croma magenta.
    """
    import numpy as np
    from PIL import Image, ImageFilter
    from scipy import ndimage

    im = np.asarray(Image.open(entrada).convert("RGB")).astype(np.float32)
    alto, ancho = im.shape[:2]
    m = max(2, min(alto, ancho) // 60)
    marco = np.concatenate([im[:m].reshape(-1, 3), im[-m:].reshape(-1, 3), im[:, :m].reshape(-1, 3), im[:, -m:].reshape(-1, 3)])
    fondo = np.median(marco, axis=0)
    if float(np.mean(np.linalg.norm(marco - fondo, axis=1) < tolerancia)) < 0.9:
        raise ErrorVox("el fondo no es uniforme: genera la imagen de nuevo sobre un color plano")
    dist = np.linalg.norm(im - fondo, axis=2)
    etiquetas, _ = ndimage.label(dist < tolerancia)
    borde = np.unique(np.concatenate([etiquetas[0], etiquetas[-1], etiquetas[:, 0], etiquetas[:, -1]]))
    es_fondo = np.isin(etiquetas, borde[borde > 0])
    # Huecos encerrados (entre un brazo y el cuerpo, perforaciones): solo si son casi idénticos al fondo.
    es_fondo |= dist < tolerancia * 0.45
    if es_fondo.all():
        raise ErrorVox("el recorte quedó vacío: no hay sujeto distinto del fondo")
    # Borde suave: la transparencia sube con la distancia de color solo en la franja pegada al fondo.
    franja = ndimage.binary_dilation(es_fondo, iterations=3) & ~es_fondo
    alfa = np.where(es_fondo, 0.0, 1.0)
    alfa[franja] = np.clip((dist[franja] - tolerancia * 0.5) / (tolerancia * 0.9), 0.15, 1.0)
    # Quitar el derrame del color de fondo únicamente en esa franja.
    canal = int(np.argmax(fondo))
    otros = [c for c in range(3) if c != canal]
    rgb = im.copy()
    rgb[..., canal][franja] = np.minimum(im[..., canal], np.maximum(im[..., otros[0]], im[..., otros[1]]))[franja]
    out = Image.fromarray(np.dstack([rgb, alfa[..., None] * 255.0]).clip(0, 255).astype(np.uint8), "RGBA")
    a = out.getchannel("A").filter(ImageFilter.GaussianBlur(0.6))
    out.putalpha(a)
    caja = a.point(lambda v: 255 if v > 24 else 0).getbbox()
    if not caja:
        raise ErrorVox("el recorte quedó vacío")
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
    "rasgar": "anoisesrc=d=0.45:c=white:a=0.7,bandpass=f=3200:w=2600,tremolo=f=38:d=0.8,afade=t=in:d=0.04,afade=t=out:st=0.25:d=0.2",
}


def sintetizar_sfx(destino: Path) -> list[str]:
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, filtro in SFX.items():
        _correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", filtro, "-ar", "48000", "-ac", "2",
                 str(destino / f"{nombre}.wav")])
    return sorted(SFX)


def _loudnorm(audio: Path, objetivo: float = -14.0, extra: str = "") -> dict:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(audio), "-af", f"loudnorm=I={objetivo}:TP=-2:LRA=11{extra}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
    if not m:
        raise ErrorVox(f"no se pudo medir la sonoridad de {audio.name}")
    return json.loads(m.group(0))


def normalizar(entrada: Path, salida: Path, objetivo: float, video: bool = False) -> str:
    """Dos pasadas: se mide y se aplica una ganancia. Devuelve 'linear' si no hubo compresión."""
    m = _loudnorm(entrada, objetivo)
    medido = (f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    tipo = _loudnorm(entrada, objetivo, medido).get("normalization_type", "")
    salida.parent.mkdir(parents=True, exist_ok=True)
    codec = ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"] if video else ["-c:a", "pcm_s16le"]
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(entrada), "-af", f"loudnorm=I={objetivo}:TP=-2:LRA=11{medido}", "-ar", "48000", *codec, str(salida)])
    return tipo


def masterizar(entrada: Path, salida: Path) -> float:
    """Lleva la mezcla a -14 LUFS con una ganancia fija y un limitador de picos; devuelve la ganancia en dB.

    La voz ya entra nivelada, así que la ganancia debe ser pequeña. Una ganancia grande
    significa que la mezcla venía mal balanceada y la auditoría lo avisa.
    """
    ganancia = round(-14.0 - float(_loudnorm(entrada)["input_i"]), 2)
    salida.parent.mkdir(parents=True, exist_ok=True)
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(entrada), "-c:v", "copy",
             "-af", f"volume={ganancia}dB,alimiter=limit=0.75:level=false:attack=3:release=60", "-ar", "48000",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(salida)])
    return ganancia


def medir(video: Path) -> dict:
    d = _loudnorm(video)
    return {"lufs": d.get("input_i"), "pico_dbtp": d.get("input_tp"), "duracion_s": round(duracion_audio(video), 2)}


def hoja_de_fotogramas(video: Path, datos: dict, salida: Path, guia: bool = False) -> None:
    """Un cuadro del inicio, el cambio y la mitad de cada escena, para auditar con los ojos.

    Con `guia` se sombrean las zonas que tapa la interfaz de TikTok (barra superior, botones
    de la derecha y descripción inferior): nada importante debe caer ahí.
    """
    cuadros = [0]
    for e in datos["escenas"]:
        cuadros += [e["desde"] + 2, e["desde"] + e["dur"] // 2]
    cuadros = sorted(set(min(c, datos["frames"] - 1) for c in cuadros + [datos["frames"] - 8]))
    sel = "+".join(f"eq(n\\,{c})" for c in cuadros)
    cols = min(8, len(cuadros))
    filas = -(-len(cuadros) // cols)
    zonas = ""
    if guia:
        zonas = ("drawbox=x=0:y=0:w=1080:h=215:color=red@0.28:t=fill,drawbox=x=0:y=1450:w=1080:h=470:color=red@0.28:t=fill,"
                 "drawbox=x=960:y=760:w=120:h=690:color=red@0.28:t=fill,")
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", f"select='{sel}',{zonas}scale=250:-1,tile={cols}x{filas}",
             "-vsync", "0", "-frames:v", "1", str(salida)])


VOZ_LUFS = -16.0        # la narración se normaliza a este nivel antes del montaje
MUSICA_BAJO_VOZ = 17.0  # LU que la música queda por debajo de la voz
VOL_EFECTO = 0.8        # ganancia de los remates sonoros (salen a -20 dBFS RMS)
LUFS_FINAL = (-15.0, -13.0)
PICO_MAX = -1.5


def auditar_audio(d: Path, datos: dict, final: dict, ganancia_master: float = 0.0) -> dict:
    """Revisión medible del sonido. No sustituye al oído de Emi: no juzga si la música gusta."""
    import math
    avisos = []
    voz = float(_loudnorm(d / "public" / datos["voz"])["input_i"])
    informe = {"voz_lufs": voz, "final_lufs": float(final["lufs"]), "final_pico_dbtp": float(final["pico_dbtp"]), "ganancia_master_db": ganancia_master}
    if abs(voz - VOZ_LUFS) > 1.5:
        avisos.append(f"la voz mide {voz} LUFS y debía quedar en {VOZ_LUFS}: vuelve a ejecutar `armar`")
    if datos.get("musica"):
        mus = float(_loudnorm(d / "public" / datos["musica"])["input_i"])
        bajo_voz = voz - (mus + 20 * math.log10(datos.get("volMusica", 0.09)))
        informe["musica_bajo_voz_lu"] = round(bajo_voz, 1)
        if bajo_voz < 12:
            avisos.append(f"la música queda solo {bajo_voz:.1f} LU bajo la voz (mínimo 12): puede taparla")
        if bajo_voz > 26:
            avisos.append(f"la música queda {bajo_voz:.1f} LU bajo la voz: casi no se oirá")
    elif datos.get("animo") != "ninguna":
        avisos.append("el video no lleva música")
    if not LUFS_FINAL[0] <= informe["final_lufs"] <= LUFS_FINAL[1]:
        avisos.append(f"sonoridad final {informe['final_lufs']} LUFS fuera de -14 ± 1")
    if informe["final_pico_dbtp"] > PICO_MAX:
        avisos.append(f"pico {informe['final_pico_dbtp']} dBTP por encima de {PICO_MAX}")
    if abs(ganancia_master) > 4:
        avisos.append(f"el master tuvo que mover {ganancia_master:+.1f} dB: la mezcla venía desbalanceada respecto a la voz")
    niveles = {}
    for nombre in sorted({e["sonido"] for e in datos["escenas"] if e.get("sonido")}):
        f = d / "public" / "sfx" / f"{nombre}.wav"
        if not f.is_file():
            avisos.append(f"falta el efecto {nombre} en public/sfx")
            continue
        sobre_voz = SON.leer_nivel(f) + 20 * math.log10(datos.get("volEfecto", VOL_EFECTO)) - voz
        niveles[nombre] = round(sobre_voz, 1)
        if sobre_voz > 0:
            avisos.append(f"el efecto {nombre} suena {sobre_voz:.1f} dB por encima de la voz")
        if sobre_voz < -16:
            avisos.append(f"el efecto {nombre} queda {-sobre_voz:.1f} dB bajo la voz: apenas se oirá")
    informe["efectos_respecto_a_voz_db"] = niveles
    try:  # prueba «a ojos cerrados»: un audio sin altibajos no tiene forma propia
        lra = float(_loudnorm(d / "out" / "final.mp4")["input_lra"])
        informe["rango_dinamico_lu"] = lra
        if lra < 1.5:
            avisos.append(f"el audio es plano (rango {lra} LU): sin la imagen no se distinguiría un momento de otro")
    except (ErrorVox, KeyError, ValueError):
        pass
    silencio = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(d / "out" / "final.mp4"), "-af", "silencedetect=n=-45dB:d=1.2", "-f", "null", "-"],
                              capture_output=True, text=True).stderr.count("silence_start")
    if silencio:
        avisos.append(f"{silencio} silencio(s) de más de 1.2 s")
    informe["avisos"] = avisos
    (d / "out" / "auditoria-audio.json").write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    return informe


ZONAS_TIKTOK = {"barra superior": (0, 0, 1080, 215), "descripción inferior": (0, 1450, 1080, 1920), "botones de la derecha": (960, 760, 1080, 1450)}


def auditar_video(d: Path, datos: dict) -> dict:
    """Revisión medible de la imagen: formato del archivo, contenido en zonas tapadas y cuadros vacíos."""
    import numpy as np
    from PIL import Image
    final = d / "out" / "final.mp4"
    avisos = []
    sonda = json.loads(_correr(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(final)],
                               capture_output=True, text=True).stdout)
    v = next(x for x in sonda["streams"] if x["codec_type"] == "video")
    au = next((x for x in sonda["streams"] if x["codec_type"] == "audio"), {})
    formato = {"codec": v["codec_name"], "ancho": v["width"], "alto": v["height"], "fps": v["r_frame_rate"], "pix_fmt": v["pix_fmt"],
               "audio": au.get("codec_name"), "audio_hz": au.get("sample_rate"), "kbps": round(int(sonda["format"]["bit_rate"]) / 1000),
               "duracion_s": round(float(sonda["format"]["duration"]), 2)}
    esperado = {"codec": "h264", "ancho": 1080, "alto": 1920, "fps": "30/1", "pix_fmt": "yuv420p", "audio": "aac", "audio_hz": "48000"}
    for k, val in esperado.items():
        if formato[k] != val:
            avisos.append(f"formato: {k} es {formato[k]} y debía ser {val}")
    if abs(formato["duracion_s"] - datos["frames"] / FPS) > 0.15:
        avisos.append(f"el archivo dura {formato['duracion_s']} s y la línea de tiempo {datos['frames'] / FPS:.2f} s")
    papel = np.array([int(datos["perfil"]["colores"]["papel"][i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32)

    def cuadro(n: int):
        tmp = d / "out" / "_cuadro.png"
        _correr(["ffmpeg", "-y", "-v", "error", "-i", str(final), "-vf", f"select='eq(n\\,{n})'", "-vsync", "0", "-frames:v", "1", str(tmp)])
        with Image.open(tmp) as im:
            a = np.asarray(im.convert("RGB")).astype(np.float32)
        tmp.unlink(missing_ok=True)
        return np.linalg.norm(a - papel, axis=2) > 90  # tinta: lo que no es papel (el grano y la viñeta no llegan a 90)

    ocupacion = {}
    for e in datos["escenas"]:  # a tres cuartos de cada escena ya entró todo y no hay transición encima
        ultima = e is datos["escenas"][-1]
        # La última escena se mira ya asentada: a tres cuartos puede estar cayendo el sello de cierre.
        tinta = cuadro(datos["frames"] - 6 if ultima else min(datos["frames"] - 1, e["desde"] + int(e["dur"] * 0.75)))
        for nombre, (x0, y0, x1, y1) in ZONAS_TIKTOK.items():
            frac = float(tinta[y0:y1, x0:x1].mean())
            ocupacion[f"{e['id']} · {nombre}"] = round(frac * 100, 2)
            if frac > 0.004:
                avisos.append(f"escena {e['id']}: hay contenido bajo la {nombre} de TikTok ({frac * 100:.1f} % de esa zona)")
        util = float(tinta[230:1440, 90:960].mean())
        if util < 0.06:
            avisos.append(f"escena {e['id']}: el cuadro está casi vacío ({util * 100:.0f} % de tinta en la zona útil)")
    if float(cuadro(0)[230:1440, 90:960].mean()) < 0.06:
        avisos.append("el primer cuadro está casi vacío: no detiene el scroll")
    informe = {"formato": formato, "ocupacion_zonas_tapadas_pct": ocupacion, "avisos": avisos}
    (d / "out" / "auditoria-video.json").write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    return informe


def recortar_al_contenido(archivos: list[Path], margen: int = 14) -> tuple[int, int]:
    """Quita el aire transparente alrededor del objeto. En una secuencia el recorte es el mismo
    para todos los cuadros (la unión de sus contornos), para que el objeto no salte de tamaño."""
    from PIL import Image
    caja = None
    for f in archivos:
        with Image.open(f) as im:
            b = im.convert("RGBA").getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if b:
            caja = b if caja is None else (min(caja[0], b[0]), min(caja[1], b[1]), max(caja[2], b[2]), max(caja[3], b[3]))
    if caja is None:
        raise ErrorVox("el render salió vacío: no hay nada que recortar")
    with Image.open(archivos[0]) as im0:
        w, h = im0.size
    caja = (max(0, caja[0] - margen), max(0, caja[1] - margen), min(w, caja[2] + margen), min(h, caja[3] + margen))
    for f in archivos:
        with Image.open(f) as im:
            rec = im.convert("RGBA").crop(caja)
        rec.save(f)
    return caja[2] - caja[0], caja[3] - caja[1]


def plan_horno(datos: dict, publico: Path) -> tuple[dict, list[dict]]:
    """Qué hay que rendir aparte con WebGL y cómo queda el video una vez horneado.

    El 3D y los sombreadores no se dibujan dentro del video principal: se hornean a imágenes
    con transparencia y el video solo las pega. Así el render no depende de WebGL ni se frena.
    """
    from PIL import Image
    colores = datos["perfil"]["colores"]
    # La firma incluye el código que dibuja: si cambia, lo horneado antes deja de valer.
    fuentes = [publico.parent / "src" / n for n in ("Tres.tsx", "Root.tsx")]
    codigo = huella(*[sha_archivo(f) for f in fuentes if f.is_file()], str(datos.get("fps", FPS)), str(LADO_HORNO))
    listo = json.loads(json.dumps(datos))
    trabajos, tratadas = [], {}
    for i, e in enumerate(listo["escenas"]):
        if e.get("objeto3d"):
            # La primera escena arranca ya asentada (el compositor le adelanta 60 cuadros): se hornea ese mismo tramo.
            inicio = ADELANTO_PRIMERA - 8 if i == 0 else 0
            cuadros = e["dur"] + 16  # cubre la entrada adelantada y el viaje de cámara de salida
            firma = huella(json.dumps(e["objeto3d"], sort_keys=True), json.dumps(colores, sort_keys=True), str(cuadros), str(inicio), codigo)[:12]
            carpeta = f"horno/{e['id']}-{firma}"
            trabajos.append({"modo": "objeto", "destino": carpeta, "cuadros": cuadros,
                             "props": {"modo": "objeto", "colores": colores, "lado": LADO_HORNO, "alto": LADO_HORNO, "frames": cuadros, "inicio": inicio,
                                       "objeto3d": e["objeto3d"], "src": "", "tratamiento": ""}})
            e["secuencia"] = {"carpeta": carpeta, "cuadros": cuadros, "bucle": False, "inicio": inicio}
        elif e.get("tratamiento") and e.get("imagen"):
            origen = publico / e["imagen"]
            with Image.open(origen) as im:
                w, h = im.size
            k = min(900 / w, 900 / h, 1.0)
            firma = huella(sha_archivo(origen), e["tratamiento"], json.dumps(colores, sort_keys=True), codigo)[:12]
            destino = f"horno/{e['id']}-{e['tratamiento']}-{firma}.png"
            trabajos.append({"modo": "foto", "destino": destino, "cuadros": 1,
                             "props": {"modo": "foto", "colores": colores, "lado": max(2, round(w * k)), "alto": max(2, round(h * k)), "frames": 1, "inicio": 0,
                                       "objeto3d": None, "src": e["imagen"], "tratamiento": e["tratamiento"]}})
            tratadas[e["imagen"]] = destino
            e["imagen"], e["tratada"] = destino, True  # `foto` se conserva: una foto real tratada sigue llevando su marco
        e.pop("objeto3d", None)
        e.pop("tratamiento", None)
    port = listo.get("portada") or {}
    if port.get("imagen") in tratadas:  # la portada muestra la misma imagen que el video, ya tratada
        port["imagen"] = tratadas[port["imagen"]]
    return listo, trabajos


def _con_contenido(archivo: Path) -> bool:
    from PIL import Image
    with Image.open(archivo) as im:
        return im.convert("RGBA").getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox() is not None


def hornear(d: Path, trabajos: list[dict], navegador: str) -> int:
    """Rinde lo pendiente del horno con WebGL por software. Lo ya horneado (misma firma) no se repite.

    Todo se arma y se comprueba en `out/_horno*` y solo al final se mueve a `public/horno`:
    un horneado fallido o interrumpido nunca queda donde la siguiente corrida lo daría por bueno.
    """
    hechos = 0
    horno = d / "public" / "horno"
    for t in trabajos:
        destino = d / "public" / t["destino"]
        completo = destino.is_file() if t["modo"] == "foto" else (destino / LISTO).is_file()
        if completo:
            continue
        props = d / "out" / "_horno.json"
        props.parent.mkdir(exist_ok=True)
        props.write_text(json.dumps(t["props"], ensure_ascii=False))
        comun = ["--props=out/_horno.json", "--gl=swangle", "--log=error"] + ([f"--browser-executable={navegador}"] if navegador else [])
        tmp, tmp_foto = d / "out" / "_horno", d / "out" / "_horno.png"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp_foto.unlink(missing_ok=True)
        try:
            if t["modo"] == "foto":
                _correr(["npx", "remotion", "still", "src/index.ts", "Horno", "out/_horno.png", "--image-format=png"] + comun, cwd=d)
                if not (tmp_foto.is_file() and _con_contenido(tmp_foto)):
                    raise ErrorVox(f"el tratamiento de {t['props']['src']} salió vacío: la imagen no cargó o WebGL falló")
                destino.parent.mkdir(parents=True, exist_ok=True)
                os.replace(tmp_foto, destino)
            else:
                _correr(["npx", "remotion", "render", "src/index.ts", "Horno", "out/_horno", "--sequence", "--image-format=png"] + comun, cwd=d)
                salidos = sorted(tmp.glob("*.png"))
                if len(salidos) != t["cuadros"]:
                    raise ErrorVox(f"el horno entregó {len(salidos)} cuadros y se esperaban {t['cuadros']}")
                ordenados = []
                for n, f in enumerate(salidos):  # primero a nombres temporales: «element-0003.png» y «0003.png» no chocan
                    ordenados.append(f.rename(tmp / f"c{n:04d}.tmp"))
                ordenados = [f.rename(tmp / f"{n:04d}.png") for n, f in enumerate(ordenados)]
                recortar_al_contenido(ordenados)
                (tmp / LISTO).write_text(str(t["cuadros"]))
                shutil.rmtree(destino, ignore_errors=True)
                destino.parent.mkdir(parents=True, exist_ok=True)
                os.replace(tmp, destino)
        finally:
            props.unlink(missing_ok=True)
            shutil.rmtree(tmp, ignore_errors=True)
            tmp_foto.unlink(missing_ok=True)
        hechos += 1
    # Lo horneado que ya no pide ninguna escena se borra: `public/` entero se copia en cada render.
    vigentes = {(d / "public" / t["destino"]).resolve() for t in trabajos}
    if horno.is_dir():
        for viejo in horno.iterdir():
            if viejo.resolve() not in vigentes:
                shutil.rmtree(viejo) if viejo.is_dir() else viejo.unlink()
    return hechos


def rendir(d: Path) -> dict:
    datos = json.loads((d / "src" / "data" / "video.json").read_text(encoding="utf-8"))
    navegador = os.environ.get("VOX_NAVEGADOR", "/usr/local/bin/chrome-headless-shell")
    listo, trabajos = plan_horno(datos, d / "public")
    hornear(d, trabajos, navegador if Path(navegador).exists() else "")
    (d / "src" / "data" / "_render.json").write_text(json.dumps(listo, ensure_ascii=False), encoding="utf-8")
    cmd = ["npx", "remotion", "render", "src/index.ts", "Vox", "out/video.mp4", "--props=src/data/_render.json",
           "--codec=h264", "--audio-codec=aac", "--pixel-format=yuv420p", "--log=error",
           "--crf=16", "--jpeg-quality=95", "--color-space=bt709"]  # fuente limpia: TikTok vuelve a comprimir
    if Path(navegador).exists():
        cmd.append(f"--browser-executable={navegador}")
    _correr(cmd, cwd=d)
    foto = ["npx", "remotion", "still", "src/index.ts", "Portada", "out/portada.png", "--props=src/data/_render.json", "--log=error"]
    _correr(foto + [c for c in cmd if c.startswith("--browser-executable")], cwd=d)
    tipo = masterizar(d / "out" / "video.mp4", d / "out" / "final.mp4")
    hoja_de_fotogramas(d / "out" / "final.mp4", datos, d / "out" / "hoja.png")
    hoja_de_fotogramas(d / "out" / "final.mp4", datos, d / "out" / "hoja-tiktok.png", guia=True)
    m = medir(d / "out" / "final.mp4")
    m["audio"] = auditar_audio(d, datos, m, tipo)
    m["video"] = auditar_video(d, datos)
    escribir_manifiesto(d, d / "out" / "final.mp4", {"skill_md": str(RAIZ / "SKILL.md"), "motor": "remotion 4.0.540",
                        "render": {"codec": "h264", "crf": 16, "jpeg_quality": 95, "color": "bt709", "audio": "aac 192k 48 kHz"},
                        "medido": {"lufs": m["lufs"], "pico_dbtp": m["pico_dbtp"], "duracion_s": m["duracion_s"]}})
    return m


# ---------- revisión del render (lo que se entrega se miró) ----------

def sha_archivo(ruta: Path, n: int = 16) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as fh:
        for trozo in iter(lambda: fh.read(1 << 20), b""):
            h.update(trozo)
    return h.hexdigest()[:n]


def hojas_de_revision(video: Path, cortes_s: list[float], salida: Path, fps: int = FPS) -> list[float]:
    """Evidencia para revisar un render: cada transición antes, durante y después, y el video a tamaño de teléfono.

    Una hoja a intervalos regulares no ve una transición rota; por eso se muestrea alrededor de cada corte.
    """
    dur = duracion_audio(video)
    total = max(1, int(dur * fps) - 1)
    if not cortes_s:  # sin cortes conocidos: un punto cada 2.5 s
        cortes_s = [x * 2.5 for x in range(1, int(dur / 2.5) + 1)]
    cortes = [c for c in cortes_s if 0.3 < c < dur - 0.2][:12]
    desfases = [-6, -3, 0, 3, 6, 12]
    cuadros = sorted({min(total, max(0, int(round(c * fps)) + o)) for c in cortes for o in desfases})
    salida.mkdir(parents=True, exist_ok=True)
    vertical = True
    sonda = json.loads(_correr(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", str(video)],
                               capture_output=True, text=True).stdout)["streams"][0]
    vertical = sonda["height"] > sonda["width"]
    if cuadros:
        sel = "+".join(f"eq(n\\,{c})" for c in cuadros)
        filas = -(-len(cuadros) // len(desfases))
        _correr(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", f"select='{sel}',scale={200 if vertical else 360}:-1,tile={len(desfases)}x{filas}",
                 "-vsync", "0", "-frames:v", "1", str(salida / "hoja-transiciones.png")])
    # Tamaño teléfono: así de chico lo ve la gente. Lo que aquí no se lee, no se lee.
    medios = [0.4] + [(a + b) / 2 for a, b in zip([0.0] + cortes, cortes + [dur])]
    cuadros_t = sorted({min(total, int(m * fps)) for m in medios})[:14]
    sel = "+".join(f"eq(n\\,{c})" for c in cuadros_t)
    _correr(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", f"select='{sel}',scale={150 if vertical else 280}:-1,tile={len(cuadros_t)}x1",
             "-vsync", "0", "-frames:v", "1", str(salida / "hoja-telefono.png")])
    return sorted({round(c / fps, 2) for c in cuadros + cuadros_t})


def crear_revision(d: Path, video: Path, cortes_s: list[float]) -> Path:
    tiempos = hojas_de_revision(video, cortes_s, d / "out")
    f = d / "out" / "revision.json"
    if f.is_file():  # repetir `revisar` sobre el mismo render no borra lo ya anotado
        try:
            if json.loads(f.read_text(encoding="utf-8")).get("render") == sha_archivo(video):
                return f
        except ValueError:
            pass
    f.write_text(json.dumps({
        "_doc": "Informe de revisión del render. Lo llena quien miró las hojas y el video; sin él no hay cierre.",
        "render": sha_archivo(video), "archivo": video.name, "segundos_revisados": tiempos,
        "hallazgos": [], "pendientes": [], "revisado_por": "", "visto_y_escuchado_por_emi": False,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    return f


def exigir_revision(d: Path, video: Path) -> dict:
    """No se cierra un video cuyo render actual no se revisó."""
    f = d / "out" / "revision.json"
    if not video.is_file():
        raise ErrorVox(f"no existe {video}: falta rendir")
    if not f.is_file():
        raise ErrorVox("falta revisar el render: ejecuta `revisar`, mira las hojas y llena out/revision.json")
    r = json.loads(f.read_text(encoding="utf-8"))
    if r.get("render") != sha_archivo(video):
        raise ErrorVox("out/revision.json es de un render anterior: vuelve a ejecutar `revisar` y revisa el video actual")
    if not (isinstance(r.get("revisado_por"), str) and r["revisado_por"].strip()):
        raise ErrorVox("out/revision.json no dice quién revisó (`revisado_por`)")
    if not isinstance(r.get("hallazgos"), list) or not isinstance(r.get("pendientes"), list):
        raise ErrorVox("out/revision.json: `hallazgos` y `pendientes` deben ser listas")
    for h in r["hallazgos"]:
        if not (isinstance(h, dict) and str(h.get("problema", "")).strip() and str(h.get("arreglo", "")).strip()):
            raise ErrorVox("out/revision.json: cada hallazgo lleva `segundo`, `problema` y `arreglo` (si ya no aplica, quítalo)")
    return r


def escribir_manifiesto(d: Path, final: Path, extra: dict) -> Path:
    """Con qué se hizo exactamente este archivo: para repetirlo o corregirlo sin usar material viejo."""
    def sha(rel: str):
        f = d / rel
        return sha_archivo(f) if f.is_file() else None
    skill = (Path(extra.pop("skill_md")).read_text(encoding="utf-8") if extra.get("skill_md") else "")
    version = re.search(r'version:\s*"([^"]+)"', skill)
    imagenes = sorted(str(f.relative_to(d)) for carpeta in ("public/img", "assets") for f in (d / carpeta).glob("*") if f.is_file())
    m = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S"), "archivo": final.name, "sha256": sha_archivo(final, 64),
         "skill_version": version.group(1) if version else None,
         "fuentes": {rel: sha(rel) for rel in ("guion.json", "brief.json", "src/data/video.json", "scenes.js", "video.js", "estados/voz.json", "estados/musica.json") if sha(rel)},
         "imagenes": {rel: sha(rel) for rel in imagenes}, **extra}
    f = d / "out" / "manifiesto.json"
    f.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    return f


def hoja_de_referencia(origen: Path, destino: Path) -> Path:
    """Convierte una imagen o un video de referencia de Emi en una hoja para mirarla y decir qué se toma de ella."""
    if not origen.is_file():
        raise ErrorVox(f"no existe {origen}")
    destino.mkdir(parents=True, exist_ok=True)
    salida = destino / f"referencia-{sha_archivo(origen, 8)}.jpg"
    if origen.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
        _correr(["ffmpeg", "-y", "-v", "error", "-i", str(origen), "-vf", "scale='min(900,iw)':-2", str(salida)])
    else:
        dur = duracion_audio(origen)
        _correr(["ffmpeg", "-y", "-v", "error", "-i", str(origen), "-vf", f"fps={8 / max(dur, 1):.4f},scale=240:-2,tile=8x1", "-frames:v", "1", str(salida)])
    return salida


# ---------- Blender: un objeto 3D rendido aparte ----------

def blender_disponible() -> bool:
    return subprocess.run([sys.executable, "-c", "import bpy"], capture_output=True).returncode == 0


def rendir_con_blender(espec: dict, espera: int = 1800) -> dict:
    """Llama a `blender_objeto.py` en otro proceso. Devuelve lo que informó (versión, cuadros) y los segundos que tardó."""
    if not blender_disponible():
        raise ErrorVox("Blender no está instalado: ejecuta `vox.py blender-instalar` (descarga unos 430 MB)")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(espec, fh, ensure_ascii=False)
        ruta = fh.name
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-W", "ignore", str(Path(__file__).with_name("blender_objeto.py")), ruta],
                           capture_output=True, text=True, timeout=espera)
    except subprocess.TimeoutExpired as exc:
        raise ErrorVox(f"Blender no terminó en {espera} s") from exc
    finally:
        Path(ruta).unlink(missing_ok=True)
    listo = re.search(r'\{"ok": true.*\}', r.stdout)
    if r.returncode != 0 or not listo:
        raise ErrorVox("Blender falló: " + (r.stderr or r.stdout)[-500:])
    return {**json.loads(listo.group(0)), "segundos": round(time.time() - t0, 1)}


# ---------- ComfyUI: generación en un servidor propio ----------

def comfy_base() -> str:
    """Dirección del servidor de ComfyUI de Emi. Sin ella no hay ComfyUI: aquí no se instala ni se simula."""
    url = os.environ.get("COMFY_URL", "").rstrip("/")
    if not url:
        raise ErrorVox("ComfyUI necesita un servidor con tarjeta gráfica: define COMFY_URL con su dirección https. "
                       "Este entorno no tiene GPU; para imágenes sin servidor propio se usa `imagen` (Kie).")
    u = urllib.parse.urlparse(url)
    if not u.hostname or not (u.scheme == "https" or (u.scheme == "http" and u.hostname in LOCALES)):
        raise ErrorVox("COMFY_URL debe ser https. Solo se acepta http si ComfyUI corre en esta misma máquina (http://127.0.0.1:8188); "
                       "un ComfyUI de otra computadora hay que publicarlo por https.")
    return url


def comfy_validar_flujo(flujo) -> None:
    if not (isinstance(flujo, dict) and flujo and all(isinstance(n, dict) and "class_type" in n for n in flujo.values())):
        raise ErrorVox("el flujo no está en formato API de ComfyUI (en la interfaz: «Export (API)»)")
    if not any("save" in str(n["class_type"]).lower() or "preview" in str(n["class_type"]).lower() for n in flujo.values()):
        raise ErrorVox("el flujo no tiene un nodo que guarde imagen (SaveImage): no habría nada que bajar")


def comfy_generar(flujo: dict, salida: Path, espera: int = 600) -> dict:
    """Envía un flujo en formato API, espera su resultado y baja la primera imagen."""
    base = comfy_base()
    comfy_validar_flujo(flujo)
    cab = {"Authorization": "Bearer " + os.environ["COMFY_TOKEN"]} if os.environ.get("COMFY_TOKEN") else {}
    pid = _json(_pedir(f"{base}/prompt", metodo="POST", cabeceras=cab, cuerpo={"prompt": flujo}, http_local=True), "ComfyUI").get("prompt_id")
    if not pid:
        raise ErrorVox("ComfyUI no aceptó el flujo (revisa nodos y modelos en el servidor)")
    limite = time.time() + espera
    while time.time() < limite:
        hist = _json(_pedir(f"{base}/history/{pid}", cabeceras=cab, espera=30, http_local=True), "ComfyUI").get(pid)
        if hist:
            if (hist.get("status") or {}).get("status_str") == "error":
                raise ErrorVox("ComfyUI terminó con error en el flujo")
            for nodo in (hist.get("outputs") or {}).values():
                for img in nodo.get("images") or []:
                    q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")})
                    datos = _pedir(f"{base}/view?{q}", cabeceras=cab, espera=120, tope=40 * 1024 * 1024, http_local=True)
                    try:
                        from PIL import Image
                        with Image.open(io.BytesIO(datos)) as im:
                            im.verify()
                    except Exception as exc:  # una página de error guardada como .png contaminaría el video
                        raise ErrorVox("ComfyUI devolvió algo que no es una imagen") from exc
                    salida.parent.mkdir(parents=True, exist_ok=True)
                    salida.write_bytes(datos)
                    return {"prompt_id": pid, "archivo": img["filename"], "bytes": len(datos)}
            raise ErrorVox("ComfyUI terminó sin ninguna imagen de salida (falta un nodo SaveImage)")
        time.sleep(3)
    raise ErrorVox(f"ComfyUI no terminó en {espera} s; el trabajo {pid} sigue en su cola")


# ---------- fotos reales (Apify) ----------

ACTOR_FOTOS = "automation-lab~google-images-scraper"


def buscar_fotos(consulta: str, maximo: int, tope_usd: float, derechos: str = "creative_commons") -> list[dict]:
    """Candidatas reales con su página de origen. Encontrar una foto no da derecho a usarla."""
    cab = {"Authorization": "Bearer " + os.environ.get("APIFY_TOKEN", MARCADOR)}
    entrada = {"queries": [consulta], "maxResultsPerQuery": maximo, "imageSize": "large", "imageType": "photo",
               "safeSearch": "strict", "language": "es", "country": "mx"}
    if derechos != "cualquiera":
        entrada["usageRights"] = derechos
    url = f"https://api.apify.com/v2/acts/{ACTOR_FOTOS}/run-sync-get-dataset-items?maxTotalChargeUsd={tope_usd}&restartOnError=false"
    datos = _json(_pedir(url, metodo="POST", cabeceras=cab, cuerpo=entrada, espera=280), "Apify")
    if not isinstance(datos, list):
        raise ErrorVox(f"Apify devolvió algo inesperado: {str(datos)[:160]}")
    return [{"imagen": x.get("imageUrl") or x.get("url"), "pagina": x.get("sourceUrl"), "dominio": x.get("sourceDomain"),
             "titulo": x.get("title"), "ancho": x.get("imageWidth") or x.get("width"), "alto": x.get("imageHeight") or x.get("height")}
            for x in datos if (x.get("imageUrl") or x.get("url"))][:maximo]


def licencia_commons(url_imagen: str) -> dict | None:
    """Autor y licencia de un archivo de Wikimedia Commons, leídos de su propia ficha."""
    u = urllib.parse.urlparse(url_imagen)
    if u.hostname != "upload.wikimedia.org" or not u.path.startswith("/wikipedia/commons/"):
        return None  # los archivos locales de cada Wikipedia (uso legítimo) no son de Commons
    partes = u.path.split("/")
    # En una miniatura (/thumb/a/ab/Nombre.jpg/1200px-Nombre.jpg) el archivo real es el penúltimo segmento.
    nombre = urllib.parse.unquote(partes[-2] if "thumb" in partes else partes[-1])
    api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=extmetadata&titles="
           + urllib.parse.quote("File:" + nombre))
    paginas = (_json(_pedir(api, espera=30), "Wikimedia Commons").get("query") or {}).get("pages") or {}
    info = next(iter(paginas.values()), {}).get("imageinfo") or [{}]
    meta = info[0].get("extmetadata") or {}
    limpio = lambda k: re.sub(r"<[^>]+>", "", str((meta.get(k) or {}).get("value", ""))).strip()
    if not limpio("LicenseShortName"):
        return None
    return {"licencia": limpio("LicenseShortName"), "autor": limpio("Artist"), "atribucion_requerida": limpio("AttributionRequired"),
            "ficha": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(nombre)}


# ---------- biblioteca para reciclar ----------

def dir_biblioteca() -> Path:
    return Path(os.environ.get("VOX_BIBLIOTECA") or RAIZ.parent.parent / "biblioteca")


def leer_catalogo() -> list[dict]:
    f = dir_biblioteca() / "catalogo.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def catalogar(d: Path) -> list[dict]:
    """Copia a la biblioteca los recortes que el video usó, con lo que muestran y cómo se hicieron."""
    g = _guion(str(d / "guion.json"))
    dir_biblioteca().mkdir(parents=True, exist_ok=True)
    cat = leer_catalogo()
    conocidos = {x["sha256"] for x in cat}
    nuevos = []
    for s in g["escenas"]:
        img = s.get("imagen_archivo")
        origen = d / "public" / img if img else None
        if not origen or not origen.is_file():
            continue
        sha = hashlib.sha256(origen.read_bytes()).hexdigest()
        if sha in conocidos:
            continue
        prompt_f = d / "prompts" / (Path(img).stem + ".txt")
        ident = f"{g['perfil']}-{d.name}-{Path(img).stem}-{sha[:8]}"  # el sha evita choques si la imagen se regenera
        destino = dir_biblioteca() / g["perfil"] / f"{ident}{origen.suffix}"
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origen, destino)
        try:  # copia ligera: basta para un video vertical y no engorda el repositorio
            from PIL import Image
            with Image.open(destino) as im:
                if max(im.size) > 1200:
                    im.thumbnail((1200, 1200))
                    im.save(destino, optimize=True)
        except ImportError:
            pass
        item = {"id": ident, "espacio": g["perfil"], "archivo": str(destino.relative_to(dir_biblioteca())), "sha256": sha,
                "muestra": prompt_f.read_text(encoding="utf-8").strip() if prompt_f.is_file() else "",
                "descripcion": s.get("descripcion_imagen", ""), "foto_real": bool(s.get("foto_real", False)),
                "origen": f"productions/{g['perfil']}/{d.name}", "fecha": time.strftime("%Y-%m-%d"), "usos": 1}
        cat.append(item)
        conocidos.add(sha)
        nuevos.append(item)
    (dir_biblioteca() / "catalogo.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return nuevos


def buscar_en_biblioteca(texto: str = "", espacio: str = "") -> list[dict]:
    terminos = [t for t in re.split(r"\W+", texto.lower()) if len(t) > 2]
    out = []
    for x in leer_catalogo():
        if espacio and x["espacio"] != espacio:
            continue
        donde = f"{x['muestra']} {x['descripcion']} {x['id']}".lower()
        if all(t in donde for t in terminos):
            out.append(x)
    return out


# ---------- CLI ----------

def _guion(ruta: str) -> dict:
    g = json.loads(Path(ruta).read_text(encoding="utf-8"))
    errores = validar_guion(g)
    if errores:
        raise ErrorVox("guion inválido: " + "; ".join(errores))
    return g


def _escribir_video(g: dict, d: Path, palabras: list[dict]) -> dict:
    import math
    cruda = d / "public" / "audio" / "voz.mp3"
    video = armar_video(g, palabras, duracion_audio(cruda), perfiles()[g["perfil"]], d / "public")
    # La voz manda: se lleva a un nivel fijo y todo lo demás se coloca respecto a ella.
    normalizar(cruda, d / "public" / "audio" / "voz-n.wav", VOZ_LUFS)
    video["voz"] = "audio/voz-n.wav"
    # Sonido nuevo para cada video: la semilla sale de su propio texto.
    semilla = int(huella(g["titulo"], texto_completo(g))[:8], 16)
    cortes_s = [e["desde"] / FPS for e in video["escenas"][1:]]
    plan = SON.plan_musica(video["animo"], semilla, cortes_s) if video["musica"] else {"tonica": 48}
    SON.sintetizar_efectos(d / "public" / "sfx", semilla, plan["tonica"])
    video["volEfecto"] = VOL_EFECTO
    pista, receta = d / "public" / "audio" / "musica.wav", d / "estados" / "musica.json"
    if video["musica"]:  # pista original, a la medida exacta y siguiendo los cambios de escena
        cortes = [e["desde"] / FPS for e in video["escenas"][1:]]
        SON.guardar(pista, SON.componer(video["animo"], video["frames"] / FPS, semilla, cortes), nivel=-20.0)
        mus = float(_loudnorm(pista)["input_i"])
        video["volMusica"] = round(min(1.0, 10 ** ((VOZ_LUFS - MUSICA_BAJO_VOZ - mus) / 20)), 4)
        receta.parent.mkdir(exist_ok=True)
        receta.write_text(json.dumps(plan))
    else:  # sin música: no dejar restos de un armado anterior
        pista.unlink(missing_ok=True)
        receta.unlink(missing_ok=True)
    for e in video["escenas"]:  # ritmo real, medido en la voz
        if e["dur"] / FPS > ESCENA_LARGA:
            print(f"⚠ la escena {e['id']} dura {e['dur'] / FPS:.1f} s: divídela o acepta el pulso automático a media escena")
    (d / "src" / "data").mkdir(parents=True, exist_ok=True)
    (d / "src" / "data" / "video.json").write_text(json.dumps(video, ensure_ascii=False, indent=1), encoding="utf-8")
    return video


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("espacios")
    sub.add_parser("saldo")
    p = sub.add_parser("proyecto"); p.add_argument("dir"); p.add_argument("--perfil", required=True)
    p = sub.add_parser("validar"); p.add_argument("guion")
    p = sub.add_parser("voz"); p.add_argument("guion"); p.add_argument("--dir", required=True); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("armar"); p.add_argument("guion"); p.add_argument("--dir", required=True)
    p = sub.add_parser("imagen"); p.add_argument("--prompt-file", required=True); p.add_argument("--out", required=True)
    p.add_argument("--estado", required=True); p.add_argument("--aspecto", default="3:4"); p.add_argument("--execute", action="store_true")
    p.add_argument("--estilo", choices=sorted(ESTILOS), default=None); p.add_argument("--perfil", default=""); p.add_argument("--modelo", choices=sorted(MODELOS_KIE), default="nano-banana-2-lite")
    p.add_argument("--croma", choices=sorted(CROMAS) + ["ninguno"], default="verde")
    p = sub.add_parser("recorte"); p.add_argument("entrada"); p.add_argument("salida")
    p = sub.add_parser("render"); p.add_argument("dir")
    sub.add_parser("blender-instalar")
    p = sub.add_parser("blender"); p.add_argument("--dir", required=True); p.add_argument("--tipo", choices=BLENDER_TIPOS, required=True)
    p.add_argument("--out", required=True); p.add_argument("--porque", required=True); p.add_argument("--perfil", required=True)
    p.add_argument("--texto", default=""); p.add_argument("--modelo", default=""); p.add_argument("--acabado", choices=["plano", "real"], default="plano")
    p.add_argument("--giro", type=int, default=0); p.add_argument("--tam", type=int, default=1024); p.add_argument("--fuente", default="")
    p = sub.add_parser("comfy"); p.add_argument("--flujo", required=True); p.add_argument("--out", required=True); p.add_argument("--dir", required=True)
    p.add_argument("--porque", required=True); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("revisar"); p.add_argument("dir")
    p = sub.add_parser("referencia"); p.add_argument("archivo"); p.add_argument("--dir", required=True)
    p = sub.add_parser("sonido"); p.add_argument("guion")
    p = sub.add_parser("foto"); p.add_argument("--consulta", required=True); p.add_argument("--dir", required=True)
    p.add_argument("--max", type=int, default=5); p.add_argument("--tope-usd", type=float, default=0.12)
    p.add_argument("--derechos", choices=["creative_commons", "commercial", "cualquiera"], default="creative_commons"); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("foto-bajar"); p.add_argument("--dir", required=True); p.add_argument("--indice", type=int, required=True)
    p.add_argument("--out", required=True); p.add_argument("--licencia", default=""); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("catalogar"); p.add_argument("dir")
    p = sub.add_parser("biblioteca"); p.add_argument("--buscar", default=""); p.add_argument("--espacio", default="")
    p = sub.add_parser("reciclar"); p.add_argument("id"); p.add_argument("--dir", required=True); p.add_argument("--como", default="")
    p = sub.add_parser("cierre"); p.add_argument("dir")
    p = sub.add_parser("aprender"); p.add_argument("texto"); p.add_argument("--espacio", default="")
    p = sub.add_parser("aprendizajes"); p.add_argument("--espacio", default="")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "espacios":
            for k, v in perfiles().items():
                print(f"{k:10} {v['nombre']:22} acento {v['colores']['acento']}  voz {v['voz']['nombre']}  [{v['estado']}]")
        elif a.cmd == "saldo":
            print(tabla_saldo(None, saldo()))
        elif a.cmd == "proyecto":
            if a.perfil not in perfiles():
                raise ErrorVox(f"espacio desconocido: {a.perfil}")
            d = Path(a.dir)
            if d.parent.name != a.perfil:
                raise ErrorVox(f"cada espacio va por separado: usa productions/{a.perfil}/{d.name}")
            if d.exists():
                raise ErrorVox(f"{d} ya existe; no se sobrescribe una producción")
            with tempfile.TemporaryDirectory() as tmp:  # los SFX se prueban antes de crear nada
                sintetizar_sfx(Path(tmp) / "sfx")
                SON.sintetizar_efectos(Path(tmp) / "sfx")
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(PLANTILLA, d, ignore=shutil.ignore_patterns("node_modules", "out"))
                shutil.copytree(Path(tmp) / "sfx", d / "public" / "sfx")
            (d / "estados").mkdir(exist_ok=True)
            (d / "estados" / "saldo-inicio.json").write_text(json.dumps(saldo()))
            print(f"Producción creada en {d}.\n\nAntes de escribir el guion, aplica esto:\n{leer_aprendizajes(a.perfil)}")
        elif a.cmd == "validar":
            g = json.loads(Path(a.guion).read_text(encoding="utf-8"))
            errores = validar_guion(g)
            for x in errores:
                print("✗", x)
            print("Guion válido." if not errores else f"{len(errores)} problema(s).")
            for x in avisos_guion(g):
                print("⚠", x)
            return 1 if errores else 0
        elif a.cmd in {"voz", "armar"}:
            g = _guion(a.guion)
            voz = perfiles()[g["perfil"]]["voz"]
            texto = texto_completo(g)
            d = Path(a.dir)
            cache = d / "estados" / "voz.json"
            firma = huella(texto, voz["voice_id"], voz.get("modelo", ""))
            guardado = json.loads(cache.read_text()) if cache.exists() else {}
            vigente = guardado.get("firma") == firma and (d / "public" / "audio" / "voz.mp3").is_file()
            if vigente:
                video = _escribir_video(g, d, guardado["palabras"])
                print(f"video.json reconstruido con la voz ya pagada: {video['frames'] / FPS:.1f} s. No se gastó nada.")
            elif a.cmd == "armar":
                raise ErrorVox("la narración cambió o no existe: ejecuta `voz --execute` (esto sí gasta caracteres)")
            elif not a.execute:
                print(f"En seco: {len(texto)} caracteres con la voz {voz['nombre']}. Añade --execute para narrar.")
            else:
                audio, palabras = narrar(texto, voz)
                destino = d / "public" / "audio" / "voz.mp3"
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(audio)
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({"firma": firma, "palabras": palabras}))  # antes de armar: lo pagado no se pierde
                video = _escribir_video(g, d, palabras)
                print(f"Voz lista: {len(texto)} caracteres, {video['frames'] / FPS:.1f} s, {len(palabras)} palabras con tiempo real.")
        elif a.cmd == "imagen":
            if a.perfil and a.perfil not in perfiles():
                raise ErrorVox(f"espacio desconocido: {a.perfil}")
            a.estilo = a.estilo or (perfiles()[a.perfil].get("estilo_imagen") if a.perfil else None) or "ilustracion"
            if a.estilo not in ESTILOS:
                raise ErrorVox(f"estilo_imagen {a.estilo!r} del espacio no existe")
            prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip() + ". " + ESTILOS[a.estilo]
            if a.croma != "ninguno":
                prompt += (f", single isolated subject, centered, full subject visible with margin, on a perfectly uniform solid "
                           f"{CROMAS[a.croma]} chroma key background, no cast shadow, no floor, no gradient")
            prompt += ", no text, no letters, no logos, no watermark"
            if not a.execute:
                print(f"En seco: 1 imagen {a.modelo} {a.aspecto}, estilo {a.estilo}. Añade --execute para generarla.")
                return 0
            generar_imagen(prompt, Path(a.out), Path(a.estado), a.aspecto, a.modelo)
            print(f"Imagen guardada en {a.out}")
        elif a.cmd == "recorte":
            print("Recorte", recortar_croma(Path(a.entrada), Path(a.salida)))
        elif a.cmd == "sonido":
            g = json.loads(Path(a.guion).read_text(encoding="utf-8"))
            pr = SON.proponer(g)
            m = pr["musica"]
            print(f"Música propuesta: {m['animo']} ({m['bpm']} bpm) — {m['porque']}")
            print("Opciones: " + "; ".join(f"{k}: {v[4]}" for k, v in SON.ANIMOS.items()))
            for x in pr["escenas"]:
                print(f"  escena {x['id']}: sonido={x['sonido'] or '—'}  remate={x['remate'] or '—'}")
            print("Efectos disponibles: " + "; ".join(f"{k} ({v[1]})" for k, v in SON.EFECTOS.items()))
            print("Es una propuesta: revísala contra el sentido de cada escena y escribe en el guion musica.animo, sonido y remate.")
        elif a.cmd == "foto":
            if not 1 <= a.max <= 10:
                raise ErrorVox("--max entre 1 y 10: se buscan pocas candidatas, no un banco de imágenes")
            # Precio del actor medido el 2026-11-10: 0.005 por arranque + 0.05 por página de resultados + 0.0023 por imagen.
            minimo = round(0.005 + 0.05 + 0.0023 * a.max + 0.005, 3)
            if a.tope_usd < minimo:
                raise ErrorVox(f"--tope-usd {a.tope_usd} no alcanza: una búsqueda de {a.max} fotos cuesta cerca de {minimo} USD y un tope menor la aborta cobrando igual")
            if not a.execute:
                print(f"En seco: hasta {a.max} fotos de «{a.consulta}», derechos {a.derechos}, tope {a.tope_usd} USD. Añade --execute.")
                return 0
            fotos = buscar_fotos(a.consulta, a.max, a.tope_usd, a.derechos)
            est = Path(a.dir) / "estados" / "fotos.json"
            est.parent.mkdir(parents=True, exist_ok=True)
            est.write_text(json.dumps({"consulta": a.consulta, "derechos": a.derechos, "candidatas": fotos}, ensure_ascii=False, indent=1))
            for i, f in enumerate(fotos):
                print(f"[{i}] {f['ancho']}x{f['alto']}  {f['dominio']}  {str(f['titulo'])[:60]}\n     página: {f['pagina']}")
            print("Antes de usar una: abre su página, confirma qué muestra y su licencia. El filtro de derechos solo orienta.")
        elif a.cmd == "foto-bajar":
            est = json.loads((Path(a.dir) / "estados" / "fotos.json").read_text())
            if not 0 <= a.indice < len(est["candidatas"]):
                raise ErrorVox(f"--indice entre 0 y {len(est['candidatas']) - 1}")
            f = est["candidatas"][a.indice]
            destino = Path(a.out)
            if Path(a.dir).resolve() not in destino.resolve().parents:
                raise ErrorVox("--out debe quedar dentro de la producción (--dir)")
            try:
                oficial = licencia_commons(f["imagen"])  # en Commons la licencia se lee de la ficha
            except ErrorVox as exc:  # su API limita peticiones: se sigue con verificación manual de la ficha
                oficial = None
                print(f"No se pudo leer la ficha automáticamente ({str(exc)[:60]}); usa --licencia tras abrirla.")
            if oficial:
                f["commons"] = oficial
                a.licencia = f"{oficial['licencia']} · {oficial['autor']}"
                print(f"Wikimedia Commons: {a.licencia}\n  ficha: {oficial['ficha']}")
            if len(a.licencia.strip()) < 8:
                raise ErrorVox("--licencia: escribe la licencia y el autor comprobados en la página de origen")
            if not a.execute:
                print(f"En seco: bajaría {f['imagen']} (página {f['pagina']}). Añade --execute.")
                return 0
            datos_img = _pedir(f["imagen"], espera=60, tope=15 * 1024 * 1024)
            try:
                import io
                from PIL import Image
                Image.open(io.BytesIO(datos_img)).verify()
            except Exception as exc:  # noqa: BLE001 - lo bajado no es una imagen
                raise ErrorVox("lo descargado no es una imagen válida; no se guardó") from exc
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(datos_img)
            f.update(licencia=a.licencia, archivo=str(destino), sha256=hashlib.sha256(destino.read_bytes()).hexdigest())
            (Path(a.dir) / "estados" / "fotos.json").write_text(json.dumps(est, ensure_ascii=False, indent=1))
            print(f"Foto guardada en {destino}. Si el host está bloqueado por la red del entorno, pide a Emi autorizar ese dominio.")
        elif a.cmd == "catalogar":
            nuevos = catalogar(Path(a.dir))
            print(f"{len(nuevos)} recurso(s) nuevos en la biblioteca: " + ", ".join(x["id"] for x in nuevos))
        elif a.cmd == "biblioteca":
            for x in buscar_en_biblioteca(a.buscar, a.espacio):
                print(f"{x['id']}  [{x['espacio']}]  usos {x['usos']}  {x['archivo']}\n    {x['muestra'] or x['descripcion']}")
            print("Reciclar solo si la imagen dice exactamente lo que la escena necesita; mírala antes. Si no, genera una nueva.")
        elif a.cmd == "reciclar":
            cat = leer_catalogo()
            x = next((c for c in cat if c["id"] == a.id), None)
            if not x:
                raise ErrorVox(f"no existe {a.id} en la biblioteca")
            destino = Path(a.dir) / "public" / "img" / Path(a.como or x["archivo"]).name  # solo el nombre: nunca fuera de la producción
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(dir_biblioteca() / x["archivo"], destino)
            x["usos"] += 1
            (dir_biblioteca() / "catalogo.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"Copiado a {destino} (uso número {x['usos']}).")
        elif a.cmd == "render":
            m = rendir(Path(a.dir))
            print(f"Final en {a.dir}/out/final.mp4 · {m['duracion_s']} s · {m['lufs']} LUFS · pico {m['pico_dbtp']} dBTP")
            au = m["audio"]
            print(f"Audio: voz {au['voz_lufs']} LUFS · música {au.get('musica_bajo_voz_lu', '—')} LU bajo la voz · efectos respecto a la voz (dB) {au['efectos_respecto_a_voz_db']} · master {au['ganancia_master_db']:+.1f} dB")
            fm = m["video"]["formato"]
            print(f"Imagen: {fm['codec']} {fm['ancho']}x{fm['alto']} {fm['fps']} {fm['pix_fmt']} · {fm['kbps']} kbps")
            for aviso in au["avisos"] + m["video"]["avisos"]:
                print(f"  ⚠ {aviso}")
            if not au["avisos"] and not m["video"]["avisos"]:
                print("  Sin avisos automáticos de audio ni de imagen.")
            print(f"Audita {a.dir}/out/hoja.png, {a.dir}/out/hoja-tiktok.png (zonas que tapa TikTok en rojo) y {a.dir}/out/portada.png antes de entregar y termina con `cierre` y `catalogar`.")
        elif a.cmd == "blender-instalar":
            if blender_disponible():
                print("Blender (módulo bpy) ya está instalado.")
            else:
                print("Instalando Blender como módulo de Python (unos 430 MB)…")
                _correr([sys.executable, "-m", "pip", "install", "--no-input", "--quiet", "bpy"])
                print("Instalado." if blender_disponible() else "No se pudo importar bpy tras instalar: revisa la versión de Python.")
        elif a.cmd == "blender":
            d = Path(a.dir).resolve()
            destino = (d / a.out).resolve()
            partes = Path(a.out).parts
            if d not in destino.parents or not ruta_segura(a.out) or len(partes) < 2 or partes[0] != "public":
                raise ErrorVox("--out debe quedar dentro de `public/` de la producción, relativo a ella (p. ej. public/img/moneda.png)")
            if a.giro and destino.suffix:
                raise ErrorVox("con --giro, --out es una carpeta (p. ej. public/seq/moneda), sin extensión")
            if not a.giro and destino.suffix.lower() != ".png":
                raise ErrorVox("sin --giro, --out es un archivo .png (Blender entrega PNG con transparencia)")
            if len(a.porque.strip()) < 20:
                raise ErrorVox("--porque: explica en una frase qué da Blender aquí que no da el 3D del compositor ni una imagen")
            if a.perfil not in perfiles():
                raise ErrorVox(f"espacio desconocido: {a.perfil}")
            if a.tipo == "texto" and not a.texto.strip():
                raise ErrorVox("--tipo texto necesita --texto")
            if a.tipo == "modelo" and not (Path(a.modelo).is_file() and Path(a.modelo).suffix.lower() in MODELOS_3D):
                raise ErrorVox(f"--tipo modelo necesita --modelo con un archivo existente {sorted(MODELOS_3D)}")
            if not 0 <= a.giro <= 240 or not 256 <= a.tam <= 2048:
                raise ErrorVox("--giro entre 0 y 240 cuadros; --tam entre 256 y 2048")
            if a.fuente and not Path(a.fuente).is_file():
                raise ErrorVox(f"no existe la tipografía {a.fuente}")
            if a.giro and destino.is_dir():  # cuadros de un giro anterior más largo contaminarían el recorte y el bucle
                for viejo in destino.glob("*.png"):
                    viejo.unlink()
            info = rendir_con_blender({"tipo": a.tipo, "texto": a.texto, "modelo": str(Path(a.modelo).resolve()) if a.modelo else "",
                                       "colores": perfiles()[a.perfil]["colores"], "acabado": a.acabado, "salida": str(destino),
                                       "giro": a.giro, "tam": a.tam, "fuente": str(Path(a.fuente).resolve()) if a.fuente else ""})
            salidos = [destino / f"{n:04d}.png" for n in range(a.giro)] if a.giro else [destino]
            if not all(f.is_file() for f in salidos):
                raise ErrorVox("Blender terminó sin escribir todos los cuadros esperados")
            tam_final = recortar_al_contenido(salidos)
            info["tam"] = list(tam_final)
            (d / "estados").mkdir(exist_ok=True)
            reg = d / "estados" / "blender.json"
            hechos = json.loads(reg.read_text()) if reg.is_file() else []
            hechos.append({"salida": a.out, "tipo": a.tipo, "acabado": a.acabado, "giro": a.giro, "porque": a.porque.strip(), **info})
            reg.write_text(json.dumps(hechos, ensure_ascii=False, indent=1))
            if a.giro:
                rel = Path(*partes[1:]).as_posix()
                print(f"{a.giro} cuadros en {a.out}/ ({info['segundos']} s, Blender {info['blender']}). En la escena: \"secuencia\": {{\"carpeta\": \"{rel}\", \"cuadros\": {a.giro}}}")
            else:
                print(f"Imagen en {a.out} ({info['segundos']} s, Blender {info['blender']}). En la escena: \"imagen_archivo\": \"{Path(*partes[1:]).as_posix()}\". Mírala antes de montar.")
        elif a.cmd == "comfy":
            d = Path(a.dir).resolve()
            destino = (d / a.out).resolve()
            if d not in destino.parents or not ruta_segura(a.out):
                raise ErrorVox("--out debe quedar dentro de la producción")
            if len(a.porque.strip()) < 20:
                raise ErrorVox("--porque: explica qué necesita esta imagen que Kie no puede dar")
            base_comfy = comfy_base()  # primero el servidor: sin él no tiene sentido leer nada más
            try:
                flujo = json.loads(Path(a.flujo).read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise ErrorVox(f"no se pudo leer el flujo {a.flujo}: debe ser el JSON de «Export (API)» de ComfyUI") from exc
            comfy_validar_flujo(flujo)
            if not a.execute:
                print(f"En seco: flujo de {len(flujo)} nodos hacia {base_comfy}. Añade --execute para enviarlo.")
                return 0
            info = comfy_generar(flujo, destino)
            (d / "estados").mkdir(exist_ok=True)
            reg = d / "estados" / "comfy.json"
            hechos = json.loads(reg.read_text()) if reg.is_file() else []
            hechos.append({"salida": a.out, "flujo": huella(json.dumps(flujo, sort_keys=True)), "porque": a.porque.strip(), **info})
            reg.write_text(json.dumps(hechos, ensure_ascii=False, indent=1))
            print(f"Imagen de ComfyUI en {a.out}. Mírala antes de montar: es generada, se revisa igual que las de Kie.")
        elif a.cmd == "revisar":
            d = Path(a.dir)
            datos = json.loads((d / "src" / "data" / "video.json").read_text(encoding="utf-8"))
            f = crear_revision(d, d / "out" / "final.mp4", [e["desde"] / FPS for e in datos["escenas"][1:]])
            print(f"Mira {d}/out/hoja-transiciones.png (cada cambio de escena: antes, durante y después) y {d}/out/hoja-telefono.png (tamaño real de un teléfono).")
            print(f"Luego llena {f}: `hallazgos` (segundo, problema, arreglo), `pendientes` y `revisado_por`. Corrige los 3 peores y vuelve a rendir.")
        elif a.cmd == "referencia":
            print(f"Hoja en {hoja_de_referencia(Path(a.archivo), Path(a.dir) / 'referencias')}. Mírala y dile a Emi qué tomas de ella (ritmo, tipografía, transiciones) antes de seguir.")
        elif a.cmd == "cierre":
            d = Path(a.dir)
            exigir_revision(d, d / "out" / "final.mp4")
            ini = d / "estados" / "saldo-inicio.json"
            ahora = saldo()
            (d / "estados").mkdir(exist_ok=True)
            (d / "estados" / "saldo-cierre.json").write_text(json.dumps(ahora))
            print(tabla_saldo(json.loads(ini.read_text()) if ini.exists() else None, ahora))
            print("\nRegistra lo aprendido en este video: vox.py aprender \"...\" [--espacio E]")
        elif a.cmd == "aprender":
            destino = archivo_aprendizajes(a.espacio)
            if not destino.exists():
                destino.write_text(f"# Aprendizajes · {a.espacio}\n\n", encoding="utf-8")
            with destino.open("a", encoding="utf-8") as fh:
                fh.write(f"- {time.strftime('%Y-%m-%d')} · {' '.join(a.texto.split())}\n")
            print(f"Aprendizaje guardado en {destino}")
        elif a.cmd == "aprendizajes":
            print(leer_aprendizajes(a.espacio))
    except ErrorVox as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except (KeyError, ValueError, OSError, IndexError, TypeError) as exc:
        print(f"Error: dato inesperado ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
