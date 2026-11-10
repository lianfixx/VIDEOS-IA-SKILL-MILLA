import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vox


def guion():
    g = {
        "perfil": "personal", "titulo": "Prueba", "cta_pregunta": "¿Tú qué opinas?",
        "opinion_emi": "Postura de prueba suficientemente larga para pasar.",
        "musica": {"animo": "tension"},
        "escenas": [{"id": f"0{i}", "narracion": f"Frase número {i} de prueba.", "keyword": f"CLAVE {i}", "resaltar": "CLAVE"} for i in range(1, 5)],
    }
    g["escenas"][0]["sonido"] = "boom"
    g["escenas"][-1]["narracion"] = "¿Tú qué opinas de esto?"
    return g


def alinear(g, paso=0.2):
    palabras, t = [], 0.0
    for w in vox.texto_completo(g).split():
        palabras.append({"t": w, "a": t, "b": t + paso * 0.8})
        t += paso
    return palabras, t


class Guion(unittest.TestCase):
    def errores(self, g):
        return " | ".join(vox.validar_guion(g))

    def test_valido(self):
        self.assertEqual(vox.validar_guion(guion()), [])

    def test_exige_opinion_y_pregunta_narrada(self):
        g = guion(); g["opinion_emi"] = ""; g["escenas"][-1]["narracion"] = "Fin."
        self.assertIn("opinion_emi", self.errores(g))
        self.assertIn("pregunta de cierre", self.errores(g))

    def test_entrada_efectiva_repetida(self):
        g = guion(); g["escenas"][2]["entrada"] = vox.ENTRADAS[1]  # la 2 usa esa por defecto
        self.assertIn("repite la entrada", self.errores(g))

    def test_resaltar_ignora_signos(self):
        g = guion(); g["escenas"][0].update(keyword="¿EN SERIO?", resaltar="SERIO")
        self.assertEqual(vox.validar_guion(g), [])
        g["escenas"][0]["resaltar"] = "OTRA"
        self.assertIn("no es una palabra", self.errores(g))

    def test_textos_que_no_caben(self):
        g = guion(); g["escenas"][0]["keyword"] = "INCONSTITUCIONALIDAD"
        self.assertIn("16 letras", self.errores(g))
        g = guion(); g["escenas"][0].update(keyword="CINCOS LETRAS VARIAS LINEAS MUCHAS", resaltar="")
        self.assertIn("líneas", self.errores(g))
        g = guion(); g["escenas"][0]["nota"] = "x" * 60
        self.assertIn("nota pasa", self.errores(g))

    def test_ruta_de_imagen(self):
        g = guion(); g["escenas"][0]["imagen_archivo"] = "../../etc/x.png"
        self.assertIn("imagen_archivo", self.errores(g))

    def test_espacios_completos(self):
        self.assertEqual(set(vox.perfiles()), {"personal", "milla", "castorena", "pan"})
        for nombre, p in vox.perfiles().items():
            c = p["colores"]
            self.assertEqual(set(c), {"papel", "tinta", "acento", "apoyo"}, nombre)
            self.assertNotEqual(c["apoyo"], c["tinta"], nombre)
            self.assertTrue(p["voz"]["voice_id"], nombre)
            self.assertIn(p["titular"], {"Anton", "Gelasio"}, nombre)


