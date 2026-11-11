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

    def test_preferencias_permanentes_no_se_vuelven_a_preguntar(self):
        pref = pizarra.preferencias()
        self.assertIn("sin personaje", pref["personaje"])
        self.assertIn("voz del espacio", pref["voz"])
        self.assertNotIn("estilo", pref)   # Emi quiere decidirlos en cada video
        self.assertNotIn("musica", pref)
        b = {**pizarra.BRIEF_BASE, "respuestas": {**pizarra.BRIEF_BASE["respuestas"], **pref}}
        self.assertEqual(len(pizarra.faltantes(b)["preguntas"]), 15)

    def test_respuestas_que_no_son_texto_no_cuentan(self):
        b = brief_completo()
        for k in b["respuestas"]:
            if k != "opinion_emi":
                b["respuestas"][k] = None
        self.assertEqual(len(pizarra.faltantes(b)["preguntas"]), 16)
        b["respuestas"] = ["x"]
        with self.assertRaises(vox.ErrorVox):
            pizarra.faltantes(b)

    def test_lectura_del_brief(self):
        self.assertEqual(pizarra.leer_formato("horizontal 16:9"), (1920, 1080))
        self.assertEqual(pizarra.leer_formato("Horizontal (YouTube)"), (1920, 1080))
        self.assertEqual(pizarra.leer_formato("vertical 9:16"), (1080, 1920))
        self.assertEqual(pizarra.leer_duracion("60s"), (60, 60))
        self.assertEqual(pizarra.leer_duracion("45 a 60"), (45, 60))
        self.assertEqual(pizarra.leer_duracion("1:00"), (60, 60))
        self.assertEqual(pizarra.leer_duracion("1 minuto"), (60, 60))
        self.assertIsNone(pizarra.leer_duracion("lo que haga falta"))
        self.assertTrue(pizarra.sin_efectos("sin efectos") and pizarra.sin_efectos("No") and not pizarra.sin_efectos("sí"))

    def test_voz_no_se_paga_sin_entrevista_ni_si_emi_no_la_pidio(self):
        real = vox.narrar
        vox.narrar = lambda *a: self.fail("no debía llamar al proveedor")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                (d / "guion.json").write_text(json.dumps({"escenas": [{"id": "01", "narracion": "Hola a todos."}]}))
                (d / "brief.json").write_text(json.dumps({**pizarra.BRIEF_BASE, "espacio": "personal"}))
                with self.assertRaises(vox.ErrorVox):
                    pizarra.narrar_guion(d, True)
                b = brief_completo(); b["respuestas"]["voz"] = "solo texto en pantalla"
                (d / "brief.json").write_text(json.dumps(b))
                with self.assertRaises(vox.ErrorVox) as cm:
                    pizarra.narrar_guion(d, True)
                self.assertIn("No se narra", str(cm.exception))
        finally:
            vox.narrar = real

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
        self.assertEqual(pizarra.main(["proyecto", "/tmp/x/productions/milla/tema", "--perfil", "personal", "--modo", "pizarron"]), 2)
        self.assertEqual(pizarra.main(["proyecto", "/tmp/x/productions/personal/tema", "--perfil", "personal", "--modo", "estilos"]), 2)
        self.assertEqual(pizarra.main(["proyecto", "/tmp/x/personal/tema", "--perfil", "personal", "--modo", "pizarron"]), 2)  # fuera de productions/

    def test_estilos_sin_personaje_y_con_subtitulos_reales(self):
        cfg = pizarra.marca_para_motor(vox.perfiles()["personal"], "estilos", "cuaderno")
        self.assertEqual((cfg["style"], cfg["mascot"], cfg["person"], cfg["words"]), ("cuaderno", "none", False, "audio/words.json"))


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
        self.assertEqual(r["strength"][:5], [1.5, 0.5, 0.5, 0.5, 1.5])
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
            self.assertEqual(pizarra.args_modo(d), ["--mode", "B"])  # con voz, sin ajuste al beat: en qa, medición y render
            self.assertAlmostEqual(r["escenas"][0]["dur"], 1.5)
            palabras = json.loads((d / "audio" / "words.json").read_text())
            self.assertEqual(palabras[0], {"w": "Uno", "s": 0.0, "e": 0.4})
            self.assertTrue((d / "audio" / "vo.wav").is_file() and (d / "tiempos.json").is_file())


