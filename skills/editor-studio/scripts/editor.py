#!/usr/bin/env python3
"""Editor Studio: edita un video que Emi grabó, con sus aprobaciones en cada compuerta.

Uso (desde la raíz del repositorio):  E="python3 skills/editor-studio/scripts/editor.py"
  $E doctor                              qué hay instalado y conectado
  $E saldo                               saldos reales de Kie, ElevenLabs y Apify
  $E aprendizajes --espacio E            lo aprendido que vale para ese espacio
  $E proyecto DIR --espacio E            crea productions/E/edicion/TEMA/ y su brief
  $E escaleta DIR                        hoja para preparar el video ANTES de grabar
  $E traer DIR --drive ID                baja el crudo de Drive (carpeta compartida por enlace)
  $E ingerir DIR ARCHIVO                 copia el crudo sin tocarlo y deja el archivo de trabajo
  $E transcribir DIR --motor scribe --execute     (o assemblyai, o --archivo export.json|srt)
  $E comparar-motores DIR                compara dos transcripciones del mismo audio
  $E cortes DIR [--ritmo natural] [--previa]      propone cortes: tabla y vista previa
  $E decidir DIR c003=descartado ...     decide cortes uno por uno (o --propuestos aprobado)
  $E aprobar DIR cortes|muestra|gasto|final --por Emi --nota "lo que dijo"
  $E cortar DIR                          aplica los cortes aprobados y verifica
  $E rostro DIR                          dónde está la cara, para no taparla y para los zooms
  $E niveles DIR                         los tres niveles para ESTE video y cuál se sugiere
  $E validar DIR                         revisa plan.json contra todas las reglas
  $E sonido DIR                          sintetiza los efectos y propone dónde van
  $E recorte DIR                         recorta a la persona donde haya texto detrás
  $E armar DIR                           escribe la composición
  $E muestra DIR --en 2.5,8 [--nombre minima]     cuadros de muestra para aprobar el estilo
  $E render DIR [--borrador]             video + mezcla + master + hojas + auditorías
  $E revisar DIR                         hojas de revisión e informe; sin él no hay cierre
  $E nota DIR                            hoja aparte con la propuesta de descripción y etiquetas
  $E cierre DIR                          comprueba todo e imprime los saldos
  $E aprender "lección" [--espacio E]
Sin --execute nada gasta saldo.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio as AUD  # noqa: E402
import corte as COR  # noqa: E402
import montaje as MON  # noqa: E402
import transcripcion as TRA  # noqa: E402
from comun import (ESPACIOS, FORMATOS, FPS, PLANTILLA, VERSION, ZONAS_APP, ErrorEditor, aprender, correr,  # noqa: E402
                   dir_produccion, duracion, escribir_json, espacio_de, formato_tiempo, huella, leer_aprendizajes,
                   leer_json, perfil, saldo, sha_archivo, sonda, tabla_saldo)

HF_VERSION = "0.9.34"
TIPOS_DE_VIDEO = {"opinion": 2, "explicacion": 2, "vlog": 2, "evento": 2, "podcast": 1, "entrevista": 1,
                  "anuncio": 3, "lanzamiento": 3, "tutorial": 2}
HDR_A_SDR = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
             "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
LOOKS = {"ninguno": "", "natural": "eq=contrast=1.04:saturation=1.05"}


# ---------- proyecto ----------

def crear_proyecto(d: Path, espacio: str) -> Path:
    dir_produccion(d, espacio)
    if (d / "brief.json").exists():
        raise ErrorEditor(f"{d} ya es una producción; no se sobrescribe")
    p = perfil(espacio)
    for sub in ("crudo", "assets", "out", "lib"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    for nombre in ("editor.css", "editor.js", "package.json", "package-lock.json"):
        shutil.copy2(PLANTILLA / nombre, d / nombre)
    escribir_json(d / "brief.json", {
        "version": 1, "espacio": espacio, "tema": d.name, "creado": time.strftime("%Y-%m-%d %H:%M:%S"),
        "skill": VERSION, "saldo_inicial": saldo(),
        "respuestas_emi": {k: "" for k in ("para_que", "a_quien", "postura", "tipo_de_video", "donde_se_publica",
                                           "duracion_objetivo", "nivel_elegido", "musica", "humor", "quienes_salen",
                                           "permiso_de_quienes_salen", "que_no_quiere", "cierre")},
        "aprobaciones": {}, "gasto_autorizado": None, "visto_y_escuchado_por_emi": False})
    escribir_json(d / "plan.json", plan_inicial(p))
    return d


def plan_inicial(p: dict) -> dict:
    ed = p["edicion"]
    return {"version": 1, "espacio": p["espacio"], "formato": "9:16", "nivel": None, "nivel_razon": "",
            "tramos": [], "color": {"look": ed.get("color", "natural")},
            "subtitulos": {"modo": "", "razon": ""},
            "piezas": [], "sonido": {"densidad": ed.get("sonido", {}).get("densidad", "minima"), "efectos": [],
                                     "musica": {"decision": "", "preguntado_a_emi": False}},
            "marca_en_pantalla": False}


ESCALETA = """# Escaleta · {tema} ({espacio})

Se llena con Emi ANTES de grabar. La skill propone; él decide.

## Lo que Emi quiere decir
- Postura (qué defiende o critica):
- A quién le habla:
- Qué debe pasar después de verlo (comentar, escribir, compartir, pensar):

## Ganchos (se proponen 3 distintos; Emi elige)
1.
2.
3.
- Elegido por Emi:

## Estructura
| Momento | Segundos aprox. | Qué dice | Qué se vería |
|---|---|---|---|
| Gancho | 0–3 | | |
| Promesa (por qué quedarse) | 3–8 | | |
| Desarrollo 1 | | | |
| Desarrollo 2 | | | |
| Giro o remate | | | |
| Cierre (pregunta o llamado) | | | |