class Sonido(unittest.TestCase):
    def test_exige_musica_y_un_efecto(self):
        g = guion(); g.pop("musica"); g["escenas"][0].pop("sonido")
        errores = " | ".join(vox.validar_guion(g))
        self.assertIn("musica.animo", errores)
        self.assertIn("ninguna escena tiene `sonido`", errores)
        g = guion(); g["escenas"][1]["sonido"] = "risas"
        self.assertIn("no existe", " | ".join(vox.validar_guion(g)))

    def test_musica_original_a_la_medida(self):
        import numpy as np
        for animo in vox.SON.ANIMOS:
            a = vox.SON.componer(animo, 6.0)
            self.assertEqual(len(a), 6 * vox.SON.SR, animo)
            self.assertLessEqual(float(np.abs(a).max()), 0.51, animo)
            self.assertGreater(float(np.sqrt((a ** 2).mean())), 0.03, animo)
            self.assertTrue(np.array_equal(a, vox.SON.componer(animo, 6.0)), animo)  # determinista

    def test_efectos_se_sintetizan(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(vox.SON.sintetizar_efectos(Path(d)), sorted(vox.SON.EFECTOS))
            self.assertTrue(all((Path(d) / f"{n}.wav").stat().st_size > 5000 for n in vox.SON.EFECTOS))

    def test_propuesta_segun_contenido_y_espacio(self):
        g = guion(); g["escenas"][1]["narracion"] = "Pero te mintieron: eso cuesta mucho dinero."
        pr = vox.SON.proponer(g)
        self.assertEqual(pr["musica"]["animo"], "tension")
        self.assertEqual(pr["escenas"][0]["sonido"], "boom")
        self.assertIn(pr["escenas"][1]["sonido"], {"caja", "scratch"})
        g["perfil"] = "castorena"; g["escenas"][2]["narracion"] = "Fracasó y nadie lo vio."
        pr = vox.SON.proponer(g)
        self.assertNotIn("trombon", [x["sonido"] for x in pr["escenas"]])
        self.assertTrue(all(not x["remate"] for x in pr["escenas"]))

    def test_portada_y_remate_en_la_linea_de_tiempo(self):
        g = guion(); g["escenas"][1]["remate"] = "plot twist"; palabras, fin = alinear(g)
        v = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])
        self.assertEqual(v["portada"]["texto"], "CLAVE 1")
        self.assertEqual(v["escenas"][1]["remate"], "PLOT TWIST")
        self.assertEqual(v["musica"], "audio/musica.wav")
        self.assertAlmostEqual(v["finVoz"], palabras[-1]["b"], places=2)


class NuevoPorVideo(unittest.TestCase):
    def test_cada_video_tiene_su_musica(self):
        import numpy as np
        p1, p2 = vox.SON.plan_musica("energia", 1), vox.SON.plan_musica("energia", 2)
        self.assertNotEqual((p1["tonica"], p1["bpm"], p1["progresion"]), (p2["tonica"], p2["bpm"], p2["progresion"]))
        a = vox.SON.componer("energia", 6.0, 1, [2.0, 4.0])
        self.assertFalse(np.array_equal(a, vox.SON.componer("energia", 6.0, 2, [2.0, 4.0])))
        self.assertFalse(np.array_equal(a, vox.SON.componer("energia", 6.0, 1)))  # sigue los cambios de escena
        self.assertTrue(np.array_equal(a, vox.SON.componer("energia", 6.0, 1, [2.0, 4.0])))

    def test_efectos_afinados_a_la_musica(self):
        with tempfile.TemporaryDirectory() as d:
            vox.SON.sintetizar_efectos(Path(d) / "a", 1, 45)
            vox.SON.sintetizar_efectos(Path(d) / "b", 1, 50)
            self.assertNotEqual((Path(d) / "a" / "ding.wav").read_bytes(), (Path(d) / "b" / "ding.wav").read_bytes())


class Biblioteca(unittest.TestCase):
    def test_catalogar_buscar_y_reciclar(self):
        import json, os
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["VOX_BIBLIOTECA"] = str(Path(tmp) / "bib")
            try:
                d = Path(tmp) / "productions" / "personal" / "tema"
                (d / "public" / "img").mkdir(parents=True); (d / "prompts").mkdir()
                Image.new("RGBA", (1600, 900), (200, 30, 30, 255)).save(d / "public" / "img" / "01.png")
                (d / "prompts" / "01.txt").write_text("Una pesa rusa roja")
                g = guion(); g["escenas"][0]["imagen_archivo"] = "img/01.png"
                (d / "guion.json").write_text(json.dumps(g))
                self.assertEqual([x["id"] for x in vox.catalogar(d)], ["personal-tema-01"])
                self.assertEqual(vox.catalogar(d), [])  # no duplica
                self.assertEqual(len(vox.buscar_en_biblioteca("pesa roja")), 1)
                self.assertEqual(vox.buscar_en_biblioteca("pesa", "milla"), [])
                self.assertEqual(vox.buscar_en_biblioteca("bicicleta"), [])
                with Image.open(Path(tmp) / "bib" / "personal" / "personal-tema-01.png") as im:
                    self.assertLessEqual(max(im.size), 1200)
                otro = Path(tmp) / "productions" / "personal" / "otro"
                self.assertEqual(vox.main(["reciclar", "personal-tema-01", "--dir", str(otro)]), 0)
                self.assertTrue((otro / "public" / "img" / "personal-tema-01.png").is_file())
                self.assertEqual(vox.leer_catalogo()[0]["usos"], 2)
            finally:
                del os.environ["VOX_BIBLIOTECA"]