class Duracion(unittest.TestCase):
    def test_lee_la_duracion_de_los_dos_motores(self):
        real = pizarra._node
        try:
            with tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                pizarra._node = lambda d, *a, **k: "stills done (1), duration 60.33s\n"
                self.assertAlmostEqual(pizarra.duracion_del_video(d), 60.33)
                (d / "engine").mkdir(); (d / "video.js").write_text("")
                visto = {}
                def estilos(d, *a, **k):
                    visto["args"] = a
                    return "stills: 1 → _medir/  (duración 43.00s)\n"
                pizarra._node = estilos
                self.assertAlmostEqual(pizarra.duracion_del_video(d), 43.0)
                self.assertIn("--outdir", visto["args"])  # no ensucia stills/
                pizarra._node = lambda d, *a, **k: "nada"
                with self.assertRaises(vox.ErrorVox):
                    pizarra.duracion_del_video(d)
        finally:
            pizarra._node = real


class Navegador(unittest.TestCase):
    def test_no_devuelve_rutas_que_no_existen(self):
        previo = os.environ.get("CHROME_PATH")
        os.environ["CHROME_PATH"] = "/no/existe/chrome"
        try:
            self.assertNotEqual(pizarra.navegador(), "/no/existe/chrome")
            self.assertTrue(pizarra.navegador() == "" or Path(pizarra.navegador()).is_file())
        finally:
            if previo is None:
                del os.environ["CHROME_PATH"]
            else:
                os.environ["CHROME_PATH"] = previo


class Cortes(unittest.TestCase):
    def test_cortes_de_la_voz_o_de_los_golpes_del_motor(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp); (d / "audio").mkdir()
            self.assertEqual(pizarra.cortes_del_video(d), [])
            (d / "hits.json").write_text(json.dumps([{"t": 9.5}, {"t": 4.25}]))
            self.assertEqual(pizarra.cortes_del_video(d), [4.25, 9.5])
            (d / "tiempos.json").write_text(json.dumps({"escenas": [{"inicio": 0}, {"inicio": 3.2}, {"inicio": 7.0}]}))
            self.assertEqual(pizarra.cortes_del_video(d), [4.25, 9.5])   # sin voz, la voz no manda
            (d / "audio" / "vo.wav").write_bytes(b"x")
            self.assertEqual(pizarra.cortes_del_video(d), [3.2, 7.0])

    def test_cierre_exige_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "out").mkdir()
            self.assertEqual(pizarra.main(["cierre", tmp]), 2)


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
        with self.assertRaises(vox.ErrorVox):
            pizarra.cuadros_de_prueba(Path("/tmp"), 0)


class Sincronia(unittest.TestCase):
    def test_desfase_entre_dos_envolventes(self):
        import math
        base = [abs(math.sin(i / 7.0)) * (1 if (i // 50) % 2 else 0.2) for i in range(2000)]
        self.assertEqual(pizarra.desfase_ms(base, base), 0)
        self.assertEqual(pizarra.desfase_ms(base, [0.0] * 25 + base), 25)
        self.assertEqual(pizarra.desfase_ms([0.0] * 12 + base, base), -12)

    def test_sin_render_no_mide(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(pizarra.ErrorVox):
                pizarra.medir_sincronia(Path(tmp))

    def test_techos_del_limitador_van_de_abierto_a_cerrado(self):
        self.assertEqual(list(pizarra.TECHOS_LIMITADOR), sorted(pizarra.TECHOS_LIMITADOR, reverse=True))
        self.assertLessEqual(max(pizarra.TECHOS_LIMITADOR), 0.75)


if __name__ == "__main__":
    unittest.main()
