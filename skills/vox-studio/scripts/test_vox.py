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
        g["perfil"] = "milla"; g["escenas"][2]["narracion"] = "Fracasó y nadie lo vio."
        pr = vox.SON.proponer(g)
        self.assertNotIn("trombon", [x["sonido"] for x in pr["escenas"]])
        self.assertTrue(all(not x["remate"] for x in pr["escenas"]))
        g["perfil"] = "castorena"  # Emi, 11/11/2026: Castorena va en corte suelto, con humor sonoro
        self.assertIn("trombon", [x["sonido"] for x in vox.SON.proponer(g)["escenas"]])

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
        self.assertEqual(v["cierre"], "OPINA")
        self.assertEqual(v["frames"], round((fin + vox.COLA) * vox.FPS))
        self.assertGreaterEqual(v["frames"] / vox.FPS - v["finVoz"], 1.2)  # hay tiempo para leer el cierre
        for p in vox.perfiles().values():
            self.assertTrue(0 < len(p["cierre"]) <= 16)
        g["cierre"] = "Su opinión"  # un video puede cambiar el llamado de su espacio
        self.assertEqual(vox.armar_video(g, palabras, fin, vox.perfiles()["castorena"])["cierre"], "SU OPINIÓN")
        g["cierre"] = "x" * 17
        self.assertIn("cierre", " | ".join(vox.validar_guion(g)))

    def test_plantilla_no_recorta_acentos_ni_desborda(self):
        tsx = (vox.SKILL / "plantilla" / "src" / "Vox.tsx").read_text(encoding="utf-8") if hasattr(vox, "SKILL") else \
            (Path(vox.__file__).resolve().parents[1] / "plantilla" / "src" / "Vox.tsx").read_text(encoding="utf-8")
        self.assertNotIn("clipPath: `inset(0 ${(1 - k) * 100}% 0 0)`", tsx)  # `mordidas` recortaba Á, Í, Ó de la primera línea
        self.assertIn("anchoLinea(l, fuente, m.ancho)", tsx)  # el titular se mide con el ancho real de las letras
        self.assertIn("tildeAlta(p, fuente)", tsx)  # el resaltador sube para cubrir la tilde de la mayúscula
        self.assertIn("kicker && tildeAlta(", tsx)  # la etiqueta no tapa la tilde de la primera línea
        for pieza in ("const Planos", "const CitaDoc", "const Lista", "const Calendario", "const DatoGrande", "const Duo",
                      "const Flujo", "const Barras", "const LineaTiempo", "const Etiquetas", "const Apunte"):
            self.assertIn(pieza, tsx)  # cada tipo de plano del guion tiene su componente
        # Un trazo con punta redonda deja un punto visible aunque su avance sea cero: solo se dibuja cuando ya empezó.
        import re as _re
        for m in _re.finditer(r"<path[^>]*strokeLinecap=\"round\"[^>]*strokeDashoffset=\{1 - (\w+)\}[^>]*/>", tsx):
            antes = tsx[max(0, m.start() - 480):m.start()]
            self.assertRegex(antes, rf"{m.group(1)} > 0", m.group(0)[:60])
        for tipo in vox.PLANOS:
            self.assertIn(f"p.tipo === '{tipo}'", tsx)  # ningún tipo validado se queda sin dibujar


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

    def test_planos_entran_con_su_palabra(self):
        g = guion()
        e = g["escenas"][1]
        e["narracion"] = "Hacienda decide dónde pagas con tarjeta, transferencia o QR."
        e["planos"] = [
            {"tipo": "cita", "texto": "podrá ser la única forma de pago", "resaltar": "única forma", "origen": "DOF · Art. 13"},
            {"en": "tarjeta", "tipo": "lista", "items": [{"texto": "Tarjeta", "marca": "si", "en": "tarjeta"}, {"texto": "QR", "marca": "si", "en": "QR"}, {"texto": "Efectivo", "marca": "no"}]},
        ]
        self.assertEqual(vox.validar_guion(g), [])
        palabras, fin = alinear(g, paso=0.4)
        v = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])
        esc = v["escenas"][1]
        cita, lista = esc["planos"]
        self.assertEqual(cita["desde"], 0)
        k = [w["t"] for w in palabras].index("tarjeta,")
        self.assertEqual(lista["desde"], round(palabras[k]["a"] * vox.FPS) - esc["desde"] - 4)  # tiempo real de la palabra
        self.assertEqual(cita["dur"], lista["desde"])
        self.assertEqual(lista["desde"] + lista["dur"], esc["dur"])
        tiempos = [it["desde"] for it in lista["items"]]
        self.assertEqual(tiempos, sorted(tiempos))
        self.assertEqual([it["texto"] for it in lista["items"]], ["TARJETA", "QR", "EFECTIVO"])

    def test_planos_mal_escritos_se_rechazan(self):
        def errores(planos, **extra):
            g = guion(); g["escenas"][1].update(narracion="Uno dos tres cuatro cinco seis.", planos=planos, **extra)
            return " | ".join(vox.validar_guion(g))
        self.assertIn("tipo", errores([{"tipo": "video"}]))
        self.assertIn("no lleva `en`", errores([{"tipo": "dato", "dato": "1", "en": "uno"}]))
        self.assertIn("palabra de la narración", errores([{"tipo": "dato", "dato": "1"}, {"tipo": "dato", "dato": "2", "en": "nueve"}]))
        self.assertIn("posterior", errores([{"tipo": "dato", "dato": "1"}, {"tipo": "dato", "dato": "2", "en": "cinco"}, {"tipo": "dato", "dato": "3", "en": "dos"}]))
        self.assertIn("fragmento literal", errores([{"tipo": "cita", "texto": "texto copiado de la fuente", "resaltar": "otra cosa", "origen": "DOF"}]))
        self.assertIn("origen", errores([{"tipo": "cita", "texto": "texto copiado de la fuente"}]))
        self.assertIn("2 a 4 items", errores([{"tipo": "lista", "items": [{"texto": "a"}]}]))
        self.assertIn("dias", errores([{"tipo": "calendario", "dias": 99}]))
        self.assertIn("dos imágenes", errores([{"tipo": "duo", "imagenes": ["img/a.png"]}]))
        self.assertIn("remate_en", errores([{"tipo": "dato", "dato": "1"}], remate="ZAS", sonido="boom", remate_en="nueve"))
        self.assertEqual(vox.imagenes_de({"imagen_archivo": "img/a.png", "planos": [{"tipo": "imagen", "imagen_archivo": "img/a.png"}, {"tipo": "duo", "imagenes": ["img/b.png", "img/c.png"]}]}),
                         ["img/a.png", "img/b.png", "img/c.png"])

    def test_motion_con_codigo_y_explicacion_a_la_par(self):
        g = guion(); e = g["escenas"][1]
        e["narracion"] = "La ley manda, Hacienda decide y tú pagas veinte pesos por cada copia simple."
        e["planos"] = [
            {"tipo": "flujo", "pasos": [{"texto": "La ley"}, {"texto": "Hacienda", "en": "Hacienda", "nota": "decide después"}, {"texto": "Tú", "en": "tú"}]},
            {"en": "veinte", "tipo": "barras", "origen": "Fuente de prueba", "barras": [{"etiqueta": "Copia", "valor": 20, "texto": "$20"}, {"etiqueta": "Costo real", "valor": 2}],
             "apunte": {"texto": "diez veces más", "en": "copia"}},
        ]
        self.assertEqual(vox.validar_guion(g), [])
        palabras, fin = alinear(g, paso=0.4)
        esc = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])["escenas"][1]
        flujo, barras = esc["planos"]
        self.assertEqual([x["texto"] for x in flujo["pasos"]], ["LA LEY", "HACIENDA", "TÚ"])
        tiempos = [x["desde"] for x in flujo["pasos"]]
        self.assertEqual(tiempos, sorted(tiempos))
        k = [w["t"] for w in palabras].index("Hacienda")
        self.assertEqual(flujo["pasos"][1]["desde"], round(palabras[k]["a"] * vox.FPS) - esc["desde"] - 4)
        self.assertGreater(barras["apunte"]["desde"], barras["desde"])
        self.assertEqual(barras["origen"], "Fuente de prueba")
        def errores(plano):
            g2 = guion(); g2["escenas"][1].update(narracion="Uno dos tres cuatro cinco seis.", planos=[plano])
            return " | ".join(vox.validar_guion(g2))
        self.assertIn("origen", errores({"tipo": "barras", "barras": [{"etiqueta": "a", "valor": 1}, {"etiqueta": "b", "valor": 2}]}))
        self.assertIn("valor", errores({"tipo": "barras", "origen": "x y z", "barras": [{"etiqueta": "a", "valor": 0}, {"etiqueta": "b", "valor": 2}]}))
        self.assertIn("de 2 a 4", errores({"tipo": "flujo", "pasos": [{"texto": "solo"}]}))
        self.assertIn("fecha", errores({"tipo": "linea", "hitos": [{"texto": "a"}, {"texto": "b"}]}))
        self.assertIn("solo va en planos de imagen", errores({"tipo": "dato", "dato": "1", "etiquetas": [{"texto": "a", "x": 0.5, "y": 0.5}]}))
        self.assertIn("entre 0 y 1", errores({"tipo": "imagen", "imagen_archivo": "img/a.png", "etiquetas": [{"texto": "a", "x": 2, "y": 0.5}]}))
        self.assertIn("apunte", errores({"tipo": "dato", "dato": "1", "apunte": {"texto": "x" * 60}}))

    def test_miniatura_de_commons(self):
        u = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Edificio_%28M%C3%A9xico%29.jpg"
        self.assertEqual(vox.miniatura_commons(u), "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Edificio_%28M%C3%A9xico%29.jpg/960px-Edificio_%28M%C3%A9xico%29.jpg")
        self.assertTrue(vox.miniatura_commons(u.replace(".jpg", ".svg")).endswith(".svg.png"))
        self.assertEqual(vox.miniatura_commons("https://ejemplo.org/foto.jpg"), "")
        self.assertEqual(vox.miniatura_commons(u + "?utm_source=commons"), vox.miniatura_commons(u))  # Apify añade parámetros

    def test_marcas_de_voz(self):
        s = {"narracion": "Sí, cheque. [pausa] En pleno [ríe] dos mil veintiséis. [pausa larga]"}
        self.assertEqual(vox.narracion_limpia(s), "Sí, cheque. En pleno dos mil veintiséis.")
        self.assertEqual(vox.texto_para_voz(s, "eleven_multilingual_v2"), 'Sí, cheque. <break time="0.5s" /> En pleno dos mil veintiséis. <break time="1.0s" />')
        self.assertEqual(vox.texto_para_voz(s, "eleven_v3"), "Sí, cheque. [pause] En pleno [laughs] dos mil veintiséis. [long pause]")
        al = [{"t": x, "a": 0.0, "b": 0.1} for x in ['Sí,', 'cheque.', '<break', 'time="0.5s"', '/>', 'En', '[laughs]', 'pleno', '[long', 'pause]', 'ya.']]
        self.assertEqual([w["t"] for w in vox.sin_etiquetas(al)], ["Sí,", "cheque.", "En", "pleno", "ya."])
        g = guion(); g["escenas"][1]["narracion"] += " [grita]"
        self.assertIn("marcas de voz desconocidas", " | ".join(vox.validar_guion(g)))
        g = guion(); g["escenas"][1]["narracion"] = "Y esto [ríe] da risa. [pausa]"
        self.assertEqual(vox.validar_guion(g), [])
        self.assertIn("modelo expresivo", " | ".join(vox.avisos_guion(g)))  # la voz clásica no ríe: se avisa
        palabras, fin = alinear(g)
        self.assertEqual(len(palabras), len(vox.texto_completo(g).split()))  # las marcas no cuentan como palabras
        vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])

    def test_cambio_de_tema_y_segunda_voz(self):
        perfil = dict(vox.perfiles()["castorena"])
        g = guion(); g["perfil"] = "castorena"
        uno = vox.plan_de_voz(g, perfil)
        self.assertEqual(len(uno), 1)
        self.assertEqual(vox.firma_de_voz(g, uno), vox.huella(vox.texto_completo(g), perfil["voz"]["voice_id"], perfil["voz"]["modelo"],
                                                             *([f"vel={uno[0]['velocidad']}"] if uno[0]["velocidad"] != 1.0 else [])))  # huella de siempre
        g["escenas"][2]["cambio_tema"] = True
        tramos = vox.plan_de_voz(g, perfil)
        self.assertEqual([t["cambio"] for t in tramos][:3], [False, True, False] if len(g["escenas"]) > 3 else [False, True])
        lento = tramos[1]
        self.assertAlmostEqual(lento["velocidad"], round(uno[0]["velocidad"] * vox.CAMBIO_TEMA["velocidad"], 3))
        self.assertEqual(lento["silencio"], vox.CAMBIO_TEMA["silencio"])
        self.assertEqual(sum(t["palabras"] for t in tramos), len(vox.texto_completo(g).split()))
        self.assertNotEqual(vox.firma_de_voz(g, tramos), vox.firma_de_voz(g, uno))
        g["escenas"][0]["cambio_tema"] = True
        self.assertIn("cambio_tema", " | ".join(vox.validar_guion(g)))
        g = guion(); g["perfil"] = "castorena"; g["escenas"][1]["voz"] = "comentario"
        self.assertEqual(vox.validar_guion(g), [])
        tramos = vox.plan_de_voz(g, perfil)
        self.assertEqual([t["comentario"] for t in tramos][:2], [False, True])
        self.assertEqual(tramos[1]["voz"]["voice_id"], perfil["voz_comentario"]["voice_id"])
        self.assertNotEqual(tramos[1]["voz"]["voice_id"], perfil["voz"]["voice_id"])
        self.assertEqual(tramos[1]["silencio"], vox.SILENCIO_ENTRE_VOCES)
        sin = {k: v for k, v in perfil.items() if k != "voz_comentario"}
        with self.assertRaises(vox.ErrorVox):
            vox.plan_de_voz(g, sin)
        palabras, fin = alinear(g)
        palabras[len(g["escenas"][0]["narracion"].split())]["c"] = True
        v = vox.armar_video(g, palabras, fin, perfil)
        self.assertTrue(v["escenas"][1]["comentario"])
        self.assertTrue(any(w.get("c") for w in v["palabras"]))
        self.assertEqual(v["etiquetaComentario"], "OPINIÓN")
        for nombre, pf in vox.perfiles().items():
            self.assertNotEqual(pf["voz_comentario"]["voice_id"], pf["voz"]["voice_id"], nombre)  # la que opina no es la que informa

    def test_estilo_pizarra(self):
        g = guion(); g["estilo"] = "pizarra"
        self.assertEqual(vox.validar_guion(g), [])
        self.assertIn("estilo pizarra sin `planos`", " | ".join(vox.avisos_guion(g)))
        g["escenas"][1].update(narracion="Uno dos tres cuatro cinco seis.", planos=[{"tipo": "imagen", "imagen_archivo": "img/a.png"}])
        self.assertIn("casi todo se dibuja", " | ".join(vox.avisos_guion(g)))
        g["escenas"][1]["planos"] = [{"tipo": "dato", "dato": "1"}, {"tipo": "flujo", "en": "tres", "pasos": [{"texto": "a"}, {"texto": "b"}]}]
        self.assertNotIn("pizarra", " | ".join(vox.avisos_guion(g)))
        palabras, fin = alinear(g)
        for nombre, pf in vox.perfiles().items():  # cualquier espacio puede hacer un video de pizarra con su marca
            v = vox.armar_video({**g, "perfil": nombre}, palabras, fin, pf)
            self.assertTrue(v["perfil"]["cuadricula"])
            self.assertEqual(v["perfil"]["colores"]["papel"], vox.PAPEL_PIZARRA)
            self.assertEqual(v["perfil"]["colores"]["acento"], pf["colores"]["acento"])
        g["estilo"] = "acuarela"
        self.assertIn("estilo", " | ".join(vox.validar_guion(g)))

    def test_hallazgos_de_la_auditoria_del_11_de_noviembre(self):
        def errores(narracion, planos=None, **extra):
            g = guion(); g["escenas"][1].update(narracion=narracion, **extra)
            if planos is not None:
                g["escenas"][1]["planos"] = planos
            return " | ".join(vox.validar_guion(g))
        # Marcas pegadas a un signo o a una palabra, y corchetes que no son marca: se rechazan antes de pagar.
        for mala in ("Espera [pausa], ya llegó.", "Eso dijo. [pausa]Y se fue.", "Mira[pausa] esto ahora.", "¡[ríe] Qué bien salió!"):
            self.assertIn("separada por espacios", errores(mala), mala)
        self.assertIn("corchetes", errores("Cita [sic y sigue hablando sin cerrar nunca."))
        self.assertIn("corchetes", errores("Esto <break> no va."))
        self.assertEqual(errores("Eso dijo. [pausa] Y se fue."), "")
        # Rutas e imágenes solo en planos de imagen; nada sale de public/.
        self.assertIn("no lleva imágenes", errores("Uno dos tres.", [{"tipo": "dato", "dato": "5", "imagen_archivo": "../../secreto.txt"}]))
        self.assertIn("no lleva imágenes", errores("Uno dos tres.", [{"tipo": "dato", "dato": "5", "imagenes": 7}]))
        self.assertEqual(vox.imagenes_de({"planos": [{"tipo": "dato", "imagen_archivo": "../x.txt"}, {"tipo": "imagen", "imagen_archivo": "../y.png"}, {"tipo": "duo", "imagenes": 7}]}), [])
        self.assertIn("debe ser texto", errores("Uno dos tres.", [{"tipo": "dato", "dato": "5", "etiqueta": None}]))
        # Foto real en un plano: la biblioteca conserva que es foto y su crédito.
        f = vox.fichas_de_imagenes({"planos": [{"tipo": "imagen", "imagen_archivo": "img/scjn.jpg", "foto_real": True, "credito": "Foto: Autor · CC BY-SA 4.0"}]})
        self.assertEqual(f["img/scjn.jpg"], {"foto_real": True, "credito": "Foto: Autor · CC BY-SA 4.0"})
        # Una pieza anclada después del plano siguiente no se vería: se rechaza.
        n = "Primero uno y luego dos y al final tres."
        mal = [{"tipo": "lista", "items": [{"texto": "Uno", "en": "uno"}, {"texto": "Tres", "en": "tres"}]}, {"tipo": "dato", "dato": "2", "en": "dos"}]
        self.assertIn("cuando ya entró el plano 2", errores(n, mal))
        # Anclas repetidas: cada pieza toma la aparición siguiente, no la misma palabra.
        g = guion(); e = g["escenas"][1]
        e["narracion"] = "Primero pagas la renta completa y al final pagas la multa entera con recargos."
        e["planos"] = [{"tipo": "dato", "dato": "1"}, {"en": "Primero", "tipo": "lista", "items": [{"texto": "Renta", "en": "pagas"}, {"texto": "Multa", "en": "pagas"}]}]
        self.assertEqual(vox.validar_guion(g), [])
        palabras, fin = alinear(g, paso=0.4)
        esc = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])["escenas"][1]
        dichas = [round(w["a"] * vox.FPS) - esc["desde"] for w in palabras if w["t"] == "pagas"]
        renta, multa = [it["desde"] for it in esc["planos"][1]["items"]]
        self.assertEqual(multa, dichas[1] - 4)  # la segunda pieza va con el segundo «pagas», no con el primero
        self.assertLess(renta, dichas[1] - 20)
        # Anclas con comillas, paréntesis o porcentaje.
        self.assertEqual(vox.buscar_ancla(["«gratis»,", "(INEGI)", "días…", "12%"], "INEGI"), 1)
        self.assertEqual(vox.buscar_ancla(["«gratis»,", "(INEGI)", "días…", "12%"], "12"), 3)
        # Piezas a ritmo fijo y remate: siempre dentro de su plano, con tiempo de verse.
        g = guion(); e = g["escenas"][1]
        e["narracion"] = "Uno dos tres cuatro cinco seis siete ocho cheque."
        e.update(remate="ZAS", sonido="boom", remate_en="cheque",
                 planos=[{"tipo": "dato", "dato": "1"}, {"en": "seis", "tipo": "linea", "hitos": [{"fecha": str(2020 + k), "texto": "hito"} for k in range(4)]}])
        self.assertEqual(vox.validar_guion(g), [])
        palabras, fin = alinear(g, paso=0.3)
        esc = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])["escenas"][1]
        linea = esc["planos"][1]
        self.assertTrue(all(linea["desde"] <= h["desde"] <= linea["desde"] + linea["dur"] - 12 for h in linea["hitos"]), linea)
        self.assertEqual([h["desde"] for h in linea["hitos"]], sorted(h["desde"] for h in linea["hitos"]))
        self.assertLessEqual(esc["remateEn"], esc["dur"] - 30)
        # Cita: el resaltado se normaliza igual que el texto.
        g = guion(); g["escenas"][1].update(narracion="Uno dos tres cuatro cinco seis.", planos=[{"tipo": "cita", "texto": "El patrón  deberá pagar\nel salario.", "resaltar": "patrón  deberá", "origen": "LFT"}])
        self.assertEqual(vox.validar_guion(g), [])
        palabras, fin = alinear(g)
        cita = vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])["escenas"][1]["planos"][0]
        self.assertIn(cita["resaltar"], cita["texto"])
        # Portada: si la escena no trae imagen propia, se toma la primera de sus planos.
        g = guion()
        for x in g["escenas"]:
            x.pop("imagen_archivo", None)
        g["escenas"][0]["planos"] = [{"tipo": "imagen", "imagen_archivo": "img/p.png"}]
        palabras, fin = alinear(g)
        self.assertEqual(vox.armar_video(g, palabras, fin, vox.perfiles()["personal"])["portada"]["imagen"], "img/p.png")
        # Velocidad con más de tres decimales: la huella sigue siendo la de siempre.
        g = guion(); g["voz_velocidad"] = 1.0625
        pf = vox.perfiles()["personal"]
        self.assertEqual(vox.firma_de_voz(g, vox.plan_de_voz(g, pf)), vox.huella(vox.texto_completo(g), pf["voz"]["voice_id"], pf["voz"]["modelo"], "vel=1.0625"))

    def test_tramos_pagados_no_se_vuelven_a_cobrar(self):
        g = guion(); g["perfil"] = "castorena"; g["escenas"][2]["cambio_tema"] = True
        perfil = vox.perfiles()["castorena"]
        llamadas = []
        real = vox.narrar
        def falso(texto, voz, velocidad=1.0, previo="", siguiente=""):
            llamadas.append(texto)
            if len(llamadas) == 2 and not getattr(falso, "sano", False):
                raise vox.ErrorVox("fallo simulado del proveedor")
            ws = [{"t": w, "a": i * 0.3, "b": i * 0.3 + 0.2} for i, w in enumerate(texto.split())]
            return (Path(__file__).parent / "__silencio.mp3").read_bytes(), ws
        d = Path(tempfile.mkdtemp())
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "1", str(Path(__file__).parent / "__silencio.mp3")], check=True)
        antes = set(Path(tempfile.gettempdir()).glob("vox-voz-*"))
        try:
            vox.narrar = falso
            with self.assertRaises(vox.ErrorVox):
                vox.narrar_guion(g, perfil, d / "voz.mp3", d / "tramos")
            self.assertEqual(set(Path(tempfile.gettempdir()).glob("vox-voz-*")), antes)  # sin carpetas temporales huérfanas
            self.assertEqual(len(list((d / "tramos").glob("*.mp3"))), 1)  # el primer tramo quedó pagado y guardado
            falso.sano = True
            palabras = vox.narrar_guion(g, perfil, d / "voz.mp3", d / "tramos")
            self.assertEqual(len(palabras), len(vox.texto_completo(g).split()))
            self.assertEqual(llamadas.count(llamadas[0]), 1)  # el tramo 1 no se volvió a pedir
        finally:
            vox.narrar = real
            (Path(__file__).parent / "__silencio.mp3").unlink(missing_ok=True)

    def test_bucle_abierto(self):
        g = guion()
        self.assertIn("falta `bucle`", " | ".join(vox.avisos_guion(g)))
        g["bucle"] = {"pregunta": "¿Quién decide los sectores?", "cierra": g["escenas"][1]["id"]}
        self.assertEqual(vox.validar_guion(g), [])
        self.assertNotIn("falta `bucle`", " | ".join(vox.avisos_guion(g)))
        g["bucle"]["cierra"] = g["escenas"][0]["id"]
        self.assertIn("bucle.cierra", " | ".join(vox.validar_guion(g)))
        g["bucle"] = {"pregunta": "corta", "cierra": "no-existe"}
        self.assertIn("bucle:", " | ".join(vox.validar_guion(g)))

    def test_aviso_de_imagen_quieta(self):
        g = guion(); g["escenas"][1]["narracion"] = "Una frase de trece palabras que se queda mirando un solo recorte muy quieto."
        self.assertIn("una sola imagen quieta", " | ".join(vox.avisos_guion(g)))
        g["escenas"][1]["planos"] = [{"tipo": "dato", "dato": "1"}, {"tipo": "dato", "dato": "2", "en": "trece"}]
        self.assertNotIn("una sola imagen quieta", " | ".join(vox.avisos_guion(g)))

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
