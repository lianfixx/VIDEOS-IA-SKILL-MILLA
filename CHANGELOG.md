# Cambios

## 2026-11-10 · Vox Studio 0.3.0: música y efectos por código, portada y subtítulos por espacio

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: en cada video analizar de qué va y proponer música, efectos y remates tipo meme creados con código; subtítulos serif para Castorena; portada automática. Sin producir un video nuevo.
- Cambios: `scripts/sonido.py` compone con numpy una pista original por ánimo (`tension`, `energia`, `serio`, `ironia`, `motivacion`) a la medida del video y sintetiza ocho remates sonoros (`boom`, `scratch`, `trombon`, `ding`, `redoble`, `suspenso`, `caja`, `error`); `vox.py sonido GUION` analiza el guion y propone ánimo, efecto por escena y remates, con límites por espacio (los jurídicos no llevan chiste). El guion exige `musica.animo` y al menos un `sonido`. Compositor: remate visual tipo sello, música que baja bajo la voz y sube al final, tipografía de subtítulos por espacio (Gelasio en Castorena) y composición `Portada`; `render` entrega también `out/portada.png`.
- Archivos: `skills/vox-studio/scripts/{sonido.py,vox.py,test_vox.py}`, `skills/vox-studio/plantilla/src/{Vox.tsx,Root.tsx}`, `skills/vox-studio/plantilla/guion.ejemplo.json`, `skills/vox-studio/SKILL.md`, `espacios/*/perfil.json`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas de vox-studio 25/25 → aprobado; `tsc --noEmit` → aprobado; el demo 2 existente se reconstruyó con `armar` (sin gastar saldo) y se rindió con música, efectos, remate y portada: 20.2 s, −14.22 LUFS, pico −1.90 dBTP → aprobado técnicamente; portadas de personal y Castorena revisadas como imagen → aprobado. Escucha de la música y los efectos → no ejecutado (la IA no oye audio; la juzga Emi).
- Pendiente: opinión de Emi sobre cómo suenan los cinco ánimos y los ocho efectos; confirmar el despacho Castorena; nombres y @ de los canales.

## 2026-11-10 · Vox Studio 0.2.0: auditoría completa, marca investigada y aprendizaje continuo

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: auditar y corregir todo; «las cosas tiemblan mucho»; imágenes más naturales, más efectos y transiciones; que la skill aprenda de todos los videos; investigar el estilo del PAN y de Castorena en sus sitios y redes oficiales; razonar por espacio.
- Cambios: (1) Movimiento: se eliminó la vibración a 12 fps; flotación lenta, rebotes amortiguados y grano discreto. (2) Transiciones nuevas `barrido` y `rasgado` además del viaje de cámara, con su efecto de sonido; rayos dibujados tras el recorte. (3) Imágenes: estilos `ilustracion` (por defecto), `foto` y `sticker`; modelo `seedream/5-lite-text-to-image` con esquema comprobado; recorte que mide el color real del fondo, quita lo conectado al borde y los huecos idénticos al fondo, con opción magenta. (4) Las 15 fallas de la revisión independiente: zoom continuo entre escenas, textos largos que ya no desbordan, límites de líneas y de notas, fuente en pantalla dentro de zona segura, `armar` para no volver a pagar la voz, estado de imagen ligado a su prompt, errores de red y de ffmpeg con mensaje claro, entrada y transición efectivas validadas, pregunta de cierre narrada, escenas mínimas de 24 frames. (5) Master en dos pasadas y comando `render` (render + master + hoja de fotogramas). (6) Aprendizaje: `espacios/APRENDIZAJES.md` y `espacios/<espacio>/aprendizajes.md`, comandos `aprender` y `aprendizajes`, lectura obligatoria antes de cada guion. (7) Marca por espacio en `MARCA.md`: PAN con colores leídos de pan.org.mx y accionjuvenil.com; Castorena con los de castorena.com.mx y titulares en Gelasio; tipografía de titular por espacio.
- Archivos: `skills/vox-studio/**`, `espacios/**`, puentes de la skill y este registro.
- Verificación: pruebas de vox-studio 20/20 → aprobado; `tsc --noEmit` → aprobado; render real del demo 2 (20.2 s, −14.09 LUFS, pico −1.80 dBTP) con 3 imágenes naturales (dos modelos) → aprobado técnicamente; hoja de fotogramas y un cuadro por espacio revisados por la IA → sin encimados; escucha y aprobación estética de Emi → no ejecutado. Gasto del demo 2: 17.5 créditos de Kie y 132 caracteres de ElevenLabs según los propios proveedores.
- Pendiente: que Emi confirme que castorena.com.mx es su despacho (la investigación no halló práctica laboral-burocrática pública); manual oficial del PAN no localizado; nombres y @ de los canales; música con derechos; token de Apify cuando haga falta una foto real.

