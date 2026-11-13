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
    shutil.copyfile(RAIZ / "skills" / "vox-studio" / "scripts" / "autoria.py", destino / "scripts" / "autoria.py")  # regla compartida
    shutil.copyfile(RAIZ / "skills" / "vox-studio" / "scripts" / "sonido.py", destino / "scripts" / "sonido.py")    # música por código
    shutil.copytree(RAIZ / "espacios", destino / "espacios", ignore=ignora)
    (destino / "cerebro").mkdir()
    shutil.copyfile(RAIZ / "cerebro" / "CEREBRO.md", destino / "cerebro" / "CEREBRO.md")
    for md in destino.rglob("*.md"):   # los enlaces que salían de la skill apuntan ahora adentro o quedan como texto
        t = md.read_text(encoding="utf-8")
        if md.parent == destino:
            t = t.replace("](../../cerebro/CEREBRO.md)", "](cerebro/CEREBRO.md)").replace("](../../espacios/", "](espacios/")
            t = t.replace("python3 skills/editor-studio/scripts/editor.py", "python3 scripts/editor.py")
        # cualquier enlace a otra skill (no viaja en el paquete) queda como texto
        t = re.sub(r"\[([^\]]+)\]\((?:\.\./)+(?:skills/)?(?:vox-studio|pizarra-studio|milla-video-studio|editor-studio)/[^)]*\)", r"\1", t)
        t = re.sub(r"\[([^\]]+)\]\(\.\./espacios/[^)]*\)", r"\1", t) if md.parent.name == "cerebro" else t
        md.write_text(t, encoding="utf-8")
    (destino / "LEEME-PAQUETE.md").write_text(
        "# Editor Studio empaquetada\n\nCopia de la skill para usarla fuera del repositorio `lianfixx/VIDEOS-IA-SKILL-MILLA`. "
        "Aquí los comandos son `python3 scripts/editor.py …`. No viajan `CHANGELOG.md`, `docs/`, `ia/` ni las tendencias: "
        "la versión vigente y la memoria completa están en el repositorio. Lo que se aprenda aquí (`aprender`) hay que llevarlo "
        "al repositorio o se pierde al reemplazar el paquete. Sin terminal: entrevista, escaleta y plan, y el traspaso de "
        "`plantilla/TRASPASO.md`.\n", encoding="utf-8")
    rotos = []
    for md in destino.rglob("*.md"):
        for enlace in re.findall(r"\]\(([^)#\s]+)", md.read_text(encoding="utf-8")):
            if not enlace.startswith(("http", "mailto")) and not (md.parent / enlace).exists():
                rotos.append(f"{md.relative_to(destino)} → {enlace}")
    if rotos:
        sys.exit("El paquete tiene enlaces rotos:\n" + "\n".join(rotos))
    r = subprocess.run([sys.executable, str(RAIZ / "ia" / "check_skill.py"), str(destino)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("El paquete no es válido para claude.ai:\n" + r.stdout + r.stderr)
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.salida, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(destino.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(tmp))
    print(f"{a.salida} · {a.salida.stat().st_size // 1024} KB · {len(zipfile.ZipFile(a.salida).namelist())} archivos")
