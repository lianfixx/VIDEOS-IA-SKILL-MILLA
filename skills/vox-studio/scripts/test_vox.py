import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vox


def guion():
    return {
        "perfil": "personal", "titulo": "Prueba", "cta_pregunta": "¿Tú qué opinas?",
        "opinion_emi": "Postura de prueba suficientemente larga para pasar.",
        "escenas": [
            {"id": f"0{i}", "narracion": f"Frase número {i} de prueba.", "keyword": f"CLAVE {i}", "resaltar": "CLAVE",
             "entrada": vox.ENTRADAS[i % len(vox.ENTRADAS)]} for i in range(1, 5)
        ],
    }


class Guion(unittest.TestCase):
    def test_valido(self):
        self.assertEqual(vox.validar_guion(guion()), [])

    def test_exige_opinion(self):
        g = guion(); g["opinion_emi"] = ""
        self.assertTrue(any("opinion_emi" in e for e in vox.validar_guion(g)))

    def test_exige_pregunta_final(self):
        g = guion(); g["cta_pregunta"] = "Sígueme"
        self.assertTrue(any("cta_pregunta" in e for e in vox.validar_guion(g)))

    def test_entrada_repetida_y_resaltar(self):
        g = guion(); g["escenas"][1]["entrada"] = g["escenas"][0]["entrada"]; g["escenas"][2]["resaltar"] = "OTRA"
        errores = " ".join(vox.validar_guion(g))
        self.assertIn("repite la entrada", errores)
        self.assertIn("no es una palabra", errores)

    def test_perfiles_completos(self):
        for nombre, p in vox.perfiles().items():
            self.assertEqual(set(p["colores"]), {"papel", "tinta", "acento", "apoyo"}, nombre)
            self.assertTrue(p["voz"]["voice_id"], nombre)


class Tiempos(unittest.TestCase):
    def test_palabras_y_escenas_salen_de_la_alineacion(self):
        g = guion()
        texto, rangos = vox.texto_completo(g)
        ini = [i * 0.05 for i in range(len(texto))]
        fin = [t + 0.05 for t in ini]
        palabras = vox.palabras_desde_alineacion(list(texto), ini, fin)
        self.assertEqual(" ".join(p["t"] for p in palabras), texto)
        v = vox.armar_video(g, palabras, fin[-1], vox.perfiles()["personal"])
        self.assertEqual(v["escenas"][0]["desde"], 0)
        self.assertEqual(sum(e["dur"] for e in v["escenas"]), v["frames"])
        for e, (a, _) in zip(v["escenas"][1:], rangos[1:]):
            self.assertAlmostEqual(e["desde"] / vox.FPS, ini[a] - 0.12, delta=0.04)

    def test_sin_alineacion_no_se_inventa(self):
        g = guion()
        with self.assertRaises(vox.ErrorVox):
            vox.armar_video(g, [], 5.0, vox.perfiles()["personal"])


class Recorte(unittest.TestCase):
    def test_croma_quita_verde_y_conserva_sujeto(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            im = Image.new("RGB", (200, 200), (0, 255, 0))
            im.paste((220, 60, 30), (60, 50, 140, 160))
            im.save(Path(d) / "a.png")
            w, h = vox.recortar_croma(Path(d) / "a.png", Path(d) / "b.png")
            self.assertTrue(70 <= w <= 84 and 100 <= h <= 114)
            out = Image.open(Path(d) / "b.png")
            self.assertEqual(out.getpixel((w // 2, h // 2))[3], 255)

    def test_modelo_sin_contrato_se_rechaza(self):
        with self.assertRaises(vox.ErrorVox):
            vox.generar_imagen("x", Path("/tmp/x.jpg"), Path("/tmp/no-existe-estado.json"), modelo="otro-modelo")


if __name__ == "__main__":
    unittest.main()
