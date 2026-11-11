import os
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
        "ganchos_propuestos": ["Te mintieron.", "Nadie te lo dijo."], "gancho_elegido": 0,
        "escenas": [{"id": f"0{i}", "narracion": f"Frase número {i} de prueba.", "keyword": f"CLAVE {i}", "resaltar": "CLAVE",
                     "funcion": ["gancho", "dato", "opinion", "cierre"][i - 1]} for i in range(1, 5)],
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

    def test_el_ejemplo_de_la_plantilla_es_valido(self):
        import json
        ej = json.loads((vox.PLANTILLA / "guion.ejemplo.json").read_text(encoding="utf-8"))
        self.assertEqual(vox.validar_guion(ej), [])

    def test_exige_opinion_y_pregunta_narrada(self):
        g = guion(); g["opinion_emi"] = ""; g["escenas"][-1]["narracion"] = "Fin."
        self.assertIn("opinion_emi", self.errores(g))
        self.assertIn("pregunta de cierre", self.errores(g))

    def test_lo_automatico_se_aparta_de_lo_elegido(self):
        g = guion(); g["escenas"][2]["entrada"] = vox.ENTRADAS[1]; g["escenas"][2]["transicion"] = "rasgado"
        self.assertEqual(vox.validar_guion(g), [])
        for campo, ciclo in (("entrada", vox.ENTRADAS), ("transicion", vox.TRANSICIONES)):
            ef = vox.efectivas(g["escenas"], campo, ciclo)
            self.assertEqual(ef[2], g["escenas"][2][campo])
            self.assertTrue(all(a != b for a, b in zip(ef, ef[1:])), ef)

    def test_dos_elegidas_iguales_seguidas_se_rechazan(self):
        g = guion(); g["escenas"][1]["entrada"] = g["escenas"][2]["entrada"] = "cae"
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
                ident = vox.catalogar(d)[0]["id"]
                self.assertTrue(ident.startswith("personal-tema-01-") and len(ident) == 25)
                self.assertEqual(vox.catalogar(d), [])  # no duplica
                self.assertEqual(len(vox.buscar_en_biblioteca("pesa roja")), 1)
                self.assertEqual(vox.buscar_en_biblioteca("pesa", "milla"), [])
                self.assertEqual(vox.buscar_en_biblioteca("bicicleta"), [])
                with Image.open(Path(tmp) / "bib" / "personal" / f"{ident}.png") as im:
                    self.assertLessEqual(max(im.size), 1200)
                otro = Path(tmp) / "productions" / "personal" / "otro"
                self.assertEqual(vox.main(["reciclar", ident, "--dir", str(otro), "--como", "../../../FUERA.png"]), 0)
                self.assertTrue((otro / "public" / "img" / "FUERA.png").is_file())  # --como no puede salir de la producción
                self.assertFalse((Path(tmp) / "FUERA.png").exists())
                self.assertEqual(vox.leer_catalogo()[0]["usos"], 2)
                Image.new("RGBA", (300, 300), (20, 200, 30, 255)).save(d / "public" / "img" / "01.png")  # la imagen se regenera
                otro_id = vox.catalogar(d)[0]["id"]
                self.assertNotEqual(otro_id, ident)
                self.assertEqual(len({c["archivo"] for c in vox.leer_catalogo()}), 2)
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


