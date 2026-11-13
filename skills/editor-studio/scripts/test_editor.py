"""Pruebas de Editor Studio. No usan red ni gastan saldo.

    python3 -m unittest discover -s skills/editor-studio/scripts -p 'test_*.py'
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
import wave
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import numpy as np  # noqa: E402

import audio as AUD  # noqa: E402
import comun  # noqa: E402
import corte as COR  # noqa: E402
import editor as ED  # noqa: E402
import montaje as MON  # noqa: E402
import transcripcion as TRA  # noqa: E402
from comun import ErrorEditor  # noqa: E402

HAY_FFMPEG = shutil.which("ffmpeg") is not None


def pal(*trios):
    return [{"i": k, "t0": a, "t1": b, "txt": t} for k, (a, b, t) in enumerate(trios)]


def wav_con_voz(ruta: Path, tramos, total: float, hz: int = 16000):
    """Tono a -20 dB donde «hay voz» y ruido a -60 dB en lo demás."""
    n = int(total * hz)
    rng = np.random.default_rng(7)
    x = rng.normal(0, 0.001, n)
    t = np.arange(n) / hz
    for a, b in tramos:
        m = (t >= a) & (t < b)
        x[m] += 0.1 * np.sin(2 * np.pi * 180 * t[m])
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(hz)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    return ruta


class Corte(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_normal_quita_acentos_y_signos(self):
        self.assertEqual(COR.normal("¿Güey?"), "guey")
        self.assertEqual(COR.normal("Básicamente,"), "basicamente")

    def test_silencio_largo_se_recorta_y_deja_aire(self):
        w = wav_con_voz(self.tmp / "a.wav", [(0.5, 2.0), (4.0, 6.0)], 6.5)
        p = COR.plan(w, pal((0.5, 2.0, "hola."), (4.0, 6.0, "adiós")), "natural", 30)
        medio = [c for c in p["cortes"] if 2.0 < c["t0"] < 4.0]
        self.assertEqual(len(medio), 1)
        c = medio[0]
        self.assertGreaterEqual(c["t0"], 2.0 + 0.16)          # aire a la izquierda (más, por ser fin de frase)
        self.assertLessEqual(c["t1"], 4.0 - 0.15)             # aire a la derecha
        self.assertAlmostEqual(c["t0"] * 30, round(c["t0"] * 30), places=3)   # cae en cuadro exacto

    def test_pausa_corta_no_se_toca_en_ritmo_natural(self):
        w = wav_con_voz(self.tmp / "a.wav", [(0.2, 2.0), (2.4, 4.0)], 4.2)
        p = COR.plan(w, pal((0.2, 2.0, "uno"), (2.4, 4.0, "dos")), "natural", 30)
        self.assertFalse([c for c in p["cortes"] if 2.0 <= c["t0"] <= 2.4])

    def test_ritmo_apretado_corta_mas_que_minimo(self):
        w = wav_con_voz(self.tmp / "a.wav", [(0.2, 2.0), (2.9, 4.0)], 4.2)
        palabras = pal((0.2, 2.0, "uno"), (2.9, 4.0, "dos"))
        quita = lambda r: sum(c["t1"] - c["t0"] for c in COR.plan(w, palabras, r, 30)["cortes"])  # noqa: E731
        self.assertGreater(quita("apretado"), quita("natural"))
        self.assertGreater(quita("natural"), quita("minimo"))

    def test_ritmo_desconocido_falla(self):
        w = wav_con_voz(self.tmp / "a.wav", [(0.2, 1.0)], 1.5)
        with self.assertRaises(ErrorEditor):
            COR.plan(w, [], "frenetico", 30)

    def test_un_corte_nunca_cae_dentro_de_una_palabra(self):
        # la transcripción dice que la palabra sigue aunque la energía baje
        w = wav_con_voz(self.tmp / "a.wav", [(0.2, 1.0), (3.0, 4.0)], 4.2)
        palabras = pal((0.2, 1.9, "larguísima"), (3.0, 4.0, "fin"))
        for c in COR.plan(w, palabras, "natural", 30)["cortes"]:
            for q in palabras:
                self.assertFalse(q["t0"] < c["t0"] < q["t1"], c)
                self.assertFalse(q["t0"] < c["t1"] < q["t1"], c)

    def test_muletilla_segura_se_propone_y_dudosa_solo_aislada(self):
        palabras = pal((0.0, 0.5, "Hola"), (0.9, 1.1, "eh"), (1.5, 2.0, "este"), (2.4, 3.0, "video"), (3.02, 3.2, "este"), (3.22, 3.6, "año"))
        m = COR.proponer_muletillas(palabras, 30)
        textos = [c["texto"] for c in m]
        self.assertIn("eh", textos)
        self.assertEqual(textos.count("este"), 1)             # el «este año» pegado no es muletilla

    def test_toma_repetida_gana_la_ultima(self):
        palabras = pal((0.0, 0.3, "La"), (0.3, 0.7, "primera"), (0.7, 1.0, "lee"), (1.0, 1.3, "la"), (1.3, 1.6, "letra."),
                       (3.0, 3.3, "La"), (3.3, 3.7, "primera"), (3.7, 4.0, "lee"), (4.0, 4.3, "la"), (4.3, 4.6, "letra"), (4.6, 5.0, "chiquita."))
        t = COR.proponer_tomas(palabras, 30)
        self.assertEqual(len(t), 1)
        self.assertLess(t[0]["t1"], 3.0)                      # no se come la toma buena
        self.assertLessEqual(t[0]["t0"], 0.05)
        self.assertIn("gana", t[0]["motivo"])

    def test_frases_distintas_no_son_toma_repetida(self):
        palabras = pal((0.0, 0.4, "Hoy"), (0.4, 0.8, "hablamos"), (0.8, 1.2, "de"), (1.2, 1.6, "contratos."),
                       (2.5, 2.9, "Mañana"), (2.9, 3.3, "vemos"), (3.3, 3.7, "otra"), (3.7, 4.1, "cosa."))
        self.assertEqual(COR.proponer_tomas(palabras, 30), [])

    def test_groseria_se_tapa_y_modismo_solo_se_avisa(self):
        c = COR.proponer_censura(pal((0, 0.3, "pendejo"), (0.4, 0.7, "güey,"), (0.8, 1.0, "casa")))
        self.assertEqual([(x["texto"], x["accion"]) for x in c], [("pendejo", "tapar"), ("güey,", "avisar")])

    def test_unir_funde_cortes_separados_por_aire_pero_no_si_hay_palabra(self):
        base = [{"t0": 1.0, "t1": 2.0, "tipo": "silencio", "motivo": "pausa"}, {"t0": 2.1, "t1": 2.5, "tipo": "muletilla", "motivo": "sonido de relleno", "texto": "eh"}]
        junto = COR.unir(base, 30, [])
        self.assertEqual(len(junto), 1)
        self.assertEqual((junto[0]["tipo"], junto[0]["t0"], junto[0]["t1"]), ("muletilla", 1.0, 2.5))
        separado = COR.unir(base, 30, pal((2.02, 2.08, "y")))
        self.assertEqual(len(separado), 2)

    def test_tramos_remapeo_y_empalmes(self):
        p = {"fps": 30, "duracion_crudo_s": 10.0, "cortes": [{"t0": 2.0, "t1": 4.0, "estado": "aprobado"}, {"t0": 6.0, "t1": 7.0, "estado": "descartado"}]}
        quedan = COR.tramos_que_quedan(p)
        self.assertEqual(quedan, [(0.0, 2.0), (4.0, 10.0)])
        limpias = COR.remapear(pal((1.0, 1.5, "a"), (2.5, 3.0, "quitada"), (5.0, 5.5, "b")), quedan)
        self.assertEqual([(w["txt"], w["t0"]) for w in limpias], [("a", 1.0), ("b", 3.0)])
        self.assertEqual(COR.empalmes(quedan), [2.0])
        self.assertEqual(COR.tiempo_limpio(5.0, quedan), 3.0)
        self.assertIsNone(COR.tiempo_limpio(3.0, quedan))

    def test_rebanada_de_menos_de_dos_cuadros_no_se_conserva(self):
        p = {"fps": 30, "duracion_crudo_s": 10.0, "cortes": [{"t0": 2.0, "t1": 9.99, "estado": "aprobado"}]}
        self.assertEqual(COR.tramos_que_quedan(p), [(0.0, 2.0)])

    def test_sin_aprobacion_no_se_corta_y_un_cambio_la_invalida(self):
        p = {"fps": 30, "duracion_crudo_s": 5.0, "cortes": [{"t0": 1.0, "t1": 2.0, "estado": "aprobado"}], "aprobacion": None}
        with self.assertRaises(ErrorEditor):
            COR.exigir_aprobacion(p)
        p["aprobacion"] = {"por": "Emi", "huella": COR.huella_plan(p)}
        COR.exigir_aprobacion(p)
        p["cortes"][0]["t1"] = 2.5
        with self.assertRaises(ErrorEditor):
            COR.exigir_aprobacion(p)

    def test_corte_sin_decidir_bloquea(self):
        p = {"fps": 30, "duracion_crudo_s": 5.0, "cortes": [{"t0": 1.0, "t1": 2.0, "estado": "dudoso"}]}
        p["aprobacion"] = {"por": "Emi", "huella": COR.huella_plan(p)}
        with self.assertRaises(ErrorEditor):
            COR.exigir_aprobacion(p)

    @unittest.skipUnless(HAY_FFMPEG, "sin FFmpeg")
    def test_aplicar_deja_la_duracion_exacta(self):
        fuente = self.tmp / "f.mp4"
        comun.correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=180x320:r=30:d=4", "-f", "lavfi", "-i", "sine=f=220:d=4",
                      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(fuente)], capture_output=True)
        COR.aplicar(fuente, self.tmp / "o.mp4", [(0.0, 1.0), (2.0, 3.5)], 30)
        self.assertAlmostEqual(comun.duracion(self.tmp / "o.mp4"), 2.5, delta=0.08)


class Transcripcion(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_srt_reparte_y_marca_aproximado(self):
        f = self.tmp / "a.srt"
        f.write_text("1\n00:00:01,000 --> 00:00:03,000\nHola a todos\n\n2\n00:00:04,000 --> 00:00:05,000\n<i>Adiós</i>\n", encoding="utf-8")
        t = TRA.de_archivo(f)
        self.assertTrue(t["aproximado"])
        self.assertEqual([p["txt"] for p in t["palabras"]], ["Hola", "a", "todos", "Adiós"])
        self.assertAlmostEqual(t["palabras"][0]["t0"], 1.0)
        self.assertAlmostEqual(t["palabras"][2]["t1"], 3.0)

    def test_json_con_palabras_en_milisegundos(self):
        f = self.tmp / "a.json"
        f.write_text(json.dumps({"words": [{"text": "Hola", "start": 100000, "end": 100400}, {"text": "tú", "start": 100500, "end": 100800}]}))
        t = TRA.de_archivo(f)
        self.assertFalse(t["aproximado"])
        self.assertAlmostEqual(t["palabras"][0]["t0"], 100.0)

    def test_json_con_frases_es_aproximado(self):
        f = self.tmp / "a.json"
        f.write_text(json.dumps({"segments": [{"text": "Hola a todos", "start": 0.0, "end": 1.5}]}))
        t = TRA.de_archivo(f)
        self.assertTrue(t["aproximado"])
        self.assertEqual(len(t["palabras"]), 3)

    def test_json_con_palabras_dentro_de_segmentos(self):
        f = self.tmp / "a.json"
        f.write_text(json.dumps({"segments": [{"text": "Hola tú", "start": 0, "end": 1, "words": [{"word": "Hola", "start": 0.0, "end": 0.4}, {"word": "tú", "start": 0.5, "end": 0.9}]},
                                              {"text": "ya", "start": 1, "end": 2, "words": [{"word": "ya", "start": 1.2, "end": 1.5}]}]}))
        t = TRA.de_archivo(f)
        self.assertFalse(t["aproximado"])
        self.assertEqual([p["txt"] for p in t["palabras"]], ["Hola", "tú", "ya"])

    def test_formato_no_admitido_y_vacio(self):
        f = self.tmp / "a.docx"
        f.write_text("x")
        with self.assertRaises(ErrorEditor):
            TRA.de_archivo(f)
        with self.assertRaises(ErrorEditor):
            TRA._salida("x", "es", [])

    def test_palabras_encimadas_se_separan(self):
        t = TRA._salida("x", "es", [{"t0": 0.0, "t1": 1.0, "txt": "a"}, {"t0": 0.8, "t1": 1.5, "txt": "b"}])
        self.assertLessEqual(t["palabras"][0]["t1"], t["palabras"][1]["t0"])

    def test_comparar_dos_motores(self):
        a = TRA._salida("uno", "es", [{"t0": 0, "t1": 0.4, "txt": "Hola"}, {"t0": 0.5, "t1": 0.7, "txt": "eh"}, {"t0": 0.8, "t1": 1.2, "txt": "mundo"}])
        b = TRA._salida("dos", "es", [{"t0": 0.02, "t1": 0.4, "txt": "hola"}, {"t0": 0.82, "t1": 1.2, "txt": "mundo"}])
        r = TRA.comparar(a, b)
        self.assertEqual(r["muletillas"], {"uno": 1, "dos": 0})
        self.assertEqual(len(r["diferencias"]), 1)

    def test_texto_legible_parte_por_pausas(self):
        t = {"palabras": pal((0, 0.5, "Hola."), (2.0, 2.5, "Adiós"))}
        self.assertEqual(TRA.texto_legible(t).count("\n"), 2)


PERFIL = {"espacio": "personal", "colores": {"papel": "#F4ECD6", "tinta": "#20180F", "acento": "#FF5A1F", "apoyo": "#FFD23F"}, "titular": "Anton",
          "subtitulos": "Anton", "edicion": {"estado": "candidato", "fuente_titular": "Anton", "fuente_texto": "Inter", "movimiento": "suave",
                                             "subtitulos": {"modo": "karaoke", "estilo": "contorno", "mayusculas": True, "zona": "pecho", "max_palabras": 3},
                                             "marca_en_pantalla": None, "nivel_tope": 3, "sonido": {"densidad": "media"}}}
BRIEF = {"respuestas_emi": {"para_que": "x", "a_quien": "x", "postura": "x", "tipo_de_video": "opinion", "donde_se_publica": "x",
                            "nivel_elegido": "2", "musica": "ninguna", "quienes_salen": "Emi"}}
PALABRAS = pal((0.5, 0.9, "Hoy"), (1.0, 1.4, "tres"), (1.5, 2.0, "cosas."), (3.0, 3.4, "Ocho"), (3.5, 3.9, "de"), (4.0, 4.5, "diez"), (6.0, 6.5, "opinas"))
ROSTRO = {"cajas": [{"t": 0.0, "x0": 300, "y0": 420, "x1": 780, "y1": 900}]}


def plan(**extra):
    p = {"espacio": "personal", "formato": "9:16", "nivel": 2, "nivel_razon": "prueba de las reglas",
         "subtitulos": {"modo": "karaoke", "razon": "reel rápido del espacio personal"}, "piezas": [],
         "sonido": {"densidad": "minima", "efectos": [], "musica": {"decision": "ninguna", "preguntado_a_emi": True}}}
    p.update(extra)
    return p


def validar(p, brief=BRIEF, rostro=ROSTRO, archivos=(), empalmes=(), aproximado=False, perfil=PERFIL):
    return MON.validar(p, brief, perfil, PALABRAS, 8.0, rostro, list(empalmes), set(archivos), 30, aproximado)


class Montaje(unittest.TestCase):
    def test_ancla_por_palabra_aparicion_y_desfase(self):
        self.assertEqual(MON.resolver_ancla({"palabra": "TRES"}, PALABRAS), 1.0)
        self.assertEqual(MON.resolver_ancla({"palabra": "cosas", "al_final": True, "desfase": 0.1}, PALABRAS), 2.1)
        self.assertEqual(MON.resolver_ancla({"t": 3.2}, PALABRAS), 3.2)
        with self.assertRaises(ErrorEditor):
            MON.resolver_ancla({"palabra": "inexistente"}, PALABRAS)
        with self.assertRaises(ErrorEditor):
            MON.resolver_ancla({"palabra": "tres"}, PALABRAS, aproximado=True)

    def test_plan_minimo_valido(self):
        err, avi, piezas = validar(plan(piezas=[{"tipo": "titulo", "texto": "Tres *cosas*", "ancla": {"palabra": "tres"}, "porque": "anuncia lo que viene"},
                                               {"tipo": "cierre", "texto": "COMENTA", "ancla": {"palabra": "opinas"}, "dura": 1.5, "porque": "la voz pide opinión"}]))
        self.assertEqual(err, [])
        self.assertEqual(piezas[0]["zona"], "arriba")

    def test_sin_entrevista_no_se_edita(self):
        err, _, _ = validar(plan(), brief={"respuestas_emi": {}})
        self.assertTrue(any("para_que" in e for e in err))
        self.assertTrue(any("musica" in e for e in err))

    def test_pieza_sin_porque_o_de_otro_nivel_falla(self):
        err, _, _ = validar(plan(nivel=1, piezas=[{"tipo": "zoom", "ancla": {"palabra": "tres"}}]),
                            brief={"respuestas_emi": {**BRIEF["respuestas_emi"], "nivel_elegido": "1"}})
        self.assertTrue(any("porque" in e for e in err))
        self.assertTrue(any("nivel 2" in e for e in err))

    def test_tramo_sube_el_nivel_solo_ahi(self):
        base = {"tipo": "particulas", "porque": "remate del cierre final"}
        err, _, _ = validar(plan(tramos=[{"de": 5.5, "a": 8, "nivel": 3}], piezas=[{**base, "ancla": {"palabra": "opinas"}}]))
        self.assertEqual(err, [])
        err, _, _ = validar(plan(tramos=[{"de": 5.5, "a": 8, "nivel": 3}], piezas=[{**base, "ancla": {"palabra": "tres"}}]))
        self.assertTrue(any("nivel 3" in e for e in err))

    def test_nivel_del_plan_debe_ser_el_que_eligio_emi(self):
        err, _, _ = validar(plan(nivel=3))
        self.assertTrue(any("Emi eligió" in e for e in err))

    def test_texto_no_tapa_la_cara_y_se_mueve_de_zona(self):
        cara_arriba = {"cajas": [{"t": 0.0, "x0": 200, "y0": 250, "x1": 900, "y1": 1000}]}
        err, avi, piezas = validar(plan(piezas=[{"tipo": "titulo", "texto": "Hola", "zona": "arriba", "ancla": {"palabra": "tres"}, "porque": "prueba de zonas"}]), rostro=cara_arriba)
        self.assertEqual(err, [])
        self.assertEqual(piezas[0]["zona"], "torso")
        self.assertGreaterEqual(piezas[0]["caja"][1], 1000)           # empieza bajo la cara
        self.assertLessEqual(piezas[0]["caja"][3], 1230)              # y termina antes de los subtítulos
        self.assertTrue(any("pasó de" in a for a in avi))

    def test_sin_zona_libre_es_error_y_la_franja_de_subtitulos_no_se_usa(self):
        enorme = {"cajas": [{"t": 0.0, "x0": 0, "y0": 230, "x1": 1080, "y1": 1200}]}
        err, _, _ = validar(plan(piezas=[{"tipo": "titulo", "texto": "Hola", "ancla": {"palabra": "tres"}, "porque": "prueba de zonas"}]), rostro=enorme)
        self.assertTrue(any("no hay zona libre" in e for e in err))
        err, _, _ = validar(plan(piezas=[{"tipo": "titulo", "texto": "Hola", "zona": "pecho", "ancla": {"palabra": "tres"}, "porque": "prueba de zonas"}]))
        self.assertTrue(any("es de los subtítulos" in e for e in err))

    def test_dos_piezas_no_comparten_zona_a_la_vez(self):
        _, _, piezas = validar(plan(piezas=[{"tipo": "titulo", "texto": "Uno", "ancla": {"t": 1.0}, "dura": 2, "porque": "prueba de zonas"},
                                           {"tipo": "sello", "texto": "DOS", "ancla": {"t": 1.5}, "dura": 1, "porque": "prueba de zonas"}]))
        self.assertNotEqual(piezas[0]["zona"], piezas[1]["zona"])

    def test_dato_sin_fuente_no_pasa(self):
        err, _, _ = validar(plan(piezas=[{"tipo": "dato", "cifra": "8 de 10", "ancla": {"palabra": "Ocho"}, "porque": "la cifra se oye ahí"}]))
        self.assertTrue(any("sin fuente" in e for e in err))

    def test_zoom_suave_lejos_de_un_corte_y_sin_encimarse(self):
        z = lambda **k: {"tipo": "zoom", "ancla": {"t": 3.0}, "porque": "subraya la cifra", **k}  # noqa: E731
        self.assertTrue(any("suaves" in e for e in validar(plan(piezas=[z(z=1.4)]))[0]))
        self.assertTrue(any("mismo cuadro de un corte" in e for e in validar(plan(piezas=[z()]), empalmes=[3.05])[0]))
        self.assertTrue(any("se encima" in e for e in validar(plan(piezas=[z(), z(ancla={"t": 3.5})]))[0]))
        self.assertEqual(validar(plan(piezas=[z()]), empalmes=[1.0])[0], [])

    def test_panel_no_convive_con_otras_piezas_ni_zoom(self):
        p = plan(piezas=[{"id": "pan", "tipo": "panel", "items": ["a", "b"], "ancla": {"t": 2.0}, "dura": 3, "porque": "resume la lista"},
                         {"id": "ti", "tipo": "titulo", "texto": "Hola", "ancla": {"t": 3.0}, "dura": 1, "porque": "prueba de panel"}])
        self.assertTrue(any("sigue en pantalla" in e for e in validar(p)[0]))

    def test_video_generado_exige_cotizacion_y_permiso(self):
        ins = {"tipo": "inserto", "archivo": "b.mp4", "origen": "generado", "ancla": {"t": 3.0}, "porque": "ilustra la analogía"}
        err, _, _ = validar(plan(nivel=3, piezas=[ins]), brief={"respuestas_emi": {**BRIEF["respuestas_emi"], "nivel_elegido": "3"}}, archivos={"b.mp4"})
        self.assertTrue(any("se cotiza" in e for e in err))
        self.assertTrue(any("gasto_autorizado" in e for e in err))
        ok = {**ins, "autorizado_por_emi": True, "costo_creditos": 9}
        err, _, _ = validar(plan(nivel=3, piezas=[ok]), brief={"respuestas_emi": {**BRIEF["respuestas_emi"], "nivel_elegido": "3"}, "gasto_autorizado": {"por": "Emi", "creditos": 20}}, archivos={"b.mp4"})
        self.assertEqual(err, [])

    def test_archivo_fuera_de_assets_o_inexistente(self):
        f = lambda a: validar(plan(piezas=[{"tipo": "foto", "archivo": a, "origen_descripcion": "captura propia", "ancla": {"t": 3.0}, "porque": "enseña el documento"}]), archivos={"si.png"})[0]  # noqa: E731
        self.assertEqual(f("si.png"), [])
        self.assertTrue(any("no existe" in e for e in f("no.png")))
        self.assertTrue(any("dentro de assets" in e for e in f("../secreto.png")))

    def test_detras_exige_su_recorte(self):
        d = {"id": "d1", "tipo": "detras", "texto": "FIRMAR", "ancla": {"t": 3.0}, "porque": "palabra clave del gancho"}
        br = {"respuestas_emi": {**BRIEF["respuestas_emi"], "nivel_elegido": "3"}}
        self.assertTrue(any("recorte-d1.webm" in e for e in validar(plan(nivel=3, piezas=[d]), brief=br)[0]))
        self.assertEqual(validar(plan(nivel=3, piezas=[d]), brief=br, archivos={"recorte-d1.webm"})[0], [])

    def test_subtitulos_necesitan_razon_y_karaoke_tiempos_exactos(self):
        self.assertTrue(any("subtitulos.razon" in e for e in validar(plan(subtitulos={"modo": "karaoke"}))[0]))
        self.assertTrue(any("aproximada" in e for e in validar(plan(), aproximado=True)[0]))

    def test_musica_y_efectos(self):
        s = lambda **k: plan(sonido={"densidad": "minima", "efectos": [], "musica": {"decision": "ninguna", "preguntado_a_emi": True}, **k})  # noqa: E731
        self.assertTrue(any("musica.decision" in e for e in validar(s(musica={"decision": "", "preguntado_a_emi": True}))[0]))
        self.assertTrue(any("origen" in e for e in validar(s(musica={"decision": "archivo", "archivo": "m.mp3", "preguntado_a_emi": True}), archivos={"m.mp3"})[0]))
        self.assertTrue(any("no existe" in e for e in validar(s(efectos=[{"t": 1, "sonido": "trompeta"}]))[0]))
        self.assertTrue(any("la pieza" in e for e in validar(s(efectos=[{"en": "fantasma", "sonido": "pop"}]))[0]))

    def test_marca_en_pantalla_solo_si_emi_la_definio(self):
        self.assertTrue(any("marca_en_pantalla" in e for e in validar(plan(marca_en_pantalla=True))[0]))

    def test_aviso_de_tramo_quieto(self):
        _, avi, _ = validar(plan())
        self.assertTrue(any("sin nada nuevo" in a for a in avi))

    def test_grupos_cortan_en_pausa_punto_y_maximo(self):
        g = MON.grupos_de_subtitulos(PALABRAS, {"modo": "karaoke", "mayusculas": True, "max_palabras": 3})
        self.assertEqual([[w["txt"] for w in x["palabras"]] for x in g], [["HOY", "TRES", "COSAS"], ["OCHO", "DE", "DIEZ"], ["OPINAS"]])
        self.assertTrue(all(a["t1"] <= b["t0"] for a, b in zip(g, g[1:])))       # nunca dos grupos a la vez
        self.assertEqual(MON.grupos_de_subtitulos(PALABRAS, {"modo": "ninguno"}), [])

    def test_groseria_tapada_no_se_lee_en_subtitulos(self):
        g = MON.grupos_de_subtitulos(pal((0, 0.4, "qué"), (0.5, 0.9, "pendejo")), {"modo": "frase"}, [{"i": 1, "accion": "tapar"}])
        self.assertEqual(g[0]["palabras"][1]["txt"], "p******")

    def test_subtitulos_ocultos_en_una_ventana(self):
        g = MON.grupos_de_subtitulos(PALABRAS, {"modo": "frase", "ocultar": [[2.5, 5.0]]})
        self.assertNotIn("Ocho", [w["txt"] for x in g for w in x["palabras"]])

    def test_tamano_de_texto_cabe_en_el_ancho(self):
        t = MON.tamano_texto("UNA FRASE BASTANTE LARGA PARA UNA LINEA", "Anton", 800, 120, 40)
        self.assertLessEqual(t * 0.47 * len("UNA FRASE BASTANTE LARGA PARA UNA LINEA"), 801)

    def test_html_cumple_el_contrato_del_motor(self):
        p = plan(piezas=[{"id": "t1", "tipo": "titulo", "texto": "Tres <b>*cosas*", "ancla": {"palabra": "tres"}, "porque": "anuncia lo que viene"},
                         {"id": "z1", "tipo": "zoom", "ancla": {"t": 3.0}, "porque": "subraya la cifra"}])
        _, _, piezas = validar(p)
        grupos = MON.grupos_de_subtitulos(PALABRAS, {"modo": "karaoke", "mayusculas": True})
        pagina, datos = MON.armar_html(p, piezas, PERFIL, grupos, 8.0, ROSTRO)
        self.assertIn('data-composition-id="main"', pagina)
        self.assertIn('id="base" class="clip"', pagina)
        self.assertIn("lib/gsap.min.js", pagina)
        self.assertNotIn("https://", pagina)                           # nada se carga de internet
        self.assertIn("&lt;b&gt;", pagina)                             # el texto de Emi no inyecta HTML
        self.assertIn('<b class="ac">cosas</b>', pagina)
        self.assertEqual(datos["foco"], [540.0, 660.0])                # el zoom va a la cara
        self.assertEqual(len(datos["grupos"]), len(grupos))

    def test_formato_horizontal(self):
        p = plan(formato="16:9", piezas=[{"tipo": "titulo", "texto": "Hola", "ancla": {"t": 1.0}, "porque": "prueba de formato"}])
        err, _, piezas = validar(p, rostro=None)
        self.assertEqual(err, [])
        pagina, datos = MON.armar_html(p, piezas, PERFIL, [], 8.0, None)
        self.assertEqual((datos["W"], datos["H"]), (1920, 1080))


class Sonido(unittest.TestCase):
    def test_propuesta_segun_densidad(self):
        piezas = [{"id": "a", "tipo": "titulo"}, {"id": "b", "tipo": "sello"}, {"id": "c", "tipo": "cierre"}]
        self.assertEqual(AUD.proponer(piezas, "ninguna"), [])
        self.assertEqual([e["en"] for e in AUD.proponer(piezas, "minima")], ["b", "c"])
        self.assertEqual(len(AUD.proponer(piezas, "media")), 3)
        with self.assertRaises(ErrorEditor):
            AUD.proponer(piezas, "brutal")

    @unittest.skipUnless(HAY_FFMPEG, "sin FFmpeg")
    def test_mezcla_deja_los_efectos_bajo_la_voz_y_tapa_la_groseria(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        comun.correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=f=200:d=4", "-ar", "48000", "-ac", "2", str(tmp / "voz.wav")], capture_output=True)
        AUD.sintetizar(tmp / "fx")
        self.assertTrue((tmp / "fx" / "bip.wav").exists())
        info = AUD.mezclar(tmp / "voz.wav", tmp / "m.wav", [{"t": 1.0, "sonido": "pop", "db": 2}], tmp / "fx", 4.0, [{"t0": 2.0, "t1": 2.5}])
        self.assertEqual(info["efectos"][0]["bajo_la_voz_db"], 6.0)    # nunca menos de 6 dB bajo la voz
        self.assertEqual(info["censuras"], 1)
        self.assertAlmostEqual(comun.duracion(tmp / "m.wav"), 4.0, delta=0.05)
        with self.assertRaises(ErrorEditor):
            AUD.mezclar(tmp / "voz.wav", tmp / "m2.wav", [{"t": 1.0, "sonido": "inexistente"}], tmp / "fx", 4.0)


class Proyecto(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        esp = self.tmp / "espacios"
        for e in comun.ESPACIOS:
            (esp / e).mkdir(parents=True)
            (esp / e / "perfil.json").write_text(json.dumps({"colores": PERFIL["colores"], "titular": "Anton"}))
            (esp / e / "edicion.json").write_text(json.dumps({**PERFIL["edicion"], "nivel_partida": 2 if e != "castorena" else 1, "nivel_tope": 2 if e in ("milla", "castorena") else 3}))
        os.environ["EDITOR_ESPACIOS"] = str(esp)
        self.addCleanup(os.environ.pop, "EDITOR_ESPACIOS", None)
        self._saldo = ED.saldo
        ED.saldo = lambda: {"fecha": "prueba"}
        self.addCleanup(setattr, ED, "saldo", self._saldo)

    def test_una_produccion_solo_vive_en_su_espacio(self):
        with self.assertRaises(ErrorEditor):
            comun.dir_produccion(self.tmp / "cualquier" / "lado")
        with self.assertRaises(ErrorEditor):
            comun.dir_produccion(self.tmp / "productions" / "milla" / "edicion" / "x", "personal")
        d = self.tmp / "productions" / "pan" / "edicion" / "tema"
        self.assertEqual(comun.espacio_de(d), "pan")

    def test_proyecto_crea_brief_vacio_y_no_sobrescribe(self):
        d = self.tmp / "productions" / "milla" / "edicion" / "tema"
        ED.crear_proyecto(d, "milla")
        b = json.loads((d / "brief.json").read_text())
        self.assertEqual(b["espacio"], "milla")
        self.assertFalse(b["visto_y_escuchado_por_emi"])
        self.assertTrue(all(v == "" for v in b["respuestas_emi"].values()))
        self.assertTrue((d / "editor.js").exists())
        with self.assertRaises(ErrorEditor):
            ED.crear_proyecto(d, "milla")

    def test_solo_emi_aprueba_y_la_prueba_tecnica_no_se_cierra(self):
        d = self.tmp / "productions" / "personal" / "edicion" / "tema"
        ED.crear_proyecto(d, "personal")
        self.assertEqual(ED.main(["aprobar", str(d), "muestra", "--por", "Claude", "--nota", "me gusta"]), 1)
        self.assertEqual(ED.main(["aprobar", str(d), "muestra", "--por", "prueba", "--nota", "prueba técnica"]), 1)   # no es carpeta prueba-
        self.assertEqual(ED.main(["aprobar", str(d), "muestra", "--por", "Emi", "--nota", "va, me gusta la opción dos"]), 0)
        self.assertEqual(json.loads((d / "brief.json").read_text())["aprobaciones"]["muestra"]["por"], "Emi")
        self.assertEqual(ED.main(["aprobar", str(d), "gasto", "--por", "Emi", "--nota", "va"]), 1)                    # falta --creditos
        dp = self.tmp / "productions" / "personal" / "edicion" / "prueba-x"
        ED.crear_proyecto(dp, "personal")
        self.assertEqual(ED.main(["aprobar", str(dp), "muestra", "--por", "prueba", "--nota", "prueba técnica"]), 0)

    def test_niveles_sugiere_el_mas_bajo_que_cumple_y_respeta_el_tope(self):
        d = self.tmp / "productions" / "castorena" / "edicion" / "tema"
        ED.crear_proyecto(d, "castorena")
        self.assertIn("Sugerencia: nivel 1", ED.explicar_niveles(d))
        d2 = self.tmp / "productions" / "milla" / "edicion" / "tema"
        ED.crear_proyecto(d2, "milla")
        b = json.loads((d2 / "brief.json").read_text())
        b["respuestas_emi"]["tipo_de_video"] = "anuncio de lanzamiento"
        (d2 / "brief.json").write_text(json.dumps(b))
        texto = ED.explicar_niveles(d2)
        self.assertIn("Sugerencia: nivel 2", texto)                    # milla no pasa de 2 sin que Emi lo pida
        b["respuestas_emi"]["tipo_de_video"] = "clip de podcast"
        (d2 / "brief.json").write_text(json.dumps(b))
        self.assertIn("Sugerencia: nivel 1", ED.explicar_niveles(d2))
        for nivel in ("Nivel 1", "Nivel 2", "Nivel 3"):
            self.assertIn(nivel, texto)                                # siempre se explican los tres

    def test_aprender_guarda_y_rechaza_lo_vago(self):
        f = comun.aprender("Emi prefiere que el título no tape el pecho cuando gesticula", "personal")
        self.assertIn("gesticula", f.read_text())
        self.assertIn("gesticula", comun.leer_aprendizajes("personal"))
        self.assertNotIn("gesticula", comun.leer_aprendizajes("milla"))    # los espacios no se mezclan
        with self.assertRaises(ErrorEditor):
            comun.aprender("ok")

    def test_revision_exige_archivo_actual_firma_y_lista_completa(self):
        d = self.tmp / "productions" / "personal" / "edicion" / "tema"
        (d / "out").mkdir(parents=True)
        (d / "out" / "FINAL.mp4").write_bytes(b"video")
        with self.assertRaises(ErrorEditor):
            ED.exigir_revision(d)
        r = {"final_sha": comun.sha_archivo(d / "out" / "FINAL.mp4"), "revisado_por": "", "lista": {"a": None}, "pendientes": []}
        guardar = lambda: (d / "out" / "revision.json").write_text(json.dumps(r))  # noqa: E731
        guardar()
        with self.assertRaises(ErrorEditor):
            ED.exigir_revision(d)                                      # sin firma
        r["revisado_por"] = "Claude Code"; guardar()
        with self.assertRaises(ErrorEditor):
            ED.exigir_revision(d)                                      # lista sin contestar
        r["lista"] = {"a": False}; guardar()
        with self.assertRaises(ErrorEditor):
            ED.exigir_revision(d)                                      # reprobado sin pendiente
        r["pendientes"] = ["corregir a"]; guardar()
        ED.exigir_revision(d)
        (d / "out" / "FINAL.mp4").write_bytes(b"otro render")
        with self.assertRaises(ErrorEditor):
            ED.exigir_revision(d)                                      # la revisión era de otro archivo

    def test_drive_rechaza_lo_que_no_es_un_id(self):
        d = self.tmp / "productions" / "personal" / "edicion" / "tema"
        with self.assertRaises(ErrorEditor):
            ED.traer_de_drive(d, "no es un id")

    def test_las_plantillas_no_cargan_nada_de_internet(self):
        for nombre in ("editor.js", "editor.css"):
            self.assertNotIn("http", (comun.PLANTILLA / nombre).read_text(encoding="utf-8"))
        js = (comun.PLANTILLA / "editor.js").read_text(encoding="utf-8")
        for prohibido in ("Date.now", "Math.random", "setTimeout", "repeat: -1"):
            self.assertNotIn(prohibido, js)                            # todo es función del tiempo


class Auditoria(unittest.TestCase):
    """Regresiones de la auditoría independiente del 11/11/2026: cada prueba es un defecto que existió."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_id_invalido_o_reservado_no_pasa(self):
        for malo in ("3a", "cam", "g0", "rcx", 'a"b', "</script>", "Mayus"):
            err, _, _ = validar(plan(piezas=[{"id": malo, "tipo": "titulo", "texto": "Hola", "ancla": {"t": 1.0}, "porque": "prueba de identificadores"}]))
            self.assertTrue(any("id inválido" in e for e in err), malo)
        err, _, _ = validar(plan(piezas=[{"id": "p1", "tipo": "panel", "items": ["a"], "ancla": {"t": 1.0}, "dura": 2, "porque": "prueba de identificadores"},
                                        {"id": "p1i0", "tipo": "sello", "texto": "X", "ancla": {"t": 5.0}, "porque": "prueba de identificadores"}]))
        self.assertTrue(any("nombres internos" in e for e in err))

    def test_los_subtitulos_no_cambian_las_cifras(self):
        g = MON.grupos_de_subtitulos(pal((0, 0.4, "Sube"), (0.5, 0.9, "3.5%,"), (1.0, 1.4, "o"), (1.5, 1.9, "$1,500.00.")), {"modo": "frase", "max_palabras": 6, "max_caracteres": 60})
        self.assertEqual([w["txt"] for w in g[0]["palabras"]], ["Sube", "3.5%", "o", "$1,500.00"])

    def test_milisegundos_en_un_clip_corto(self):
        f = self.tmp / "a.json"
        f.write_text(json.dumps({"words": [{"text": "Hola", "start": 500, "end": 900}, {"text": "tú", "start": 1000, "end": 1400}]}))
        self.assertAlmostEqual(TRA.de_archivo(f, duracion=20.0)["palabras"][0]["t0"], 0.5)
        f.write_text(json.dumps({"words": [{"text": "Hola", "start": 0.5, "end": 0.9}]}))
        self.assertAlmostEqual(TRA.de_archivo(f, duracion=20.0)["palabras"][0]["t0"], 0.5)

    def test_comparar_el_mismo_motor_dos_veces_no_pierde_datos(self):
        a = TRA._salida("archivo", "es", [{"t0": 0, "t1": 0.4, "txt": "Hola"}, {"t0": 0.5, "t1": 0.7, "txt": "eh"}])
        b = TRA._salida("archivo", "es", [{"t0": 0, "t1": 0.4, "txt": "Hola"}])
        self.assertEqual(len(TRA.comparar(a, b)["palabras"]), 2)

    def test_sticker_va_en_una_esquina_libre_y_nunca_sobre_subtitulos_ni_cara(self):
        br = {"respuestas_emi": {**BRIEF["respuestas_emi"], "nivel_elegido": "3"}}
        st = {"id": "s1", "tipo": "sticker", "archivo": "s.webm", "origen": "propio", "ancla": {"t": 3.0}, "porque": "acompaña la analogía"}
        err, _, piezas = validar(plan(nivel=3, piezas=[st]), brief=br, archivos={"s.webm"})
        self.assertEqual(err, [])
        self.assertLessEqual(piezas[0]["caja"][3], MON.ZONAS["9:16"]["pecho"][1])           # termina antes de la franja de subtítulos
        cara_baja = {"cajas": [{"t": 0.0, "x0": 60, "y0": 700, "x1": 600, "y1": 1200}]}
        err, _, _ = validar(plan(nivel=3, piezas=[st]), brief=br, archivos={"s.webm"}, rostro=cara_baja)
        self.assertTrue(any("tapa la cara" in e and "libres" in e for e in err))
        err, _, _ = validar(plan(nivel=3, piezas=[{**st, "esquina": "centro"}]), brief=br, archivos={"s.webm"})
        self.assertTrue(any("esquina debe ser" in e for e in err))
        _, _, piezas = validar(plan(nivel=3, piezas=[st]), brief=br, archivos={"s.webm"})
        pagina, _ = MON.armar_html(plan(nivel=3, piezas=[st]), piezas, PERFIL, [], 8.0, ROSTRO)
        self.assertIn('class="pz sticker" style="left:', pagina)

    def test_texto_no_puede_pedir_zona_pantalla(self):
        err, _, _ = validar(plan(piezas=[{"tipo": "titulo", "texto": "Hola", "zona": "pantalla", "ancla": {"t": 1.0}, "porque": "prueba de zonas"}]))
        self.assertTrue(any("no admitida para texto" in e for e in err))

    def test_un_zoom_agranda_la_cara_al_elegir_zona(self):
        justo = {"cajas": [{"t": 0.0, "x0": 300, "y0": 420, "x1": 780, "y1": 960}]}
        ti = {"id": "t1", "tipo": "titulo", "texto": "Hola", "zona": "torso", "ancla": {"t": 3.0}, "dura": 2, "porque": "prueba de zoom y zonas"}
        _, _, sin = validar(plan(piezas=[ti]), rostro=justo)
        _, _, con = validar(plan(piezas=[ti, {"id": "z1", "tipo": "zoom", "z": 1.2, "ancla": {"t": 3.2}, "dura": 1.5, "porque": "subraya la cifra"}]), rostro=justo)
        self.assertGreater(con[0]["caja"][1], sin[0]["caja"][1])                             # el título baja para no tocar la barbilla

    def test_estilo_de_subtitulos_y_modos_cerrados(self):
        self.assertTrue(any("subtitulos.estilo" in e for e in validar(plan(subtitulos={"modo": "frase", "estilo": "x onload=1", "razon": "prueba de estilos cerrados"}))[0]))
        self.assertTrue(any("modo debe ser" in e for e in validar(plan(piezas=[{"tipo": "zoom", "modo": "golpe", "ancla": {"t": 3.0}, "porque": "prueba de modos"}]))[0]))

    def test_efecto_sin_pieza_ni_tiempo_y_anclas_ilegibles_no_truenan(self):
        p = plan(sonido={"densidad": "minima", "efectos": [{"sonido": "pop"}], "musica": {"decision": "ninguna", "preguntado_a_emi": True}})
        self.assertTrue(any("lleva `en`" in e for e in validar(p)[0]))
        err, _, _ = validar(plan(piezas=[{"tipo": "titulo", "texto": "Hola", "ancla": {"palabra": "tres", "n": "dos"}, "porque": "prueba de anclas"}]))
        self.assertTrue(any("número ilegible" in e for e in err))
        err, _, _ = validar(plan(piezas=[{"tipo": "titulo", "texto": "Hola", "ancla": {"t": 1}, "dura": "mucho", "porque": "prueba de anclas"}]))
        self.assertTrue(any("`dura`" in e for e in err))

    def test_una_palabra_en_voz_baja_dentro_del_silencio_no_se_corta(self):
        w = wav_con_voz(self.tmp / "a.wav", [(0.2, 1.0), (3.0, 4.0)], 4.2)
        palabras = pal((0.2, 1.0, "claro"), (1.8, 2.1, "¿no?"), (3.0, 4.0, "sigue"))
        for c in COR.plan(w, palabras, "natural", 30)["cortes"]:
            self.assertFalse(c["t0"] < 1.95 < c["t1"], c)

    def test_una_toma_repetida_no_se_come_la_palabra_anterior(self):
        palabras = pal((0.0, 0.5, "Listo."), (0.5, 0.8, "La"), (0.8, 1.2, "primera"), (1.2, 1.5, "lee"), (1.5, 1.9, "esto."),
                       (3.0, 3.3, "La"), (3.3, 3.7, "primera"), (3.7, 4.0, "lee"), (4.0, 4.4, "esto"), (4.4, 4.8, "bien."))
        t = COR.proponer_tomas(palabras, 30)
        self.assertEqual(len(t), 1)
        self.assertGreaterEqual(t[0]["t0"], 0.5)

    def test_la_tabla_no_cuenta_dos_veces_lo_encimado(self):
        p = {"fps": 30, "ritmo": "natural", "duracion_crudo_s": 10.0, "cortes": [
            {"id": "c1", "t0": 2.0, "t1": 5.0, "tipo": "toma", "motivo": "x", "estado": "aprobado"},
            {"id": "c2", "t0": 4.0, "t1": 6.0, "tipo": "silencio", "motivo": "x", "estado": "propuesto"}]}
        self.assertIn("se quitarían 4.0 s", COR.tabla(p))

    def test_censura_sigue_a_la_palabra_aunque_cambien_los_tiempos(self):
        palabras = pal((0.0, 0.4, "uno"), (2.0, 2.4, "pendejo"), (2.5, 2.9, "dos"))
        limpias = COR.remapear(palabras, [(0.0, 0.5), (1.9, 3.0)])
        self.assertEqual([w["i_crudo"] for w in limpias], [0, 1, 2])
        g = MON.grupos_de_subtitulos(limpias, {"modo": "frase"}, [{"i": 1, "accion": "tapar"}])
        self.assertIn("p******", [w["txt"] for x in g for w in x["palabras"]])


