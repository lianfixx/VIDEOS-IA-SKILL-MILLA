# Cambios

## 2026-11-10 · Vox Studio 0.6.0: segunda auditoría independiente (15 fallas) y niveles de audio

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: «audita de fondo, corrige errores».
- Cambios: Audio: la narración se normaliza a −16 LUFS, la música se coloca 17 LU por debajo con ganancia calculada, los ocho efectos salen al mismo nivel (−20 dBFS RMS) y afinados a la tonalidad, y el master pasa a ganancia fija con limitador; la auditoría mide cada efecto respecto a la voz y la ganancia del master. Música: todos los ánimos respiran por escena y `serio` ya no recibe golpes. Sello: sincronizado con su sonido, anclado a la esquina del recorte, exige `sonido` y no va en la primera escena. Seguridad y robustez: `reciclar --como` y `foto-bajar --out` no salen de la producción; índice validado; descarga con tope de 15 MB y comprobación de que es imagen; tipos inesperados en el guion ya no rompen el validador. Biblioteca: el id incluye el sha, `catalogar` valida el guion y crea la carpeta. Commons: miniaturas resueltas al archivo real y solo `/wikipedia/commons/`. Propuesta de sonido con límites de palabra («decreto» ya no vota gimnasio). `imagen --perfil E` aplica el estilo del espacio. Documentación alineada con el código.
- Archivos: `skills/vox-studio/scripts/{vox.py,sonido.py,test_vox.py}`, `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/{SKILL.md,CATALOGO.md}`, `biblioteca/**`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas 40/40 → aprobado; `tsc --noEmit` → aprobado; demo 2 reconstruido sin gasto y rendido: −14.04 LUFS, pico −2.41 dBTP, voz −16.12 LUFS, música 16.9 LU bajo la voz, efectos −5.7 dB respecto a la voz, master −1.1 dB, sin avisos → aprobado técnicamente; sellos revisados como imagen → aprobado. Escucha de Emi → no ejecutado.
- Pendiente: añadir las pruebas de vox-studio al control previo al commit (cambia `ia/politica.json`; requiere confirmación de Emi).

## 2026-11-10 · Vox Studio 0.5.1: auditoría de fondo, solo video y cuentas por red

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: fusionar a `main`; `@emilianomilla_` es de X y la cuenta de TikTok aún no existe; «no combinar cosas, aquí es puro video»; auditar de fondo y corregir errores.
- Cambios: (1) El guion de ejemplo no pasaba su validador: las entradas y transiciones automáticas ahora se apartan de las que el guion fija (antes y después), y el ejemplo tiene su prueba. (2) La sección «Puente con x-viral» se sustituye por «Solo video»: esta skill no redacta ni programa publicaciones. (3) Espacio personal: `handle` vacío (no hay TikTok) y `cuentas.x` con `@emilianomilla_`; el @ de X no se muestra en los videos. (4) `README.md` presenta Vox Studio y `docs/VALIDACION.md` registra el render ya comprobado y los controles de la skill.
- Archivos: `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/vox-studio/SKILL.md`, `skills/vox-studio/plantilla/guion.ejemplo.json`, `espacios/personal/{perfil.json,MARCA.md}`, `espacios/APRENDIZAJES.md`, `README.md`, `docs/VALIDACION.md` y este registro.
- Verificación: pruebas de vox-studio 33/33 → aprobado; flujo desde un proyecto nuevo (`proyecto`, `npm ci`, `tsc`, cuadro del video y portada) sin gasto → aprobado; `validar` del ejemplo → aprobado.
- Pendiente: integrar la segunda revisión independiente del código (en curso); las pruebas de vox-studio no corren en el control previo al commit porque añadirlas cambia `ia/politica.json`, que requiere confirmación de Emi.

