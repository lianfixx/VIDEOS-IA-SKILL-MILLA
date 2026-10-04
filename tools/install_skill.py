#!/usr/bin/env python3
"""Copy the complete portable skill without overwriting existing installations."""
import argparse
from pathlib import Path
import shutil
import sys

p = argparse.ArgumentParser(description=__doc__)
g = p.add_mutually_exclusive_group(required=True)
g.add_argument('--target', choices=['claude'])
g.add_argument('--destination', type=Path)
a = p.parse_args()
source = Path(__file__).resolve().parents[1] / 'skills' / 'milla-video-studio'
destination = a.destination.expanduser() if a.destination else Path.home() / '.claude' / 'skills' / 'milla-video-studio'
if destination.exists() or destination.is_symlink():
    sys.exit('La ruta ya existe. Revisa la instalación y respáldala antes de actualizar; no se sobrescribió nada.')
if not (source / 'SKILL.md').is_file():
    sys.exit('Falta la carpeta completa de la skill; descarga el repositorio completo.')
if any(f.is_symlink() for f in source.rglob('*')):
    sys.exit('La fuente contiene enlaces simbólicos; revisar antes de instalar.')
shutil.copytree(source, destination, ignore=shutil.ignore_patterns('__pycache__', 'node_modules', 'out', '*.pyc'))
print('Skill copiada a ' + str(destination.resolve()) + '. No se configuraron proveedores ni claves.')