class Niveles(unittest.TestCase):
    def test_todos_los_efectos_al_mismo_nivel(self):
        with tempfile.TemporaryDirectory() as d:
            vox.SON.sintetizar_efectos(Path(d), 5, 47)
            for n in vox.SON.EFECTOS:
                self.assertAlmostEqual(vox.SON.leer_nivel(Path(d) / f"{n}.wav"), vox.SON.NIVEL_EFECTO, delta=2.5, msg=n)

    def test_la_musica_respira_con_las_escenas(self):
        import numpy as np
        for animo in ("serio", "ironia", "energia"):
            a = vox.SON.componer(animo, 24.0, 3, [8.0, 16.0])
            rms = [float(np.sqrt(np.mean(a[int(i * 8 * vox.SON.SR) + vox.SON.SR:int((i + 1) * 8 * vox.SON.SR) - vox.SON.SR] ** 2))) for i in range(3)]
            self.assertLess(rms[1], rms[2] * 0.93, animo)  # la escena intermedia es más ligera que el cierre

    def test_propuesta_no_confunde_palabras(self):
        g = guion()
        for s, txt in zip(g["escenas"], ["El decreto es secreto.", "Una leyenda de metal.", "Algo concreto pasó.", "¿Y luego?"]):
            s["narracion"] = txt
        self.assertEqual(sum(vox.SON.proponer(g)["musica"]["votos"].values()), 0)

    def test_remate_exige_sonido_y_no_va_en_la_primera(self):
        g = guion(); g["escenas"][2]["remate"] = "ASÍ NO"
        self.assertIn("cae con su sonido", " | ".join(vox.validar_guion(g)))
        g = guion(); g["escenas"][0]["remate"] = "ZAS"
        self.assertIn("primera escena", " | ".join(vox.validar_guion(g)))

    def test_tipos_raros_no_rompen_el_validador(self):
        g = guion(); g["escenas"][1]["transicion"] = ["x"]
        self.assertIn("debe ser texto", " | ".join(vox.validar_guion(g)))

    def test_commons_miniatura_y_archivo_local(self):
        import json
        real = vox._pedir
        visto = {}
        def falso(url, **kw):
            visto["url"] = url
            return json.dumps({"query": {"pages": {"1": {"imageinfo": [{"extmetadata": {"LicenseShortName": {"value": "CC0"}}}]}}}}).encode()
        vox._pedir = falso
        try:
            vox.licencia_commons("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Palacio_Nacional.jpg/1200px-Palacio_Nacional.jpg")
            self.assertIn("File%3APalacio_Nacional.jpg", visto["url"])
            self.assertIsNone(vox.licencia_commons("https://upload.wikimedia.org/wikipedia/en/a/ab/Logo.png"))
        finally:
            vox._pedir = real

    def test_foto_bajar_valida_indice_y_destino(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "p"; (d / "estados").mkdir(parents=True)
            (d / "estados" / "fotos.json").write_text(json.dumps({"candidatas": [{"imagen": "https://ejemplo.org/a.jpg", "pagina": "x"}]}))
            self.assertEqual(vox.main(["foto-bajar", "--dir", str(d), "--indice", "5", "--out", str(d / "a.jpg"), "--licencia", "CC0 de alguien"]), 2)
            self.assertEqual(vox.main(["foto-bajar", "--dir", str(d), "--indice", "-1", "--out", str(d / "a.jpg"), "--licencia", "CC0 de alguien"]), 2)
            self.assertEqual(vox.main(["foto-bajar", "--dir", str(d), "--indice", "0", "--out", str(Path(tmp) / "fuera.jpg"), "--licencia", "CC0 de alguien"]), 2)


class Oficio(unittest.TestCase):
    def test_avisos_de_guion(self):
        g = guion()
        g["escenas"][0]["narracion"] = " ".join(["palabra"] * 30)
        avisos = " | ".join(vox.avisos_guion(g))
        for esperado in ("el gancho tiene 30 palabras", "escena 1: 30 palabras", "sin imagen ni dato", "empiezan igual"):
            self.assertIn(esperado, avisos)
        self.assertEqual(vox.validar_guion(g), [])  # son avisos: no bloquean

    def test_cola_y_cierre_por_espacio(self):
        g = guion(); palabras, fin = alinear(g)
        v = vox.armar_video(g, palabras, fin, vox.perfiles()["castorena"])
        self.assertEqual(v["cierre"], "SU OPINIÓN")
        self.assertEqual(v["frames"], round((fin + vox.COLA) * vox.FPS))
        self.assertGreaterEqual(v["frames"] / vox.FPS - v["finVoz"], 1.2)  # hay tiempo para leer el cierre
        for p in vox.perfiles().values():
            self.assertTrue(0 < len(p["cierre"]) <= 16)


class ImagenAuditada(unittest.TestCase):
    def test_detecta_contenido_bajo_la_interfaz_de_tiktok(self):
        import shutil, subprocess
        if not shutil.which("ffmpeg"):
            self.skipTest("sin ffmpeg")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp); (d / "out").mkdir()
            base = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=0xF4ECD6:s=1080x1920:r=30:d=2",
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac"]
            centro = "drawbox=x=200:y=500:w=600:h=600:color=black:t=fill"
            datos = {"frames": 60, "perfil": {"colores": {"papel": "#F4ECD6"}}, "escenas": [{"id": "01", "desde": 0, "dur": 60}]}
            subprocess.run(base + ["-vf", centro, str(d / "out" / "final.mp4")], check=True)
            limpio = vox.auditar_video(d, datos)
            self.assertEqual(limpio["avisos"], [])
            self.assertEqual(limpio["formato"]["ancho"], 1080)
            subprocess.run(base + ["-vf", centro + ",drawbox=x=980:y=900:w=90:h=300:color=black:t=fill", str(d / "out" / "final.mp4")], check=True)
            self.assertIn("botones de la derecha", " | ".join(vox.auditar_video(d, datos)["avisos"]))
            subprocess.run(base + [str(d / "out" / "final.mp4")], check=True)
            self.assertIn("casi vacío", " | ".join(vox.auditar_video(d, datos)["avisos"]))