## 2026-11-10 · Vox Studio 0.5.0: Apify de punta a punta y puente con x-viral

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: «ya tengo el token de Apify, continúa con todo» (tras consultarle la petición de la sesión de x-viral).
- Cambios: `foto-bajar` lee autor y licencia de la ficha de Wikimedia Commons y, si su API limita, sigue con `--licencia` manual; cabecera de cliente genérica en las peticiones. Skill: preferencia de licencias (dominio público, CC0, CC BY; BY-SA con aviso a Emi) y sección «Puente con x-viral». Espacio personal: `handle` `@emilianomilla_`. Entorno `videos-ia-skill-milla`: se autorizaron `upload.wikimedia.org` y `commons.wikimedia.org`.
- Archivos: `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/vox-studio/SKILL.md`, `espacios/personal/{perfil.json,MARCA.md}`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas 31/31 → aprobado. Descarga real de una foto de Commons (4140×2760, CC BY-SA 3.0, autor comprobado en su ficha y vista como imagen) → aprobado. Lectura automática de la licencia: falló dos veces por límite de peticiones (HTTP 429) y funcionó a la tercera; por eso el respaldo manual.
- Pendiente: confirmar que `@emilianomilla_` es también el @ de TikTok; fusionar esta rama a `main` para que el puente de x-viral lea Vox Studio (requiere que Emi lo pida).

## 2026-11-10 · Apify conectado y probado en real

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: usar Apify (entregó el token por el formulario seguro).
- Cambios: `foto` exige un tope de gasto acorde al precio real del actor (0.005 de arranque + 0.05 por página + 0.0023 por foto) y su valor por defecto sube a 0.12 USD; se leen `imageWidth` e `imageHeight` del resultado. Aprendizaje y skill actualizados con el costo medido.
- Archivos: `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/vox-studio/SKILL.md`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas 30/30 → aprobado. Llamadas reales a Apify: la primera, con tope 0.05 USD, falló (abortada por el tope, cobró 0.05); la segunda, con tope 0.12, devolvió 3 candidatas con su página de origen → aprobado. Saldo según Apify tras ambas: 4.895 de 5 USD. Descarga real de una foto (`foto-bajar`) → no ejecutado: el dominio de cada foto debe autorizarse en la red del entorno.
- Pendiente: probar `foto-bajar` en el primer video que necesite una foto real.

## 2026-11-10 · Vox Studio 0.4.0: sonido nuevo por video, auditoría de audio, Apify y biblioteca

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: generar con Apify; que la música se audite y que todo se genere nuevo acorde a cada video; documentar lo que ya existe para reciclarlo solo si de verdad queda.
- Cambios: la música y los efectos se generan con una semilla que sale del texto de cada guion (tonalidad, tempo, progresión, patrón y arreglo por escena distintos; efectos afinados a la tonalidad) y se registran en `estados/musica.json`. `render` audita el audio (música respecto a la voz, sonoridad, pico, efectos faltantes, silencios) y deja `out/auditoria-audio.json`; la música baja a 0.09 para quedar 13.9 LU bajo la voz en el demo. Comandos `foto` y `foto-bajar` para fotos reales con Apify (token en cabecera, tope de gasto, filtro Creative Commons, licencia obligatoria al bajar). Biblioteca: `catalogar`, `biblioteca` y `reciclar`, con `biblioteca/catalogo.json`. Nuevo `skills/vox-studio/CATALOGO.md` con todo lo programado.
- Archivos: `skills/vox-studio/scripts/{vox.py,sonido.py,test_vox.py}`, `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/{SKILL.md,CATALOGO.md}`, `biblioteca/**` (3 recortes del demo 2), `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas de vox-studio 30/30 → aprobado; demo 2 reconstruido sin gasto y rendido: −14.15 LUFS, pico −1.87 dBTP, música 13.9 LU bajo la voz, sin avisos → aprobado técnicamente. Apify: probado con respuesta simulada y en seco; llamada real → no ejecutado (falta el token). Escucha de Emi → no ejecutado.
- Pendiente: token de Apify y una búsqueda real acotada; opinión de Emi sobre cómo suena; petición de la sesión de x-viral (sección «Puente con x-viral» en la skill y @ del espacio personal) sin aplicar hasta que Emi la confirme.

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