class Cierre(unittest.TestCase):
    """`cierre` solo deja pasar el archivo que corresponde a lo aprobado."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        esp = self.tmp / "espacios"
        for e in comun.ESPACIOS:
            (esp / e).mkdir(parents=True)
            (esp / e / "perfil.json").write_text(json.dumps({"colores": PERFIL["colores"], "titular": "Anton"}))
            (esp / e / "edicion.json").write_text(json.dumps(PERFIL["edicion"]))
        os.environ["EDITOR_ESPACIOS"] = str(esp)
        self.addCleanup(os.environ.pop, "EDITOR_ESPACIOS", None)
        self._saldo = ED.saldo
        ED.saldo = lambda: {"fecha": "prueba"}
        self.addCleanup(setattr, ED, "saldo", self._saldo)
        d = self.d = self.tmp / "productions" / "personal" / "edicion" / "tema"
        (d / "out").mkdir(parents=True)
        (d / "assets").mkdir()
        self.cortes = {"fps": 30, "duracion_crudo_s": 9.0, "cortes": [{"id": "c1", "t0": 8.0, "t1": 9.0, "estado": "aprobado"}]}
        self.cortes["aprobacion"] = {"por": "Emi", "huella": COR.huella_plan(self.cortes)}
        self.plan = plan(piezas=[{"id": "fin", "tipo": "cierre", "texto": "COMENTA", "ancla": {"t": 6.0}, "dura": 1.5, "porque": "la voz pide opinión"}])
        self.brief = {**BRIEF, "aprobaciones": {"muestra": {"por": "Emi", "nota": "va"}}, "visto_y_escuchado_por_emi": False}
        (d / "out" / "FINAL.mp4").write_bytes(b"video final")
        self.escribir()
        escribir = lambda n, x: (d / n).write_text(json.dumps(x))  # noqa: E731
        escribir("medios.json", {"formato": "9:16", "fps": 30, "original": {"sha": "x"}})
        escribir("palabras_limpio.json", {"palabras": PALABRAS})
        escribir("out/auditoria-audio.json", {"avisos": []})
        escribir("out/auditoria-video.json", {"avisos": []})
        escribir("out/revision.json", {"final_sha": comun.sha_archivo(d / "out" / "FINAL.mp4"), "revisado_por": "Claude Code", "lista": {"a": True}, "pendientes": []})
        (d / "out" / "publicacion.md").write_text("x")

    def escribir(self):
        d = self.d
        (d / "cortes.json").write_text(json.dumps(self.cortes))
        (d / "plan.json").write_text(json.dumps(self.plan))
        (d / "brief.json").write_text(json.dumps(self.brief))
        (d / "cortes-aplicados.json").write_text(json.dumps({"quedan": [[0, 8.0]], "empalmes": [], "duracion_s": 8.0, "censura": [], "huella": getattr(self, "huella_aplicada", COR.huella_plan(self.cortes))}))
        (d / "out" / "manifiesto.json").write_text(json.dumps({"sha": comun.sha_archivo(d / "out" / "FINAL.mp4"), "plan": getattr(self, "plan_rendido", ED.huella_de_plan(self.plan)),
                                                               "cortes": getattr(self, "huella_aplicada", COR.huella_plan(self.cortes))}))

    def test_todo_en_orden_cierra_y_dice_que_falta_emi(self):
        self.assertIn("FALTA que Emi lo vea y lo escuche", ED.cierre(self.d))

    def test_plan_cambiado_despues_del_render_no_cierra(self):
        self.plan_rendido = ED.huella_de_plan(self.plan)
        self.plan["piezas"][0]["texto"] = "OPINA"
        self.escribir()
        with self.assertRaisesRegex(ErrorEditor, "cambiaron después del render"):
            ED.cierre(self.d)

    def test_cortes_cambiados_despues_de_cortar_no_cierran(self):
        self.huella_aplicada = COR.huella_plan(self.cortes)
        self.cortes["cortes"][0]["t0"] = 7.0
        self.cortes["aprobacion"]["huella"] = COR.huella_plan(self.cortes)
        self.escribir()
        with self.assertRaisesRegex(ErrorEditor, "después de `cortar`"):
            ED.cierre(self.d)

    def test_sin_aprobacion_de_cortes_o_de_muestra_no_cierra(self):
        self.cortes["aprobacion"] = None
        self.escribir()
        with self.assertRaisesRegex(ErrorEditor, "no están aprobados"):
            ED.cierre(self.d)
        self.cortes["aprobacion"] = {"por": "Emi", "huella": COR.huella_plan(self.cortes)}
        self.brief["aprobaciones"] = {}
        self.escribir()
        with self.assertRaisesRegex(ErrorEditor, "muestra de estilo"):
            ED.cierre(self.d)

    def test_otro_archivo_o_avisos_sin_atender_no_cierran(self):
        (self.d / "out" / "auditoria-audio.json").write_text(json.dumps({"avisos": ["pico alto"]}))
        with self.assertRaisesRegex(ErrorEditor, "avisos sin atender"):
            ED.cierre(self.d)
        (self.d / "out" / "FINAL.mp4").write_bytes(b"otro archivo")
        with self.assertRaisesRegex(ErrorEditor, "no es el archivo"):
            ED.cierre(self.d)

    def test_quitar_a_mano_valida_el_tramo(self):
        self.cortes.update({"ritmo": "natural", "censura": []})
        for c in self.cortes["cortes"]:
            c.update({"tipo": "silencio", "motivo": "pausa"})
        self.escribir()
        (self.d / "palabras.json").write_text(json.dumps({"palabras": PALABRAS}))
        self.assertEqual(ED.main(["decidir", str(self.d), "--quitar", "5~2", "--motivo", "tramo que no aporta"]), 1)
        self.assertEqual(ED.main(["decidir", str(self.d), "--quitar", "a~b", "--motivo", "tramo que no aporta"]), 1)
        self.assertEqual(ED.main(["decidir", str(self.d), "--quitar", "2~3", "--motivo", "tramo que no aporta"]), 0)
        despues = json.loads((self.d / "cortes.json").read_text())
        self.assertIsNone(despues["aprobacion"])                                   # cualquier cambio invalida la aprobación
        self.assertTrue(any(c["tipo"] == "manual" for c in despues["cortes"]))


class Auditoria2(unittest.TestCase):
    """Regresiones de la segunda auditoría (11/11/2026): estrés del flujo, imagen y sonido, y reglas que solo cumplía la prosa."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    @unittest.skipUnless(HAY_FFMPEG, "sin FFmpeg")
    def test_muchos_cortes_no_desfasan_y_no_dejan_basura(self):
        fuente = self.tmp / "f.mp4"
        comun.correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=180x320:r=30:d=40", "-f", "lavfi", "-i", "sine=f=220:d=40",
                      "-c:v", "libx264", "-g", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(fuente)], capture_output=True)
        quedan = [(k * 2.0, k * 2.0 + 1.2) for k in range(20)]                # 19 empalmes
        COR.aplicar(fuente, self.tmp / "o.mp4", quedan, 30)
        self.assertAlmostEqual(comun.duracion(self.tmp / "o.mp4"), 24.0, delta=0.1)
        v, a = ED.duracion_de(self.tmp / "o.mp4", "v"), ED.duracion_de(self.tmp / "o.mp4", "a")
        self.assertLess(abs(v - a), 0.08)                                    # imagen y sonido terminan juntos
        self.assertFalse((self.tmp / "o.tramos").exists())

    def test_con_ruido_de_fondo_fuerte_se_apoya_en_la_transcripcion_y_avisa(self):
        n, hz = int(8 * 16000), 16000
        rng = np.random.default_rng(3)
        x = rng.normal(0, 0.02, n)                                           # fondo a unos -34 dB: solo 14 dB bajo la voz... se sube abajo
        x = rng.normal(0, 0.035, n)
        t = np.arange(n) / hz
        for a, b in ((0.3, 2.5), (5.0, 7.5)):
            m = (t >= a) & (t < b)
            x[m] += 0.1 * np.sin(2 * np.pi * 180 * t[m])
        w = self.tmp / "r.wav"
        with wave.open(str(w), "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(hz)
            f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        p = COR.plan(w, pal((0.3, 2.5, "hola."), (5.0, 7.5, "adiós")), "natural", 30)
        self.assertTrue(any("ruido o música de fondo" in a for a in p["avisos"]))
        self.assertTrue([c for c in p["cortes"] if 2.5 < c["t0"] < 5.0], "debía proponer la pausa de 2.5 s que marca la transcripción")

    def test_audio_en_silencio_avisa(self):
        w = wav_con_voz(self.tmp / "s.wav", [], 3.0)
        self.assertTrue(any("silencio" in a for a in COR.plan(w, [], "natural", 30)["avisos"]))

    def test_repeticion_con_frases_en_medio_queda_dudosa(self):
        palabras = pal((0.0, 0.4, "La"), (0.4, 0.8, "ley"), (0.8, 1.2, "dice"), (1.2, 1.6, "sí."),
                       (2.5, 2.9, "Pero"), (2.9, 3.3, "nadie"), (3.3, 3.7, "la"), (3.7, 4.1, "respeta."),
                       (5.0, 5.4, "La"), (5.4, 5.8, "ley"), (5.8, 6.2, "dice"), (6.2, 6.6, "sí."))
        t = COR.proponer_tomas(palabras, 30)
        self.assertEqual(t[0].get("estado"), "dudoso")
        self.assertIn("frases de en medio", t[0]["motivo"])

    def test_cambiar_la_censura_invalida_la_aprobacion(self):
        p = {"fps": 30, "cortes": [], "censura": [{"i": 3, "accion": "tapar"}]}
        antes = COR.huella_plan(p)
        p["censura"][0]["accion"] = "dejar"
        self.assertNotEqual(antes, COR.huella_plan(p))

    def test_transcripcion_desordenada_o_con_una_palabra_dentro_de_otra(self):
        t = TRA._salida("x", "es", [{"t0": 5.0, "t1": 5.4, "txt": "b"}, {"t0": 1.0, "t1": 3.0, "txt": "a"}, {"t0": 1.8, "t1": 2.2, "txt": "dentro"}])
        self.assertTrue(all(w["t1"] > w["t0"] for w in t["palabras"]))
        self.assertEqual([w["t0"] for w in t["palabras"]], sorted(w["t0"] for w in t["palabras"]))
        self.assertEqual([w["i"] for w in t["palabras"]], list(range(len(t["palabras"]))))

    def test_el_tope_del_espacio_se_cumple(self):
        castorena = {**PERFIL, "espacio": "castorena", "edicion": {**PERFIL["edicion"], "nivel_tope": 2, "sonido": {"densidad": "ninguna"}, "movimiento": "sobrio"}}
        br = {"respuestas_emi": {**BRIEF["respuestas_emi"], "nivel_elegido": "3"}}
        err, _, _ = validar(plan(espacio="castorena", nivel=3), brief=br, perfil=castorena)
        self.assertTrue(any("no pasa de nivel 2" in e for e in err))
        err, _, _ = validar(plan(espacio="castorena", nivel=3, sobre_tope_pedido_por_emi="Emi: en este sí quiero nivel 3"), brief=br, perfil=castorena)
        self.assertFalse(any("no pasa de nivel" in e for e in err))
        con_efecto = plan(espacio="castorena", sonido={"densidad": "ninguna", "efectos": [{"t": 1.0, "sonido": "pop"}], "musica": {"decision": "ninguna", "preguntado_a_emi": True}})
        self.assertTrue(any("no lleva efectos" in e for e in validar(con_efecto, perfil=castorena)[0]))
        mas = plan(sonido={"densidad": "alta", "efectos": [], "musica": {"decision": "ninguna", "preguntado_a_emi": True}})
        self.assertTrue(any("pasa de la del espacio" in e for e in validar(mas)[0]))

    def test_lo_que_solo_cumplia_la_prosa(self):
        sin_preguntar = plan(sonido={"densidad": "minima", "efectos": [], "musica": {"decision": "ninguna", "preguntado_a_emi": False}})
        self.assertTrue(any("preguntado_a_emi" in e for e in validar(sin_preguntar)[0]))
        br = {"respuestas_emi": {**BRIEF["respuestas_emi"], "quienes_salen": "Emi y dos compañeros del comité"}}
        self.assertTrue(any("permiso_de_quienes_salen" in e for e in validar(plan(), brief=br)[0]))
        br["respuestas_emi"]["permiso_de_quienes_salen"] = "sí, los dos lo dijeron por WhatsApp el 11/11"
        self.assertFalse(any("permiso" in e for e in validar(plan(), brief=br)[0]))
        sin_tipo = {"respuestas_emi": {**BRIEF["respuestas_emi"], "tipo_de_video": ""}}
        self.assertTrue(any("tipo_de_video" in e for e in validar(plan(), brief=sin_tipo)[0]))

    def test_plan_mal_formado_se_dice_claro_y_no_truena(self):
        casos = [dict(tramos=[{"de": 1}]), dict(tramos=[{"de": 3, "a": 1, "nivel": 2}]), dict(nivel="2"),
                 dict(subtitulos={"modo": "frase", "razon": "prueba de forma del plan", "ocultar": [[1]]}),
                 dict(subtitulos={"modo": "frase", "razon": "prueba de forma del plan", "max_palabras": "tres"}),
                 dict(piezas=[{"tipo": "rotulo", "texto": None, "ancla": {"t": 1}, "porque": "prueba de forma"}]),
                 dict(piezas=[{"tipo": "titulo", "texto": "Hola", "ancla": {"t": "nan"}, "porque": "prueba de forma"}]),
                 dict(piezas=[{"tipo": "titulo", "texto": "Hola", "ancla": {"t": 4}, "hasta": {"t": 2}, "porque": "prueba de forma"}]),
                 dict(sonido={"densidad": "minima", "efectos": [{"t": 1, "sonido": "pop", "db": "fuerte"}], "musica": {"decision": "ninguna", "preguntado_a_emi": True}}),
                 dict(sonido={"densidad": "minima", "efectos": [], "musica": {"decision": "archivo", "archivo": "base.mp4", "origen": "mío", "preguntado_a_emi": True}})]
        for extra in casos:
            err, _, _ = validar(plan(**extra), archivos={"base.mp4"})
            self.assertTrue(err, extra)

    def test_barrido_solo_sobre_un_corte(self):
        b = {"tipo": "barrido", "ancla": {"t": 3.0}, "dura": 0.5, "porque": "cambia de sección"}
        self.assertTrue(any("empalme" in e for e in validar(plan(piezas=[b]))[0]))
        self.assertEqual(validar(plan(piezas=[b]), empalmes=[3.25])[0], [])

    def test_panel_con_renglon_largo_y_tres_detras(self):
        largo = {"tipo": "panel", "items": ["x" * 40], "ancla": {"t": 2.0}, "dura": 3, "porque": "resume la lista"}
        self.assertTrue(any("pasa de 32 letras" in e for e in validar(plan(piezas=[largo]))[0]))
        br = {"respuestas_emi": {**BRIEF["respuestas_emi"], "nivel_elegido": "3"}}
        tres = [{"id": f"d{k}", "tipo": "detras", "texto": "PALABRA", "ancla": {"t": 1.0 + 2 * k}, "dura": 1, "porque": "prueba de límite"} for k in range(3)]
        err, _, _ = validar(plan(nivel=3, piezas=tres), brief=br, archivos={f"recorte-d{k}.webm" for k in range(3)})
        self.assertTrue(any("más de dos textos detrás" in e for e in err))

    def test_foto_en_tarjeta_no_tapa_la_cara(self):
        f = {"id": "f1", "tipo": "foto", "modo": "tarjeta", "archivo": "a.png", "origen_descripcion": "captura propia", "ancla": {"t": 2.0}, "porque": "enseña el documento"}
        enorme = {"cajas": [{"t": 0.0, "x0": 100, "y0": 250, "x1": 980, "y1": 1150}]}
        self.assertTrue(any("no cabe sin tapar la cara" in e for e in validar(plan(piezas=[f]), archivos={"a.png"}, rostro=enorme)[0]))
        err, _, piezas = validar(plan(piezas=[f]), archivos={"a.png"}, rostro={"cajas": [{"t": 0.0, "x0": 300, "y0": 300, "x1": 780, "y1": 760}]})
        self.assertEqual(err, [])
        self.assertGreaterEqual(piezas[0]["caja"][1], 760)

    def test_colores_que_si_se_leen(self):
        pan = {"papel": "#F3EFE6", "tinta": "#253775", "acento": "#0043A1", "apoyo": "#EDBF4D"}
        self.assertEqual(MON.mejor_sobre("#151515", [pan["acento"], pan["apoyo"]]), pan["apoyo"])     # el azul sobre oscuro no se lee
        pagina, _ = MON.armar_html(plan(), [], PERFIL, [], 8.0, ROSTRO)
        self.assertIn("--resalte:#FF5A1F", pagina)                           # el naranja de Emi sí se lee: se queda
        self.assertGreater(MON.contraste("#FFFFFF", "#000000"), 20)
        perfil_pan = {**PERFIL, "espacio": "pan", "colores": pan}
        _, _, piezas = validar(plan(espacio="pan"), perfil=perfil_pan)
        pagina, datos = MON.armar_html(plan(espacio="pan"), piezas, perfil_pan, MON.grupos_de_subtitulos(PALABRAS, {"modo": "karaoke", "mayusculas": True}), 8.0, ROSTRO)
        self.assertEqual(datos["subs"]["activo"], pan["apoyo"])
        self.assertIn("--resalte:#EDBF4D", pagina)

    def test_titulo_largo_en_serif_parte_en_dos_o_se_rechaza(self):
        caja = (90, 240, 960, 520)
        tam, lineas = MON.tam_titulo("¿POR QUÉ NADIE LEE LA LETRA CHIQUITA HOY?", "Gelasio", caja, 1080)
        self.assertEqual(lineas, 2)
        ancho = max(len(x) for x in MON._lineas("¿POR QUÉ NADIE LEE LA LETRA CHIQUITA HOY?", 2)) * 0.80 * tam
        self.assertLessEqual(ancho, (caja[2] - caja[0]))
        castorena = {**PERFIL, "edicion": {**PERFIL["edicion"], "fuente_titular": "Gelasio"}}
        cerrado = {"cajas": [{"t": 0.0, "x0": 200, "y0": 250, "x1": 900, "y1": 1080}]}
        err, _, _ = validar(plan(piezas=[{"tipo": "titulo", "texto": "¿POR QUÉ NADIE LEE LA LETRA CHIQUITA HOY?", "ancla": {"t": 1}, "porque": "prueba de ancho"}]), perfil=castorena, rostro=cerrado)
        self.assertTrue(any("no cabe legible" in e for e in err))

    def test_los_subtitulos_tienen_un_solo_tamano(self):
        import re
        palabras = pal((0, 0.4, "Sí"), (0.5, 0.9, "claro"), (2.0, 2.6, "extraordinariamente"), (2.7, 3.3, "complicadísimo"))
        grupos = MON.grupos_de_subtitulos(palabras, {"modo": "frase", "max_palabras": 2, "max_caracteres": 40})
        pagina, _ = MON.armar_html(plan(), [], PERFIL, grupos, 8.0, ROSTRO)
        tamanos = set(re.findall(r'class="grupo" id="g\d+" style="font-size:(\d+)px"', pagina))
        self.assertEqual(len(tamanos), 1)

    def test_panel_calcula_la_letra_para_que_quepa(self):
        import re
        pz = {"id": "pan1", "tipo": "panel", "titulo": "Antes de firmar", "items": ["Lee la letra chiquita completa", "Pregunta cuánto cuesta salirte", "Nunca firmes con prisa", "Pide copia sellada"], "ancla": {"t": 2.0}, "dura": 4, "porque": "resume la lista"}
        _, _, piezas = validar(plan(piezas=[pz]))
        pagina, _ = MON.armar_html(plan(piezas=[pz]), piezas, PERFIL, [], 8.0, ROSTRO)
        letra = int(re.search(r'class="pz panel"[^>]*><div class="in" style="font-size:(\d+)px"', pagina).group(1))
        alto = MON.PANEL_CAJA["9:16"][3] - MON.PANEL_CAJA["9:16"][1]
        self.assertGreaterEqual(letra, MON.LETRA_MINIMA)
        self.assertLessEqual(4 * letra * 1.14 + 4 * 20 + 68 + alto * 0.17 * 1.25, alto + 1)          # cabecera y cuatro renglones caben
        self.assertGreaterEqual(letra, 40)                                   # y no queda diminuta

    def test_el_movimiento_no_deja_saltos(self):
        js = (comun.PLANTILLA / "editor.js").read_text(encoding="utf-8")
        self.assertNotIn("immediateRender", js)                              # el estado inicial se fija al hacerse visible
        self.assertNotIn('tl.set("#cam", { scale: 1, x: 0, y: 0 }, t1)', js)   # el zoom nunca regresa de golpe
        css = (comun.PLANTILLA / "editor.css").read_text(encoding="utf-8")
        self.assertIn(".mov-sobrio .cierre .flecha{display:none}", css)

    @unittest.skipUnless(HAY_FFMPEG, "sin FFmpeg")
    def test_los_efectos_se_nivelan_por_como_suenan(self):
        AUD.sintetizar(self.tmp / "fx")
        niveles = {n: AUD.sonoridad_corta(self.tmp / "fx" / f"{n}.wav") for n in AUD.EFECTOS}
        self.assertTrue(all(v > -45 for v in niveles.values()), niveles)     # ninguno sale mudo (filtro mal puesto)
        comun.correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anoisesrc=c=pink:a=0.3:d=4", "-ar", "48000", "-ac", "2", str(self.tmp / "voz.wav")], capture_output=True)
        info = AUD.mezclar(self.tmp / "voz.wav", self.tmp / "m.wav", [{"t": 1.0, "sonido": "ding", "db": 8}], self.tmp / "fx", 4.0)
        self.assertAlmostEqual(niveles["ding"] + info["efectos"][0]["ganancia_db"], AUD.VOZ_LUFS - 8, delta=0.2)


class Compuertas2(Cierre):
    """Más comprobaciones de que lo rendido corresponde a lo aprobado (hereda la producción armada de `Cierre`)."""

    def test_recortar_despues_de_cortar_se_detecta_antes_de_rendir(self):
        self.huella_aplicada = COR.huella_plan(self.cortes)
        self.cortes["cortes"][0]["t0"] = 7.5
        self.escribir()
        err, _, _, _ = ED.validar_produccion(self.d)
        self.assertTrue(any("cambiaron después de `cortar`" in e for e in err))

    def test_regla_de_emi_nunca_decir_que_lo_hizo_una_ia(self):
        err, avi, _, _ = ED.validar_produccion(self.d)
        self.assertFalse(any("Regla de Emi" in e for e in err))
        self.plan["piezas"][0]["texto"] = "LO HIZO UNA IA"           # texto que añade la skill: error
        self.escribir()
        err, _, _, _ = ED.validar_produccion(self.d)
        self.assertTrue(any("Regla de Emi" in e for e in err))
        self.plan["piezas"][0]["texto"] = "COMENTA"
        self.escribir()
        dicho = [dict(w) for w in PALABRAS]                          # lo que Emi dice a cámara: aviso, decide él
        for w, nuevo in zip(dicho, ["nadie", "lo", "editó"]):
            w["txt"] = nuevo
        (self.d / "palabras_limpio.json").write_text(json.dumps({"palabras": dicho}))
        err, avi, _, _ = ED.validar_produccion(self.d)
        self.assertFalse(any("Regla de Emi" in e for e in err))
        self.assertTrue(any("nunca que el video lo hizo una IA" in x for x in avi))

    def test_mapa_de_rostro_de_otro_corte(self):
        (self.d / "limpio.mp4").write_bytes(b"corte nuevo")
        (self.d / "rostro.json").write_text(json.dumps({"cajas": ROSTRO["cajas"], "limpio": "otro"}))
        err, _, _, _ = ED.validar_produccion(self.d)
        self.assertTrue(any("mapa de rostro es de otro corte" in e for e in err))

    def test_visto_bueno_final_solo_de_emi_y_para_este_archivo(self):
        self.assertEqual(ED.main(["aprobar", str(self.d), "final", "--por", "Claude", "--nota", "se ve bien"]), 1)
        self.assertEqual(ED.main(["aprobar", str(self.d), "final", "--por", "Emi", "--nota", "va, así publícalo"]), 0)
        self.assertIn("TERMINADO", ED.cierre(self.d))
        visto = json.loads((self.d / "brief.json").read_text())["visto_y_escuchado_por_emi"]
        visto["final_sha"] = "otro"
        b = json.loads((self.d / "brief.json").read_text()); b["visto_y_escuchado_por_emi"] = visto
        (self.d / "brief.json").write_text(json.dumps(b))
        self.assertIn("FALTA que Emi", ED.cierre(self.d))


class Paletas(unittest.TestCase):
    """Una serie puede llevar una paleta propia aprobada por Emi, sin tocar la marca del espacio."""

    def test_paleta_de_serie(self):
        pal = {"ia-derecho": {"colores": {"papel": "#F4ECD6", "tinta": "#0D1B2A", "acento": "#FF5A1F", "apoyo": "#C8A96B"},
                              "aprobada_por_emi": "13/11/2026: sí"}}
        con = {**PERFIL, "paletas": pal}
        self.assertEqual(validar(plan(paleta="ia-derecho"), perfil=con)[0], [])
        pagina, _ = MON.armar_html(plan(paleta="ia-derecho"), [], con, [], 8.0, ROSTRO)
        self.assertIn("--tinta:#0D1B2A", pagina)
        self.assertIn("--apoyo:#C8A96B", pagina)
        pagina, _ = MON.armar_html(plan(), [], con, [], 8.0, ROSTRO)
        self.assertIn("--tinta:#20180F", pagina)                         # sin `paleta`, la marca de siempre
        self.assertTrue(any("no existe" in e for e in validar(plan(paleta="otra"), perfil=con)[0]))
        sin_ok = {**PERFIL, "paletas": {"x": {"colores": pal["ia-derecho"]["colores"]}}}
        self.assertTrue(any("aprobada_por_emi" in e for e in validar(plan(paleta="x"), perfil=sin_ok)[0]))
        mala = {**PERFIL, "paletas": {"x": {"colores": {"papel": "crema"}, "aprobada_por_emi": "sí"}}}
        self.assertTrue(any("hexadecimal" in e for e in validar(plan(paleta="x"), perfil=mala)[0]))

    def test_la_paleta_ia_derecho_del_repositorio_esta_aprobada_y_se_lee(self):
        p = json.loads((comun.RAIZ.parent.parent / "espacios" / "personal" / "paletas.json").read_text(encoding="utf-8"))["paletas"]["ia-derecho"]
        self.assertTrue(p["aprobada_por_emi"])
        c = p["colores"]
        self.assertGreaterEqual(MON.contraste(c["papel"], c["tinta"]), 7)       # texto sobre los bloques de tinta
        self.assertGreaterEqual(MON.contraste(c["acento"], "#151515"), 4.5)     # el naranja se lee sobre oscuro


class Decisiones13Nov(unittest.TestCase):
    """Respuestas de Emi del 13/11/2026 (recogidas por la Matriz de Redes): música por código y modismos fuera."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_modismos_se_proponen_cortar_y_no_quedan_como_aviso(self):
        palabras = pal((0.0, 0.5, "Nunca"), (0.6, 1.0, "firmes,"), (1.1, 1.4, "güey."), (2.0, 2.5, "Fin"))
        w = wav_con_voz(self.tmp / "a.wav", [(0.0, 1.4), (2.0, 2.5)], 3.0)
        p = COR.plan(w, palabras, "natural", 30, modismos="cortar")
        self.assertTrue(any(c["tipo"] == "modismo" and c["t0"] <= 1.1 and c["t1"] >= 1.4 for c in p["cortes"]))
        self.assertFalse([c for c in p["censura"] if c["accion"] == "avisar"])
        p2 = COR.plan(w, palabras, "natural", 30)
        self.assertFalse(any(c["tipo"] == "modismo" for c in p2["cortes"]))
        self.assertTrue(any(c["accion"] == "avisar" for c in p2["censura"]))

    def test_musica_por_codigo(self):
        s = lambda m: plan(sonido={"densidad": "minima", "efectos": [], "musica": {"preguntado_a_emi": True, **m}})  # noqa: E731
        self.assertEqual(validar(s({"decision": "codigo", "animo": "serio"}))[0], [])
        self.assertTrue(any("animo" in e for e in validar(s({"decision": "codigo", "animo": "épico"}))[0]))

    @unittest.skipUnless(HAY_FFMPEG, "sin FFmpeg")
    def test_la_pista_compuesta_queda_muy_bajo_la_voz(self):
        musica = ED.componer_musica(self.tmp / "m.wav", "serio", 6.0, [2.0, 4.0], "a1b2c3d4")
        self.assertAlmostEqual(comun.duracion(musica), 6.0, delta=0.2)
        comun.correr(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anoisesrc=c=pink:a=0.3:d=6", "-ar", "48000", "-ac", "2", str(self.tmp / "voz.wav")], capture_output=True)
        AUD.sintetizar(self.tmp / "fx")
        info = AUD.mezclar(self.tmp / "voz.wav", self.tmp / "mx.wav", [], self.tmp / "fx", 6.0, musica=musica)
        self.assertGreaterEqual(info["musica"]["bajo_la_voz_lu"], 17)

    def test_el_espacio_personal_corta_modismos(self):
        ed = json.loads((comun.RAIZ.parent.parent / "espacios" / "personal" / "edicion.json").read_text(encoding="utf-8"))
        self.assertEqual(ed["modismos_accion"], "cortar")


if __name__ == "__main__":
    unittest.main()
