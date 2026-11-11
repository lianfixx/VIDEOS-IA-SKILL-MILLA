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
        g["escenas"][1]["narracion"] = "El 73 por ciento lo ignora."
        avisos = " | ".join(vox.avisos_guion(g))
        for esperado in ("el gancho tiene 30 palabras", "escena 1: 30 palabras", "sin imagen ni dato", "ninguna escena muestra `fuente`", "empiezan igual"):
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
        g["cierre"] = "Opina"  # un video puede cambiar el llamado de su espacio
        self.assertEqual(vox.armar_video(g, palabras, fin, vox.perfiles()["castorena"])["cierre"], "OPINA")
        g["cierre"] = "x" * 17
        self.assertIn("cierre", " | ".join(vox.validar_guion(g)))

    def test_plantilla_no_recorta_acentos_ni_desborda(self):
        tsx = (vox.SKILL / "plantilla" / "src" / "Vox.tsx").read_text(encoding="utf-8") if hasattr(vox, "SKILL") else \
            (Path(vox.__file__).resolve().parents[1] / "plantilla" / "src" / "Vox.tsx").read_text(encoding="utf-8")
        self.assertNotIn("clipPath: `inset(0 ${(1 - k) * 100}% 0 0)`", tsx)  # `mordidas` recortaba Á, Í, Ó de la primera línea
        self.assertIn("anchoLinea(l, fuente, m.ancho)", tsx)  # el titular se mide con el ancho real de las letras


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

    def test_velocidad_de_voz(self):
        self.assertEqual(vox.velocidad_voz({}, {}), 1.0)
        self.assertEqual(vox.velocidad_voz({}, {"velocidad": 1.1}), 1.1)
        self.assertEqual(vox.velocidad_voz({"voz_velocidad": 1.15}, {"velocidad": 1.1}), 1.15)
        for mala in (1.5, 0.5, "rapido", True):
            with self.assertRaises(vox.ErrorVox):
                vox.velocidad_voz({"voz_velocidad": mala}, {})
        self.assertNotIn("speed", vox.ajustes_voz())
        self.assertEqual(vox.ajustes_voz(1.15)["speed"], 1.15)

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
