@AGENTS.md

# Claude Code en este repositorio

- La skill `milla-video-studio` está en `skills/milla-video-studio/` y se carga desde `.claude/skills/milla-video-studio` (invocable como `/milla-video-studio`).
- Frenos activos en `.claude/settings.json` (política en `.claude/hooks/policy.json`, pruebas en `.claude/hooks/test_guard.py`). Si un freno bloquea algo legítimo, explícaselo a Emi; no lo desactives ni lo rodees.
- Reglas por tipo de archivo en `.claude/rules/` (se cargan solas al tocar esos archivos).
- Plan y entrevista, subagentes, `/goal` y demás trabajo en Claude Code: `skills/milla-video-studio/references/claude-code.md`.