## 2026-11-10 · espacios separados y reporte de saldos

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: que cada espacio (personal, MILLA, Castorena, PAN) esté por separado y que en cada video se le diga cuánto queda en ElevenLabs, Kie y Apify; auditar y corregir lo construido.
- Cambios: los perfiles pasan de `skills/vox-studio/perfiles.json` a `espacios/<espacio>/perfil.json`, con `ideas.md` por espacio; `vox.py proyecto` solo crea producciones en `productions/<espacio>/`. Nuevos `vox.py saldo` y `vox.py cierre DIR` (gastado y restante por proveedor; Apify se informa como no conectado si falta el token). Correcciones visuales tras auditar el demo cuadro por cuadro: subtítulos sin hueco vacío (palabras por decir atenuadas), nota manuscrita que ya no pisa el recorte, recortes más grandes y viñeta más ligera.
- Archivos: `espacios/**`, `skills/vox-studio/scripts/vox.py`, `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/SKILL.md` y este registro.
- Verificación: pruebas de vox-studio 9/9 → aprobado; `vox.py saldo` contra los proveedores reales → aprobado (Kie 232 créditos; ElevenLabs 39,608 de 40,000; Apify no conectado). Render con las correcciones visuales → no ejecutado todavía en este commit.
- Pendiente: integrar la revisión de código independiente y la investigación de marca de PAN y Castorena (en curso); volver a rendir y auditar el demo.

## 2026-11-10 · Vox Studio 0.1.0 (candidato) y entorno en la nube

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: configurar el entorno en la nube, instalar y mejorar el sistema del video «video-vox», crear shorts estilo Vox con su opinión y humor, con Daniel y Laura como voces y un perfil por espacio (personal, MILLA, Castorena, PAN).
- Cambios: nueva skill `skills/vox-studio/` con compositor Remotion propio (cámara continua sin fades, seis entradas, stickers a 12 fps, resaltador, subtítulos por palabra con tiempos reales del proveedor, fuentes empaquetadas), `scripts/vox.py` (guion con opinión obligatoria, voz ElevenLabs con alineación, imagen Kie nano-banana-2-lite, recorte por croma, SFX sintetizados, master) y cuatro perfiles candidatos. Puentes en `.claude/skills/` y `.agents/skills/`. No se copió código de `santmun/video-vox` (no tiene licencia). Preferencia nueva de Emi registrada: GPT Image solo si es necesario; el freno de `ia/politica.json` no se tocó.
- Archivos: `skills/vox-studio/**`, `.claude/skills/vox-studio/SKILL.md`, `.agents/skills/vox-studio/SKILL.md` y este registro.
- Verificación: `python3 -m unittest discover -s skills/vox-studio/scripts -p 'test_*.py'` → 9/9 aprobado; `tsc --noEmit` → aprobado; render real de un demo de 20.3 s (1080×1920, H.264/AAC, −14.3 LUFS) con 2 imágenes Kie (8 créditos) y 331 caracteres de voz → aprobado técnicamente, hoja de fotogramas revisada por la IA; escucha y aprobación estética de Emi → no ejecutado. El compositor de MILLA también rindió aquí con el Chromium preinstalado (`--browser-executable=/usr/local/bin/chrome-headless-shell`), lo que resuelve el bloqueo de render anotado en `docs/VALIDACION.md`. Entorno `videos-ia-skill-milla` creado con script de configuración; el script se probó a mano, no en un arranque nuevo.
- Pendiente: aprobación de Emi del demo; nombres y @ de cada canal; cotejar colores de PAN y Castorena con sus manuales; esquema de Seedream; música con derechos; el true peak del master quedó en −0.9 dBTP (objetivo −1.5).