class Fotos(unittest.TestCase):
    def test_candidatas_con_su_fuente(self):
        import json
        real = vox._pedir
        visto = {}
        def falso(url, **kw):
            visto.update(url=url, **kw)
            return json.dumps([{"imageUrl": "https://ejemplo.org/a.jpg", "sourceUrl": "https://ejemplo.org/p", "sourceDomain": "ejemplo.org", "title": "A", "imageWidth": 1200, "imageHeight": 800}, {"title": "sin imagen"}]).encode()
        vox._pedir = falso
        try:
            fotos = vox.buscar_fotos("Palacio de Bellas Artes", 5, 0.1)
        finally:
            vox._pedir = real
        self.assertEqual(fotos, [{"imagen": "https://ejemplo.org/a.jpg", "pagina": "https://ejemplo.org/p", "dominio": "ejemplo.org", "titulo": "A", "ancho": 1200, "alto": 800}])
        self.assertIn("maxTotalChargeUsd=0.1", visto["url"])
        self.assertNotIn("token=", visto["url"])  # el token va en cabecera, nunca en la URL
        self.assertEqual(visto["cuerpo"]["usageRights"], "creative_commons")

    def test_licencia_de_commons(self):
        import json
        real = vox._pedir
        vox._pedir = lambda url, **kw: json.dumps({"query": {"pages": {"1": {"imageinfo": [{"extmetadata": {
            "LicenseShortName": {"value": "CC BY-SA 3.0"}, "Artist": {"value": "<a href='x'>Autora</a>"}, "AttributionRequired": {"value": "true"}}}]}}}}).encode()
        try:
            lic = vox.licencia_commons("https://upload.wikimedia.org/wikipedia/commons/9/97/Foto_01.jpg?utm=1")
            self.assertEqual((lic["licencia"], lic["autor"]), ("CC BY-SA 3.0", "Autora"))
            self.assertTrue(lic["ficha"].endswith("File:Foto_01.jpg"))
            self.assertIsNone(vox.licencia_commons("https://otro.sitio/foto.jpg"))
        finally:
            vox._pedir = real

    def test_en_seco_no_llama(self):
        self.assertEqual(vox.main(["foto", "--consulta", "x", "--dir", "/tmp/nada"]), 0)
        self.assertEqual(vox.main(["foto", "--consulta", "x", "--dir", "/tmp/nada", "--max", "50", "--execute"]), 2)
        self.assertEqual(vox.main(["foto", "--consulta", "x", "--dir", "/tmp/nada", "--tope-usd", "0.05", "--execute"]), 2)  # tope que abortaría cobrando


class Tiempos(unittest.TestCase):
    def test_escenas_salen_de_las_palabras(self):
        g = guion(); palabras, fin = alinear(g)
        v = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])
        self.assertEqual(v["escenas"][0]["desde"], 0)
        self.assertEqual(sum(e["dur"] for e in v["escenas"]), v["frames"])
        self.assertAlmostEqual(v["escenas"][1]["desde"] / vox.FPS, palabras[5]["a"] - 0.12, delta=0.04)
        self.assertEqual(len({(a["transicion"], b["transicion"]) for a, b in zip(v["escenas"][1:], v["escenas"][2:]) if a["transicion"] == b["transicion"]}), 0)

    def test_alineacion_incompleta_no_se_inventa(self):
        g = guion(); palabras, fin = alinear(g)
        with self.assertRaises(vox.ErrorVox):
            vox.armar_video(g, palabras[:-1], fin, vox.perfiles()["personal"])

    def test_escena_demasiado_corta(self):
        g = guion(); palabras, fin = alinear(g, paso=0.02)
        with self.assertRaises(vox.ErrorVox):
            vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])

    def test_imagen_inexistente(self):
        g = guion(); g["escenas"][0]["imagen_archivo"] = "img/no.png"; palabras, fin = alinear(g)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(vox.ErrorVox):
            vox.armar_video(g, palabras, fin, vox.perfiles()["personal"], Path(d))

    def test_caracteres_a_palabras(self):
        t = "Hola,  mundo cruel"
        p = vox.palabras_desde_alineacion(list(t), [i * 0.1 for i in range(len(t))], [i * 0.1 + 0.1 for i in range(len(t))])
        self.assertEqual([x["t"] for x in p], ["Hola,", "mundo", "cruel"])


