"""Pruebas de exportar_web.py (versión web de un video aprobado). Clips sintéticos, sin red ni gasto."""
import contextlib
import hashlib
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import exportar_web  # noqa: E402

RAIZ = AQUI.parents[2]
COPIAS = [RAIZ / "skills" / s / "scripts" / "exportar_web.py" for s in ("vox-studio", "editor-studio", "milla-video-studio")]


def _hay_ffmpeg():
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        return False
    enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    return all(e in enc for e in ("libx264", "libvpx-vp9", "libwebp", "libopus"))


def _ff(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def _atomos(ruta):
    d, i, out = Path(ruta).read_bytes(), 0, []
    while i + 8 <= len(d):
        n, t = struct.unpack(">I4s", d[i:i + 8])
        out.append(t.decode("latin-1"))
        i += n if n > 1 else len(d)
    return out


def _probe(ruta, entradas, flujo=None):
    a = ["ffprobe", "-v", "error"] + (["-select_streams", flujo] if flujo else []) + \
        ["-show_entries", entradas, "-of", "csv=p=0", str(ruta)]
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout.split()


def _correr(*args):
    with contextlib.redirect_stdout(io.StringIO()):
        return exportar_web.main(list(map(str, args)))


class CopiasIdenticas(unittest.TestCase):
    def test_las_tres_skills_tienen_el_mismo_archivo(self):
        existentes = [c for c in COPIAS if c.exists()]
        if len(existentes) < len(COPIAS):
            self.skipTest("fuera del repositorio completo")
        hashes = {hashlib.sha256(c.read_bytes()).hexdigest() for c in existentes}
        self.assertEqual(len(hashes), 1, "exportar_web.py difiere entre skills: copiar la versión corregida a las tres")


@unittest.skipUnless(_hay_ffmpeg(), "ffmpeg con libx264, libvpx-vp9, libwebp y libopus no disponible")
class ExportarWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.vertical = cls.tmp / "vertical.mp4"
        _ff("-f", "lavfi", "-i", "testsrc2=size=360x640:rate=30:duration=3", "-f", "lavfi",
            "-i", "sine=frequency=440:duration=3", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(cls.vertical))
        cls.loop = cls.tmp / "loop.mp4"   # el tono da una vuelta completa en 3 s: cierra sin salto
        _ff("-f", "lavfi", "-i", "color=c=red:size=640x360:rate=30:duration=3", "-vf",
            "drawbox=x=40:y=40:w=200:h=150:color=white:t=fill,hue=h=t*120", "-c:v", "libx264",
            "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(cls.loop))
        cls.deriva = cls.tmp / "deriva.mp4"   # el cuadro se desplaza y no vuelve: el loop brinca
        _ff("-f", "lavfi", "-i", "color=c=navy:size=640x360:rate=30:duration=3", "-f", "lavfi",
            "-i", "color=c=yellow:size=120x120:rate=30:duration=3", "-filter_complex",
            "[0][1]overlay=x='t*150':y=100:shortest=1", "-c:v", "libx264",
            "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(cls.deriva))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_fondo_vertical_sin_audio_faststart_y_tope(self):
        out = self.tmp / "o1"
        inf = _correr(self.vertical, "--out", out, "--lado-corto", 240)
        self.assertEqual(_probe(out / "web.mp4", "stream=width,height", "v:0"), ["240,426"])
        self.assertEqual(_probe(out / "web.mp4", "stream=codec_type"), ["video"])
        self.assertEqual(_probe(out / "web.webm", "stream=codec_name"), ["vp9"])
        self.assertLess(_atomos(out / "web.mp4").index("moov"), _atomos(out / "web.mp4").index("mdat"))
        self.assertEqual(inf["tope_mb"], 3.0)
        self.assertTrue(inf["mp4"]["cabe_en_tope"] and inf["webm"]["cabe_en_tope"])
        for f in ("poster.webp", "poster.jpg", "web.json"):
            self.assertTrue((out / f).stat().st_size > 0, f)
        self.assertEqual(json.loads((out / "web.json").read_text())["uso"], "fondo en loop")

    def test_explicativo_conserva_audio_y_no_aplica_tope(self):
        out = self.tmp / "o2"
        inf = _correr(self.vertical, "--out", out, "--lado-corto", 240, "--con-audio")
        self.assertIn("aac", _probe(out / "web.mp4", "stream=codec_name"))
        self.assertIn("opus", _probe(out / "web.webm", "stream=codec_name"))
        self.assertIsNone(inf["tope_mb"])
        self.assertIsNone(inf["loop"])

    def test_scrub_tiene_un_cuadro_clave_por_cuadro(self):
        out = self.tmp / "o3"
        _correr(self.vertical, "--out", out, "--lado-corto", 240, "--scrub")
        claves = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame", "nokey",
                                 "-show_entries", "frame=pts_time", "-of", "csv=p=0", str(out / "scrub.mp4")],
                                capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(len(claves), 90)

    def test_tope_imposible_sube_compresion_y_avisa(self):
        out = self.tmp / "o4"
        inf = _correr(self.vertical, "--out", out, "--lado-corto", 240, "--tope-mb", 0.001)
        self.assertEqual(inf["mp4"]["crf"], 36)
        self.assertEqual(inf["webm"]["crf"], 48)
        self.assertTrue(any("no cabe" in x for x in inf["avisos"]))

    def test_revision_del_loop(self):
        bueno = _correr(self.loop, "--out", self.tmp / "o5", "--lado-corto", 240)
        malo = _correr(self.deriva, "--out", self.tmp / "o6", "--lado-corto", 240)
        self.assertTrue(bueno["loop"]["sin_salto"])
        self.assertFalse(malo["loop"]["sin_salto"])
        self.assertTrue(any("brincar" in x for x in malo["avisos"]))

    def test_poster_en_otro_segundo(self):
        out = self.tmp / "o7"
        _correr(self.deriva, "--out", out, "--lado-corto", 240, "--poster-en", 2)
        inicio = self.tmp / "o7-ini.png"
        _ff("-i", str(self.deriva), "-frames:v", "1", "-vf", exportar_web.escala(240), str(inicio))
        self.assertNotEqual(hashlib.sha256((out / "poster.jpg").read_bytes()).hexdigest(),
                            hashlib.sha256(inicio.read_bytes()).hexdigest())

    def test_errores_claros(self):
        with self.assertRaises(SystemExit):
            _correr(self.loop, "--out", self.tmp / "o8", "--con-audio")       # no tiene audio
        with self.assertRaises(SystemExit):
            _correr(self.loop, "--out", self.tmp / "o9", "--poster-en", 99)   # fuera del video


if __name__ == "__main__":
    unittest.main()