## 2026-11-04 · corrección: puentes de skill con YAML válido

- Agente: Claude Code (sesión en la nube)
- Solicitud: autocorrección de Claude Code al revisar la skill matriz-castorena (4/11/2026).
- Cambios: los puentes `.claude/skills/` y `.agents/skills/` copiaban la descripción sin comillas; si contenía «: » el YAML quedaba inválido (afectaba a tareas-maestria y meta-ads-client-onboarding). Ahora va entre comillas, `ia/check_skill.py` rechaza valores que rompan el YAML y el control previo al commit revisa también los puentes.
- Archivos: `ia/check_skill.py`, `ia/politica.json`, `ia/REGLAS.md`, puentes de skill (si existen) y este registro.
- Verificación: `python3 ia/test_guard.py` → aprobado; `python3 ia/verificar.py inicio` → aprobado.
- Pendiente: ninguno.

## 2026-11-04 · corrección: flag de push mal formado

- Agente: Claude Code (sesión en la nube)
- Solicitud: autocorrección de Claude Code al revisar su propio comando (4/11/2026).
- Cambios: la regla que prohíbe forzar el push no atrapaba flags cortos mal formados que contienen `f` o `d` (por ejemplo `-f-never`); el patrón ahora es `-(?!-)\S*[fd]\S*`. Se añadió el caso a las pruebas. Ese push concreto (rama de mes.) fue de avance lineal y no borró historial.
- Archivos: `ia/politica.json`, `ia/REGLAS.md`, `ia/INSTRUCCIONES_PROYECTO.md` y este registro.
- Verificación: `python3 ia/test_guard.py` → aprobado; `python3 ia/verificar.py inicio` → aprobado.
- Pendiente: ninguno.

## 2026-11-04 · frenos de git también para Codex, ChatGPT y Gemini

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 4/11/2026: que los frenos de git funcionen también con Codex y ChatGPT, no solo con Claude.
- Cambios: `python3 ia/verificar.py inicio`, que `AGENTS.md` pide ejecutar a cualquier IA al empezar, ahora también activa los hooks de git si faltan (antes solo lo hacía el hook de Claude Code). Así Codex, ChatGPT con terminal y Gemini CLI quedan con los mismos frenos de commit y push. `AGENTS.md` e `ia/INSTRUCCIONES_PROYECTO.md` lo indican.
- Archivos: `ia/verificar.py`, `ia/test_guard.py`, `ia/INSTRUCCIONES_PROYECTO.md`, `AGENTS.md` y este registro.
- Verificación: `python3 ia/test_guard.py` → aprobado; `python3 ia/verificar.py inicio` → aprobado.
- Pendiente: ninguno.

## 2026-11-04 · arranque común entre IA (protocolo 1.1.0)

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 4/11/2026: «haz lo que tengas que hacer para que entiendas» las reglas al trabajar.
- Cambios: `python3 ia/verificar.py inicio` resume al empezar rama, último commit y su IA, reglas, registro vigente y hooks de git; en Claude Code corre solo con un hook `SessionStart` y activa los hooks de git si faltan. `ia/PROTOCOLO.md` pasa a 1.1.0; `AGENTS.md`, `GEMINI.md` e `ia/INSTRUCCIONES_PROYECTO.md` indican el comando a las demás IA.
- Archivos: `.claude/settings.json`, `ia/verificar.py`, `ia/test_guard.py`, `ia/PROTOCOLO.md`, `ia/INSTRUCCIONES_PROYECTO.md`, `AGENTS.md`, `GEMINI.md` y este registro.
- Verificación: `python3 ia/test_guard.py` → aprobado; `python3 ia/verificar.py inicio` → aprobado.
- Pendiente: ninguno.

## 2026-11-04 · 1.1.1 · registro obligatorio y trabajo entre IA

