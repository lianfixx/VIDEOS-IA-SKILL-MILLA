"""Montaje: valida el plan de edición y lo convierte en una composición de HyperFrames.

El plan (plan.json) son datos: qué pieza, anclada a qué palabra, por qué. El movimiento vive en
plantilla/editor.js. Aquí se resuelven los tiempos, se comprueban las reglas y se escribe el HTML.
"""
from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

from comun import FORMATOS, SEGURA, ZONAS_APP, ErrorEditor
from corte import fin_de_frase, normal

# tipo: (nivel mínimo, zona por defecto, descripción)
PIEZAS = {
    "titulo": (1, "arriba", "frase corta en un punto clave"),
    "rotulo": (1, "torso", "nombre y cargo de quien habla, o etiqueta de sección"),
    "fuente": (1, "torso", "de dónde sale un dato"),
    "foto": (1, "pantalla", "foto, captura o documento real a pantalla completa"),
    "cierre": (1, "medio", "llamado final"),
    "zoom": (2, "", "acercamiento suave a la cara en una palabra clave"),
    "sello": (2, "arriba", "remate corto en diagonal"),
    "dato": (2, "arriba", "una cifra con su etiqueta y su fuente"),
    "barra": (2, "", "barra de avance para listas y tutoriales"),
    "panel": (2, "", "la cámara se hace tarjeta y deja sitio a una lista o una imagen"),
    "barrido": (2, "", "transición entre secciones"),
    "detras": (3, "", "palabra grande detrás de quien habla"),
    "inserto": (3, "pantalla", "animación o B-roll a pantalla completa"),
    "sticker": (3, "", "animación recortada en una esquina"),
    "particulas": (3, "", "estallido breve en un remate"),
}
SIN_CARA = {"zoom", "barra", "barrido", "detras", "particulas", "panel", "foto", "inserto"}   # no se comprueban contra el rostro
# Zonas base por formato. `arriba` y `torso` se ajustan a la cara de cada tramo (ver zonas_libres);
# los subtítulos tienen su propia franja y ninguna pieza de texto la pisa.
ZONAS = {
    "9:16": {"arriba": (90, 240, 960, 520), "medio": (90, 560, 960, 900), "torso": (90, 930, 960, 1214),
             "pecho": (90, 1230, 960, 1400), "abajo": (90, 1290, 960, 1440), "pantalla": (0, 0, 1080, 1920)},
    "16:9": {"arriba": (160, 60, 1760, 250), "medio": (160, 300, 1760, 560), "torso": (160, 600, 1760, 840),
             "pecho": (160, 860, 1760, 1010), "abajo": (160, 880, 1760, 1026), "pantalla": (0, 0, 1920, 1080)},
    "1:1": {"arriba": (70, 60, 1010, 250), "medio": (70, 300, 1010, 560), "torso": (70, 590, 1010, 800),
            "pecho": (70, 820, 1010, 980), "abajo": (70, 850, 1010, 1010), "pantalla": (0, 0, 1080, 1080)},
}
ZONAS_SUB = ("pecho", "abajo")
ALTO_MINIMO = 110        # px: una zona más baja que esto no aloja una línea legible
ALTO_PIEZA = {"titulo": 110, "rotulo": 130, "fuente": 70, "sello": 120, "dato": 124, "cierre": 120}
LIMITES = {"titulo": 42, "rotulo": 34, "fuente": 60, "sello": 14, "cierre": 22, "detras": 12}
SUB_MODOS = ("karaoke", "frase", "ninguno")
SUB_ESTILOS = ("contorno", "caja", "sobrio")
ESQUINAS = ("abajo-izq", "abajo-der", "arriba-izq", "arriba-der")
ID_VALIDO = re.compile(r"[a-z][a-z0-9_-]{0,30}")
IDS_RESERVADOS = {"root", "fondo", "camwrap", "cam", "base", "detras", "insertos", "graficos", "subs"}
TEXTO_EN_ZONA = ("titulo", "rotulo", "fuente", "sello", "dato", "cierre")
ORIGENES_INSERTO = ("propio", "codigo-pizarra", "codigo-vox", "generado")
QUIETO = {1: 9.0, 2: 5.0, 3: 3.5}      # segundos sin nada nuevo en pantalla antes de avisar
ANCHO_LETRA = {"Anton": 0.47, "Gelasio": 0.62, "Inter": 0.6}
ANCHO_MAYUS = {"Anton": 0.50, "Gelasio": 0.80, "Inter": 0.68}     # en mayúsculas cada letra ocupa más
ORDEN_DENSIDAD = ["ninguna", "minima", "media", "alta"]
MAX_ITEM = 32                # letras por renglón de un panel
LETRA_MINIMA = 34            # px en 1080 de ancho: menos que esto no se lee en un teléfono    # em promedio por carácter, medido al alza
PANEL_CAM = {"9:16": (90, 830, 990, 1440), "16:9": (1010, 90, 1830, 990), "1:1": (70, 540, 1010, 1010)}
PANEL_CAJA = {"9:16": (90, 250, 990, 790), "16:9": (90, 90, 960, 990), "1:1": (70, 70, 1010, 520)}


# ---------- tiempos ----------

def resolver_ancla(ancla, palabras: list[dict], aproximado: bool = False) -> float:
    if isinstance(ancla, (int, float)) and not isinstance(ancla, bool):
        return float(ancla)
    if not isinstance(ancla, dict):
        raise ErrorEditor(f"ancla ilegible: {ancla!r}")
    try:
        desfase, n = float(ancla.get("desfase", 0)), int(ancla.get("n", 1))
        if "t" in ancla:
            return float(ancla["t"]) + desfase
    except (TypeError, ValueError) as exc:
        raise ErrorEditor(f"ancla con un número ilegible: {ancla!r}") from exc
    if "palabra" not in ancla:
        raise ErrorEditor(f"un ancla necesita «palabra» o «t»: {ancla!r}")
    if aproximado:
        raise ErrorEditor("la transcripción es aproximada (viene de SRT o frases): ancla por segundo con {\"t\": ...}")
    buscada, vistas = normal(str(ancla["palabra"])), 0
    for p in palabras:
        if normal(p["txt"]) == buscada:
            vistas += 1
            if vistas == n:
                base = p["t1"] if ancla.get("al_final") else p["t0"]
                return round(base + desfase, 3)
    raise ErrorEditor(f"la palabra «{ancla['palabra']}» (aparición {n}) no está en el video cortado; "
                      "revisa cómo quedó escrita en palabras_limpio.json")


