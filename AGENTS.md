# Instrucciones para agentes que trabajen en este repositorio

Leer START_HERE.md y skills/milla-video-studio/SKILL.md. Mantener correcciones vigentes y distinción entre evidencia, candidatos y aprobaciones.

No introducir claves, datos de clientes, MP4 privados, URLs firmadas, estados reales o transcriptos crudos. No generar contenido de pago ni publicar en redes durante pruebas. No cambiar aprobación de voz para hacer pasar validadores.

Fuentes canónicas: skill y references. MANUAL_COMPLETO.md es derivado; regenerarlo con tools/build_manual.py. Probar Python y plantilla con los comandos reproducibles de docs/VALIDACION.md. No atribuir pruebas simuladas a servicios en vivo. Mantener preguntas y explicaciones breves y orientadas a resultados.

Los cambios de método deben registrar motivo/evidencia, pruebas y versión. Actualizaciones de preferencias explícitas prevalecen; experimentos deben quedar como candidatos. Mantener el perfil MILLA separado de otros perfiles.

## Qué skill usar (hay cuatro en este repositorio)

| Emi pide | Skill |
|---|---|
| Editar un video que **ya grabó** (a cámara, entrevista, evento, vlog), cortarlo, subtitularlo, o preparar la escaleta antes de grabar | `skills/editor-studio/SKILL.md` |
| Un video explicativo **desde un guion**, estilo documental-collage | `skills/vox-studio/SKILL.md` |
| Un video **dibujado a mano** (pizarra, acuarela, cuaderno, minimal) | `skills/pizarra-studio/SKILL.md` |
| Un video jurídico de MILLA ABOGADOS con su estándar | `skills/milla-video-studio/SKILL.md` |

El mapa de cómo se conectan sin mezclarse está en `cerebro/CEREBRO.md`. Sin terminal (chat de ChatGPT, Gemini, Muse, DeepSeek u otra IA) no se corta ni se rinde video: se hace la entrevista, la escaleta y el plan, y se entrega el traspaso de `skills/editor-studio/plantilla/TRASPASO.md` para producirlo en Claude Code o Codex.

## Trabajo entre IA (obligatorio para cualquier IA o persona)

Este repositorio sigue el protocolo común de `ia/PROTOCOLO.md`; las reglas concretas están en `ia/REGLAS.md`.
- Al empezar, ejecuta `python3 ia/verificar.py inicio`: resume rama, último commit y su IA, reglas y registro, y activa los hooks de git si faltan (en Claude Code corre solo).
- Fuente de verdad: el repositorio remoto y su estado vigente (el `project.json` de cada producción privada y `CHANGELOG.md`), no la memoria de una conversación.
- Todo cambio se registra en el mismo commit, con la línea `Agente:` (protocolo, sección 3). Sin escritura, entrega un «Registro pendiente para el repositorio».
- Lo prohibido y lo que requiere confirmación de Emi vale en Claude, ChatGPT, Codex, Gemini y cualquier otra IA. Con terminal, ejecuta `sh ia/instalar.sh` una vez por copia. GitHub revisa cada push con `registro-ia.yml`.
- Para pasar trabajo a otra IA: `ia/plantillas/PETICION.md` y `ia/plantillas/ENTREGA.md`.