class Estructura(unittest.TestCase):
    def err(self, g):
        return " | ".join(vox.validar_guion(g))

    def test_cada_escena_dice_para_que_existe(self):
        g = guion(); g["escenas"][1].pop("funcion")
        self.assertIn("falta `funcion`", self.err(g))
        g = guion(); g["escenas"][0]["funcion"] = "dato"
        self.assertIn("primera escena debe ser el `gancho`", self.err(g))
        g = guion(); g["escenas"][-1]["funcion"] = "remate"
        self.assertIn("última escena debe ser el `cierre`", self.err(g))

    def test_la_opinion_de_emi_tiene_que_oirse(self):
        g = guion(); g["escenas"][2]["funcion"] = "prueba"
        self.assertIn("funcion `opinion`", self.err(g))

    def test_emi_elige_el_gancho(self):
        g = guion(); g["ganchos_propuestos"] = ["solo uno"]
        self.assertIn("ganchos_propuestos", self.err(g))
        g = guion(); g["gancho_elegido"] = 5
        self.assertIn("gancho_elegido", self.err(g))
        g = guion(); g["gancho_elegido"] = True
        self.assertIn("gancho_elegido", self.err(g))

    def test_una_cifra_sin_fuente_no_pasa(self):
        for frase in ("El 73 % lo ignora.", "Te cuesta $500 al mes.", "Son 3 millones de personas.", "Pasó en 2019."):
            g = guion(); g["escenas"][1]["narracion"] = frase
            self.assertIn("no muestra `fuente`", self.err(g), frase)
            g["escenas"][1]["fuente"] = "INEGI, 2025"
            self.assertEqual(vox.validar_guion(g), [], frase)
        g = guion(); g["escenas"][1]["narracion"] = "Son 3 pasos y 1 idea."   # contar no es un dato
        self.assertEqual(vox.validar_guion(g), [])
        g = guion(); g["escenas"][1]["narracion"] = "El 73 % lo ignora."; g["cifras_sin_fuente"] = "es una cifra de ejemplo que el video declara como hipotética"
        self.assertEqual(vox.validar_guion(g), [])


class Revision(unittest.TestCase):
    def test_tempo_ajustado_a_los_cortes(self):
        cortes = [3.1, 6.3, 9.8, 13.2]
        def error(bpm):
            n = 60 / bpm
            return sum(min(c % n, n - c % n) for c in cortes) / len(cortes)
        nuevo = vox.SON.ajustar_bpm(120, cortes)
        self.assertTrue(120 * 0.92 <= nuevo <= 120 * 1.08)
        self.assertLessEqual(error(nuevo), error(120))
        self.assertEqual(vox.SON.ajustar_bpm(120, []), 120.0)
        self.assertEqual(vox.SON.plan_musica("energia", 4, cortes), vox.SON.plan_musica("energia", 4, cortes))

    def test_no_se_cierra_sin_revisar_el_render_actual(self):
        import shutil, subprocess, json
        if not shutil.which("ffmpeg"):
            self.skipTest("sin ffmpeg")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp); (d / "out").mkdir()
            final = d / "out" / "final.mp4"
            hacer = lambda color: subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c={color}:s=270x480:r=30:d=4",
                                                  "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-pix_fmt", "yuv420p", str(final)], check=True)
            with self.assertRaises(vox.ErrorVox):
                vox.exigir_revision(d, final)                      # ni siquiera hay render
            hacer("red")
            with self.assertRaises(vox.ErrorVox):
                vox.exigir_revision(d, final)                      # render sin revisar
            f = vox.crear_revision(d, final, [1.5, 3.0])
            self.assertTrue((d / "out" / "hoja-transiciones.png").is_file() and (d / "out" / "hoja-telefono.png").is_file())
            with self.assertRaises(vox.ErrorVox):
                vox.exigir_revision(d, final)                      # nadie firmó la revisión
            r = json.loads(f.read_text()); r["revisado_por"] = "IA"; r["hallazgos"] = [{"segundo": 1.5, "problema": "texto encimado"}]
            f.write_text(json.dumps(r))
            with self.assertRaises(vox.ErrorVox):
                vox.exigir_revision(d, final)                      # hallazgo sin arreglo
            r["hallazgos"][0]["arreglo"] = "se bajó el recorte"; f.write_text(json.dumps(r))
            self.assertEqual(vox.exigir_revision(d, final)["revisado_por"], "IA")
            vox.crear_revision(d, final, [1.5, 3.0])           # repetir no borra lo anotado
            self.assertEqual(vox.exigir_revision(d, final)["revisado_por"], "IA")
            hacer("blue")
            with self.assertRaises(vox.ErrorVox) as cm:
                vox.exigir_revision(d, final)                      # se volvió a rendir: la revisión ya no vale
            self.assertIn("render anterior", str(cm.exception))
            m = json.loads(vox.escribir_manifiesto(d, final, {"motor": "x"}).read_text())
            self.assertEqual(len(m["sha256"]), 64)