## Para grabar
- Duración objetivo:
- Encuadre (vertical, plano medio, ojos en el tercio superior, aire para subtítulos abajo):
- Apoyos reales que conviene tener a la mano (capturas, documentos, fotos):
- Datos que llevan fuente:
"""


# ---------- crudo ----------

def traer_de_drive(d: Path, ident: str, nombre: str = "") -> Path:
    """Descarga directa de un archivo de Drive compartido por enlace."""
    import re
    m = re.search(r"(?:/d/|id=)([\w-]{20,})", ident)
    ident = m.group(1) if m else ident
    if not re.fullmatch(r"[\w-]{20,}", ident):
        raise ErrorEditor("no parece un ID ni un enlace de archivo de Drive")
    url = f"https://drive.usercontent.google.com/download?id={ident}&export=download&confirm=t"
    destino = d / "crudo" / (nombre or f"drive-{ident[:8]}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": f"editor-studio/{VERSION}"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as fh:
            tipo = r.headers.get("Content-Type", "")
            cabecera = r.headers.get("Content-Disposition", "")
            if "text/html" in tipo:
                raise ErrorEditor("Drive devolvió una página y no el archivo: comparte el archivo (o su carpeta) con «cualquier persona con el enlace»")
            shutil.copyfileobj(r, fh, 1 << 20)
    except OSError as exc:
        destino.unlink(missing_ok=True)
        raise ErrorEditor(f"no se pudo bajar de Drive: {exc}. Si el dominio está bloqueado, hay que permitir drive.usercontent.google.com en el entorno") from exc
    m = re.search(r'filename="([^"]+)"', cabecera)
    if m and not nombre:
        final = destino.with_name(Path(m.group(1)).name)
        destino.rename(final)
        destino = final
    return destino


def ingerir(d: Path, archivo: Path, formato: str = "9:16", encuadre: str = "", fps: int = FPS) -> dict:
    """Guarda el crudo sin tocarlo y deja un archivo de trabajo parejo: tamaño, cuadros fijos, color estándar."""
    dir_produccion(d)
    if formato not in FORMATOS:
        raise ErrorEditor(f"formato desconocido: {formato}")
    info = sonda(archivo)
    if not info["tiene_video"] or not info["tiene_audio"]:
        raise ErrorEditor("el archivo necesita imagen y sonido")
    crudo = d / "crudo" / archivo.name
    if archivo.resolve() != crudo.resolve():
        crudo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(archivo, crudo)
    W, H = FORMATOS[formato]
    razon, pedida = info["ancho"] / info["alto"], W / H
    if abs(razon - pedida) / pedida > 0.03 and encuadre not in ("recortar", "ajustar"):
        raise ErrorEditor(f"el crudo es {info['ancho']}x{info['alto']} y el formato pedido es {formato}: "
                          "elige --encuadre recortar (llena el cuadro y pierde orillas) o ajustar (bandas), o cambia --formato")
    if encuadre == "ajustar":
        escala = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2"
    else:
        escala = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    filtros = ([HDR_A_SDR] if info["hdr"] else []) + [escala, f"fps={fps}", "format=yuv420p"]
    trabajo = d / "trabajo.mp4"
    # imagen y sonido pueden durar distinto en el crudo: se trabaja hasta donde hay los dos
    dv, da = duracion_de(crudo, "v"), duracion_de(crudo, "a")
    tope = ["-t", f"{min(dv, da):.3f}"] if dv and da and abs(dv - da) > 0.1 else []
    # aresample con first_pts=0 conserva el desfase con que arranca el audio (celulares y grabadoras externas);
    # sin él, toda la producción queda con la voz adelantada
    correr(["ffmpeg", "-y", "-v", "error", "-i", str(crudo), *tope, "-vf", ",".join(filtros),
            "-af", "aresample=async=1:first_pts=0", "-c:v", "libx264", "-preset", "medium",
            "-crf", "15", "-g", str(fps), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", str(trabajo)],
           capture_output=True)
    correr(["ffmpeg", "-y", "-v", "error", "-i", str(trabajo), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(d / "audio.wav")],
           capture_output=True)
    medios = {"original": {"nombre": crudo.name, "sha": sha_archivo(crudo), **info}, "formato": formato, "fps": fps,
              "encuadre": encuadre or "igual", "hdr_convertido": info["hdr"], "duracion_s": round(duracion(trabajo), 3),
              "recortado_por_duracion": bool(tope), "imagen_s": dv, "sonido_s": da,
              "fecha": time.strftime("%Y-%m-%d %H:%M:%S")}
    escribir_json(d / "medios.json", medios)
    return medios


def duracion_de(ruta: Path, flujo: str) -> float | None:
    """Duración de la imagen («v») o del sonido («a») de un archivo, por separado."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", f"{flujo}:0", "-show_entries", "stream=duration:format=duration",
                        "-of", "json", str(ruta)], capture_output=True, text=True)
    try:
        datos = json.loads(r.stdout)
        valor = (datos.get("streams") or [{}])[0].get("duration")
        return round(float(valor), 3) if valor not in (None, "N/A") else None
    except (ValueError, IndexError, TypeError):
        return None


# ---------- rostro ----------

