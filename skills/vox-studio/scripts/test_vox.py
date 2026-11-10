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