class Recorte(unittest.TestCase):
    def recorta(self, fondo, pintar):
        from PIL import Image
        d = Path(tempfile.mkdtemp())
        im = Image.new("RGB", (200, 200), fondo)
        pintar(im)
        im.save(d / "a.png")
        size = vox.recortar_croma(d / "a.png", d / "b.png")
        out = Image.open(d / "b.png"); out.load()
        return size, out

    def test_quita_fondo_y_conserva_sujeto(self):
        (w, h), out = self.recorta((0, 255, 0), lambda im: im.paste((220, 60, 30), (60, 50, 140, 160)))
        self.assertTrue(74 <= w <= 86 and 104 <= h <= 116)
        self.assertEqual(out.getpixel((w // 2, h // 2)), (220, 60, 30, 255))

    def test_verde_dentro_del_sujeto_no_se_agujera(self):
        def pintar(im):
            im.paste((220, 60, 30), (50, 40, 150, 170))
            im.paste((40, 150, 50), (85, 90, 115, 120))  # una hoja: verde, pero no el del fondo
            im.paste((0, 255, 0), (60, 50, 80, 70))  # hueco real: idéntico al fondo
        (w, h), out = self.recorta((0, 255, 0), pintar)
        self.assertEqual(out.getpixel((w // 2, h // 2))[3], 255)
        self.assertEqual(out.getpixel((20, 20))[3], 0)

    def test_fondo_magenta_o_verde_oscuro(self):
        for fondo in [(255, 0, 255), (0, 60, 0), (200, 255, 200)]:
            (w, h), _ = self.recorta(fondo, lambda im: im.paste((30, 30, 200), (60, 50, 140, 160)))
            self.assertTrue(w < 100 and h < 130, fondo)

    def test_sin_sujeto_o_fondo_irregular(self):
        with self.assertRaises(vox.ErrorVox):
            self.recorta((0, 255, 0), lambda im: None)
        with self.assertRaises(vox.ErrorVox):
            self.recorta((0, 255, 0), lambda im: im.paste((250, 250, 250), (0, 0, 200, 60)))


class Proveedor(unittest.TestCase):
    def test_modelo_sin_contrato(self):
        with self.assertRaises(vox.ErrorVox):
            vox.generar_imagen("x", Path("/tmp/x.jpg"), Path("/tmp/no-existe.json"), modelo="otro")

    def test_estado_de_otro_prompt(self):
        with tempfile.TemporaryDirectory() as d:
            est = Path(d) / "e.json"
            est.write_text('{"taskId": "t", "firma": "vieja"}')
            with self.assertRaises(vox.ErrorVox):
                vox.generar_imagen("nuevo prompt", Path(d) / "o.jpg", est)

    def test_solo_https(self):
        with self.assertRaises(vox.ErrorVox):
            vox._pedir("http://api.kie.ai/x")

    def test_tabla_de_saldo(self):
        t = vox.tabla_saldo({"kie_creditos": 240, "elevenlabs_usados": 100},
                            {"kie_creditos": 232, "elevenlabs_usados": 431, "elevenlabs_restantes": 39569, "elevenlabs_limite": 40000, "apify": "no conectado (falta el token)"})
        self.assertIn("8 créditos | 232", t)
        self.assertIn("331 caracteres | 39569", t)
        self.assertIn("no conectado", t)


if __name__ == "__main__":
    unittest.main()