class TresDe(unittest.TestCase):
    def err(self, g):
        return " | ".join(vox.validar_guion(g))

    def test_el_3d_exige_un_porque(self):
        g = guion(); g["escenas"][1]["objeto3d"] = {"tipo": "monedas", "valores": [4]}
        self.assertIn("objeto3d.porque", self.err(g))
        g["escenas"][1]["objeto3d"]["porque"] = "el dinero apilado se entiende mejor con volumen"
        self.assertEqual(vox.validar_guion(g), [])
        g["escenas"][1]["objeto3d"]["tipo"] = "dragon"
        self.assertIn("objeto3d.tipo", self.err(g))

    def test_barras_son_datos(self):
        g = guion(); g["escenas"][1]["objeto3d"] = {"tipo": "barras", "valores": [3], "porque": "comparar dos cantidades reales con volumen"}
        e = self.err(g)
        self.assertIn("al menos 2 valores", e); self.assertIn("necesita `fuente`", e)
        g["escenas"][1]["objeto3d"]["valores"] = [3, 8]; g["escenas"][1]["fuente"] = "INEGI, 2025"
        self.assertEqual(vox.validar_guion(g), [])
        g["escenas"][1]["objeto3d"]["valores"] = [3, -1]
        self.assertIn("no negativos", self.err(g))
        for malo in ([3, float("inf")], [0, 0]):
            g["escenas"][1]["objeto3d"]["valores"] = malo
            self.assertTrue(self.err(g), malo)
        g["escenas"][1]["objeto3d"]["valores"] = [3, 8]
        for malo in (7, -1, "1", 0.5, True):                       # resaltar: índice real de una barra
            g["escenas"][1]["objeto3d"]["resaltar"] = malo
            self.assertIn("objeto3d.resaltar", self.err(g), malo)
        g["escenas"][1]["objeto3d"]["resaltar"] = 0
        self.assertEqual(vox.validar_guion(g), [])

    def test_monedas_de_2_a_8(self):
        g = guion(); g["escenas"][1]["objeto3d"] = {"tipo": "monedas", "porque": "el dinero apilado se entiende mejor con volumen"}
        self.assertEqual(vox.validar_guion(g), [])                 # sin valores: tres por defecto
        for malo in ([0], [100], [2.5]):
            g["escenas"][1]["objeto3d"]["valores"] = malo
            self.assertIn("entero de 2 a 8", self.err(g), malo)
        g["escenas"][1]["objeto3d"].update(valores=[5], resaltar=1)
        self.assertIn("solo existe en barras", self.err(g))

    def test_un_solo_recurso_por_escena(self):
        g = guion(); g["escenas"][1].update(objeto3d={"tipo": "caja", "porque": "mostrar el paquete completo con volumen"}, dato="7")
        self.assertIn("ocupa el lugar del recorte", self.err(g))
        g = guion(); g["escenas"][1]["tratamiento"] = "semitono"
        self.assertIn("solo aplica a una escena con imagen_archivo", self.err(g))
        g = guion(); g["escenas"][1].update(tratamiento="neon", imagen_archivo="img/a.png")
        self.assertIn("no existe", self.err(g))

    def test_secuencia_completa_o_no_se_arma(self):
        g = guion(); g["escenas"][1]["secuencia"] = {"carpeta": "../fuera", "cuadros": 4}
        self.assertIn("secuencia necesita", self.err(g))
        g["escenas"][1]["secuencia"] = {"carpeta": "seq/x", "cuadros": 3}
        self.assertIn("secuencia.porque", self.err(g))
        g["escenas"][1]["secuencia"]["porque"] = "el objeto real se entiende al verlo por todos sus lados"
        self.assertEqual(vox.validar_guion(g), [])
        palabras, fin = alinear(g)
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "seq" / "x").mkdir(parents=True)
            for n in (0, 1):
                (Path(d) / "seq" / "x" / f"{n:04d}.png").write_bytes(b"x")
            with self.assertRaises(vox.ErrorVox) as cm:
                vox.armar_video(g, palabras, fin, vox.perfiles()["personal"], Path(d))
            self.assertIn("faltan 1", str(cm.exception))
            (Path(d) / "seq" / "x" / "0002.png").write_bytes(b"x")
            v = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"], Path(d))
            self.assertEqual(v["escenas"][1]["secuencia"], {"carpeta": "seq/x", "cuadros": 3})
            self.assertIsNone(v["escenas"][0]["secuencia"])

    PORQUE = "la diferencia entre cantidades se entiende con altura"

    def test_cada_objeto_en_su_momento(self):
        # El gancho necesita un sujeto con carácter; la opinión y el cierre son de Emi: ahí no va 3D.
        for tipo, lugar, vale in (("barras", 1, True), ("barras", 0, False), ("monedas", 2, False), ("caja", 1, False), ("globo", 1, True), ("globo", 3, False)):
            g = guion()
            g["escenas"][lugar].update(objeto3d={"tipo": tipo, "valores": [2, 6] if tipo == "barras" else [], "porque": self.PORQUE}, fuente="INEGI, 2025")
            e = self.err(g)
            self.assertEqual("no va en una escena" in e, not vale, (tipo, lugar, e))
        g = guion(); g["escenas"][2]["secuencia"] = {"carpeta": "seq/x", "cuadros": 3, "porque": self.PORQUE}
        self.assertIn("ese momento es de Emi", self.err(g))

    def test_un_solo_3d_por_video_salvo_que_emi_pida_mas(self):
        g = guion(); g["escenas"].insert(2, {"id": "09", "narracion": "Otra frase de prueba.", "keyword": "OTRA", "funcion": "prueba"})
        for i in (1, 2):
            g["escenas"][i].update(objeto3d={"tipo": "barras", "valores": [2, 6], "porque": self.PORQUE}, fuente="INEGI, 2025")
        self.assertIn("como mucho 1 por video", self.err(g))
        g["excepcion_3d"] = "sí"
        self.assertIn("excepcion_3d", self.err(g))                 # la excepción se justifica con el pedido de Emi
        g["excepcion_3d"] = "Emi, 12/11/2026: «en este quiero dos gráficas en 3D»"
        self.assertEqual(vox.validar_guion(g), [])
        g["escenas"][0].update(objeto3d={"tipo": "caja", "porque": self.PORQUE})   # con excepción también se levanta el lugar
        self.assertEqual(vox.validar_guion(g), [])

    def test_un_solo_tratamiento_por_video(self):
        g = guion()
        g["escenas"][1].update(imagen_archivo="img/a.png", tratamiento="semitono", foto_real=True)
        g["escenas"][2].update(imagen_archivo="img/b.png", tratamiento="duotono", foto_real=True)
        self.assertIn("un solo tratamiento", self.err(g))
        g["escenas"][2]["tratamiento"] = "semitono"
        self.assertEqual(vox.validar_guion(g), [])
        self.assertEqual([a for a in vox.avisos_guion(g) if "tratamiento" in a], [])
        g["escenas"][2]["foto_real"] = False
        self.assertIn("no es foto real", " | ".join(vox.avisos_guion(g)))

    def test_avisos_de_oficio_del_3d(self):
        g = guion(); g["escenas"][1].update(objeto3d={"tipo": "barras", "valores": [10, 11], "porque": self.PORQUE}, fuente="INEGI, 2025")
        a = " | ".join(vox.avisos_guion(g))
        self.assertIn("se parecen demasiado", a); self.assertIn("alternativa_plana", a)
        g["escenas"][1]["objeto3d"]["valores"] = [10, 30]; g["escenas"][1]["alternativa_plana"] = {"dato": "x3"}
        a = " | ".join(vox.avisos_guion(g))
        self.assertNotIn("se parecen", a); self.assertNotIn("alternativa_plana", a)
        self.assertEqual(vox.validar_guion(g), [])
        for malo in ({"dato": ""}, {"otra": "x"}, {"imagen_archivo": "../x.png"}, "x3"):
            g["escenas"][1]["alternativa_plana"] = malo
            self.assertIn("alternativa_plana", self.err(g), malo)
        g = guion(); g["escenas"][1]["alternativa_plana"] = {"dato": "7"}
        self.assertIn("solo tiene sentido", self.err(g))

    def test_comparar_con_y_sin(self):
        import json
        from PIL import Image
        g = guion()
        g["escenas"][1].update(objeto3d={"tipo": "barras", "valores": [2, 6.5], "porque": self.PORQUE}, fuente="INEGI, 2025")
        palabras, fin = alinear(g)
        vistos = []
        def falso(cmd, cwd=None, **kw):
            props = json.loads((Path(cwd) / next(c for c in cmd if c.startswith("--props=")).split("=", 1)[1]).read_text())
            vistos.append(props["escenas"][1])
            Image.new("RGB", (108, 192), (200, 0, 0) if props["escenas"][1].get("secuencia") else (0, 0, 200)).save(Path(cwd) / cmd[5])
        real_c, real_h = vox._correr, vox.hornear
        vox._correr, vox.hornear = falso, lambda *a, **k: 0
        try:
            with tempfile.TemporaryDirectory() as d:
                d = Path(d); (d / "src" / "data").mkdir(parents=True); (d / "out").mkdir(); (d / "public").mkdir()
                (d / "src" / "data" / "video.json").write_text(json.dumps(vox.armar_video(g, palabras, fin, vox.perfiles()["personal"], d / "public")))
                f = vox.comparar(d, "02")
                with Image.open(f) as im:
                    self.assertEqual(im.size, (1110, 1030))
                    self.assertEqual((im.getpixel((270, 500)), im.getpixel((840, 500))), ((200, 0, 0), (0, 0, 200)))   # A con, B sin
                self.assertEqual(sorted(x.name for x in (d / "out").iterdir()), ["comparacion-02.png"])
                with self.assertRaises(vox.ErrorVox):
                    vox.comparar(d, "01")                           # esa escena no lleva nada que comparar
        finally:
            vox._correr, vox.hornear = real_c, real_h
        con, sin = vistos
        self.assertTrue(con["secuencia"] and not con["dato"])
        self.assertEqual((sin["secuencia"], sin["dato"]), (None, "6.5"))   # sin alternativa escrita, las barras se vuelven su cifra

    def test_demasiado_3d_avisa(self):
        g = guion()
        for i in (1, 2):
            g["escenas"][i]["objeto3d"] = {"tipo": "caja", "porque": "x" * 20}
        self.assertIn("el 3D es un acento", " | ".join(vox.avisos_guion(g)))

    def test_blender_pide_razon_y_destino_dentro(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = ["blender", "--dir", tmp, "--perfil", "personal", "--tipo", "caja"]
            self.assertEqual(vox.main(base + ["--out", "public/img/a.png", "--porque", "porque sí"]), 2)
            self.assertEqual(vox.main(base + ["--out", "../a.png", "--porque", "x" * 25]), 2)
            self.assertEqual(vox.main(["blender", "--dir", tmp, "--perfil", "personal", "--tipo", "texto", "--out", "public/a.png", "--porque", "x" * 25]), 2)
            self.assertEqual(vox.main(["blender", "--dir", tmp, "--perfil", "personal", "--tipo", "modelo", "--modelo", "/no/hay.glb", "--out", "public/a.png", "--porque", "x" * 25]), 2)
            # el destino se valida antes de gastar minutos de render: dentro de public/, .png si es imagen, carpeta si gira
            llamado = []
            real = vox.rendir_con_blender
            vox.rendir_con_blender = lambda *a, **k: llamado.append(1)
            try:
                for malo in (["--out", "seq/y", "--giro", "4"], ["--out", "public/img/caja"], ["--out", "public/img/caja.jpg"], ["--out", "public/seq/y.png", "--giro", "4"]):
                    self.assertEqual(vox.main(base + malo + ["--porque", "x" * 25]), 2, malo)
            finally:
                vox.rendir_con_blender = real
            self.assertEqual(llamado, [])

    def test_blender_limpia_el_giro_anterior(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "public" / "seq" / "x"; destino.mkdir(parents=True)
            for n in range(6):                                     # restos de un giro más largo, con el objeto en otra esquina
                im = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); im.paste((0, 0, 255, 255), (150, 150, 190, 190)); im.save(destino / f"{n:04d}.png")
            def falso(espec, espera=1800):
                self.assertEqual(list(Path(espec["salida"]).glob("*.png")), [])   # llegó limpia
                for n in range(espec["giro"]):
                    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); im.paste((255, 0, 0, 255), (20, 20, 60, 60)); im.save(Path(espec["salida"]) / f"{n:04d}.png")
                return {"ok": True, "blender": "prueba", "cuadros": espec["giro"], "segundos": 0.0}
            real = vox.rendir_con_blender
            vox.rendir_con_blender = falso
            try:
                self.assertEqual(vox.main(["blender", "--dir", tmp, "--perfil", "personal", "--tipo", "caja", "--giro", "3", "--out", "public/seq/x", "--porque", "x" * 25]), 0)
            finally:
                vox.rendir_con_blender = real
            self.assertEqual(sorted(f.name for f in destino.glob("*.png")), ["0000.png", "0001.png", "0002.png"])
            with Image.open(destino / "0000.png") as im:
                self.assertEqual(im.size, (68, 68))                # recortado al objeto nuevo, sin el resto viejo


