@AGENTS.md

# Claude Code en este repositorio

- La skill `milla-video-studio` está en `skills/milla-video-studio/` y se carga desde el puente `.claude/skills/milla-video-studio` (invocable como `/milla-video-studio`).
- Las otras skills se cargan igual desde `.claude/skills/`: `/editor-studio` (editar lo que Emi graba), `/vox-studio` y `/pizarra-studio`. Cuál usar: tabla de `AGENTS.md`.
- Reglas comunes entre IA: `ia/REGLAS.md` y `ia/PROTOCOLO.md`. Frenos activos en `.claude/settings.json` → `ia/guard.py` (política en `ia/politica.json`, pruebas en `ia/test_guard.py`). Si un freno bloquea algo legítimo, explícaselo a Emi; no lo desactives ni lo rodees. Todo cambio se registra en el mismo commit con `Agente: Claude Code`.
- Reglas por tipo de archivo en `.claude/rules/` (se cargan solas al tocar esos archivos).
- Plan y entrevista, subagentes, `/goal` y demás trabajo en Claude Code: `skills/milla-video-studio/references/claude-code.md`.