def mapa_de_rostro(d: Path, manual: str = "", video: str = "limpio.mp4") -> dict:
    """Caja de la cara cada medio segundo. Con --caja x0,y0,x1,y1 se da a mano mirando un cuadro."""
    medios = leer_json(d / "medios.json")
    W, H = FORMATOS[medios["formato"]]
    if manual:
        try:
            x0, y0, x1, y1 = (float(v) for v in manual.split(","))
        except ValueError as exc:
            raise ErrorEditor("--caja lleva cuatro números: x0,y0,x1,y1") from exc
        if not (0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H):
            raise ErrorEditor(f"la caja debe caber en {W}x{H}")
        datos = {"origen": "manual", "cajas": [{"t": 0.0, "x0": x0, "y0": y0, "x1": x1, "y1": y1}]}
    else:
        try:
            import cv2
        except ImportError as exc:
            raise ErrorEditor("falta opencv (python3 -m pip install 'opencv-python-headless<5') o da la caja a mano con --caja") from exc
        if not hasattr(cv2, "CascadeClassifier"):
            raise ErrorEditor("esta versión de opencv ya no trae el detector de rostros: instala 'opencv-python-headless<5' o da la caja con --caja")
        fuente = d / video
        if not fuente.exists():
            raise ErrorEditor(f"falta {video}: corre `cortar` primero")
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        cap, cajas, fps = cv2.VideoCapture(str(fuente)), [], medios["fps"]
        paso, n = max(1, fps // 2), 0
        while True:
            ok, cuadro = cap.read()
            if not ok:
                break
            if n % paso == 0:
                chico = cv2.resize(cuadro, (W // 3, H // 3))
                gris = cv2.cvtColor(chico, cv2.COLOR_BGR2GRAY)
                for (x, y, w, h) in detector.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=6, minSize=(W // 30, W // 30)):
                    mx, my = w * 0.12, h * 0.2          # margen: el detector da la cara, no el pelo ni la barbilla
                    cajas.append({"t": round(n / fps, 2), "x0": max(0, (x - mx) * 3), "y0": max(0, (y - my) * 3),
                                  "x1": min(W, (x + w + mx) * 3), "y1": min(H, (y + h + my) * 3)})
            n += 1
        cap.release()
        if not cajas:
            raise ErrorEditor("no se encontró ningún rostro: mira un cuadro y da la caja con --caja x0,y0,x1,y1")
        datos = {"origen": "detector", "cajas": [{k: (round(v, 1) if k != "t" else v) for k, v in c.items()} for c in cajas]}
    datos["formato"] = medios["formato"]
    if (d / video).exists():
        datos["limpio"] = sha_archivo(d / video)          # para saber si el mapa es de este corte
    escribir_json(d / "rostro.json", datos)
    return datos


# ---------- niveles ----------

def explicar_niveles(d: Path) -> str:
    brief, esp = leer_json(d / "brief.json"), espacio_de(d)
    p = perfil(esp)
    resp = brief.get("respuestas_emi") or {}
    dur = leer_json(d / "medios.json")["duracion_s"] if (d / "medios.json").exists() else None
    if (d / "cortes-aplicados.json").exists():
        dur = leer_json(d / "cortes-aplicados.json")["duracion_s"]
    partida = int(p["edicion"].get("nivel_partida", 2))
    tipo = str(resp.get("tipo_de_video", "")).strip().lower()
    por_tipo = next((n for clave, n in TIPOS_DE_VIDEO.items() if clave in tipo), None)
    sugerido, razones = partida, [f"el espacio «{esp}» parte de nivel {partida}"]
    if por_tipo is not None:
        if por_tipo < sugerido:
            sugerido = por_tipo
            razones.append(f"un video de tipo «{tipo}» se sostiene con nivel {por_tipo}")
        elif por_tipo > sugerido:
            razones.append(f"el tipo «{tipo}» admitiría nivel {por_tipo}: propónselo solo en el gancho o el cierre (tramos)")
    tope = int(p["edicion"].get("nivel_tope", 3))
    if sugerido > tope:
        sugerido = tope
        razones.append(f"en «{esp}» no se pasa de nivel {tope} sin que Emi lo pida")
    if dur and dur > 120 and sugerido == 3:
        sugerido = 2
        razones.append("pasa de dos minutos: nivel 3 en todo el video cansa y cuesta; mejor 2 con remates de 3")
    cuando = f"{dur:.0f} s" if dur else "duración aún sin medir"
    return f"""Los tres niveles para este video ({esp}, {cuando})

| | Nivel 1 · Limpio | Nivel 2 · Movimiento | Nivel 3 · Producción |
|---|---|---|---|
| Lleva | Cortes, subtítulos, títulos en los puntos clave, rótulo, fotos reales, cierre | Lo del 1 + zooms suaves, sellos, datos con fuente, barra de avance, cámara-tarjeta con panel, barridos | Lo del 2 + texto detrás de quien habla, insertos animados o B-roll, stickers, partículas, música |
| Se siente | La persona hablando, sin estorbos | Un reel trabajado | Un anuncio |
| Sirve para | Opinión del día, clips, publicar seguido | Explicar, la mayoría de los reels | Lanzamientos, campañas, la pieza que debe lucir |
| Tiempo y consumo | Bajo | Medio | Alto |
| Gasto de créditos | Ninguno | Ninguno | Solo si hay imagen o video generado: se cotiza antes |
| Riesgo | Que el guion no sostenga | Saturar | Que se vea «hecho por IA» |

Sugerencia: nivel {sugerido}. Por qué: {'; '.join(razones)}.
Regla: el nivel más bajo que cumpla el propósito. Se pueden combinar con `tramos` (por ejemplo 2 en todo y 3 solo en el gancho).
Decide Emi. Su respuesta va en brief.json → respuestas_emi.nivel_elegido y en plan.json → nivel y nivel_razon."""


# ---------- validar y armar ----------

def cargar_todo(d: Path) -> dict:
    dir_produccion(d)
    esp = espacio_de(d)
    faltan = [n for n in ("brief.json", "plan.json", "medios.json", "palabras_limpio.json", "cortes-aplicados.json") if not (d / n).exists()]
    if faltan:
        raise ErrorEditor("faltan pasos previos: " + ", ".join(faltan))
    pal = leer_json(d / "palabras_limpio.json")
    aplicado = leer_json(d / "cortes-aplicados.json")
    return {"d": d, "espacio": esp, "perfil": perfil(esp), "brief": leer_json(d / "brief.json"), "plan": leer_json(d / "plan.json"),
            "medios": leer_json(d / "medios.json"), "palabras": pal["palabras"], "aproximado": pal.get("aproximado", False),
            "aplicado": aplicado, "duracion": aplicado["duracion_s"],
            "rostro": leer_json(d / "rostro.json") if (d / "rostro.json").exists() else None,
            "archivos": {f.name for f in (d / "assets").glob("*") if f.is_file()}}


def validar_produccion(d: Path) -> tuple[list[str], list[str], list[dict], dict]:
    t = cargar_todo(d)
    err, avi, piezas = MON.validar(t["plan"], t["brief"], t["perfil"], t["palabras"], t["duracion"], t["rostro"],
                                   t["aplicado"]["empalmes"], t["archivos"], t["medios"]["fps"], t["aproximado"])
    if t["plan"].get("formato") != t["medios"]["formato"]:
        err.append(f"el plan es {t['plan'].get('formato')} y el video de trabajo es {t['medios']['formato']}")
    censura = [c for c in t["aplicado"].get("censura", []) if c.get("accion") == "tapar"]
    pendientes = [c for c in t["aplicado"].get("censura", []) if c.get("accion") == "avisar"]
    if pendientes:
        avi.append("modismos fuertes sin decidir (¿se quedan o se tapan?): " + ", ".join(f"«{c['texto']}» {formato_tiempo(c['t0'])}" for c in pendientes))
    if (d / "cortes.json").exists() and t["aplicado"].get("huella") != COR.huella_plan(leer_json(d / "cortes.json")):
        err.append("los cortes cambiaron después de `cortar`: repite `aprobar`, `cortar`, `rostro` y `armar`")
    if t["rostro"] and t["rostro"].get("limpio") and (d / "limpio.mp4").exists() and t["rostro"]["limpio"] != sha_archivo(d / "limpio.mp4"):
        err.append("el mapa de rostro es de otro corte: corre `rostro` otra vez")
    for p in piezas:
        if p.get("tipo") == "detras" and (d / "assets" / f"recorte-{p['id']}.webm").exists():
            meta = d / "assets" / f"recorte-{p['id']}.json"
            m = leer_json(meta) if meta.exists() else {}
            base = d / "assets" / "base.mp4"
            if (abs(m.get("t0", -9) - p["t0"]) > 0.02 or abs(m.get("t1", -9) - p["t1"]) > 0.02
                    or (base.exists() and m.get("base") != sha_archivo(base))):
                err.append(f"{p['id']} (detras): su recorte es de otro tramo o de otro corte; repite `recorte`")
    t["piezas"], t["censura"] = piezas, censura
    return err, avi, piezas, t


def huella_de_plan(plan: dict) -> str:
    return huella(json.dumps(plan, ensure_ascii=False, sort_keys=True))[:16]


def instalar_dependencias(d: Path) -> None:
    if not (d / "node_modules" / "gsap").is_dir() or not (d / "node_modules" / "@fontsource" / "inter").is_dir():
        for nombre in ("package.json", "package-lock.json"):
            shutil.copy2(PLANTILLA / nombre, d / nombre)
        correr(["npm", "ci", "--no-audit", "--no-fund"], cwd=d, capture_output=True)
    (d / "lib").mkdir(exist_ok=True)
    (d / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(d / "node_modules/gsap/dist/gsap.min.js", d / "lib/gsap.min.js")     # nunca de internet: el render no la alcanza
    shutil.copy2(d / "node_modules/@fontsource/anton/files/anton-latin-400-normal.woff2", d / "assets/fonts/anton.woff2")
    shutil.copy2(d / "node_modules/@fontsource/gelasio/files/gelasio-latin-700-normal.woff2", d / "assets/fonts/gelasio-700.woff2")
    for peso in (400, 700):
        shutil.copy2(d / f"node_modules/@fontsource/inter/files/inter-latin-{peso}-normal.woff2", d / f"assets/fonts/inter-{peso}.woff2")
    for nombre in ("editor.css", "editor.js"):                                        # la plantilla vigente manda
        shutil.copy2(PLANTILLA / nombre, d / nombre)


def base_con_color(d: Path, look: str, fps: int) -> None:
    """El video cortado, con el color del plan, listo para que el motor lo busque cuadro por cuadro."""
    if look not in LOOKS:
        raise ErrorEditor(f"look desconocido: {look}. Opciones: {', '.join(LOOKS)}")
    destino, marca = d / "assets" / "base.mp4", d / "assets" / ".base"
    firma = f"{sha_archivo(d / 'limpio.mp4')}:{look}"
    if destino.exists() and marca.exists() and marca.read_text() == firma:
        return
    if LOOKS[look]:
        correr(["ffmpeg", "-y", "-v", "error", "-i", str(d / "limpio.mp4"), "-an", "-vf", LOOKS[look], "-c:v", "libx264", "-preset", "medium",
                "-crf", "15", "-g", str(fps), "-pix_fmt", "yuv420p", str(destino)], capture_output=True)
    else:
        correr(["ffmpeg", "-y", "-v", "error", "-i", str(d / "limpio.mp4"), "-an", "-c:v", "copy", str(destino)], capture_output=True)
    marca.write_text(firma)


def armar(d: Path) -> dict:
    err, avi, piezas, t = validar_produccion(d)
    if err:
        raise ErrorEditor("el plan no pasa la validación:\n  - " + "\n  - ".join(err))
    instalar_dependencias(d)
    base_con_color(d, (t["plan"].get("color") or {}).get("look", "natural"), t["medios"]["fps"])
    sub = {**(t["perfil"]["edicion"].get("subtitulos") or {}), **(t["plan"].get("subtitulos") or {})}
    grupos = MON.grupos_de_subtitulos(t["palabras"], sub, t["aplicado"].get("censura"))
    pagina, datos = MON.armar_html(t["plan"], piezas, t["perfil"], grupos, t["duracion"], t["rostro"])
    (d / "index.html").write_text(pagina, encoding="utf-8")
    escribir_json(d / "hyperframes.json", {"name": d.name})
    escribir_json(d / "out" / "armado.json", {"huella_plan": huella_de_plan(t["plan"]), "cortes": t["aplicado"].get("huella"),
                                             "limpio": sha_archivo(d / "limpio.mp4"), "piezas": piezas, "grupos": len(grupos),
                                             "duracion_s": t["duracion"], "avisos": avi, "fecha": time.strftime("%Y-%m-%d %H:%M:%S")})
    try:
        r = subprocess.run(["npx", "--no-install", "hyperframes", "lint"], cwd=d, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise ErrorEditor("falta npx (Node 22 o superior)") from exc
    salida = (r.stdout + r.stderr).strip().splitlines()
    # el motor avisa que hay WAV sin <audio>: es a propósito, la mezcla se hace fuera y se une al final
    otros = [x.strip() for x in salida if x.strip().startswith("⚠") and "audio_file_without_element" not in x]
    return {"piezas": len(piezas), "grupos": len(grupos), "avisos": avi + [f"motor: {x}" for x in otros], "lint": salida[-1:] or [""],
            "lint_ok": r.returncode == 0}


def recortar_persona(d: Path) -> list[str]:
    """Un recorte con transparencia por cada texto que va detrás de quien habla. Es lento: entre 1 y 2 cuadros por segundo."""
    _, _, piezas, t = validar_recorte(d)
    hechos = []
    for p in piezas:
        if p.get("tipo") != "detras":
            continue
        salida = d / "assets" / f"recorte-{p['id']}.webm"
        tramo = d / "out" / f"tramo-{p['id']}.mp4"
        correr(["ffmpeg", "-y", "-v", "error", "-ss", f"{p['t0']:.3f}", "-i", str(d / "assets" / "base.mp4"), "-t", f"{p['t1'] - p['t0']:.3f}",
                "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-g", str(t["medios"]["fps"]), str(tramo)], capture_output=True)
        correr(["npx", "--no-install", "hyperframes", "remove-background", str(tramo.resolve()), "--output", str(salida.resolve()), "--quality", "balanced"],
               cwd=d, capture_output=True)
        tramo.unlink(missing_ok=True)
        escribir_json(salida.with_suffix(".json"), {"t0": p["t0"], "t1": p["t1"], "base": sha_archivo(d / "assets" / "base.mp4")})
        hechos.append(salida.name)
    return hechos


def validar_recorte(d: Path):
    """Como validar, pero tolera que aún falten los recortes (es lo que este paso va a producir)."""
    t = cargar_todo(d)
    piezas = MON.resolver(t["plan"], t["palabras"], t["duracion"], t["aproximado"])
    instalar_dependencias(d)
    base_con_color(d, (t["plan"].get("color") or {}).get("look", "natural"), t["medios"]["fps"])
    return [], [], piezas, t


# ---------- hojas ----------

def cuadro(video: Path, t: float, ancho: int = 0):
    from PIL import Image
    import io
    vf = ["-vf", f"scale={ancho}:-2"] if ancho else []
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", str(video), "-frames:v", "1", *vf, "-f", "image2pipe",
                        "-vcodec", "png", "-"], capture_output=True)
    if r.returncode or not r.stdout:
        raise ErrorEditor(f"no se pudo sacar el cuadro {t:.2f} s de {video.name}")
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def hoja(video: Path, tiempos: list[tuple[float, str]], salida: Path, ancho: int = 270, columnas: int = 6, zonas: bool = False) -> Path:
    """Hoja de contacto con la hora y una etiqueta bajo cada cuadro."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        letra = ImageFont.truetype("DejaVuSans.ttf", 13)
    except OSError:
        letra = ImageFont.load_default()
    if not tiempos:
        raise ErrorEditor("no hay momentos que poner en la hoja")
    primero = cuadro(video, tiempos[0][0], ancho)
    w, h = primero.size
    filas = (len(tiempos) + columnas - 1) // columnas
    lienzo = Image.new("RGB", (columnas * (w + 8) + 8, filas * (h + 34) + 8), "#18181c")
    dib = ImageDraw.Draw(lienzo, "RGBA")
    for k, (t, etiqueta) in enumerate(tiempos):
        img = primero if k == 0 else cuadro(video, t, ancho)
        x, y = 8 + (k % columnas) * (w + 8), 8 + (k // columnas) * (h + 34)
        lienzo.paste(img, (x, y))
        if zonas and h > w:
            e = w / 1080
            for (x0, y0, x1, y1) in ZONAS_APP.values():
                dib.rectangle([x + x0 * e, y + y0 * e, x + x1 * e, y + y1 * e], fill=(255, 0, 0, 70))
        dib.text((x + 2, y + h + 6), f"{t:.2f}s {etiqueta}"[:int(w / 7)], fill="#e8e8e8", font=letra)
    salida.parent.mkdir(parents=True, exist_ok=True)
    lienzo.save(salida)
    return salida


def momentos_clave(piezas: list[dict], empalmes: list[float], dur: float) -> list[tuple[float, str]]:
    out = [(0.05, "inicio"), (min(dur - 0.05, 1.0), "1 s")]
    for p in piezas:
        if p["tipo"] in ("barra",):
            continue
        out.append((min(dur - 0.05, p["t0"] + 0.35), f"{p['id']} {p['tipo']} entra"))
        out.append((min(dur - 0.05, (p["t0"] + p["t1"]) / 2), f"{p['id']} mitad"))
    out += [(min(dur - 0.05, e + 0.1), "empalme") for e in empalmes[:12]]
    out.append((max(0.0, dur - 0.15), "último cuadro"))
    return sorted(set(out))


# ---------- render ----------

def render(d: Path, borrador: bool = False) -> dict:
    err, avi, piezas, t = validar_produccion(d)
    if err:
        raise ErrorEditor("el plan no pasa la validación:\n  - " + "\n  - ".join(err))
    armado = leer_json(d / "out" / "armado.json") if (d / "out" / "armado.json").exists() else {}
    if armado.get("huella_plan") != huella_de_plan(t["plan"]) or not (d / "index.html").exists():
        raise ErrorEditor("el plan cambió después de armar: corre `armar` otra vez")
    if armado.get("cortes") != t["aplicado"].get("huella") or armado.get("limpio") != sha_archivo(d / "limpio.mp4"):
        raise ErrorEditor("se volvió a cortar después de armar: la imagen armada ya no corresponde a la voz. Corre `rostro` y `armar` otra vez")
    if not borrador and t["perfil"]["edicion"].get("estado") != "aprobado":
        ap = (t["brief"].get("aprobaciones") or {}).get("muestra") or {}
        if not ap.get("por"):
            raise ErrorEditor("el estilo de este espacio aún no está aprobado por Emi: enséñale la `muestra` y registra su respuesta "
                              "con `aprobar DIR muestra` (o rinde un borrador con --borrador)")
    out = d / "out"
    mudo = out / ("borrador-mudo.mp4" if borrador else "video-mudo.mp4")
    correr(["npx", "--no-install", "hyperframes", "render", "--quality", "draft" if borrador else "high", "--fps", str(t["medios"]["fps"]),
            "--output", str(mudo.resolve()), "--quiet"], cwd=d, capture_output=True)
    if not mudo.exists():
        raise ErrorEditor("el motor terminó sin dejar el video: corre `npx hyperframes render` dentro de la producción para ver el error")
    # sonido
    AUD.sintetizar(out / "efectos")
    ids = {p["id"]: p for p in piezas}
    efectos = []
    for e in (t["plan"].get("sonido") or {}).get("efectos") or []:
        cuando = ids[e["en"]]["t0"] if "en" in e else float(e.get("t", 0))
        efectos.append({"t": cuando, "sonido": e["sonido"], "db": e.get("db", AUD.EFECTO_BAJO_VOZ)})
    mus = (t["plan"].get("sonido") or {}).get("musica") or {}
    pista = d / "assets" / mus["archivo"] if mus.get("decision") == "archivo" else None
    voz = out / "voz.wav"
    correr(["ffmpeg", "-y", "-v", "error", "-i", str(d / "limpio.mp4"), "-vn", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(voz)], capture_output=True)
    info = AUD.mezclar(voz, out / "mezcla.wav", efectos, out / "efectos", t["duracion"], t["censura"], pista)
    final = out / ("BORRADOR.mp4" if borrador else "FINAL.mp4")
    ganancia = AUD.masterizar(mudo, out / "mezcla.wav", final)
    auditoria = AUD.auditar(final, info, ganancia, t["duracion"])
    pre = "borrador-" if borrador else ""          # un borrador nunca pisa las auditorías ni las hojas del final
    escribir_json(out / f"{pre}auditoria-audio.json", auditoria)
    # imagen
    momentos = momentos_clave(piezas, t["aplicado"]["empalmes"], t["duracion"])
    hoja(final, momentos, out / f"{pre}hoja.png")
    if t["medios"]["formato"] == "9:16":
        hoja(final, momentos, out / f"{pre}hoja-app.png", zonas=True)
    video_av = auditar_video(final, t)
    escribir_json(out / f"{pre}auditoria-video.json", video_av)
    if not borrador:
        escribir_json(out / "manifiesto.json", {
            "skill": VERSION, "motor": f"hyperframes {HF_VERSION}", "espacio": t["espacio"], "final": final.name, "sha": sha_archivo(final),
            "crudo": t["medios"]["original"]["sha"], "plan": huella_de_plan(t["plan"]), "cortes": t["aplicado"].get("huella"),
            "nivel": t["plan"]["nivel"],
            "transcripcion": leer_json(d / "palabras.json").get("motor"), "duracion_s": auditoria["duracion_s"],
            "lufs": auditoria["lufs"], "fecha": time.strftime("%Y-%m-%d %H:%M:%S")})
    return {"final": str(final), "avisos_plan": avi, "avisos_audio": auditoria["avisos"], "avisos_video": video_av["avisos"],
            "lufs": auditoria["lufs"], "pico": auditoria["pico_dbtp"], "duracion_s": auditoria["duracion_s"]}


def auditar_video(final: Path, t: dict) -> dict:
    info, avisos = sonda(final), []
    W, H = FORMATOS[t["medios"]["formato"]]
    if (info["ancho"], info["alto"]) != (W, H):
        avisos.append(f"el archivo mide {info['ancho']}x{info['alto']} y debía medir {W}x{H}")
    if abs(info["fps"] - t["medios"]["fps"]) > 0.01:
        avisos.append(f"salió a {info['fps']} cuadros por segundo y debía ser {t['medios']['fps']}")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final), "-vf", "blackdetect=d=0.2:pix_th=0.06", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    import re
    negros = re.findall(r"black_start:([\d.]+)", r.stderr)
    if negros:
        avisos.append("cuadros en negro en: " + ", ".join(f"{float(x):.2f} s" for x in negros[:6]))
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final), "-vf", "freezedetect=n=0.001:d=2.5", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    congelados = re.findall(r"freeze_start: ([\d.]+)", r.stderr)
    if congelados:
        avisos.append("imagen congelada más de 2.5 s desde: " + ", ".join(f"{float(x):.2f} s" for x in congelados[:6]))
    return {"ancho": info["ancho"], "alto": info["alto"], "fps": info["fps"], "codec": info["codec"], "avisos": avisos}


def crear_revision(d: Path) -> Path:
    err, _, piezas, t = validar_produccion(d)
    final = d / "out" / "FINAL.mp4"
    if not final.exists():
        raise ErrorEditor("no hay out/FINAL.mp4: se revisa el archivo rendido, no la intención")
    out, dur, fps = d / "out", t["duracion"], t["medios"]["fps"]
    cambios = sorted({p["t0"] for p in piezas if p["tipo"] != "barra"} | set(t["aplicado"]["empalmes"][:10]))
    tr = []
    for c in cambios[:14]:
        for k in (-6, -3, 0, 3, 6, 12):
            tt = c + k / fps
            if 0 <= tt < dur:
                tr.append((round(tt, 3), f"{'+' if k > 0 else ''}{k}"))
    hoja(final, tr or [(0.1, "inicio")], out / "hoja-transiciones.png", columnas=6)
    paso = max(0.5, dur / 24)
    hoja(final, [(round(k * paso + 0.2, 2), "") for k in range(int(dur / paso)) if k * paso + 0.2 < dur], out / "hoja-telefono.png", ancho=180, columnas=8)
    informe = out / "revision.json"
    escribir_json(informe, {"final_sha": sha_archivo(final), "fecha": time.strftime("%Y-%m-%d %H:%M:%S"), "revisado_por": "",
                            "lista": {k: None for k in ("los_2_primeros_segundos_enganchan", "todo_se_lee_en_telefono", "nada_tapa_la_cara",
                                                        "nada_bajo_la_interfaz_de_la_app", "solo_colores_y_fuentes_del_espacio",
                                                        "cada_pieza_dice_algo_de_lo_que_se_oye", "sin_cuadros_rotos_ni_vacios",
                                                        "subtitulos_van_con_la_voz", "el_ultimo_cuadro_cierra", "se_ve_hecho_por_una_persona")},
                            "hallazgos": [], "pendientes": [], "no_juzgable_por_ia": ["cómo suena la voz", "si la música y los efectos molestan",
                                                                                     "si el chiste da risa", "si el ritmo se siente natural"]})
    return informe


def exigir_revision(d: Path) -> dict:
    final, informe = d / "out" / "FINAL.mp4", d / "out" / "revision.json"
    if not informe.exists():
        raise ErrorEditor("falta out/revision.json: corre `revisar`, mira las hojas y llena el informe")
    r = leer_json(informe)
    if r.get("final_sha") != sha_archivo(final):
        raise ErrorEditor("la revisión es de un render anterior: vuelve a correr `revisar` sobre el archivo actual")
    if not str(r.get("revisado_por", "")).strip():
        raise ErrorEditor("la revisión no dice quién revisó")
    sin = [k for k, v in (r.get("lista") or {}).items() if v is None]
    if sin:
        raise ErrorEditor("la lista de revisión tiene puntos sin contestar: " + ", ".join(sin))
    malos = [k for k, v in r["lista"].items() if v is False]
    if malos and not r.get("pendientes"):
        raise ErrorEditor("hay puntos reprobados sin pendiente escrito: " + ", ".join(malos))
    return r


NOTA = """# Publicación · {tema} ({espacio})

Hoja aparte: la skill edita video y no publica. Esto es una propuesta para que Emi la ajuste.

## Descripción (2 opciones)
1.
2.

## Etiquetas candidatas (pocas y del tema; se revisan contra el radar de la semana)
-

## Portada
- Cuadro sugerido (segundo):
- Texto en portada:

## Para X e Historias (ideas que cruzan por el puente, no órdenes)
-

## Lo que hay que mirar después de publicar
- Retención a los 3 s, al 50 % y al final; guardados, compartidos y comentarios. Emi pasa la captura y se anota con `aprender`.
"""


def cierre(d: Path) -> str:
    err, avi, _, t = validar_produccion(d)
    if err:
        raise ErrorEditor("el plan no pasa la validación:\n  - " + "\n  - ".join(err))
    final = d / "out" / "FINAL.mp4"
    if not final.exists():
        raise ErrorEditor("no hay out/FINAL.mp4")
    sellos = [leer_json(d / "cortes.json").get("aprobacion") or {}, (t["brief"].get("aprobaciones") or {}).get("muestra") or {},
              t["brief"].get("gasto_autorizado") or {}]
    if d.resolve().name.startswith("prueba-") or any(str(x.get("por", "")).lower() == "prueba" for x in sellos):
        raise ErrorEditor("esta es una producción de prueba técnica: sus aprobaciones no son de Emi y no se cierra ni se entrega")
    cortes = leer_json(d / "cortes.json")
    COR.exigir_aprobacion(cortes)
    if t["aplicado"].get("huella") != COR.huella_plan(cortes):
        raise ErrorEditor("los cortes cambiaron después de `cortar`: el video no corresponde a lo aprobado. Repite `cortar`, `armar` y `render`")
    if t["perfil"]["edicion"].get("estado") != "aprobado" and not ((t["brief"].get("aprobaciones") or {}).get("muestra") or {}).get("por"):
        raise ErrorEditor("falta la aprobación de Emi sobre la muestra de estilo (`aprobar DIR muestra`)")
    if not (d / "out" / "manifiesto.json").exists():
        raise ErrorEditor("no hay manifiesto: el FINAL.mp4 no salió de un `render` completo")
    man = leer_json(d / "out" / "manifiesto.json")
    if man.get("sha") != sha_archivo(final):
        raise ErrorEditor("out/FINAL.mp4 no es el archivo que dejó el último `render`")
    if man.get("plan") != huella_de_plan(t["plan"]) or man.get("cortes") != t["aplicado"].get("huella"):
        raise ErrorEditor("el plan o los cortes cambiaron después del render: el video no corresponde. Repite `armar`, `render` y `revisar`")
    exigir_revision(d)
    for nombre in ("auditoria-audio.json", "auditoria-video.json"):
        a = leer_json(d / "out" / nombre)
        if a.get("avisos") and not a.get("avisos_atendidos"):
            raise ErrorEditor(f"{nombre} tiene avisos sin atender: corrígelos o escribe en `avisos_atendidos` por qué se aceptan:\n  - "
                              + "\n  - ".join(a["avisos"]))
    if not (d / "out" / "publicacion.md").exists():
        raise ErrorEditor("falta la hoja de publicación: `nota DIR` y llénala")
    ahora = saldo()
    escribir_json(d / "out" / "saldo-final.json", ahora)
    visto = t["brief"].get("visto_y_escuchado_por_emi")
    if isinstance(visto, dict) and visto.get("final_sha") != sha_archivo(final):
        visto = None                                   # su visto bueno era de otro render
    estado = ("visto y escuchado por Emi: TERMINADO" if visto
              else "listo para enseñárselo. FALTA que Emi lo vea y lo escuche (`aprobar DIR final --por Emi --nota ...`); hasta entonces no está terminado")
    return f"Entrega: {final}\nEstado: {estado}\n\n" + tabla_saldo(t["brief"].get("saldo_inicial"), ahora)


# ---------- doctor ----------

def doctor() -> list[tuple[str, bool, str]]:
    filas = []

    def prog(nombre, args, pista):
        try:
            r = subprocess.run([nombre, *args], capture_output=True, text=True, timeout=60)
            linea = (r.stdout or r.stderr).strip().splitlines()[0][:70] if (r.stdout or r.stderr).strip() else ""
            filas.append((nombre, r.returncode == 0, linea))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            filas.append((nombre, False, pista))
    prog("ffmpeg", ["-version"], "instalar FFmpeg")
    prog("ffprobe", ["-version"], "viene con FFmpeg")
    prog("node", ["--version"], "instalar Node 22 o superior")
    prog("npm", ["--version"], "viene con Node")
    filtros = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout if shutil.which("ffmpeg") else ""
    filas.append(("ffmpeg: zscale y tonemap (HDR del iPhone)", " zscale " in filtros and " tonemap " in filtros, "sin ellos un crudo HDR sale lavado"))
    for mod, para in (("numpy", "cortar por energía"), ("PIL", "hojas de revisión"), ("cv2", "mapa de rostro (opcional: se puede dar la caja a mano)")):
        try:
            __import__(mod)
            filas.append((f"python: {mod}", True, para))
        except ImportError:
            filas.append((f"python: {mod}", False, f"falta; sirve para {para}"))
    navegador = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome-headless-shell")
    filas.append(("navegador para el render", bool(navegador), navegador or "HyperFrames baja el suyo si puede"))
    s = saldo()
    filas.append(("Kie (imagen y video generado)", s.get("kie_creditos") is not None, f"{s.get('kie_creditos')} créditos" if s.get("kie_creditos") is not None else s.get("kie_error", "")))
    filas.append(("ElevenLabs (transcripción Scribe)", "elevenlabs_restantes" in s, f"{s.get('elevenlabs_restantes')} caracteres" if "elevenlabs_restantes" in s else s.get("elevenlabs_error", "")))
    filas.append(("Apify (radar de tendencias)", "apify_restante_usd" in s, f"{s.get('apify_restante_usd')} USD" if "apify_restante_usd" in s else s.get("apify_error", "")))
    try:
        from comun import ASSEMBLY, cab_assembly, pedir
        pedir(f"{ASSEMBLY}/transcript?limit=1", cabeceras=cab_assembly(), espera=20)
        filas.append(("AssemblyAI (transcripción)", True, "conectado"))
    except ErrorEditor as exc:
        filas.append(("AssemblyAI (transcripción)", False, "sin conexión (opcional): " + str(exc)[:70]))
    return filas


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="editor.py", description="Editor Studio " + VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def con_dir(nombre, ayuda=""):
        s = sub.add_parser(nombre, help=ayuda)
        s.add_argument("dir", type=Path)
        return s
    sub.add_parser("doctor")
    sub.add_parser("saldo")
    s = sub.add_parser("aprendizajes"); s.add_argument("--espacio", default="")
    s = sub.add_parser("aprender"); s.add_argument("texto"); s.add_argument("--espacio", default="")
    s = con_dir("proyecto"); s.add_argument("--espacio", required=True, choices=ESPACIOS)
    con_dir("escaleta")
    s = con_dir("traer"); s.add_argument("--drive", required=True); s.add_argument("--nombre", default="")
    s = con_dir("ingerir"); s.add_argument("archivo", type=Path); s.add_argument("--formato", default="9:16", choices=list(FORMATOS))
    s.add_argument("--encuadre", default="", choices=["", "recortar", "ajustar"])
    s = con_dir("transcribir"); s.add_argument("--motor", default="scribe", choices=TRA.MOTORES); s.add_argument("--archivo", type=Path)
    s.add_argument("--idioma", default="es"); s.add_argument("--hablantes", action="store_true"); s.add_argument("--execute", action="store_true")
    s.add_argument("--como", default="", help="guardar aparte para comparar (palabras-<como>.json) sin reemplazar la vigente")
    s = con_dir("comparar-motores"); s.add_argument("a"); s.add_argument("b")
    s = con_dir("cortes"); s.add_argument("--ritmo", default=""); s.add_argument("--muletillas", default="", choices=["", "seguras", "todas", "ninguna"])
    s.add_argument("--previa", action="store_true")
    s = con_dir("decidir"); s.add_argument("decisiones", nargs="*"); s.add_argument("--propuestos", choices=["aprobado", "descartado"])
    s.add_argument("--quitar", default="", help="corte manual: 12.4~18.9 con su motivo en --motivo"); s.add_argument("--motivo", default="")
    s.add_argument("--censura", default="", help="índice=tapar|dejar, por ejemplo 2=dejar")
    s = con_dir("aprobar"); s.add_argument("que", choices=["cortes", "muestra", "gasto", "final"]); s.add_argument("--por", required=True)
    s.add_argument("--nota", required=True); s.add_argument("--creditos", type=float)
    con_dir("cortar")
    s = con_dir("rostro"); s.add_argument("--caja", default="")
    con_dir("niveles"); con_dir("validar"); con_dir("recorte"); con_dir("armar"); con_dir("revisar"); con_dir("nota"); con_dir("cierre")
    s = con_dir("sonido"); s.add_argument("--densidad", default="")
    s = con_dir("muestra"); s.add_argument("--en", required=True); s.add_argument("--nombre", default="muestra")
    s = con_dir("render"); s.add_argument("--borrador", action="store_true")
    a = ap.parse_args(argv)
    try:
        return despachar(a)
    except ErrorEditor as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1
    except (KeyError, ValueError, TypeError, OSError) as exc:
        if os.environ.get("EDITOR_DEBUG"):
            raise
        print(f"✗ un archivo de la producción está incompleto o mal formado ({type(exc).__name__}: {exc}). "
              "Corre `validar`; con EDITOR_DEBUG=1 se ve el detalle.", file=sys.stderr)
        return 1


def despachar(a) -> int:
    c = a.cmd
    if c == "doctor":
        filas = doctor()
        for nombre, ok, nota in filas:
            print(f"{'✓' if ok else '✗'} {nombre:<44} {nota}")
        return 0
    if c == "saldo":
        print(tabla_saldo(None, saldo())); return 0
    if c == "aprendizajes":
        print(leer_aprendizajes(a.espacio)); return 0
    if c == "aprender":
        print(f"anotado en {aprender(a.texto, a.espacio)}"); return 0
    d: Path = a.dir
    if c == "proyecto":
        crear_proyecto(d, a.espacio)
        print(f"producción creada en {d}\n\nAprendizajes vigentes para «{a.espacio}»:\n{leer_aprendizajes(a.espacio)}\n\n"
              "Sigue: la entrevista (ENTREVISTA.md). Las respuestas de Emi van en brief.json.")
        return 0
    dir_produccion(d)
    if c == "escaleta":
        f = d / "escaleta.md"
        if f.exists():
            raise ErrorEditor("ya hay una escaleta; no se sobrescribe")
        f.write_text(ESCALETA.format(tema=d.name, espacio=espacio_de(d)), encoding="utf-8")
        print(f"escaleta en {f}: se llena con Emi antes de grabar"); return 0
    if c == "traer":
        print(f"descargado: {traer_de_drive(d, a.drive, a.nombre)}"); return 0
    if c == "ingerir":
        m = ingerir(d, a.archivo, a.formato, a.encuadre)
        o = m["original"]
        print(f"crudo {o['ancho']}x{o['alto']} a {o['fps']} c/s, {formato_tiempo(o['duracion_s'])}"
              + (" · HDR convertido a color estándar" if m["hdr_convertido"] else "")
              + (" · cuadros variables emparejados" if o.get("fps_variable") else "")
              + f"\ntrabajo: {d / 'trabajo.mp4'} ({m['formato']} a {m['fps']} c/s) · audio para transcribir: {d / 'audio.wav'}")
        return 0
    if c == "transcribir":
        if a.motor == "archivo" or a.archivo:
            if not a.archivo:
                raise ErrorEditor("--motor archivo necesita --archivo export.json|srt|vtt")
            if not a.archivo.is_file():
                raise ErrorEditor(f"no existe {a.archivo}")
            t = TRA.de_archivo(a.archivo, a.idioma, duracion(d / "audio.wav") if (d / "audio.wav").exists() else None)
        else:
            wav = d / "audio.wav"
            if not wav.exists():
                raise ErrorEditor("falta audio.wav: corre `ingerir` primero")
            seg = duracion(wav)
            if not a.execute:
                print(f"Se transcribirían {seg:.0f} s con {a.motor}. Tiene costo en el proveedor. Repite con --execute para hacerlo."); return 0
            t = TRA.con_scribe(wav, a.idioma, a.hablantes) if a.motor == "scribe" else TRA.con_assemblyai(wav, a.idioma, a.hablantes)
        destino = d / (f"palabras-{a.como}.json" if a.como else "palabras.json")
        escribir_json(destino, t)
        if not a.como:
            (d / "transcripcion.txt").write_text(TRA.texto_legible(t), encoding="utf-8")
        print(f"{len(t['palabras'])} palabras con {t['motor']}" + (" (tiempos APROXIMADOS por frase: no sirven para cortar muletillas)" if t["aproximado"] else "")
              + f" → {destino}\nLee transcripcion.txt completa antes de proponer nada.")
        return 0
    if c == "comparar-motores":
        r = TRA.comparar(leer_json(d / f"palabras-{a.a}.json"), leer_json(d / f"palabras-{a.b}.json"))
        escribir_json(d / "out" / f"comparacion-{a.a}-{a.b}.json", r)
        print(json.dumps({k: v for k, v in r.items() if k != "diferencias"}, ensure_ascii=False, indent=1))
        for x in r["diferencias"][:25]:
            print(f"  {formato_tiempo(x['t'])}  " + "  |  ".join(f"{k}: «{v}»" for k, v in x.items() if k != "t"))
        return 0
    if c == "cortes":
        medios, pal = leer_json(d / "medios.json"), leer_json(d / "palabras.json")
        ed = perfil(espacio_de(d))["edicion"]
        ritmo = a.ritmo or ed.get("ritmo", "natural")
        mul = a.muletillas or ed.get("muletillas", "seguras")
        palabras = [] if pal.get("aproximado") else pal["palabras"]
        p = COR.plan(d / "audio.wav", palabras, ritmo, medios["fps"], mul)
        if pal.get("aproximado"):
            p["avisos"].append("transcripción aproximada: solo se proponen silencios; muletillas y tomas se marcan a mano con `decidir --quitar`")
        p["palabras_sha"] = sha_archivo(d / "palabras.json")       # los cortes valen para ESTA transcripción
        COR.guardar(p, d / "cortes.json")
        (d / "out").mkdir(exist_ok=True)
        (d / "out" / "cortes.md").write_text(COR.tabla(p) + "\n", encoding="utf-8")
        print(COR.tabla(p))
        for x in p["avisos"]:
            print(f"⚠ {x}")
        if a.previa:
            COR.aplicar(d / "trabajo.mp4", d / "out" / "previa-cortes.mp4", COR.tramos_que_quedan(p, incluir_propuestos=True), medios["fps"], previa=True)
            print(f"\nvista previa ligera: {d / 'out' / 'previa-cortes.mp4'}")
        print("\nSigue: revisar cada toma y cada muletilla dudosa leyendo la frase, enseñarle a Emi tabla y vista previa, `decidir` y `aprobar`.")
        return 0
    if c == "decidir":
        p = leer_json(d / "cortes.json")
        por_id = {x["id"]: x for x in p["cortes"]}
        for par in a.decisiones:
            ident, _, estado = par.partition("=")
            if ident not in por_id or estado not in ("aprobado", "descartado", "propuesto"):
                raise ErrorEditor(f"decisión ilegible: {par}. Formato: c003=aprobado|descartado")
            por_id[ident]["estado"] = estado
        if a.propuestos:
            for x in p["cortes"]:
                if x["estado"] == "propuesto":
                    x["estado"] = a.propuestos
        if a.quitar:
            if len(a.motivo.strip()) < 8:
                raise ErrorEditor("un corte manual lleva --motivo")
            fps = p["fps"]
            for tramo in a.quitar.split(","):
                t0, _, t1 = tramo.partition("~")
                try:
                    t0, t1 = float(t0), float(t1)
                except ValueError as exc:
                    raise ErrorEditor(f"tramo ilegible: «{tramo}». Formato: 12.4~18.9 (segundos del crudo)") from exc
                if not 0 <= t0 < t1 <= p["duracion_crudo_s"] + 0.05:
                    raise ErrorEditor(f"tramo fuera de lugar: «{tramo}». Debe cumplir 0 ≤ inicio < fin ≤ {p['duracion_crudo_s']:.2f}")
                p["cortes"].append({"t0": COR._al_cuadro(t0, fps, True), "t1": COR._al_cuadro(min(t1, p["duracion_crudo_s"]), fps), "tipo": "manual",
                                    "motivo": a.motivo.strip(), "estado": "propuesto"})
            p["cortes"] = COR.unir(p["cortes"], fps, leer_json(d / "palabras.json")["palabras"])
        if a.censura:
            for par in a.censura.split(","):
                k, _, accion = par.partition("=")
                if accion not in ("tapar", "dejar") or not k.isdigit() or int(k) >= len(p["censura"]):
                    raise ErrorEditor(f"censura ilegible: {par}. Formato: 0=tapar,1=dejar (el número es la posición en la lista)")
                p["censura"][int(k)]["accion"] = accion
        p["aprobacion"] = None              # cualquier cambio invalida la aprobación anterior
        COR.guardar(p, d / "cortes.json")
        (d / "out" / "cortes.md").write_text(COR.tabla(p) + "\n", encoding="utf-8")
        print(COR.tabla(p)); return 0
    if c == "aprobar":
        de_prueba = d.resolve().name.startswith("prueba-") and a.por.strip().lower() == "prueba"
        if a.por.strip().lower() not in ("emi", "emiliano") and not de_prueba:
            raise ErrorEditor("las compuertas las aprueba Emi; aquí se registra lo que él dijo, con sus palabras en --nota. "
                              "(Solo una producción de prueba, en una carpeta `prueba-...`, admite --por prueba, y nunca se puede cerrar.)")
        sello = {"por": a.por.strip(), "nota": a.nota.strip(), "fecha": time.strftime("%Y-%m-%d %H:%M:%S")}
        if len(sello["nota"]) < 4:
            raise ErrorEditor("--nota lleva lo que dijo Emi")
        if a.que == "cortes":
            p = leer_json(d / "cortes.json")
            sin = [x["id"] for x in p["cortes"] if x["estado"] in ("propuesto", "dudoso")]
            if sin:
                raise ErrorEditor("quedan cortes sin decidir: " + ", ".join(sin) + ". Usa `decidir`")
            p["aprobacion"] = {**sello, "huella": COR.huella_plan(p)}
            COR.guardar(p, d / "cortes.json")
        else:
            b = leer_json(d / "brief.json")
            if a.que == "muestra":
                b.setdefault("aprobaciones", {})["muestra"] = sello
            elif a.que == "final":
                final = d / "out" / "FINAL.mp4"
                if not final.exists():
                    raise ErrorEditor("no hay out/FINAL.mp4 que Emi haya podido ver")
                if de_prueba:
                    raise ErrorEditor("una producción de prueba no recibe visto bueno final")
                b["visto_y_escuchado_por_emi"] = {**sello, "final_sha": sha_archivo(final)}
            else:
                if a.creditos is None:
                    raise ErrorEditor("aprobar gasto lleva --creditos (el tope que Emi autorizó para este video)")
                b["gasto_autorizado"] = {**sello, "creditos": a.creditos}
            escribir_json(d / "brief.json", b)
        print(f"registrado: {a.que} aprobado por {sello['por']} · «{sello['nota']}»"); return 0
    if c == "cortar":
        medios, p, pal = leer_json(d / "medios.json"), leer_json(d / "cortes.json"), leer_json(d / "palabras.json")
        COR.exigir_aprobacion(p)
        if p.get("palabras_sha") and p["palabras_sha"] != sha_archivo(d / "palabras.json"):
            raise ErrorEditor("la transcripción cambió después de proponer los cortes: repite `cortes`, enséñaselos a Emi y vuelve a aprobar")
        quedan = COR.tramos_que_quedan(p)
        COR.aplicar(d / "trabajo.mp4", d / "limpio.mp4", quedan, medios["fps"])
        correr(["ffmpeg", "-y", "-v", "error", "-i", str(d / "limpio.mp4"), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(d / "limpio.wav")], capture_output=True)
        limpias = COR.remapear(pal["palabras"], quedan)
        esperado, real = sum(b - a_ for a_, b in quedan), duracion(d / "limpio.mp4")
        avisos = COR.verificar(d / "limpio.wav", quedan, limpias, p["umbral_db"], esperado, real, medios["fps"],
                               duracion_de(d / "limpio.mp4", "v"), duracion_de(d / "limpio.mp4", "a"))
        censura = []
        for x in p.get("censura", []):
            w = next((w for w in limpias if w.get("i_crudo") == x["i"]), None)       # la misma palabra, ya en el video cortado
            if w is None:
                if x.get("accion") == "tapar":
                    avisos.append(f"la palabra «{x['texto']}» ({formato_tiempo(x['t0'])} del crudo) quedó dentro de un corte: ya no hay nada que tapar")
                continue
            if COR.normal(w["txt"]) != COR.normal(x["texto"]):
                raise ErrorEditor(f"la palabra a tapar («{x['texto']}») ya no coincide con la transcripción («{w['txt']}»): repite `cortes`")
            censura.append({"i": w["i_crudo"], "t0": w["t0"], "t1": w["t1"], "texto": x["texto"], "accion": x["accion"]})
        escribir_json(d / "palabras_limpio.json", {**{k: v for k, v in pal.items() if k != "palabras"}, "palabras": limpias})
        escribir_json(d / "cortes-aplicados.json", {"quedan": quedan, "empalmes": COR.empalmes(quedan), "duracion_s": round(real, 3),
                                                    "censura": censura, "avisos": avisos, "huella": COR.huella_plan(p)})
        print(f"limpio.mp4: {formato_tiempo(real)} (el crudo duraba {formato_tiempo(p['duracion_crudo_s'])}), {len(quedan) - 1} empalmes")
        for x in avisos:
            print(f"⚠ {x}")
        if not avisos:
            print("verificación: duración exacta y ningún empalme en plena voz")
        return 0
    if c == "rostro":
        r = mapa_de_rostro(d, a.caja)
        u = MON.rostro_en(r, 0, 1e9)
        print(f"rostro ({r['origen']}, {len(r['cajas'])} muestras): de ({u[0]:.0f}, {u[1]:.0f}) a ({u[2]:.0f}, {u[3]:.0f})"); return 0
    if c == "niveles":
        print(explicar_niveles(d)); return 0
    if c == "validar":
        err, avi, piezas, _ = validar_produccion(d)
        for x in err:
            print(f"✗ {x}")
        for x in avi:
            print(f"⚠ {x}")
        print(f"{len(piezas)} piezas · {len(err)} errores · {len(avi)} avisos")
        return 1 if err else 0
    if c == "sonido":
        _, _, piezas, t = validar_produccion(d)
        nombres = AUD.sintetizar(d / "out" / "efectos")
        dens = a.densidad or (t["plan"].get("sonido") or {}).get("densidad", "minima")
        print(f"efectos disponibles ({d / 'out' / 'efectos'}): {', '.join(nombres)}\n\nPropuesta para densidad «{dens}» (revísala contra el sentido de cada pieza):")
        print(json.dumps(AUD.proponer(piezas, dens), ensure_ascii=False, indent=1))
        print("\nLa música se le pregunta a Emi en cada video; su respuesta va en plan.json → sonido.musica."); return 0
    if c == "recorte":
        print("recortes: " + (", ".join(recortar_persona(d)) or "ninguna pieza `detras` en el plan")); return 0
    if c == "armar":
        r = armar(d)
        for x in r["avisos"]:
            print(f"⚠ {x}")
        print(f"composición armada: {r['piezas']} piezas, {r['grupos']} grupos de subtítulos · lint: {'sin errores' if r['lint_ok'] else 'CON ERRORES'} {r['lint'][0]}")
        return 0 if r["lint_ok"] else 1
    if c == "muestra":
        try:
            tiempos = [float(x) for x in a.en.split(",")]
        except ValueError as exc:
            raise ErrorEditor("--en lleva segundos separados por comas") from exc
        destino = d / "out" / "muestras" / a.nombre
        correr(["npx", "--no-install", "hyperframes", "snapshot", "--at", ",".join(f"{x:g}" for x in tiempos), "--no-end", "-o", str(destino.resolve())], cwd=d, capture_output=True)
        from PIL import Image
        cuadros = sorted(destino.glob("*.png"))
        if not cuadros:
            raise ErrorEditor("el motor no devolvió cuadros")
        imgs = [Image.open(f).convert("RGB") for f in cuadros]
        w, h = imgs[0].size
        e = 360 / w
        tira = Image.new("RGB", (len(imgs) * 368 + 8, int(h * e) + 16), "#18181c")
        for k, im in enumerate(imgs):
            tira.paste(im.resize((360, int(h * e))), (8 + k * 368, 8))
        tira.save(d / "out" / f"muestra-{a.nombre}.png")
        print(f"muestra: {d / 'out' / f'muestra-{a.nombre}.png'} ({len(imgs)} cuadros). Enséñasela a Emi antes de rendir."); return 0
    if c == "render":
        r = render(d, a.borrador)
        print(f"{r['final']}: {r['duracion_s']} s, {r['lufs']} LUFS, pico {r['pico']} dBTP")
        for grupo in ("avisos_plan", "avisos_audio", "avisos_video"):
            for x in r[grupo]:
                print(f"⚠ {x}")
        print("Sigue: `revisar`, mirar las hojas y llenar out/revision.json. Sin avisos significa en rango, no aprobado.")
        return 0
    if c == "revisar":
        print(f"hojas en {d / 'out'} (hoja.png, hoja-app.png, hoja-transiciones.png, hoja-telefono.png).\nMíralas y llena {crear_revision(d)}: "
              "los tres peores defectos con su segundo, corregir, volver a rendir y volver a revisar."); return 0
    if c == "nota":
        f = d / "out" / "publicacion.md"
        if f.exists():
            raise ErrorEditor("ya hay hoja de publicación; no se sobrescribe")
        f.parent.mkdir(exist_ok=True)
        f.write_text(NOTA.format(tema=d.name, espacio=espacio_de(d)), encoding="utf-8")
        print(f"hoja de publicación en {f}"); return 0
    if c == "cierre":
        print(cierre(d)); return 0
    raise ErrorEditor(f"comando desconocido: {c}")


if __name__ == "__main__":
    raise SystemExit(main())
