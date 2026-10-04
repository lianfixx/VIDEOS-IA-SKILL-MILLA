# Portabilidad

La unidad portable es la carpeta con SKILL.md, referencias, scripts y plantillas. Leerla transmite el método. Ejecutar depende del entorno y permisos, no del nombre del modelo.

| Entorno | Uso | Condición |
|---|---|---|
| Agent Skills compatible | Instalar carpeta completa | Verificar ruta/mecanismo del producto |
| Claude Code | `.claude/skills/milla-video-studio/` o `~/.claude/skills/milla-video-studio/` | Invocar `/milla-video-studio`; mantener referencias relativas |
| ChatGPT Work con Skills | Instalación mediante habilidades personales | Comprobar que aparezca en Skills |
| Gemini, Grok, DeepSeek, Kimi u otro chat | Leer método y guiar acciones | No presumir instalación nativa, terminal, MCP ni render |
| Agente con terminal/red | Ejecutar scripts/compositor | Python, Node/npm, FFmpeg, dependencias y proveedores |
| Sin red | Preparar con fuentes existentes y medios locales | No afirmar investigación actual o generación remota |

Cada usuario conecta sus propias cuentas y guarda secretos fuera del chat. Instalar no instala un MCP ni entrega credenciales. Transferir proyectos con brief, estado, manifiesto, medios, fuentes y aprobaciones mediante canal autorizado. Una URL privada inaccesible no basta; adjuntar archivos si la IA no puede leerlos.

Prompt: “Lee SKILL.md y referencias. Detecta herramientas disponibles. Quiero {nuevo video/corrección} sobre {tema}. Conserva el estándar vigente. Ejecuta lo posible y guíame brevemente por la primera conexión faltante. No declares generación, revisión o aprobación sin evidencia.”

Fuentes consultadas 2026-10-04: https://agentskills.io/specification y https://code.claude.com/docs/en/skills. La tabla es condicional: no certifica soporte nativo en todas las apps mencionadas.
