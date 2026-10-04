#!/usr/bin/env python3
"""Build the read-only portable manual from canonical skill references."""
from pathlib import Path
import re
root = Path(__file__).resolve().parents[1]
skill = root / 'skills' / 'milla-video-studio'
files = [skill/'SKILL.md'] + [skill/'references'/name for name in (
    'standard.md','workflow.md','connections.md','media-prep.md','prompts.md',
    'rendering.md','quality.md','improvement.md','portability.md','evidence.md')]
text = ['# MILLA Video Studio · manual portable\n\nGenerado desde la skill; editar los originales y ejecutar tools/build_manual.py.\nEste archivo transmite instrucciones. Para ejecutar se necesita la carpeta de código completa.\n']
for f in files:
    body = f.read_text(encoding='utf-8')
    def portable_link(match):
        label, target = match.groups()
        clean, marker, fragment = target.partition('#')
        if not clean or re.match(r'^[a-z]+://', clean) or clean.startswith('/'):
            return match.group(0)
        resolved = (f.parent / clean).resolve()
        try:
            relative = resolved.relative_to(root).as_posix()
        except ValueError:
            return match.group(0)
        return f'[{label}]({relative}{marker}{fragment})'
    body = re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)', portable_link, body)
    text.append('\n---\n\n## Archivo: '+str(f.relative_to(root))+'\n\n'+body)
(root/'MANUAL_COMPLETO.md').write_text('\n'.join(text),encoding='utf-8')
print('MANUAL_COMPLETO.md actualizado')