class Horno(unittest.TestCase):
    def test_recorte_comun_para_toda_la_secuencia(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            rutas = []
            for n, caja in enumerate([(100, 120, 160, 200), (140, 100, 220, 180)]):
                im = Image.new("RGBA", (400, 400), (0, 0, 0, 0)); im.paste((255, 0, 0, 255), caja)
                f = Path(d) / f"{n:04d}.png"; im.save(f); rutas.append(f)
            w, h = vox.recortar_al_contenido(rutas, margen=10)
            self.assertEqual((w, h), (140, 120))                 # unión de los dos contornos + margen
            for f in rutas:
                with Image.open(f) as im:
                    self.assertEqual(im.size, (140, 120))
            vacio = Path(d) / "v.png"; Image.new("RGBA", (50, 50), (0, 0, 0, 0)).save(vacio)
            with self.assertRaises(vox.ErrorVox):
                vox.recortar_al_contenido([vacio])

    def test_plan_del_horno(self):
        from PIL import Image
        g = guion()
        g["escenas"][1]["objeto3d"] = {"tipo": "monedas", "valores": [4], "porque": "el dinero apilado se entiende con volumen"}
        g["escenas"][2].update(imagen_archivo="img/f.png", tratamiento="duotono")
        palabras, fin = alinear(g)
        with tempfile.TemporaryDirectory() as d:
            pub = Path(d); (pub / "img").mkdir()
            Image.new("RGBA", (1800, 1200), (9, 9, 9, 255)).save(pub / "img" / "f.png")
            datos = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"], pub)
            listo, trabajos = vox.plan_horno(datos, pub)
            self.assertEqual([t["modo"] for t in trabajos], ["objeto", "foto"])
            e1, e2 = listo["escenas"][1], listo["escenas"][2]
            self.assertEqual(e1["secuencia"]["bucle"], False)
            self.assertEqual(e1["secuencia"]["cuadros"], datos["escenas"][1]["dur"] + 16)
            self.assertTrue(e2["imagen"].startswith("horno/03-duotono-") and e2["tratada"] is True)
            self.assertEqual(e1["secuencia"]["inicio"], 0)
            self.assertEqual((trabajos[1]["props"]["lado"], trabajos[1]["props"]["alto"]), (900, 600))
            self.assertTrue(all("objeto3d" not in e and "tratamiento" not in e for e in listo["escenas"]))
            self.assertEqual(datos["escenas"][1]["objeto3d"]["tipo"], "monedas")       # el original no se toca
            self.assertEqual(vox.plan_horno(datos, pub)[1][0]["destino"], trabajos[0]["destino"])  # misma firma: se reutiliza
            datos["escenas"][1]["objeto3d"]["valores"] = [6]
            self.assertNotEqual(vox.plan_horno(datos, pub)[1][0]["destino"], trabajos[0]["destino"])

    def test_la_firma_cambia_con_el_codigo_y_la_primera_escena_se_hornea_asentada(self):
        from PIL import Image
        g = guion()
        g["escenas"][0].update(imagen_archivo="", objeto3d={"tipo": "caja", "porque": "mostrar el paquete completo con volumen"})
        g["escenas"][2].update(imagen_archivo="img/f.png", tratamiento="semitono", foto_real=True)
        g["portada"] = {"imagen_archivo": "img/f.png"}
        palabras, fin = alinear(g)
        with tempfile.TemporaryDirectory() as d:
            pub = Path(d) / "public"; (pub / "img").mkdir(parents=True); (Path(d) / "src").mkdir()
            Image.new("RGBA", (300, 200), (9, 9, 9, 255)).save(pub / "img" / "f.png")
            (Path(d) / "src" / "Tres.tsx").write_text("v1")
            datos = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"], pub)
            listo, trabajos = vox.plan_horno(datos, pub)
            sec = listo["escenas"][0]["secuencia"]
            self.assertEqual(sec["inicio"], vox.ADELANTO_PRIMERA - 8)      # el compositor pide desde ese cuadro
            self.assertEqual(trabajos[0]["props"]["inicio"], sec["inicio"])
            self.assertTrue(listo["escenas"][2]["foto"])                    # la foto real tratada conserva su marco
            self.assertEqual(listo["portada"]["imagen"], listo["escenas"][2]["imagen"])  # la portada usa la tratada
            (Path(d) / "src" / "Tres.tsx").write_text("v2")
            self.assertNotEqual(vox.plan_horno(datos, pub)[1][0]["destino"], trabajos[0]["destino"])
            self.assertNotEqual(vox.plan_horno(datos, pub)[1][1]["destino"], trabajos[1]["destino"])

    def hornear_con(self, d, trabajos, cuadro):
        """Sustituye a Remotion: `cuadro(n)` devuelve la imagen del cuadro n, o None para no escribirlo."""
        real = vox._correr
        def falso(cmd, cwd=None, **kw):
            if "still" in cmd:
                im = cuadro(0)
                if im is not None:
                    im.save(Path(cwd) / "out" / "_horno.png")
            else:
                (Path(cwd) / "out" / "_horno").mkdir()
                for n in range(trabajos[0]["cuadros"]):
                    im = cuadro(n)
                    if im is not None:
                        im.save(Path(cwd) / "out" / "_horno" / f"element-{n:03d}.png")
        vox._correr = falso
        try:
            return vox.hornear(Path(d), trabajos, "")
        finally:
            vox._correr = real

    def test_un_horneado_fallido_no_queda_como_bueno(self):
        from PIL import Image
        vacio = lambda n: Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        def lleno(n):
            im = Image.new("RGBA", (100, 100), (0, 0, 0, 0)); im.paste((255, 0, 0, 255), (30, 30, 60, 60)); return im
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "public" / "horno" / "vieja-000").mkdir(parents=True)
            sec = [{"modo": "objeto", "destino": "horno/02-abc", "cuadros": 3, "props": {}}]
            for _ in (1, 2):                                       # la segunda corrida tampoco lo da por bueno
                with self.assertRaises(vox.ErrorVox):
                    self.hornear_con(d, sec, vacio)
                self.assertFalse((Path(d) / "public" / "horno" / "02-abc").exists())
            with self.assertRaises(vox.ErrorVox):                  # faltó un cuadro
                self.hornear_con(d, sec, lambda n: lleno(n) if n < 2 else None)
            self.assertEqual(self.hornear_con(d, sec, lleno), 1)
            destino = Path(d) / "public" / "horno" / "02-abc"
            self.assertEqual(sorted(f.name for f in destino.iterdir()), [".listo", "0000.png", "0001.png", "0002.png"])
            self.assertFalse((Path(d) / "public" / "horno" / "vieja-000").exists())   # lo que ya nadie pide se borra
            self.assertEqual(self.hornear_con(d, sec, vacio), 0)   # ya horneado: no se repite
            foto = [{"modo": "foto", "destino": "horno/03-semitono-x.png", "cuadros": 1, "props": {"src": "img/f.png"}}]
            with self.assertRaises(vox.ErrorVox):                  # textura que no cargó: PNG transparente
                self.hornear_con(d, foto, vacio)
            self.assertFalse((Path(d) / "public" / "horno" / "03-semitono-x.png").exists())
            self.assertEqual(self.hornear_con(d, foto, lleno), 1)
            self.assertFalse(destino.exists())                     # el plan cambió: la secuencia anterior se limpia


