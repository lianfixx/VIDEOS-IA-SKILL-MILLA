"""Pruebas del radar. No usan red ni gastan saldo.

    python3 -m unittest discover -s cerebro -p 'test_*.py'
"""
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import radar  # noqa: E402

HOY = dt.date(2026, 11, 11)
TT = {"webVideoUrl": "https://www.tiktok.com/@a/video/1", "text": "Nadie te dice esto antes de firmar. #contratos #abogadosmexico", "playCount": 90000, "diggCount": 5000,
      "commentCount": 300, "shareCount": 200, "collectCount": 100, "createTimeISO": "2026-11-08T10:00:00.000Z", "videoMeta": {"duration": 34},
      "authorMeta": {"name": "a"}, "hashtags": [{"name": "contratos"}, {"name": "abogadosmexico"}], "musicMeta": {"musicName": "sonido original"},
      "searchHashtag": {"name": "abogadosmexico"}}
IG = {"url": "https://www.instagram.com/reel/x/", "type": "Video", "caption": "¿Te pueden correr sin pagarte?\n#derecholaboral", "likesCount": 800, "commentsCount": 40,
      "videoPlayCount": 20000, "videoDuration": 41.2, "timestamp": "2026-11-05T12:00:00.000Z", "ownerUsername": "b", "hashtags": ["derecholaboral"],
      "inputUrl": "https://www.instagram.com/explore/tags/derechofamiliar"}


class Radar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for e, tags in (("milla", ["abogadosmexico", "derechofamiliar"]), ("castorena", ["#Abogados Mexico", "amparo"])):
            (self.tmp / e).mkdir()
            (self.tmp / e / "radar.json").write_text(json.dumps({"etiquetas": {"tiktok": tags, "instagram": tags[:1]}}))
        os.environ["RADAR_ESPACIOS"] = str(self.tmp)
        self.addCleanup(os.environ.pop, "RADAR_ESPACIOS", None)

    def test_consultas_unen_etiquetas_y_recuerdan_de_quien_son(self):
        c = radar.consultas()
        self.assertEqual(c["tiktok"]["abogadosmexico"], ["milla", "castorena"])     # la misma etiqueta se consulta una vez
        self.assertEqual(sorted(c["instagram"]), ["abogadosmexico"])

    def test_costo_maximo(self):
        m = radar.costo_maximo(radar.consultas(), 10)
        self.assertAlmostEqual(m["tiktok"], 3 * 10 * 0.0037, places=3)
        self.assertAlmostEqual(m["total"], m["tiktok"] + m["instagram"], places=3)
        self.assertGreaterEqual(m["autorizado"], 0.5)          # el actor de TikTok exige al menos 0.50 de tope

    def test_el_tope_semanal_limita_lo_que_de_verdad_se_autoriza(self):
        llamadas = []
        with self.assertRaises(radar.ErrorRadar):               # lo esperado cabe en 0.20, pero se autorizarían 0.50 o más
            radar.correr(5, 0.20, HOY, pedir=lambda *a: llamadas.append(a) or [])
        self.assertEqual(llamadas, [])
        radar.correr(5, 0.70, HOY, pedir=lambda *a: llamadas.append(a) or [])
        self.assertLessEqual(sum(x[2] for x in llamadas), 0.70)

    def test_normaliza_las_dos_plataformas_igual(self):
        a, b = radar.normalizar("tiktok", TT), radar.normalizar("instagram", IG)
        self.assertEqual(set(a), set(b))
        self.assertEqual((a["vistas"], a["duracion_s"], a["fecha"], a["consulta"]), (90000, 34, "2026-11-08", "abogadosmexico"))
        self.assertEqual((b["vistas"], b["fecha"], b["consulta"]), (20000, "2026-11-05", "derechofamiliar"))

    def test_descarta_errores_y_lo_que_no_es_video(self):
        self.assertIsNone(radar.normalizar("tiktok", {"error": "no encontrado"}))
        self.assertIsNone(radar.normalizar("instagram", {"url": "https://x", "type": "Image"}))
        with self.assertRaises(radar.ErrorRadar):
            radar.normalizar("otra", {})

    def test_puntaje_premia_alcance_reciente_y_participacion(self):
        base = radar.normalizar("tiktok", TT)
        viejo = {**base, "fecha": "2026-01-01"}
        frio = {**base, "likes": 10, "comentarios": 0, "compartidos": 0, "guardados": 0}
        self.assertGreater(radar.puntaje(base, HOY), radar.puntaje(viejo, HOY))
        self.assertGreater(radar.puntaje(base, HOY), radar.puntaje(frio, HOY))
        self.assertEqual(radar.puntaje({"fecha": "", "vistas": None}, HOY), 0.0)

    def test_gancho_es_la_primera_frase_sin_etiquetas(self):
        self.assertEqual(radar.gancho("Nadie te dice esto antes de firmar. #contratos"), "Nadie te dice esto antes de firmar")
        self.assertEqual(radar.gancho(""), "")

    def test_correr_reparte_por_espacio_sin_tocar_la_red(self):
        llamadas = []

        def falso(actor, entrada, tope):
            llamadas.append((actor, entrada, tope))
            return [TT] if "tiktok" in actor else [IG, {"url": "https://y", "type": "Image"}]
        d = radar.correr(5, 1.0, HOY, pedir=falso)
        self.assertEqual(d["semana"], "2026-S46")
        self.assertEqual(len(llamadas), 2)                                       # una consulta por plataforma
        self.assertGreaterEqual(llamadas[0][2], 0.5)                             # el tope respeta el mínimo del actor
        self.assertFalse(llamadas[0][1]["shouldDownloadVideos"])
        self.assertEqual(len(d["videos"]), 2)
        self.assertEqual(d["videos"][0]["espacios"], ["castorena", "milla"])
        texto = radar.informe(d)
        self.assertIn("## milla", texto)
        self.assertIn("observación", texto)
        self.assertIn("Nadie te dice esto antes de firmar", texto)

    def test_el_informe_no_lleva_identificadores_largos_de_solo_digitos(self):
        import re
        d = radar.correr(5, 1.0, HOY, pedir=lambda actor, *a: [{**TT, "webVideoUrl": "https://www.tiktok.com/@a/video/7699152372362153237"}] if "tiktok" in actor else [{**IG, "inputUrl": "https://www.instagram.com/explore/tags/abogadosmexico"}])
        texto = radar.informe(d)
        self.assertIsNone(re.search(r"\d{13,}", texto))                         # el detector de tarjetas del repositorio no se dispara
        self.assertIn("https://www.tiktok.com/@a (video del 2026-11-08)", texto)
        self.assertIn("https://www.instagram.com/reel/x/", texto)                # los enlaces sin ese problema se conservan

    def test_no_corre_si_el_plan_pasa_del_tope(self):
        with self.assertRaises(radar.ErrorRadar):
            radar.correr(50, 0.10, HOY, pedir=lambda *a: [])

    def test_un_proveedor_caido_se_informa_y_no_tumba_al_otro(self):
        def falso(actor, entrada, tope):
            if "tiktok" in actor:
                raise radar.ErrorRadar("sin respuesta")
            return [IG]
        d = radar.correr(5, 1.0, HOY, pedir=falso)
        self.assertEqual(len(d["errores"]), 1)
        self.assertEqual(len(d["videos"]), 1)
        self.assertIn("no se pudo consultar", radar.informe(d))


if __name__ == "__main__":
    unittest.main()
