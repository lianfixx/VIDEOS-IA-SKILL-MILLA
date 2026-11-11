#!/usr/bin/env python3
"""Empaqueta Editor Studio en un .zip autocontenido para subirlo a claude.ai u otra IA como skill.

Uso: python3 tools/empaquetar_editor.py [--salida dist/editor-studio.zip]

Incluye la skill, una copia de `espacios/` y el mapa del cerebro dentro de ella (en el repositorio
viven aparte). No incluye dependencias, producciones ni ninguna clave. Sin terminal la skill sirve
para la entrevista, la escaleta, leer una transcripción y dejar el plan; cortar y rendir requiere
Claude Code con este repositorio.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--salida", type=Path, default=RAIZ / "dist" / "editor-studio.zip")
a = ap.parse_args()

with tempfile.TemporaryDirectory() as tmp:
    destino = Path(tmp) / "editor-studio"
    ignora = shutil.ignore_patterns("node_modules", "out", "__pycache__", "*.pyc", "test_*.py")
    shutil.copytree(RAIZ / "skills" / "editor-studio", destino, ignore=ignora)
    shutil.copytree(RAIZ / "espacios", destino / "espacios", ignore=ignora)
    (destino / "cerebro").mkdir()
    shutil.copyfile(RAIZ / "cerebro" / "CEREBRO.md", destino / "cerebro" / "CEREBRO.md")
    for md in destino.rglob("*.md"):   # los enlaces que salían de la skill apuntan ahora adentro o quedan como texto
        t = md.read_text(encoding="utf-8")
        if md.parent == destino:
            t = t.replace("](../../cerebro/CEREBRO.md)", "](cerebro/CEREBRO.md)").replace("](../../espacios/", "](espacios/")
        t = re.sub(r"\[([^\]]+)\]\(\.\./(?:\.\./skills/)?(?:vox-studio|pizarra-studio|milla-video-studio|editor-studio)/SKILL\.md\)", r"\1", t)
        md.write_text(t, encoding="utf-8")
    r = subprocess.run([sys.executable, str(RAIZ / "ia" / "check_skill.py"), str(destino)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("El paquete no es válido para claude.ai:\n" + r.stdout + r.stderr)
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.salida, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(destino.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(tmp))
    print(f"{a.salida} · {a.salida.stat().st_size // 1024} KB · {len(zipfile.ZipFile(a.salida).namelist())} archivos")