class Comfy(unittest.TestCase):
    FLUJO = {"3": {"class_type": "KSampler", "inputs": {}}, "9": {"class_type": "SaveImage", "inputs": {}}}

    def con_url(self, valor):
        previo = os.environ.get("COMFY_URL")
        if valor is None:
            os.environ.pop("COMFY_URL", None)
        else:
            os.environ["COMFY_URL"] = valor
        return previo

    def test_sin_servidor_no_se_simula(self):
        previo = self.con_url(None)
        try:
            with self.assertRaises(vox.ErrorVox) as cm:
                vox.comfy_generar(self.FLUJO, Path("/tmp/x.png"))
            self.assertIn("COMFY_URL", str(cm.exception))
        finally:
            self.con_url(previo)

    def test_envia_espera_y_baja_la_imagen(self):
        import json
        from PIL import Image
        import io
        mem = io.BytesIO(); Image.new("RGB", (8, 8), (200, 30, 30)).save(mem, "PNG"); self.png = mem.getvalue()
        previo = self.con_url("https://comfy.ejemplo")
        real = vox._pedir
        vistas = []
        def falso(url, **kw):
            vistas.append((url, kw.get("metodo", "GET")))
            if url.endswith("/prompt"):
                self.assertEqual(kw["cuerpo"], {"prompt": self.FLUJO})
                return json.dumps({"prompt_id": "abc"}).encode()
            if "/history/abc" in url:
                return json.dumps({"abc": {"status": {"status_str": "success"}, "outputs": {"9": {"images": [{"filename": "a b.png", "subfolder": "", "type": "output"}]}}}}).encode()
            if "/view?" in url:
                self.assertIn("filename=a+b.png", url)
                return self.png
            raise AssertionError(url)
        vox._pedir = falso
        try:
            with tempfile.TemporaryDirectory() as d:
                info = vox.comfy_generar(self.FLUJO, Path(d) / "img" / "c.png")
                self.assertEqual((Path(d) / "img" / "c.png").read_bytes(), self.png)
                self.assertEqual(info["prompt_id"], "abc")
                with self.assertRaises(vox.ErrorVox):
                    vox.comfy_generar({"nodos": []}, Path(d) / "x.png")   # no es formato API
                with self.assertRaises(vox.ErrorVox):
                    vox.comfy_generar({"3": {"class_type": "KSampler", "inputs": {}}}, Path(d) / "x.png")   # no guarda imagen
                self.png = b"<html>error</html>"
                with self.assertRaises(vox.ErrorVox):
                    vox.comfy_generar(self.FLUJO, Path(d) / "img" / "malo.png")
                self.assertFalse((Path(d) / "img" / "malo.png").exists())
        finally:
            vox._pedir = real
            self.con_url(previo)
        self.assertEqual([m for _, m in vistas], ["POST", "GET", "GET"] * 2)   # la buena y la que devolvió HTML

    def test_direccion_del_servidor(self):
        for url, vale in (("https://comfy.ejemplo", True), ("http://127.0.0.1:8188", True), ("http://localhost:8188", True),
                          ("http://192.168.1.20:8188", False), ("http://comfy.ejemplo", False), ("ftp://x", False)):
            previo = self.con_url(url)
            try:
                if vale:
                    self.assertEqual(vox.comfy_base(), url)
                else:
                    with self.assertRaises(vox.ErrorVox) as cm:
                        vox.comfy_base()
                    self.assertIn("COMFY_URL", str(cm.exception))
            finally:
                self.con_url(previo)
        with self.assertRaises(vox.ErrorVox):                      # http local solo para ComfyUI, no para otros proveedores
            vox._pedir("http://127.0.0.1:1/x")

    def test_en_seco_valida_el_flujo(self):
        previo = self.con_url("https://comfy.ejemplo")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                malo = Path(tmp) / "interfaz.json"; malo.write_text('{"nodes": [], "links": []}')
                self.assertEqual(vox.main(["comfy", "--dir", tmp, "--flujo", str(malo), "--out", "public/img/a.png", "--porque", "x" * 25]), 2)
        finally:
            self.con_url(previo)

    def test_error_del_flujo(self):
        import json
        previo = self.con_url("https://comfy.ejemplo")
        real = vox._pedir
        vox._pedir = lambda url, **kw: json.dumps({"prompt_id": "z"} if url.endswith("/prompt") else {"z": {"status": {"status_str": "error"}, "outputs": {}}}).encode()
        try:
            with self.assertRaises(vox.ErrorVox):
                vox.comfy_generar(self.FLUJO, Path("/tmp/no.png"))
        finally:
            vox._pedir = real
            self.con_url(previo)


