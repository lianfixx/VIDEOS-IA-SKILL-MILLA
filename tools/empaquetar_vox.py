#!/usr/bin/env python3
"""Empaqueta Vox Studio en un .zip autocontenido para subirlo a claude.ai como skill personal.

Uso: python3 tools/empaquetar_vox.py [--salida dist/vox-studio.zip]

Incluye la skill y una copia de `espacios/` dentro de ella (en el repositorio viven aparte).
No incluye dependencias, producciones, la biblioteca ni ninguna clave. En claude.ai la skill
sirve para guion, método y consulta; rendir video requiere Claude Code con este repositorio.
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
ap.add_argument("--salida", type=Path, default=RAIZ / "dist" / "vox-studio.zip")
a = ap.parse_args()

with tempfile.TemporaryDirectory() as tmp:
    destino = Path(tmp) / "vox-studio"
    ignora = shutil.ignore_patterns("node_modules", "out", "__pycache__", "*.pyc", "test_*.py", "horno", "_render.json")
    shutil.copytree(RAIZ / "skills" / "vox-studio", destino, ignore=ignora)
    shutil.copytree(RAIZ / "espacios", destino / "espacios", ignore=ignora)
    # Guía de entrevista de pizarra: en la app no se produce, pero sí se puede entrevistar y dejar el traspaso listo.
    (destino / "pizarra").mkdir()
    shutil.copyfile(RAIZ / "skills" / "pizarra-studio" / "SKILL.md", destino / "pizarra" / "PIZARRA.md")
    shutil.copyfile(RAIZ / "skills" / "pizarra-studio" / "brief.ejemplo.json", destino / "pizarra" / "brief.ejemplo.json")
    pz = (destino / "pizarra" / "PIZARRA.md").read_text(encoding="utf-8")
    pz = re.sub(r"\A---\n.*?\n---\n", "", pz, flags=re.S)  # sin frontmatter: es un documento de apoyo, no otra skill
    pz = pz.replace("](../vox-studio/SKILL.md)", "](../SKILL.md)").replace("](../../espacios/", "](../espacios/")
    (destino / "pizarra" / "PIZARRA.md").write_text(pz, encoding="utf-8")
    for md in destino.rglob("*.md"):  # los enlaces que salían de la skill apuntan ahora adentro o quedan como texto
        t = md.read_text(encoding="utf-8")
        t = t.replace("](../../espacios/", "](espacios/").replace("](../../biblioteca/)", "](#)")
        if md.parent.name != "pizarra":
            t = t.replace("](../pizarra-studio/SKILL.md)", "](pizarra/PIZARRA.md)")
        t = re.sub(r"\[([^\]]+)\]\(\.\./milla-video-studio/SKILL\.md\)", r"\1", t)
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