- Agente: Claude Code (sesión en la nube; modelo según la sesión)
- Solicitud: Emi, 4/11/2026: auditar y documentar las mejoras, hacerlas funcionar igual con ChatGPT, Gemini u otra IA, y documentar siempre todo cambio, use la IA que use, bajo las mismas reglas.
- Cambios: capa común `ia/` (protocolo común 1.0.0 basado en el de Mes, `REGLAS.md` generadas de `politica.json`, frenos para Claude Code, hooks de git para cualquier IA, workflow `registro-ia.yml`, `INSTRUCCIONES_PROYECTO.md` para ChatGPT y Gemini, plantillas de petición y entrega); `GEMINI.md`; sección «Trabajo entre IA» en `AGENTS.md`; `.claude/settings.json` apunta a `ia/guard.py` (se retira `.claude/hooks/`); auditoría en `ia/AUDITORIA_2026-11-04.md`. Skill 1.1.1: sección «Registro y continuidad entre IA» y nota de portabilidad en `references/claude-code.md`; el método no cambia.
- Archivos: ver `ia/AUDITORIA_2026-11-04.md`, sección «Archivos cambiados».
- Verificación: `python3 ia/test_guard.py` → aprobado; `python3 ia/verificar.py reglas --check` → aprobado; pruebas Python de la skill → aprobado (43); `milla.py secret-scan .` → sin hallazgos; `MANUAL_COMPLETO.md` regenerado.
- Revisión independiente: 17 hallazgos sobre el código común; corregidos los reproducidos, con pruebas de regresión (detalle en `ia/AUDITORIA_2026-11-04.md`).
- Pendiente: activar los hooks de git en cada copia (`sh ia/instalar.sh`); opcionalmente exigir el check `registro-ia` con protección de rama en GitHub.

## 1.1.0 · 2026-11-04

- SKILL.md añade la sección «Terminado y trabajo en Claude Code»: criterio de terminado verificable, entrevista inicial solo para un video nuevo con datos faltantes y pasos de máxima profundidad.
- Nueva referencia `references/claude-code.md`: frenos activos del repositorio, plan y entrevista, reparto en paralelo con un único `project.json`, `/goal`, `/loop` para consultar tareas ya enviadas, navegador y atajos de sesión. Se incluye en `MANUAL_COMPLETO.md`.
- La portada o miniatura queda explícita como entregable con revisión propia de píxeles (SKILL.md y `references/quality.md`), con las mismas reglas de imágenes.
- Versión de la plantilla Remotion alineada a 1.1.0, sin cambios de código ni dependencias.
- No cambian el método, los proveedores preferidos, los validadores ni los criterios de aprobación.

## 1.0.2 · 2026-11-03

- Se añadieron metadatos explícitos de versión, fecha e idioma al frontmatter de la skill.
- Remotion y sus paquetes se actualizaron de `4.0.532` a `4.0.540`; `npm audit --omit=dev` quedó en cero avisos.
- No cambian el método, los proveedores preferidos ni los criterios de aprobación.

## 1.0.1 · 2026-10-04

- Unificación de rutas: el mismo `public/<path>` se valida por hash y se renderiza con Remotion.
- `init-project` crea una producción autocontenida y conserva la negativa a sobrescribir.
- Paridad Python/Remotion para transiciones, escenas, diagramas, cues, palabras y SFX.
- Fish alineado a WAV 44.1 kHz; unidades de true peak explícitas en dBTP.
- Apify consolidado en una sola guía y endpoint vigente; requisitos de Python unificados.
- Informes JSON con hash de los dos MP4 recuperados y suites ampliadas a 43 y 16 pruebas.

## 1.0.0 · 2026-10-04

- Consolidación del estándar vigente y recapitulación con límites de evidencia.
- Skill portable, manual único e instalación sin sobrescritura.
- Kie Lite/Fish con simulación y recuperación por estado.
- Validador de proyectos y auditoría técnica del MP4.
- Plantilla Remotion original y pruebas de regresión.
- Voz Fish V3 pendiente, ChatGPT Image excluido y partículas prohibidas.

Consultar docs/VALIDACION.md para pruebas y límites; la versión no afirma que el diseño nuevo esté aprobado.
