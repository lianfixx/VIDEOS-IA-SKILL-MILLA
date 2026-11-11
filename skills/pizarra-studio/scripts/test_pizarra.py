import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pizarra
vox = pizarra.vox


def brief_completo():
    b = json.loads((pizarra.RAIZ / "brief.ejemplo.json").read_text(encoding="utf-8"))
    b["aprobaciones"] = {"resumen": True, "storyboard": True}
    return b


class Entrevista(unittest.TestCase):
    def test_el_ejemplo_responde_todas_las_preguntas(self):
        f = pizarra.faltantes(json.loads((pizarra.RAIZ / "brief.ejemplo.json").read_text(encoding="utf-8")))
        self.assertEqual(f["preguntas"], {})
        self.assertEqual(set(f["aprobaciones"]), {"resumen", "storyboard"})  # responder no es aprobar

    def test_brief_vacio_pide_todo(self):
        f = pizarra.faltantes(pizarra.BRIEF_BASE)
        self.assertEqual(set(f["preguntas"]), set(pizarra.PREGUNTAS))
        self.assertEqual(len(pizarra.PREGUNTAS), 17)

    def test_postura_de_relleno_no_cuenta(self):
        b = brief_completo(); b["respuestas"]["opinion_emi"] = "ok"
        self.assertIn("opinion_emi", pizarra.faltantes(b)["preguntas"])

    def test_render_exige_entrevista_y_storyboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            b = brief_completo(); b["aprobaciones"]["storyboard"] = False
            (d / "brief.json").write_text(json.dumps(b))
            with self.assertRaises(vox.ErrorVox) as cm:
                pizarra.rendir(d)
            self.assertIn("aprobación: storyboard", str(cm.exception))
            (d / "brief.json").write_text(json.dumps(brief_completo()))
            self.assertEqual(pizarra.exigir_aprobado(d)["espacio"], "personal")

    def test_aprobacion_debe_ser_true_exacto(self):
        b = brief_completo(); b["aprobaciones"]["resumen"] = "sí"
        self.assertIn("resumen", pizarra.faltantes(b)["aprobaciones"])


class Marca(unittest.TestCase):
    def test_cada_espacio_llega_al_motor_con_sus_colores(self):
        for nombre, p in vox.perfiles().items():
            piz = pizarra.marca_para_motor(p, "pizarron")
            self.assertEqual(piz["palette"]["orange"], p["colores"]["acento"], nombre)
            self.assertEqual(piz["palette"]["ink"], p["colores"]["tinta"], nombre)
            est = pizarra.marca_para_motor(p, "estilos")
            self.assertEqual(est["palette"], {"accent": p["colores"]["acento"], "bg": p["colores"]["papel"]}, nombre)
        self.assertEqual(pizarra.marca_para_motor(vox.perfiles()["castorena"], "estilos")["font"]["display"], "Gelasio")

    def test_proyecto_no_mezcla_espacios_ni_inventa_estilo(self):
        self.assertEqual(pizarra.main(["proyecto", "/tmp/x/milla/tema", "--perfil", "personal", "--modo", "pizarron"]), 2)
        self.assertEqual(pizarra.main(["proyecto", "/tmp/x/personal/tema", "--perfil", "personal", "--modo", "estilos"]), 2)


class Motor(unittest.TestCase):
    def test_sin_motor_o_con_otro_commit_no_se_produce(self):
        previo = os.environ.get("PIZARRA_MOTOR")
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["PIZARRA_MOTOR"] = tmp
            try:
                with self.assertRaises(vox.ErrorVox):
                    pizarra.exigir_motor()
            finally:
                if previo is None:
                    del os.environ["PIZARRA_MOTOR"]
                else:
                    os.environ["PIZARRA_MOTOR"] = previo
        self.assertEqual(len(pizarra.MOTOR_COMMIT), 40)

    def test_el_codigo_del_motor_no_esta_en_el_repositorio(self):
        raiz = pizarra.RAIZ
        self.assertFalse(any(raiz.rglob("engine.js")))
        self.assertFalse((raiz / "template").exists() or (raiz / "template-estilos").exists())


class Sonido(unittest.TestCase):
    def test_rejilla_de_beats_exacta(self):
        r = pizarra.rejilla_beats({"bpm": 120}, 10.0, [3.0, 6.5])
        self.assertEqual(r["tempo"], 120.0)
        self.assertEqual(r["beats"][:3], [0.0, 0.5, 1.0])
        self.assertEqual(len(r["beats"]), len(r["strength"]))
        self.assertEqual(r["strength"][:5], [1.0, 0.45, 0.45, 0.45, 1.0])
        self.assertEqual(r["sections"], [0.0, 3.0, 6.5])

    def test_voz_reparte_tiempos_reales_sin_volver_a_pagar(self):
        import shutil, subprocess
        if not shutil.which("ffmpeg"):
            self.skipTest("sin ffmpeg")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp); (d / "audio").mkdir()
            (d / "brief.json").write_text(json.dumps(brief_completo()))
            (d / "guion.json").write_text(json.dumps({"escenas": [{"id": "01", "narracion": "Uno dos tres."}, {"id": "02", "narracion": "Cuatro cinco."}]}))
            self.assertTrue(pizarra.narrar_guion(d, False)["en_seco"])
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=f=220:d=3", str(d / "t.mp3")], check=True)
            llamadas = []
            real = vox.narrar
            def falso(texto, voz):
                llamadas.append(texto)
                return (d / "t.mp3").read_bytes(), [{"t": w, "a": i * 0.5, "b": i * 0.5 + 0.4} for i, w in enumerate(texto.split())]
            vox.narrar = falso
            try:
                r = pizarra.narrar_guion(d, True)
                pizarra.narrar_guion(d, True)  # misma narración: usa lo ya pagado
            finally:
                vox.narrar = real
            self.assertEqual(len(llamadas), 1)
            self.assertEqual([t["inicio"] for t in r["escenas"]], [0.0, 1.5])
            self.assertAlmostEqual(r["escenas"][0]["dur"], 1.5)
            palabras = json.loads((d / "audio" / "words.json").read_text())
            self.assertEqual(palabras[0], {"w": "Uno", "s": 0.0, "e": 0.4})
            self.assertTrue((d / "audio" / "vo.wav").is_file() and (d / "tiempos.json").is_file())


class Hoja(unittest.TestCase):
    def test_hoja_de_contacto_con_guia(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp); (d / "stills").mkdir()
            for i in range(3):
                Image.new("RGB", (1080, 1920), "white").save(d / "stills" / f"s_{i}.jpg")
            self.assertEqual(pizarra.hoja(d, d / "out" / "hoja.jpg", cols=3), 3)
            with Image.open(d / "out" / "hoja.jpg") as im:
                self.assertEqual(im.size[0], 660)
                r, g, b = im.getpixel((110, 5))       # barra superior: sombreada
                self.assertTrue(r > g + 20)
                self.assertEqual(im.getpixel((110, 200))[1] > 240, True)  # zona útil: intacta
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(vox.ErrorVox):
            pizarra.hoja(Path(tmp), Path(tmp) / "h.jpg")


if __name__ == "__main__":
    unittest.main()
