# Trabajo en Claude Code

Complemento operativo para Claude Code. No cambia el estándar, los proveedores ni los criterios de aprobación: si algo aquí parece contradecir [SKILL.md](../SKILL.md) o [standard.md](standard.md), prevalecen ellos.

## Frenos activos (hooks)

El repositorio configura estos frenos:

1. Bloquear generación de imágenes con OpenAI, ChatGPT o DALL·E: llamadas a `api.openai.com/v1/images` y conectores con esos nombres.
2. Antes de un commit que toque `skills/`, correr las pruebas Python de la skill.
3. Antes de `git push`, ejecutar `milla.py secret-scan .` y preguntar antes de subir; `push --force` queda bloqueado.
4. Antes de cada commit, buscar secretos y datos personales en el diff.
5. Si cambia SKILL.md, comprobar que siga siendo compatible con claude.ai.

Solo actúan en Claude Code dentro de este repositorio, no en claude.ai ni en otras IA. No sustituyen las reglas de la skill: la prohibición de ChatGPT Image, la revisión de píxeles y la escucha siguen valiendo donde no hay hook.

## Plan y entrevista

Usar modo plan (Shift+Tab) para un video nuevo o un cambio del estándar: investiga y propone sin tocar archivos ni gastar saldo. En una revisión o reanudación, recuperar primero `project.json` y `state.json`.

Pedir la entrevista solo al empezar un video nuevo cuando falten en el proyecto objetivo, audiencia, plataforma, jurisdicción, CTA o presupuesto autorizado. Voz y música no se preguntan en abstracto: se preparan muestras y luego se pide la elección. Prompt listo para copiar:

> Antes de armar el plan, entrevístame. Hazme una pregunta a la vez solo sobre lo que falte en el proyecto: objetivo, audiencia, plataforma, jurisdicción, CTA y presupuesto autorizado. No repitas lo ya registrado ni pidas otra vez aprobaciones existentes. Después muéstrame el plan.

## Reparto en paralelo

Para un video con varios recursos, dividir por tipo de recurso:

- Investigación y guion: fuentes oficiales, mapa de afirmaciones y storyboard en `research/`.
- Prompts de imágenes: un prompt por escena según [prompts.md](prompts.md), con las exclusiones del estándar.
- Música y SFX: candidatos, contrato y derechos documentados.
- Diagramas: nodos y aristas nativos, con la fuente de cada dato.

Hay un único manifiesto, `project.json`, y solo quien consolida lo edita, junto con `state.json`. Los subagentes entregan archivos o propuestas en su carpeta; no editan el manifiesto ni aprueban recursos. Cada tarea de proveedor usa su propio archivo de estado. Nadie ejecuta `--execute` ni gasta saldo fuera del presupuesto autorizado. Ningún subagente entrega, publica ni declara el video terminado: eso lo hace quien consolida, tras validar.

## /goal

> /goal Terminar el video en RUTA: `milla.py validate RUTA/project.json` pasa sin `--allow-pending` y existe un `RUTA/qa.json` nuevo de `inspect-video`. Si falta una escucha o aprobación humana, detente y pídela; no la registres por tu cuenta.

## /loop

Para tareas ya enviadas, consultar estado en vez de reenviar tras un timeout:

> /loop 3m Consulta una vez la tarea Kie con `python3 scripts/providers.py --workspace RUTA kie-status --state estados/imagen-01.json --execute`. No crees otra tarea. Detente en `success` o `fail` y dime el resultado.

Usar intervalos de 2 a 5 minutos. El adaptador de Fish no consulta estado: si un estado quedó en `submission_unconfirmed`, no reenviar en bucle; revisar la cuenta antes de volver a pagar. `/loop` dura mientras la sesión esté abierta (hasta 7 días).

## Navegador

Claude in Chrome usa tu Chrome con tus sesiones: sirve para revisar en los paneles de Kie, Fish o Apify el historial, precio o saldo antes de reenviar o gastar. No escribe claves en el chat, no recarga saldo ni contrata planes. Playwright abre un navegador aparte, para probar páginas; el render lo hace Remotion con su propio navegador. Nunca usar ninguno para eludir accesos.

## En la sesión

- `/context`: ver cuánto espacio ocupan skill, referencias y conectores.
- `/compact conserva project.json, task IDs, hashes y aprobaciones`: liberar espacio sin perder el estado.
- `/clear`: entre un video y otro, para que un tema nuevo no se vuelva V2 del anterior.
- `/rewind` (o Esc Esc): volver a un punto anterior si una corrección tomó mal camino.
- `/btw`: preguntar algo mientras corre un render sin mezclarlo en la conversación.
- `!python3 scripts/milla.py doctor`: correr el diagnóstico directo en la terminal.
- `/remote-control`: seguir desde el teléfono una sesión con render o consultas largas.

## Mejora continua

En Claude Code local, `/insights` ayuda a detectar patrones de uso. Sus sugerencias son candidatas: siguen el procedimiento de [mejora continua](improvement.md) con observación, evidencia, prueba y versión, nunca reglas automáticas.