class MusicaExterna(unittest.TestCase):
    def tono(self, ruta, segundos, silencio=0.0):
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"sine=frequency=330:duration={segundos}", "-af", f"adelay={int(silencio * 1000)}:all=1", str(ruta)], check=True)

    def test_guion_exige_origen_y_ruta_segura(self):
        g = guion(); g["musica"]["archivo"] = "originales/musica/p.wav"
        self.assertIn("musica.origen", " | ".join(vox.validar_guion(g)))
        g["musica"]["origen"] = "Flow Music, cuenta de Emi, 11/11/2026"
        self.assertEqual(vox.validar_guion(g), [])
        for malo in ("../p.wav", "originales/p.txt", 7):
            g["musica"]["archivo"] = malo
            self.assertIn("musica.archivo", " | ".join(vox.validar_guion(g)), malo)

    def test_recorta_a_la_medida_y_salta_el_silencio(self):
        with tempfile.TemporaryDirectory() as d:
            origen, destino = Path(d) / "o.wav", Path(d) / "m.wav"
            self.tono(origen, 6, silencio=0.8)
            inicio = vox.recortar_pista(origen, destino, 4.0)
            self.assertAlmostEqual(inicio, 0.8, delta=0.08)
            self.assertAlmostEqual(vox.duracion_audio(destino), 4.0, delta=0.05)
            with self.assertRaises(vox.ErrorVox):                  # más corta que el video: no se estira ni se repite
                vox.recortar_pista(origen, destino, 30.0)


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