def resolver(plan: dict, palabras: list[dict], duracion: float, aproximado: bool = False) -> list[dict]:
    """Cada pieza con su inicio y su fin en segundos del video cortado."""
    out = []
    for k, p in enumerate(plan.get("piezas", [])):
        if not isinstance(p, dict):
            raise ErrorEditor(f"la pieza {k + 1} no es un objeto")
        q = dict(p)
        q["id"] = str(q.get("id") or f"p{k + 1}")
        t0 = resolver_ancla(p.get("ancla", {}), palabras, aproximado) if p.get("tipo") != "barra" or "ancla" in p else 0.0
        if "hasta" in p:
            t1 = resolver_ancla(p["hasta"], palabras, aproximado)
        elif p.get("tipo") == "barra" and "dura" not in p:
            t1 = duracion
        else:
            try:
                t1 = t0 + float(p.get("dura", {"zoom": 1.6, "sello": 1.4, "barrido": 0.5, "particulas": 1.2}.get(p.get("tipo"), 2.4)))
            except (TypeError, ValueError) as exc:
                raise ErrorEditor(f"{q['id']}: `dura` debe ser un número de segundos") from exc
        if not (math.isfinite(t0) and math.isfinite(t1)):
            raise ErrorEditor(f"{q['id']}: su tiempo no es un número válido")
        if t1 <= t0:
            raise ErrorEditor(f"{q['id']}: termina antes de empezar (revisa `hasta` o `dura`)")
        q["t0"], q["t1"] = round(max(0.0, t0), 3), round(min(duracion, t1), 3)
        out.append(q)
    return out


def nivel_en(plan: dict, t: float) -> int:
    for tr in plan.get("tramos", []) or []:
        if tr["de"] <= t < tr["a"]:
            return int(tr["nivel"])
    return int(plan.get("nivel") or 0)


def revisar_forma(plan: dict) -> list[str]:
    """Tipos de los campos del plan: un dato mal escrito debe decirse aquí, no tronar a medio render."""
    err = []
    if not isinstance(plan.get("piezas", []), list):
        err.append("`piezas` debe ser una lista")
    for k, tr in enumerate(plan.get("tramos") or []):
        ok = (isinstance(tr, dict) and all(isinstance(tr.get(c), (int, float)) and not isinstance(tr.get(c), bool) for c in ("de", "a"))
              and tr.get("nivel") in (1, 2, 3) and tr["de"] < tr["a"])
        if not ok:
            err.append(f"tramo {k + 1}: lleva `de` y `a` en segundos (de < a) y `nivel` 1, 2 o 3")
    sub = plan.get("subtitulos") or {}
    if not isinstance(sub, dict):
        return err + ["`subtitulos` debe ser un objeto"]
    for campo in ("max_palabras", "max_caracteres", "tamano"):
        if campo in sub and (not isinstance(sub[campo], (int, float)) or isinstance(sub[campo], bool) or sub[campo] <= 0):
            err.append(f"subtitulos.{campo} debe ser un número mayor que cero")
    for k, v in enumerate(sub.get("ocultar") or []):
        if not (isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v) and v[0] < v[1]):
            err.append(f"subtitulos.ocultar[{k}] debe ser [inicio, fin] en segundos")
    for k, p in enumerate(plan.get("piezas") or []):
        if isinstance(p, dict):
            for campo in ("texto", "sub", "pie", "titulo", "etiqueta", "fuente", "porque"):
                if campo in p and not isinstance(p[campo], str):
                    err.append(f"pieza {p.get('id', k + 1)}: `{campo}` debe ser texto")
            if "items" in p and not (isinstance(p["items"], list) and all(isinstance(x, str) for x in p["items"])):
                err.append(f"pieza {p.get('id', k + 1)}: `items` debe ser una lista de textos")
    for k, e in enumerate(((plan.get("sonido") or {}).get("efectos")) or []):
        if not isinstance(e, dict):
            err.append(f"efecto {k + 1}: debe ser un objeto")
        elif "db" in e and (not isinstance(e["db"], (int, float)) or isinstance(e["db"], bool)):
            err.append(f"efecto {k + 1}: `db` debe ser un número (cuántos dB bajo la voz)")
    return err


# ---------- geometría ----------

