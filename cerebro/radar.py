#!/usr/bin/env python3
"""Radar semanal: qué está funcionando en TikTok y Reels en los temas de cada espacio.

Solo observa y ordena. No cambia el estilo de ningún espacio: lo que salga de aquí entra como
candidato y Emi decide. Sin --execute no gasta nada.

  python3 cerebro/radar.py plan                       qué se consultaría y cuánto costaría como máximo
  python3 cerebro/radar.py correr --execute           consulta, guarda datos e informe base de la semana
  python3 cerebro/radar.py informe private/tendencias/AAAA-Sss.json    rehace el informe desde los datos

Los datos crudos (enlaces exactos, descripciones completas y cuentas de terceros) se guardan en
private/tendencias/, que git ignora: no van al repositorio público. Al repositorio va solo el informe.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ESPACIOS = ("personal", "milla", "castorena", "pan")
MARCADOR = "proxy-injected"
# precio por resultado en el plan gratuito, leído de la ficha de cada actor el 11/11/2026
ACTORES = {
    "tiktok": {"actor": "clockworks~tiktok-scraper", "usd_por_resultado": 0.0037, "tope_minimo_usd": 0.5},
    "instagram": {"actor": "apify~instagram-hashtag-scraper", "usd_por_resultado": 0.0026, "tope_minimo_usd": 0.01},
}
POR_ETIQUETA = 8          # resultados por etiqueta
# USD que se le autorizan a Apify por semana. Emi aprobó 0.50 el 11/11/2026 y dijo «si es necesario usar más, hazlo».
# Hace falta 0.70: el actor de TikTok no acepta un tope menor de 0.50 por corrida, aunque lo esperado sea la mitad.
TOPE_SEMANAL = 0.70


class ErrorRadar(Exception):
    pass


def dir_espacios() -> Path:
    return Path(os.environ["RADAR_ESPACIOS"]) if os.environ.get("RADAR_ESPACIOS") else RAIZ.parent / "espacios"


def consultas() -> dict:
    """{plataforma: {etiqueta: [espacios que la siguen]}} a partir de espacios/<e>/radar.json."""
    out: dict = {p: {} for p in ACTORES}
    for e in ESPACIOS:
        f = dir_espacios() / e / "radar.json"
        if not f.exists():
            continue
        cfg = json.loads(f.read_text(encoding="utf-8"))
        for plataforma in ACTORES:
            for et in (cfg.get("etiquetas") or {}).get(plataforma, []):
                et = re.sub(r"[^\wáéíóúñü]", "", et.lower())
                if et:
                    out[plataforma].setdefault(et, []).append(e)
    return out


def tope_de(plataforma: str, etiquetas: int, por_etiqueta: int) -> float:
    """Lo que se le autoriza a Apify para esa corrida: lo esperado más 10 %, sin bajar del mínimo que exige el actor."""
    if not etiquetas:
        return 0.0
    cfg = ACTORES[plataforma]
    return max(cfg["tope_minimo_usd"], round(etiquetas * por_etiqueta * cfg["usd_por_resultado"] * 1.1, 3))


def costo_maximo(c: dict, por_etiqueta: int = POR_ETIQUETA) -> dict:
    """`total` es lo esperado (resultados × precio); `autorizado` es el tope real que se manda a Apify, que es lo que limita el gasto."""
    por = {p: round(len(c[p]) * por_etiqueta * ACTORES[p]["usd_por_resultado"], 3) for p in ACTORES}
    return {**por, "total": round(sum(por.values()), 3),
            "autorizado": round(sum(tope_de(p, len(c[p]), por_etiqueta) for p in ACTORES), 3)}


def _api(url: str, cuerpo: dict | None = None, espera: int = 60):
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode() if cuerpo is not None else None,
                                 method="POST" if cuerpo is not None else "GET",
                                 headers={"Authorization": "Bearer " + os.environ.get("APIFY_TOKEN", MARCADOR),
                                          "Content-Type": "application/json", "User-Agent": "radar-video/0.1 (python-urllib)"})
    with urllib.request.urlopen(req, timeout=espera) as r:
        return json.loads(r.read())


def _apify(actor: str, entrada: dict, tope: float, espera: int = 540) -> list:
    """Lanza la corrida, espera a que termine y trae sus resultados.

    No se usa la llamada «síncrona» de Apify: en corridas de más de un minuto la conexión se corta
    con un 502 aunque la corrida siga y se cobre (visto el 11/11/2026).
    """
    base = "https://api.apify.com/v2"
    try:
        corrida = _api(f"{base}/acts/{actor}/runs?maxTotalChargeUsd={tope}", entrada)["data"]
        limite = time.time() + espera
        while corrida.get("status") in ("READY", "RUNNING"):
            if time.time() > limite:
                raise ErrorRadar(f"{actor} no terminó en {espera} s (corrida {corrida.get('id')}); no se relanza para no cobrar doble")
            time.sleep(8)
            corrida = _api(f"{base}/actor-runs/{corrida['id']}")["data"]
        if corrida.get("status") != "SUCCEEDED":
            raise ErrorRadar(f"{actor} terminó como {corrida.get('status')} (corrida {corrida.get('id')})")
        datos = _api(f"{base}/datasets/{corrida['defaultDatasetId']}/items?clean=true", espera=120)
    except urllib.error.HTTPError as exc:
        raise ErrorRadar(f"Apify respondió HTTP {exc.code} con {actor}: {exc.read()[:200]!r}") from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
        raise ErrorRadar(f"sin respuesta de Apify con {actor}: {exc}. No se sabe si cobró: revisa el historial antes de reintentar") from exc
    if not isinstance(datos, list):
        raise ErrorRadar(f"Apify devolvió algo inesperado con {actor}: {str(datos)[:160]}")
    return datos


def _fecha(v) -> str:
    if isinstance(v, (int, float)) and v > 0:
        return dt.datetime.fromtimestamp(v, dt.timezone.utc).strftime("%Y-%m-%d")
    return str(v or "")[:10]


def normalizar(plataforma: str, x: dict) -> dict | None:
    """Un video de cualquiera de las dos plataformas, con los mismos campos. Lo que no venga queda en None."""
    if plataforma == "tiktok":
        if x.get("error") or not (x.get("webVideoUrl") or x.get("id")):
            return None
        etiquetas = [h.get("name") if isinstance(h, dict) else h for h in x.get("hashtags") or []]
        return {"plataforma": "tiktok", "url": x.get("webVideoUrl"), "autor": (x.get("authorMeta") or {}).get("name"),
                "texto": (x.get("text") or "").strip(), "duracion_s": (x.get("videoMeta") or {}).get("duration"),
                "vistas": x.get("playCount"), "likes": x.get("diggCount"), "comentarios": x.get("commentCount"),
                "compartidos": x.get("shareCount"), "guardados": x.get("collectCount"),
                "fecha": _fecha(x.get("createTimeISO") or x.get("createTime")), "etiquetas": [e for e in etiquetas if e],
                "sonido": (x.get("musicMeta") or {}).get("musicName"), "consulta": (x.get("searchHashtag") or {}).get("name") or x.get("input")}
    if plataforma == "instagram":
        if x.get("error") or not x.get("url"):
            return None
        if str(x.get("type", "")).lower() not in ("video", "reel", "clips") and not x.get("videoUrl") and x.get("videoDuration") is None:
            return None                      # solo video: una foto o un carrusel no dicen nada de edición
        entrada = str(x.get("inputUrl") or "")
        m = re.search(r"/tags/([^/?#]+)", entrada)
        return {"plataforma": "instagram", "url": x.get("url"), "autor": x.get("ownerUsername"),
                "texto": (x.get("caption") or "").strip(), "duracion_s": x.get("videoDuration"),
                "vistas": x.get("videoPlayCount") or x.get("videoViewCount"), "likes": x.get("likesCount"),
                "comentarios": x.get("commentsCount"), "compartidos": None, "guardados": None,
                "fecha": _fecha(x.get("timestamp")), "etiquetas": list(x.get("hashtags") or []),
                "sonido": (x.get("musicInfo") or {}).get("song_name"), "consulta": m.group(1) if m else None}
    raise ErrorRadar(f"plataforma desconocida: {plataforma}")


def puntaje(v: dict, hoy: dt.date) -> float:
    """Alcance por día y participación, en escala logarítmica. Sirve para ordenar, no es una métrica oficial."""
    vistas = v.get("vistas") or 0
    try:
        dias = max(1, (hoy - dt.date.fromisoformat(v["fecha"])).days)
    except (ValueError, TypeError):
        dias = 30
    interacciones = sum(v.get(k) or 0 for k in ("likes", "comentarios", "compartidos", "guardados"))
    participacion = interacciones / vistas if vistas else 0.0
    return round(0.6 * math.log10(1 + vistas / dias) + 0.4 * math.log10(1 + 1000 * participacion), 3)


def gancho(texto: str) -> str:
    """Primera línea de la descripción: lo más parecido al gancho que se puede leer sin ver el video."""
    primera = re.split(r"[\n.!?¿¡]", texto.strip())[0] if texto.strip() else ""
    primera = re.sub(r"#\S+", "", primera).strip()
    return primera[:90]


def enlace_publico(v: dict) -> str:
    """Enlace que puede ir al repositorio. Un identificador largo de solo dígitos (los de TikTok) dispara el
    detector de números de tarjeta del repositorio, así que ahí se enlaza el perfil y se da la fecha del video."""
    url = str(v.get("url") or "")
    if re.search(r"\d{13,}", url):
        autor = re.sub(r"[^\w.]", "", str(v.get("autor") or ""))
        base = f"https://www.{v.get('plataforma')}.com/@{autor}" if autor else v.get("plataforma", "")
        return f"{base} (video del {v.get('fecha') or 's/f'})"
    return url


def correr(por_etiqueta: int = POR_ETIQUETA, tope_semanal: float = TOPE_SEMANAL, hoy: dt.date | None = None, pedir=_apify) -> dict:
    hoy = hoy or dt.date.today()
    c = consultas()
    maximo = costo_maximo(c, por_etiqueta)
    if maximo["autorizado"] > tope_semanal + 1e-9:
        raise ErrorRadar(f"el plan autorizaría hasta {maximo['autorizado']} USD y el tope semanal es {tope_semanal}: baja --por-etiqueta, "
                         "quita etiquetas en espacios/<e>/radar.json o pídele a Emi subir el tope")
    videos, errores = [], []
    for plataforma, etiquetas in c.items():
        if not etiquetas:
            continue
        cfg = ACTORES[plataforma]
        tope = tope_de(plataforma, len(etiquetas), por_etiqueta)
        if plataforma == "tiktok":
            entrada = {"hashtags": sorted(etiquetas), "resultsPerPage": por_etiqueta, "shouldDownloadVideos": False,
                       "shouldDownloadCovers": False, "shouldDownloadSubtitles": False, "shouldDownloadSlideshowImages": False}
        else:
            entrada = {"hashtags": sorted(etiquetas), "resultsLimit": por_etiqueta, "resultsType": "reels"}
        try:
            crudos = pedir(cfg["actor"], entrada, tope)
        except ErrorRadar as exc:
            errores.append(str(exc))
            continue
        for x in crudos:
            v = normalizar(plataforma, x)
            if not v:
                continue
            consulta = re.sub(r"[^\wáéíóúñü]", "", str(v.get("consulta") or "").lower())
            propias = {re.sub(r"[^\wáéíóúñü]", "", str(e).lower()) for e in v["etiquetas"]}
            v["espacios"] = sorted({e for et, esp in etiquetas.items() if et == consulta or et in propias for e in esp})
            v["puntaje"] = puntaje(v, hoy)
            videos.append(v)
    semana = f"{hoy.isocalendar().year}-S{hoy.isocalendar().week:02d}"
    return {"semana": semana, "fecha": hoy.isoformat(), "por_etiqueta": por_etiqueta, "costo_maximo_usd": maximo,
            "consultas": {p: sorted(e) for p, e in c.items()}, "errores": errores,
            "videos": sorted(videos, key=lambda v: -v["puntaje"])}


def _mediana(xs: list) -> float | None:
    xs = sorted(x for x in xs if isinstance(x, (int, float)))
    return xs[len(xs) // 2] if xs else None


def informe(datos: dict) -> str:
    """Informe base: solo lo observado. La lectura («qué proponer») la añade quien revisa, marcada como inferencia."""
    L = [f"# Tendencias · {datos['semana']}", "",
         f"Generado el {datos['fecha']} con `cerebro/radar.py`. **Todo aquí es observación**, no regla: nada cambia el estilo de un espacio "
         "hasta que Emi lo apruebe o un video suyo lo confirme con sus propias métricas.", "",
         "Límites: son pocos videos por etiqueta (una muestra, no un censo); las plataformas no publican su algoritmo; "
         "las vistas de un tercero no dicen por qué funcionó.", ""]
    if datos.get("errores"):
        L += ["## Lo que no se pudo consultar", ""] + [f"- {e}" for e in datos["errores"]] + [""]
    for e in ESPACIOS:
        suyos = [v for v in datos["videos"] if e in v.get("espacios", [])]
        L += [f"## {e}", ""]
        if not suyos:
            L += ["Sin videos esta semana (revisa las etiquetas en `espacios/" + e + "/radar.json`).", ""]
            continue
        dur = _mediana([v.get("duracion_s") for v in suyos[:10]])
        et = Counter(x.lower() for v in suyos for x in v["etiquetas"]).most_common(8)
        son = Counter(v["sonido"] for v in suyos if v.get("sonido")).most_common(3)
        L += [f"- Videos vistos: {len(suyos)}. Duración mediana de los 10 mejores: {f'{dur:.0f} s' if dur else 'sin dato'}.",
              "- Etiquetas que más se repiten: " + (", ".join(f"#{k} ({n})" for k, n in et) or "sin dato") + ".",
              "- Sonidos repetidos: " + (", ".join(f"«{k}» ({n})" for k, n in son if n > 1) or "ninguno se repite") + ".", "",
              "| # | Plataforma | Vistas | Dura | Arranque de la descripción | Enlace |", "|---|---|---|---|---|---|"]
        for k, v in enumerate(suyos[:8], 1):
            dura = f"{v['duracion_s']:.0f} s" if isinstance(v.get("duracion_s"), (int, float)) else "—"
            vistas = f"{v['vistas']:,}".replace(",", " ") if isinstance(v.get("vistas"), int) else "—"
            L.append(f"| {k} | {v['plataforma']} | {vistas} | {dura} | {gancho(v['texto']).replace('|', '/') or '—'} | {enlace_publico(v)} |")
        L.append("")
    L += ["## Lectura de la semana (la escribe quien revisa)", "",
          "Para cada espacio: qué se repite en los mejores (duración, tipo de gancho, cierres, ritmo de edición si se vieron), "
          "qué se propone probar y en qué video. Cada frase lleva su tipo: **declaración oficial** (con enlace), **observación** (de la tabla) "
          "o **inferencia**.", "", "## Fuentes oficiales revisadas", "", "- (enlace, fecha y qué dice)", "",
          "## Bibliotecas de sonido revisadas", "", "- (nombre, licencia leída y enlace; nada entra a una skill sin esto)", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Radar semanal de tendencias de video")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nombre in ("plan", "correr"):
        s = sub.add_parser(nombre)
        s.add_argument("--por-etiqueta", type=int, default=POR_ETIQUETA)
        s.add_argument("--tope", type=float, default=TOPE_SEMANAL)
        if nombre == "correr":
            s.add_argument("--execute", action="store_true")
    s = sub.add_parser("informe"); s.add_argument("datos", type=Path)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "informe":
            try:
                print(informe(json.loads(a.datos.read_text(encoding="utf-8"))))
            except (OSError, ValueError, KeyError) as exc:
                raise ErrorRadar(f"no se pudo leer {a.datos}: {exc}") from exc
            return 0
        c = consultas()
        maximo = costo_maximo(c, a.por_etiqueta)
        if a.cmd == "plan" or not a.execute:
            for p, et in c.items():
                print(f"{p}: {len(et)} etiquetas × {a.por_etiqueta} resultados → hasta {maximo[p]} USD\n  " + ", ".join(f"#{k} ({'/'.join(v)})" for k, v in sorted(et.items())))
            print(f"Costo esperado: {maximo['total']} USD. Tope que se autoriza a Apify: {maximo['autorizado']} USD (tope semanal {a.tope}). "
                  + ("" if a.cmd == "plan" else "Repite con --execute para consultar."))
            if maximo["autorizado"] > a.tope:
                print("✗ pasa del tope semanal: no correría.")
                return 1
            return 0
        datos = correr(a.por_etiqueta, a.tope)
        destino = RAIZ.parent / "private" / "tendencias" / f"{datos['semana']}.json"      # privado: git lo ignora
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        publico = RAIZ / "tendencias" / f"{datos['semana']}.md"
        publico.parent.mkdir(exist_ok=True)
        publico.write_text(informe(datos), encoding="utf-8")
        print(f"{len(datos['videos'])} videos → informe {publico}; datos completos (privados, con los enlaces exactos) {destino}")
        for e in datos["errores"]:
            print(f"⚠ {e}")
        return 0
    except ErrorRadar as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