def choca(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def rostro_en(rostro: dict | None, t0: float, t1: float):
    """Caja que une todos los rostros vistos en ese tramo (con medio segundo de margen)."""
    if not rostro or not rostro.get("cajas"):
        return None
    cajas = [c for c in rostro["cajas"] if t0 - 0.6 <= c["t"] <= t1 + 0.6] or rostro["cajas"]
    return (min(c["x0"] for c in cajas), min(c["y0"] for c in cajas), max(c["x1"] for c in cajas), max(c["y1"] for c in cajas))


def luminancia(hexa: str) -> float:
    h = hexa.lstrip("#")
    if len(h) != 6:
        return 0.5
    canales = []
    for k in (0, 2, 4):
        c = int(h[k:k + 2], 16) / 255
        canales.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canales[0] + 0.7152 * canales[1] + 0.0722 * canales[2]


def contraste(a: str, b: str) -> float:
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def mejor_sobre(fondo: str, candidatos: list[str]) -> str:
    """De los colores de la marca, el que más contrasta con ese fondo."""
    return max(candidatos, key=lambda c: contraste(c, fondo))


def tamano_texto(texto: str, fuente: str, ancho: int, base: int, minimo: int, lineas: int = 1, mayusculas: bool = False) -> int:
    """Tamaño de letra para que el texto quepa en `ancho`, sin medir en el navegador."""
    largo = max(len(x) for x in _lineas(texto, lineas)) or 1
    factor = (ANCHO_MAYUS if mayusculas else ANCHO_LETRA).get(fuente, 0.68 if mayusculas else 0.6)
    return int(max(minimo, min(base, ancho / (largo * factor))))


def tam_titulo(texto: str, fuente: str, caja, W: int, mayus: bool = True) -> tuple[int, int]:
    """(tamaño, líneas) de un título en su caja: una línea si cabe a buen tamaño; si no, dos.
    Va en mayúsculas salvo en los espacios de movimiento sobrio, que lo llevan en altas y bajas."""
    ancho, alto = int((caja[2] - caja[0]) * 0.9), caja[3] - caja[1]
    uno = min(tamano_texto(texto, fuente, ancho, int(W * 0.115), 1, 1, mayus), int((alto - 40) / 1.25))
    if uno >= 60 or alto < 200:
        return uno, 1
    dos = min(tamano_texto(texto, fuente, ancho, int(W * 0.115), 1, 2, mayus), int((alto - 40) / 2.5))
    return (dos, 2) if dos > uno else (uno, 1)


def _lineas(texto: str, maximo: int) -> list[str]:
    limpio = texto.replace("*", "")
    if maximo <= 1 or len(limpio) <= 16:
        return [limpio]
    palabras, mitad = limpio.split(), len(limpio) / maximo
    out, actual = [], ""
    for w in palabras:
        if actual and len(actual) + len(w) + 1 > mitad * 1.15 and len(out) < maximo - 1:
            out.append(actual)
            actual = w
        else:
            actual = (actual + " " + w).strip()
    return out + [actual]


def zonas_libres(formato: str, cara, caja_sub) -> dict:
    """Zonas donde cabe texto en ese tramo: sobre la cara, entre la cara y los subtítulos, o al centro si no hay cara."""
    base, out = ZONAS[formato], {}
    x0, y0, x1, y1 = base["arriba"]
    tope = min(y1, cara[1] - 12) if cara else y1
    if tope - y0 >= ALTO_MINIMO:
        out["arriba"] = (x0, y0, x1, int(tope))
    x0, y0, x1, y1 = base["torso"]
    piso = min(y1, caja_sub[1] - 16) if caja_sub else y1
    inicio = max(y0, cara[3] + 12) if cara else y0
    if piso - inicio >= ALTO_MINIMO:
        out["torso"] = (x0, int(inicio), x1, int(piso))
    if not cara or not choca(base["medio"], cara):
        out["medio"] = base["medio"]
    return out


def caja_de_esquina(formato: str, esquina: str, caja_sub) -> tuple:
    """Caja de un sticker en una esquina de la zona segura, siempre por encima de los subtítulos."""
    W, H = FORMATOS[formato]
    x0, y0, x1, y1 = SEGURA[formato]
    lado = int(min(W, H) * 0.28)
    piso = (caja_sub[1] - 16) if caja_sub else y1
    x = x0 if esquina.endswith("izq") else x1 - lado
    y = y0 + 10 if esquina.startswith("arriba") else piso - lado
    return (x, int(y), x + lado, int(y) + lado)


def agrandar(caja, z: float):
    """La cara, como se ve durante un zoom de factor z hacia su centro."""
    cx, cy = (caja[0] + caja[2]) / 2, (caja[1] + caja[3]) / 2
    return (cx + (caja[0] - cx) * z, cy + (caja[1] - cy) * z, cx + (caja[2] - cx) * z, cy + (caja[3] - cy) * z)


def elegir_zona(pieza: dict, formato: str, cara, ocupadas: list[tuple], caja_sub=None) -> tuple[str, tuple | None]:
    preferida = pieza.get("zona") or PIEZAS[pieza["tipo"]][1]
    if preferida in ("pantalla", ""):
        return preferida, ZONAS[formato].get(preferida)
    libres = zonas_libres(formato, cara, caja_sub)
    for z in [preferida] + [z for z in ("arriba", "torso", "medio") if z != preferida]:
        if z not in libres or libres[z][3] - libres[z][1] < ALTO_PIEZA.get(pieza["tipo"], ALTO_MINIMO):
            continue
        if any(z == oz and pieza["t0"] < ot1 and ot0 < pieza["t1"] for oz, ot0, ot1 in ocupadas):
            continue
        return z, libres[z]
    return "", None


# ---------- subtítulos ----------

def grupos_de_subtitulos(palabras: list[dict], cfg: dict, censura: list[dict] | None = None) -> list[dict]:
    """Agrupa palabras: corta en pausa, en punto o al llegar al máximo. Un grupo a la vez en pantalla."""
    if cfg.get("modo") == "ninguno":
        return []
    max_p = int(cfg.get("max_palabras", 3))
    max_c = int(cfg.get("max_caracteres", 18 if cfg.get("mayusculas") else 26))
    tapadas = {c["i"] for c in (censura or []) if c.get("accion") == "tapar"}
    ocultar = cfg.get("ocultar") or []
    grupos, actual = [], []

    def cerrar():
        if actual:
            grupos.append({"t0": actual[0]["t0"], "t1": actual[-1]["t1"], "palabras": list(actual)})
            actual.clear()

    for i, p in enumerate(palabras):
        if any(a <= p["t0"] < b for a, b in ocultar):
            cerrar()
            continue
        # se quitan los signos, pero el punto y la coma entre cifras se quedan: «3.5%» no puede salir «35%»
        txt = re.sub(r"(?<!\d)[.,]|[.,](?!\d)|[¿¡?!;:\"“”]", "", p["txt"]) if cfg.get("sin_signos", True) else p["txt"]
        if p.get("i_crudo", p.get("i", i)) in tapadas:
            txt = txt[:1] + "*" * max(2, len(txt) - 1)
        if cfg.get("mayusculas"):
            txt = txt.upper()
        if not txt:
            continue
        largo = sum(len(w["txt"]) + 1 for w in actual) + len(txt)
        if actual and (len(actual) >= max_p or largo > max_c):
            cerrar()
        actual.append({"t0": p["t0"], "t1": p["t1"], "txt": txt})
        sig = palabras[i + 1] if i + 1 < len(palabras) else None
        if sig is None or sig["t0"] - p["t1"] >= 0.25 or fin_de_frase(p["txt"]):
            cerrar()
    cerrar()
    for g, sig in zip(grupos, grupos[1:] + [None]):       # el grupo dura hasta que entra el siguiente, sin pasar de 0.6 s
        tope = sig["t0"] if sig else g["t1"] + 0.4
        g["encadenado"] = bool(sig and sig["t0"] - g["t1"] < 0.25)
        g["t1"] = round(min(tope, g["t1"] + 0.6), 3)
        g["t0"] = round(g["t0"], 3)
    return grupos


# ---------- validación ----------

def validar(plan: dict, brief: dict, perfil: dict, palabras: list[dict], duracion: float, rostro: dict | None,
            empalmes: list[float], archivos: set[str], fps: int = 30, aproximado: bool = False) -> tuple[list[str], list[str], list[dict]]:
    """Devuelve (errores, avisos, piezas resueltas). Con errores no se arma."""
    err, avi = [], []
    formato = plan.get("formato", "9:16")
    if formato not in FORMATOS:
        return [f"formato desconocido: {formato}"], [], []
    if plan.get("espacio") != perfil["espacio"]:
        err.append(f"el plan dice espacio «{plan.get('espacio')}» y la producción es de «{perfil['espacio']}»")
    forma = revisar_forma(plan)
    if forma:
        return err + forma, avi, []
    if plan.get("paleta"):
        pal = (perfil.get("paletas") or {}).get(plan["paleta"])
        if not pal:
            err.append(f"paleta «{plan['paleta']}» no existe en espacios/{perfil['espacio']}/paletas.json; "
                       f"hay: {', '.join(perfil.get('paletas') or {}) or 'ninguna'}")
        elif not str(pal.get("aprobada_por_emi", "")).strip():
            err.append(f"la paleta «{plan['paleta']}» no tiene `aprobada_por_emi`: una combinación de colores la decide Emi")
        elif sorted(pal.get("colores", {})) != ["acento", "apoyo", "papel", "tinta"] or not all(
                re.fullmatch(r"#[0-9A-Fa-f]{6}", str(v)) for v in pal["colores"].values()):
            err.append(f"la paleta «{plan['paleta']}» debe traer papel, tinta, acento y apoyo en hexadecimal (#RRGGBB)")
    nivel = plan.get("nivel")
    if nivel not in (1, 2, 3) or isinstance(nivel, bool):
        err.append("falta `nivel` (1, 2 o 3, como número): se le explican los tres a Emi y elige")
        nivel = None
    ed = perfil["edicion"]
    # el tope del espacio se cumple, no solo se sugiere
    tope_nivel = int(ed.get("nivel_tope", 3))
    mas_alto = max([nivel or 0] + [tr["nivel"] for tr in plan.get("tramos") or []])
    if mas_alto > tope_nivel and len(str(plan.get("sobre_tope_pedido_por_emi", "")).strip()) < 8:
        err.append(f"el espacio «{perfil['espacio']}» no pasa de nivel {tope_nivel} y el plan usa nivel {mas_alto}: "
                   "solo si Emi lo pidió, con sus palabras en `sobre_tope_pedido_por_emi`")
    # lo que Emi respondió
    resp = brief.get("respuestas_emi") or {}
    for clave in ("para_que", "a_quien", "postura", "tipo_de_video", "donde_se_publica", "nivel_elegido", "musica", "quienes_salen"):
        if not str(resp.get(clave, "")).strip():
            err.append(f"brief.json: falta la respuesta de Emi a «{clave}»; sin entrevista no se edita")
    quienes = str(resp.get("quienes_salen", "")).strip().lower()
    solo_emi = quienes in ("emi", "yo", "solo emi", "solo yo", "emiliano", "emi solo")
    if quienes and not solo_emi and len(str(resp.get("permiso_de_quienes_salen", "")).strip()) < 3:
        err.append("brief.json: sale a cuadro alguien más que Emi y falta `permiso_de_quienes_salen` (quién dio permiso y cómo consta)")
    if resp.get("nivel_elegido") and nivel and str(resp["nivel_elegido"]).strip()[:1] != str(nivel) and not plan.get("tramos"):
        err.append(f"Emi eligió nivel {resp['nivel_elegido']} y el plan dice {nivel}")
    if not str(plan.get("nivel_razon", "")).strip():
        err.append("falta `nivel_razon`: por qué ese nivel para este video")
    # subtítulos
    sub = plan.get("subtitulos") or {}
    if sub.get("modo") not in SUB_MODOS:
        err.append(f"subtitulos.modo debe ser uno de {SUB_MODOS}")
    if len(str(sub.get("razon", "")).strip()) < 12:
        err.append("falta `subtitulos.razon`: el estilo de subtítulos se razona según el espacio, el contexto y el tipo de video")
    if sub.get("modo") == "karaoke" and aproximado:
        err.append("subtítulos palabra por palabra con una transcripción aproximada: usa `frase` o transcribe con tiempo por palabra")
    try:
        piezas = resolver(plan, palabras, duracion, aproximado)
    except ErrorEditor as exc:
        return err + [str(exc)], avi, []
    zona_sub = {**(perfil["edicion"].get("subtitulos") or {}), **sub}.get("zona", "pecho")
    if zona_sub not in ZONAS_SUB:
        err.append(f"subtitulos.zona debe ser una de {ZONAS_SUB}")
        zona_sub = "pecho"
    caja_sub = None if sub.get("modo") == "ninguno" else ZONAS[formato][zona_sub]
    if rostro is None:
        avi.append("no hay mapa de rostro (`rostro`): no se puede comprobar que nada tape la cara")
    if sub.get("estilo", "contorno") not in SUB_ESTILOS:
        err.append(f"subtitulos.estilo debe ser uno de {SUB_ESTILOS}")
    cara_global = rostro_en(rostro, 0, duracion)
    if caja_sub and cara_global and choca(caja_sub, cara_global):
        otra = "abajo" if zona_sub == "pecho" else "pecho"
        if not choca(ZONAS[formato][otra], cara_global):
            avi.append(f"los subtítulos en «{zona_sub}» taparían la cara en algún momento: usa subtitulos.zona «{otra}»")
        else:
            avi.append("la franja de subtítulos se encima con la cara (encuadre muy bajo o muy cerrado): míralo en la muestra; "
                       "quizá convenga `frase` más chica o regrabar con más aire abajo")
    todos_los_zooms = []
    for q in piezas:
        if q.get("tipo") == "zoom":
            try:
                todos_los_zooms.append((q["t0"], q["t1"], float(q.get("z", 1.1))))
            except (TypeError, ValueError):
                pass
    ids, ocupadas, zooms, generados = set(), [], [], 0
    for p in piezas:
        ident, tipo = p["id"], p.get("tipo")
        if ident in ids:
            err.append(f"{ident}: id repetido")
        ids.add(ident)
        if not ID_VALIDO.fullmatch(ident) or ident in IDS_RESERVADOS or re.fullmatch(r"g\d+.*|rc.*", ident):
            err.append(f"«{ident}»: id inválido o reservado. Usa minúsculas, números y guiones, empezando por letra (y no g1…, rc…, cam, subs…)")
            continue
        if any(o != ident and o.startswith(ident) and re.fullmatch(r"(i\d+|k\d+|v)", o[len(ident):]) for o in (q["id"] for q in piezas)):
            err.append(f"«{ident}»: choca con los nombres internos de otra pieza; cámbialo")
        if tipo not in PIEZAS:
            err.append(f"{ident}: tipo desconocido «{tipo}». Existen: {', '.join(PIEZAS)}")
            continue
        if len(str(p.get("porque", "")).strip()) < 10:
            err.append(f"{ident} ({tipo}): falta `porque`. Cada pieza dice algo de lo que se oye en ese segundo; si no, sobra")
        if p["t1"] - p["t0"] < 0.3:
            err.append(f"{ident} ({tipo}): dura {p['t1'] - p['t0']:.2f} s; no alcanza a verse")
        if p["t0"] >= duracion:
            err.append(f"{ident} ({tipo}): empieza después de que termina el video")
        minimo = PIEZAS[tipo][0]
        if tipo == "foto" and p.get("modo") == "tarjeta":
            minimo = 2
        if tipo == "barrido" and not any(abs((p["t0"] + p["t1"]) / 2 - e) <= 3 / fps for e in empalmes):
            err.append(f"{ident} (barrido): un barrido tapa un corte; su centro debe caer en un empalme "
                       f"({', '.join(f'{e:.2f}' for e in empalmes[:8]) or 'no hay ninguno'}). A media frase solo estorba")
        if tipo == "detras" and rostro_en(rostro, p["t0"], p["t1"]):
            c = rostro_en(rostro, p["t0"], p["t1"])
            ancho_texto = min(FORMATOS[formato][0] * 0.84, len(str(p.get("texto", ""))) * ANCHO_MAYUS.get(ed.get("fuente_titular", "Anton"), 0.6) * FORMATOS[formato][0] * 0.34)
            if ancho_texto and (c[2] - c[0]) / ancho_texto > 0.6:
                avi.append(f"{ident} (detras): la cabeza taparía más de la mitad de «{p.get('texto')}»; con este encuadre no se leerá. "
                           "Mira la muestra, usa una palabra más larga o un `titulo`")
        nv = nivel_en(plan, p["t0"])
        if nv and minimo > nv:
            err.append(f"{ident}: «{tipo}» es de nivel {minimo} y ese tramo es nivel {nv}. Súbelo con `tramos` o quita la pieza")
        texto = str(p.get("texto", ""))
        if tipo in LIMITES and len(texto.replace("*", "")) > LIMITES[tipo]:
            err.append(f"{ident} ({tipo}): «{texto}» pasa de {LIMITES[tipo]} caracteres")
        if tipo in ("titulo", "rotulo", "fuente", "sello", "cierre", "detras") and not texto.strip():
            err.append(f"{ident} ({tipo}): falta `texto`")
        if tipo == "dato":
            if not str(p.get("cifra", "")).strip() or not str(p.get("fuente", "")).strip():
                err.append(f"{ident} (dato): una cifra en pantalla lleva `cifra` y `fuente`; un dato sin fuente no se publica")
        if tipo in ("foto", "inserto", "sticker"):
            arch = str(p.get("archivo", ""))
            if not arch or ".." in arch or arch.startswith("/"):
                err.append(f"{ident} ({tipo}): `archivo` debe ser un nombre dentro de assets/")
            elif arch not in archivos:
                err.append(f"{ident} ({tipo}): no existe assets/{arch}")
            if not str(p.get("origen_descripcion" if tipo == "foto" else "origen", "")).strip():
                err.append(f"{ident} ({tipo}): falta decir de dónde salió (`origen_descripcion` en foto; `origen` en inserto y sticker)")
        if tipo in ("inserto", "sticker"):
            if p.get("origen") not in ORIGENES_INSERTO:
                err.append(f"{ident}: origen debe ser uno de {ORIGENES_INSERTO}")
            if p.get("origen") == "generado":
                generados += 1
                if not p.get("autorizado_por_emi") or p.get("costo_creditos") is None:
                    err.append(f"{ident}: video generado sin `autorizado_por_emi` y `costo_creditos`: se cotiza y Emi lo aprueba antes")
        if tipo == "foto" and p.get("modo", "pantalla") not in ("pantalla", "tarjeta"):
            err.append(f"{ident} (foto): modo debe ser «pantalla» o «tarjeta»")
        if tipo == "zoom" and p.get("modo", "punch") not in ("punch", "push"):
            err.append(f"{ident} (zoom): modo debe ser «punch» o «push»")
        if tipo == "sticker":
            esquina = p.get("esquina", "abajo-izq")
            if esquina not in ESQUINAS:
                err.append(f"{ident} (sticker): esquina debe ser una de {ESQUINAS}")
            else:
                cara = rostro_en(rostro, p["t0"], p["t1"])
                caja = caja_de_esquina(formato, esquina, caja_sub)
                if cara and choca(caja, cara):
                    libres = [e for e in ESQUINAS if not choca(caja_de_esquina(formato, e, caja_sub), cara)]
                    err.append(f"{ident} (sticker): en «{esquina}» tapa la cara" + (f"; libres: {', '.join(libres)}" if libres else "; no hay esquina libre en ese tramo"))
                p["esquina"], p["caja"] = esquina, list(caja)
        if tipo == "zoom":
            try:
                z = float(p.get("z", 1.1))
            except (TypeError, ValueError):
                err.append(f"{ident} (zoom): z debe ser un número")
                continue
            if not 1.04 <= z <= 1.2:
                err.append(f"{ident} (zoom): z={z}; los zooms son suaves, entre 1.04 y 1.20")
            for e in empalmes:
                if abs(p["t0"] - e) < 4 / fps:
                    err.append(f"{ident} (zoom): arranca en el mismo cuadro de un corte ({e:.2f} s); recórrelo 4 cuadros")
            for a, b in zooms:
                if p["t0"] < b + 0.4 and a < p["t1"]:
                    err.append(f"{ident} (zoom): se encima con otro zoom o le pisa los talones")
            zooms.append((p["t0"], p["t1"]))
        if tipo == "detras" and f"recorte-{ident}.webm" not in archivos:
            err.append(f"{ident} (detras): falta assets/recorte-{ident}.webm; córrelo con `recorte`")
        if tipo == "panel":
            if not (p.get("items") or p.get("imagen")):
                err.append(f"{ident} (panel): lleva `items` (hasta 4) o `imagen`")
            if len(p.get("items") or []) > 4:
                err.append(f"{ident} (panel): más de 4 renglones no se leen")
            for it in p.get("items") or []:
                if len(it.replace("*", "")) > MAX_ITEM:
                    err.append(f"{ident} (panel): «{it}» pasa de {MAX_ITEM} letras; un renglón de panel es una idea corta")
            if p.get("imagen") and p["imagen"] not in archivos:
                err.append(f"{ident} (panel): no existe assets/{p['imagen']}")
            for q in piezas:
                if q is p or not (q["t0"] < p["t1"] and p["t0"] < q["t1"]):
                    continue
                if q.get("tipo") == "zoom":
                    err.append(f"{ident} (panel): hay un zoom ({q['id']}) mientras la cámara es tarjeta")
                elif q.get("tipo") in ("titulo", "rotulo", "fuente", "sello", "dato", "cierre", "detras", "sticker", "panel"):
                    err.append(f"{ident} (panel): «{q['id']}» ({q['tipo']}) sigue en pantalla mientras la cámara es tarjeta; "
                               "el panel reacomoda todo: termina esa pieza antes o empieza el panel después")
        # zona y rostro
        if tipo == "foto" and p.get("modo") == "tarjeta":
            cara = rostro_en(rostro, p["t0"], p["t1"])
            libres = zonas_libres(formato, cara, caja_sub)
            caja = next((libres[z] for z in ("torso", "arriba", "medio") if z in libres and libres[z][3] - libres[z][1] >= 260), None)
            if caja is None:
                err.append(f"{ident} (foto en tarjeta): no cabe sin tapar la cara con este encuadre; usa `modo: pantalla`")
            else:
                p["caja"] = list(caja)
        if tipo not in SIN_CARA:
            if tipo == "sticker":
                continue                                # su caja ya se resolvió por esquina
            if p.get("zona") in ZONAS_SUB:
                err.append(f"{ident} ({tipo}): la zona «{p['zona']}» es de los subtítulos; usa arriba, torso o medio")
                continue
            if p.get("zona") and p["zona"] not in ("arriba", "torso", "medio"):
                err.append(f"{ident} ({tipo}): zona «{p['zona']}» no admitida para texto; usa arriba, torso o medio")
                continue
            cara = rostro_en(rostro, p["t0"], p["t1"])
            for a, b, z in todos_los_zooms:             # durante un zoom la cara ocupa más cuadro
                if cara and a < p["t1"] and p["t0"] < b:
                    cara = agrandar(cara, z + 0.012)
            zona, caja = elegir_zona(p, formato, cara, ocupadas, caja_sub)
            if not zona:
                err.append(f"{ident} ({tipo}): no hay zona libre que no tape la cara ni se encime con otra pieza en ese momento; "
                           "muévela de segundo, acórtala o usa una foto o un panel")
            else:
                if p.get("zona") and zona != p["zona"]:
                    avi.append(f"{ident} ({tipo}): pasó de «{p['zona']}» a «{zona}» para no tapar la cara ni encimarse")
                p["zona"], p["caja"] = zona, list(caja)
                ocupadas.append((zona, p["t0"], p["t1"]))
                if tipo == "titulo" and tam_titulo(str(p.get("texto", "")), ed.get("fuente_titular", "Anton"), caja, FORMATOS[formato][0],
                                                   ed.get("movimiento") != "sobrio")[0] < 46:
                    err.append(f"{ident} (titulo): «{p.get('texto')}» no cabe legible en la zona «{zona}» con este encuadre; acórtalo")
    # reglas de conjunto
    if not any(p.get("tipo") == "cierre" for p in piezas):
        avi.append("no hay pieza `cierre`: el último cuadro debería invitar a algo")
    if sum(1 for p in piezas if p.get("tipo") == "detras") > 2:
        err.append("más de dos textos detrás de la persona en un video: el recurso se gasta")
    if sum(1 for p in piezas if p.get("tipo") == "particulas") > max(1, int(duracion // 25)):
        avi.append("demasiadas partículas: como mucho una cada 25 s")
    if generados and not brief.get("gasto_autorizado"):
        err.append("hay video generado y brief.json no tiene `gasto_autorizado`")
    visibles = sorted(p["t0"] for p in piezas if p.get("tipo") not in ("barra",)) + [duracion]
    previo, tope = 0.0, QUIETO.get(nivel or 1, 9.0)
    for t in visibles:
        if t - previo > tope:
            avi.append(f"{previo:.1f}–{t:.1f} s: {t - previo:.1f} s sin nada nuevo en pantalla para un nivel {nivel}")
        previo = t
    if piezas and duracion / max(1, len([p for p in piezas if p.get('tipo') != 'barra'])) < 1.2:
        avi.append("más de una pieza cada 1.2 s: se satura; quita las que menos digan")
    # sonido
    son = plan.get("sonido") or {}
    mus = son.get("musica") or {}
    if mus.get("decision") not in ("ninguna", "archivo", "codigo"):
        err.append("sonido.musica.decision debe ser «ninguna», «codigo» (compuesta aquí, sin derechos de terceros) o «archivo» "
                   "(la pista se le pregunta a Emi en cada video)")
    if mus.get("decision") == "codigo":
        try:
            import sonido as SON
            animos = set(SON.ANIMOS)
        except ImportError:
            animos = {"tension", "energia", "serio", "ironia", "motivacion"}
        if mus.get("animo") not in animos:
            err.append(f"sonido.musica.animo debe ser uno de {sorted(animos)} para componer la pista")
    if mus.get("decision") == "archivo" and (mus.get("archivo") not in archivos or not str(mus.get("origen", "")).strip()):
        err.append("sonido.musica: falta el archivo en assets/ o su `origen` (de dónde salió y con qué derecho se usa)")
    if mus.get("decision") == "archivo" and str(mus.get("archivo", "")).lower().rsplit(".", 1)[-1] not in ("mp3", "wav", "m4a", "aac", "flac", "ogg"):
        err.append("sonido.musica.archivo debe ser un archivo de audio (mp3, wav, m4a, aac, flac u ogg)")
    if mus.get("preguntado_a_emi") is not True:
        err.append("sonido.musica.preguntado_a_emi debe ser true: la música se le pregunta a Emi en cada video, con una sugerencia")
    del_espacio = (ed.get("sonido") or {}).get("densidad", "media")
    pedida = son.get("densidad", "minima")
    if (pedida in ORDEN_DENSIDAD and del_espacio in ORDEN_DENSIDAD and ORDEN_DENSIDAD.index(pedida) > ORDEN_DENSIDAD.index(del_espacio)
            and len(str(son.get("densidad_pedida_por_emi", "")).strip()) < 8):
        err.append(f"sonido.densidad «{pedida}» pasa de la del espacio «{perfil['espacio']}» («{del_espacio}»): "
                   "solo si Emi lo pidió, con sus palabras en `sonido.densidad_pedida_por_emi`")
    if del_espacio == "ninguna" and (son.get("efectos") or []) and len(str(son.get("densidad_pedida_por_emi", "")).strip()) < 8:
        err.append(f"el espacio «{perfil['espacio']}» no lleva efectos de sonido y el plan trae {len(son['efectos'])}")
    efectos = son.get("efectos") or []
    tope_efectos = {"ninguna": 0, "minima": duracion / 10, "media": duracion / 4, "alta": duracion / 2}.get(son.get("densidad", "minima"))
    if tope_efectos is None:
        err.append("sonido.densidad debe ser ninguna, minima, media o alta")
    elif len(efectos) > tope_efectos + 1:
        avi.append(f"{len(efectos)} efectos de sonido para densidad «{son.get('densidad')}»: sobran")
    from audio import EFECTOS
    seguidos = 0
    for k, e in enumerate(efectos):
        if e.get("sonido") not in EFECTOS:
            err.append(f"efecto {k + 1}: «{e.get('sonido')}» no existe. Hay: {', '.join(EFECTOS)}")
        if "en" in e and e["en"] not in ids:
            err.append(f"efecto {k + 1}: la pieza «{e['en']}» no existe")
        if "en" not in e and not isinstance(e.get("t"), (int, float)):
            err.append(f"efecto {k + 1}: lleva `en` (id de una pieza) o `t` (segundos)")
        seguidos = seguidos + 1 if k and e.get("sonido") == efectos[k - 1].get("sonido") else 1
        if seguidos == 4:
            avi.append(f"«{e.get('sonido')}» suena cuatro veces seguidas: pierde la gracia")
    # marca
    if plan.get("marca_en_pantalla") and not perfil["edicion"].get("marca_en_pantalla"):
        err.append("marca_en_pantalla: el logo o el @ de este espacio aún no está definido por Emi")
    return err, avi, piezas


# ---------- HTML ----------

def _t(texto: str) -> str:
    """Texto seguro con *acento* convertido en resaltado."""
    return re.sub(r"\*([^*]+)\*", r'<b class="ac">\1</b>', html.escape(texto))


def _px(caja) -> str:
    return f"left:{caja[0]}px;top:{caja[1]}px;width:{caja[2] - caja[0]}px;height:{caja[3] - caja[1]}px"


def armar_html(plan: dict, piezas: list[dict], perfil: dict, grupos: list[dict], duracion: float, rostro: dict | None,
               censura: list[dict] | None = None) -> tuple[str, dict]:
    """Devuelve (index.html, datos que lee editor.js)."""
    formato = plan.get("formato", "9:16")
    W, H = FORMATOS[formato]
    ed, col = perfil["edicion"], perfil["colores"]
    if plan.get("paleta") and (perfil.get("paletas") or {}).get(plan["paleta"]):
        col = perfil["paletas"][plan["paleta"]]["colores"]           # paleta aprobada por Emi para una serie
    titular, texto = ed.get("fuente_titular", perfil.get("titular", "Anton")), ed.get("fuente_texto", "Inter")
    sub = {**(ed.get("subtitulos") or {}), **(plan.get("subtitulos") or {})}
    zonas = ZONAS[formato]
    zona_sub_html = sub.get("zona", "pecho") if sub.get("zona") in ZONAS_SUB else "pecho"
    caja_sub_html = zonas[zona_sub_html]
    cara = rostro_en(rostro, 0, duracion)
    foco = ((cara[0] + cara[2]) / 2, (cara[1] + cara[3]) / 2) if cara else (W / 2, H * 0.36)
    partes, datos_piezas = [], []
    detras_html, frente_html, insertos_html, recortes_html = [], [], [], []
    for p in piezas:
        tipo, ident = p["tipo"], p["id"]
        d = {"id": ident, "tipo": tipo, "t0": p["t0"], "t1": p["t1"]}
        caja = tuple(p["caja"]) if p.get("caja") else zonas.get(p.get("zona", ""), None)
        alto = (caja[3] - caja[1]) if caja else H
        zc = f"z-{p.get('zona', '')}"
        if tipo == "titulo":
            tam, n_lineas = tam_titulo(p["texto"], titular, caja, W, ed.get("movimiento") != "sobrio")
            lineas = _lineas(p["texto"], n_lineas)
            cuerpo = "<br>".join(_t(x) for x in _partir_marcado(p["texto"], lineas))
            frente_html.append(f'<div id="{ident}" class="pz titulo {zc}" style="{_px(caja)}"><div class="in" style="font-size:{tam}px">{cuerpo}</div></div>')
        elif tipo == "rotulo":
            tam = tamano_texto(p["texto"], titular, int((caja[2] - caja[0]) * 0.8), int(W * 0.06), 40, 1, titular == "Anton")
            subt = f'<div class="sub">{_t(p["sub"])}</div>' if p.get("sub") else ""
            frente_html.append(f'<div id="{ident}" class="pz rotulo {zc}" style="{_px(caja)}"><div class="in"><div class="barra"></div>'
                               f'<div class="tx" style="font-size:{tam}px">{_t(p["texto"])}</div>{subt}</div></div>')
        elif tipo == "fuente":
            frente_html.append(f'<div id="{ident}" class="pz fuente {zc}" style="{_px(caja)}"><div class="in">Fuente: {_t(p["texto"])}</div></div>')
        elif tipo == "sello":
            tam = min(tamano_texto(p["texto"], titular, int(W * 0.5), int(W * 0.085), 46, 1, True), int((alto - 50) / 1.4))
            frente_html.append(f'<div id="{ident}" class="pz sello {zc}" style="{_px(caja)}"><div class="in" style="font-size:{tam}px">{_t(p["texto"])}</div></div>')
        elif tipo == "dato":
            tam = min(tamano_texto(str(p["cifra"]), titular, int(W * 0.34), int(W * 0.16), 70), int(alto * 0.66))
            frente_html.append(f'<div id="{ident}" class="pz dato {zc}" style="{_px(caja)}"><div class="in"><div class="cifra" style="font-size:{tam}px">{_t(str(p["cifra"]))}</div>'
                               f'<div class="eti">{_t(p.get("etiqueta", ""))}</div><div class="fu">Fuente: {_t(p["fuente"])}</div></div></div>')
        elif tipo == "cierre":
            tam = min(tamano_texto(p["texto"], titular, int(W * 0.6), int(W * 0.11), 60, 1, True), int(alto * 0.56))
            frente_html.append(f'<div id="{ident}" class="pz cierre {zc}" style="{_px(caja)}"><div class="in" style="font-size:{tam}px"><span>{_t(p["texto"])}</span>'
                               f'<svg class="flecha" viewBox="0 0 60 90"><path d="M30 4v70M8 54l22 24 22-24" fill="none" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>')
        elif tipo == "foto":
            modo = p.get("modo", "pantalla")
            d["modo"] = modo
            cls = "foto pantalla" if modo == "pantalla" else "foto tarjeta"
            abajo = (H - caja_sub_html[1] + 16) if modo == "pantalla" else 0
            pie = f'<div class="pie" style="bottom:{abajo}px">{_t(p["pie"])}</div>' if p.get("pie") else ""
            lugar = f' style="{_px(tuple(p["caja"]))}"' if modo == "tarjeta" and p.get("caja") else ""
            insertos_html.append(f'<div id="{ident}" class="pz {cls}"{lugar}><div class="in"><img src="assets/{html.escape(p["archivo"])}" alt="">{pie}</div></div>')
        elif tipo == "inserto":
            insertos_html.append(f'<div id="{ident}" class="pz inserto"><div class="in"><video id="{ident}v" class="clip" src="assets/{html.escape(p["archivo"])}" '
                                 f'data-start="{p["t0"]}" data-duration="{round(p["t1"] - p["t0"], 3)}" data-track-index="{10 + len(insertos_html)}" muted playsinline></video></div></div>')
        elif tipo == "sticker":
            frente_html.append(f'<div id="{ident}" class="pz sticker" style="{_px(tuple(p["caja"]))}"><div class="in"><video id="{ident}v" class="clip" src="assets/{html.escape(p["archivo"])}" '
                               f'data-start="{p["t0"]}" data-duration="{round(p["t1"] - p["t0"], 3)}" data-track-index="{30 + len(frente_html)}" muted playsinline></video></div></div>')
        elif tipo == "detras":
            tam = tamano_texto(p["texto"], titular, int(W * 0.84), int(W * 0.34), 120, 1, True)
            # arranca dentro de la zona segura y la cabeza tapa entre un tercio y la mitad de la palabra
            y = max(SEGURA[formato][1], int((cara[1] if cara else H * 0.2) - tam * 0.45))
            detras_html.append(f'<div id="{ident}" class="pz detras" style="top:{y}px"><div class="in" style="font-size:{tam}px">{_t(p["texto"].upper())}</div></div>')
            recortes_html.append(f'<video id="rc{ident}" class="clip rec" src="assets/recorte-{ident}.webm" data-start="{p["t0"]}" '
                                 f'data-duration="{round(p["t1"] - p["t0"], 3)}" data-track-index="{50 + len(recortes_html)}" '
                                 f'data-layout-allow-occlusion muted playsinline></video>')
        elif tipo == "zoom":
            d.update({"z": float(p.get("z", 1.1)), "modo": p.get("modo", "punch")})
        elif tipo == "barra":
            frente_html.append(f'<div id="{ident}" class="pz barra"><div class="in"></div></div>')
        elif tipo == "barrido":
            frente_html.append(f'<div id="{ident}" class="pz barrido"><div class="in"></div></div>')
        elif tipo == "particulas":
            origen_y = int(min(H * 0.7, (cara[3] + 70) if cara else H * 0.55))      # bajo la cara: nunca estallan sobre ella
            puntos = "".join(f'<i id="{ident}k{n}"></i>' for n in range(18))
            frente_html.append(f'<div id="{ident}" class="pz particulas" style="left:{int(W / 2)}px;top:{origen_y}px">{puntos}</div>')
            d["n"] = 18
            d["caida"] = max(30, int(caja_sub_html[1] - origen_y - 40))        # nunca llegan a la franja de subtítulos
        elif tipo == "panel":
            cam, caja_p = PANEL_CAM[formato], PANEL_CAJA[formato]
            ancho_c, alto_c = cam[2] - cam[0], cam[3] - cam[1]
            s = max(ancho_c / W, alto_c / H, 0.62)
            x = min(cam[0], max(cam[2] - W * s, (cam[0] + cam[2]) / 2 - foco[0] * s))
            y = min(cam[1], max(cam[3] - H * s, (cam[1] + cam[3]) / 2 - foco[1] * s))
            d.update({"cam": {"s": round(s, 4), "x": round(x, 1), "y": round(y, 1),
                              "recorte": f"inset({cam[1]}px {W - cam[2]}px {H - cam[3]}px {cam[0]}px round 36px)"}})
            ancho_p, alto_p = caja_p[2] - caja_p[0], caja_p[3] - caja_p[1]
            n_items = len(p.get("items") or [])
            alto_cab = 0
            estilo_cab = ""
            if p.get("titulo"):
                t_cab = min(tamano_texto(p["titulo"], titular, ancho_p - 90, int(min(W, H) * 0.074), 40, 1, True), int(alto_p * 0.17))
                alto_cab = int(t_cab * 1.25)
                estilo_cab = f' style="font-size:{t_cab}px"'
            t_item = LETRA_MINIMA
            if n_items:
                # la letra más grande con la que cabecera y renglones caben; un renglón largo puede ocupar dos líneas
                libre, ancho_txt = alto_p - 68 - alto_cab - 20 * n_items, ancho_p - 80
                for f in range(int(min(W, H) * 0.052), LETRA_MINIMA - 1, -2):
                    lineas = sum(max(1, math.ceil(len(it.replace("*", "")) * ANCHO_LETRA.get(texto, 0.6) * f / (ancho_txt - 1.9 * f))) for it in p["items"])
                    if lineas * f * 1.14 <= libre:
                        t_item = f
                        break
            if p.get("imagen"):
                cuerpo = f'<img src="assets/{html.escape(p["imagen"])}" alt="">'
            else:
                cuerpo = "".join(f'<div class="item" id="{ident}i{n}"><span class="n">{n + 1}</span><span>{_t(it)}</span></div>' for n, it in enumerate(p.get("items", [])))
                d["items"] = len(p.get("items", []))
            cab = f'<div class="cab"{estilo_cab}>{_t(p["titulo"])}</div>' if p.get("titulo") else ""
            frente_html.append(f'<div id="{ident}" class="pz panel" style="{_px(caja_p)}"><div class="in" style="font-size:{t_item}px">{cab}{cuerpo}</div></div>')
        datos_piezas.append(d)
    # subtítulos
    zona_sub = sub.get("zona", "pecho") if sub.get("zona") in ZONAS_SUB else "pecho"
    caja_sub = zonas[zona_sub]
    f_sub = sub.get("fuente", perfil.get("subtitulos", titular))
    base_sub = int(sub.get("tamano", min(W, H) * (0.085 if sub.get("mayusculas") else 0.062)))
    # un solo tamaño para todo el video: que cambie de grupo a grupo se ve descuidado
    tam = min([base_sub] + [tamano_texto(" ".join(w["txt"] for w in g["palabras"]), f_sub, int((caja_sub[2] - caja_sub[0]) * 0.96), base_sub, 46,
                                         1, bool(sub.get("mayusculas"))) for g in grupos])
    subs_html, datos_grupos = [], []
    for k, g in enumerate(grupos):
        spans = " ".join(f'<span class="w" id="g{k}w{n}">{html.escape(w["txt"])}</span>' for n, w in enumerate(g["palabras"]))
        subs_html.append(f'<div class="grupo" id="g{k}" style="font-size:{tam}px">{spans}</div>')
        datos_grupos.append({"t0": g["t0"], "t1": g["t1"], "enc": g.get("encadenado", False),
                             "w": [[w["t0"], w["t1"]] for w in g["palabras"]]})
    fuentes_css = "\n".join(
        f"@font-face{{font-family:'{n}';src:url('assets/fonts/{a}') format('woff2');font-weight:{w};font-display:block}}"
        for n, a, w in (("Anton", "anton.woff2", 400), ("Gelasio", "gelasio-700.woff2", 700),
                        ("Inter", "inter-400.woff2", 400), ("Inter", "inter-700.woff2", 700)) if n in (titular, f_sub, texto))
    recorte = "".join(recortes_html)
    # sobre oscuro manda el acento de la marca; solo si no se lee (contraste menor de 4.5) entra el color de apoyo
    resalte = col["acento"] if contraste(col["acento"], "#151515") >= 4.5 else mejor_sobre("#151515", [col["acento"], col["apoyo"]])
    sobre_acento = mejor_sobre(col["acento"], [col["tinta"], col["papel"]])
    sobre_papel = mejor_sobre(col["papel"], [col["acento"], col["tinta"]]) if contraste(col["acento"], col["papel"]) >= 3 else col["tinta"]
    css = f""":root{{--papel:{col['papel']};--tinta:{col['tinta']};--acento:{col['acento']};--apoyo:{col['apoyo']};
--resalte:{resalte};--sobre-acento:{sobre_acento};--sobre-papel:{sobre_papel};
--titular:'{titular}';--texto:'{texto}';--subs:'{f_sub}';--W:{W}px;--H:{H}px}}
{fuentes_css}"""
    datos = {"duracion": duracion, "formato": formato, "W": W, "H": H, "foco": [round(foco[0], 1), round(foco[1], 1)],
             "movimiento": ed.get("movimiento", "suave"), "piezas": datos_piezas, "grupos": datos_grupos,
             "subs": {"modo": sub.get("modo", "karaoke"), "estilo": sub.get("estilo", "contorno") if sub.get("estilo") in SUB_ESTILOS else "contorno",
                      "color": col["papel"] if sub.get("estilo") == "caja" else "#ffffff", "activo": resalte},
             "detras": [p["id"] for p in piezas if p["tipo"] == "detras"]}
    pagina = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width={W}, height={H}">
<script src="lib/gsap.min.js"></script>
<style>
{css}
</style>
<link rel="stylesheet" href="editor.css">
</head>
<body>
<div id="root" class="mov-{html.escape(str(ed.get('movimiento', 'suave')))}" data-composition-id="main" data-start="0" data-duration="{duracion}" data-width="{W}" data-height="{H}">
  <div id="fondo"></div>
  <div id="camwrap"><div id="cam">
    <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{duracion}" data-track-index="0" muted playsinline></video>
    <div id="detras">{''.join(detras_html)}</div>
    {recorte}
  </div></div>
  <div id="insertos">{''.join(insertos_html)}</div>
  <div id="graficos" data-track-kind="graphics">{''.join(frente_html)}</div>
  <div id="subs" class="subs-{datos['subs']['estilo']}" data-track-kind="captions" style="{_px(caja_sub)}">{''.join(subs_html)}</div>
</div>
<script>window.PLAN = {json.dumps(datos, ensure_ascii=False)};</script>
<script src="editor.js"></script>
</body>
</html>
"""
    return pagina, datos


def _partir_marcado(texto: str, lineas: list[str]) -> list[str]:
    """Reparte el texto con *acentos* en las mismas líneas que se calcularon sin ellos."""
    if len(lineas) == 1:
        return [texto]
    palabras, out, k = texto.split(), [], 0
    for linea in lineas:
        n = len(linea.split())
        out.append(" ".join(palabras[k:k + n]))
        k += n
    if k < len(palabras):
        out[-1] += " " + " ".join(palabras[k:])
    # un *acento* que quedó partido entre dos líneas se cierra y se reabre
    abiertos = False
    for i, linea in enumerate(out):
        if abiertos:
            linea = "*" + linea
        if linea.count("*") % 2:
            linea += "*"
            abiertos = True
        else:
            abiertos = False
        out[i] = linea
    return out
