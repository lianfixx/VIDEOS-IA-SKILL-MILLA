# Cambios

## 2026-11-11 · Vox Studio 0.12.0 y MILLA Video Studio 1.3.1: el código se suma a las imágenes, no las sustituye

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026, al ver las muestras v3, v4 y la de pizarra: «está mal, el anterior ya estaba perfecto; los quiero así; solo te dije que agregaras cosas con código, no que todo lo reemplazaras con él».
- Motivo: error de interpretación del agente. En las muestras se cambiaron imágenes y un sello por diagramas, y la muestra de pizarra no llevaba ninguna imagen; además se había escrito en la skill la regla contraria («código primero»).
- Cambios en Vox Studio: (1) plano de imagen con `junto`: una pieza de código (`dato`, `lista`, `calendario`, `barras`, `linea`, `flujo`) que entra a su lado con su palabra mientras la imagen se queda. (2) Reglas reescritas en `SKILL.md`, `NARRATIVA.md` y `CATALOGO.md`: la imagen es la base de cada escena y el código se suma; se retiró «código primero» y el aviso que pedía dibujar casi todo en estilo pizarra. (3) `validar` avisa de cualquier escena que quede solo con código. (4) Producción `pagos-digitales-v5`: el guion del video aprobado sin quitarle nada, con su voz original, más cinco añadidos (tres apuntes, un flujo junto al reloj de arena y unas barras junto a la pila de hojas).
- Cambios en MILLA Video Studio 1.3.1: los `beats` ya conviven con las imágenes de la escena (van debajo, donde iría el diagrama) en lugar de excluirlas; solo excluyen `diagram`, y `body` cuando hay imágenes. Mismas reglas en Python y Remotion.
- Archivos: `skills/vox-studio/{SKILL.md,NARRATIVA.md,CATALOGO.md,TECNICA.md}`, `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/milla-video-studio/{SKILL.md,references/rendering.md,references/narrative-motion.md}`, `skills/milla-video-studio/assets/remotion-template/src/{MillaVideo.tsx,manifest-validation.mjs}`, `skills/milla-video-studio/assets/remotion-template/test/timeline.test.mjs`, `skills/milla-video-studio/assets/remotion-template/{package.json,package-lock.json}`, `skills/milla-video-studio/scripts/{milla.py,test_milla.py}`, `MANUAL_COMPLETO.md`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas de vox-studio 57/57 → aprobado; pruebas Python de milla-video-studio 45/45 y del compositor 17/17 → aprobado; `tsc --noEmit` en ambas plantillas → aprobado. Cuadros de prueba: flujo junto al reloj, barras junto a la pila de hojas y apunte junto al billete (Vox); imagen con cifra y con barras debajo (pizarra) → aprobado. La v5 conserva los mismos planos y tiempos del video aprobado (56.1 s, voz ya pagada, sin gasto) → aprobado. Render completo de la v5 → en curso al registrar. Opinión de Emi → no ejecutado.
- Pendiente: que Emi vea la v5; las muestras v3, v4 y la primera de pizarra quedan descartadas.

## 2026-11-11 · MILLA Video Studio 1.3.0: planos animados en el compositor de pizarra

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: «tenemos dos formas de crear videos aquí, por vox y con pizarra estilo motion»; las mejoras debían llegar también a la segunda, que solo había recibido documentación. Sobre la voz del video aprobado: dejarla como está.
- Cambios: (1) `beats` por escena en el compositor de MILLA: `quote`, `list`, `calendar`, `figure`, `timeline`, `bars`, `image` y `note`, con entrada y salida por plano, en marfil, azul y dorado, sin partículas ni anillos. (2) Las mismas reglas en `milla.py` y `manifest-validation.mjs`. (3) Comando `milla.py anchor-beats`: fija `at` de cada plano y pieza desde la palabra real de la voz (`subtitleCues[].words`, con `wordTimestampsVerified`). (4) Documentación en `references/rendering.md` y `references/narrative-motion.md`; manual regenerado. (5) Lección general: no cambiar la voz de un video aprobado.
- Archivos: `skills/milla-video-studio/assets/remotion-template/src/{MillaVideo.tsx,types.ts,manifest-validation.mjs}`, `skills/milla-video-studio/assets/remotion-template/test/timeline.test.mjs`, `skills/milla-video-studio/assets/remotion-template/{package.json,package-lock.json}`, `skills/milla-video-studio/scripts/{milla.py,test_milla.py}`, `skills/milla-video-studio/{SKILL.md,references/rendering.md,references/narrative-motion.md}`, `MANUAL_COMPLETO.md`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas Python de milla-video-studio 45/45 → aprobado; pruebas del compositor 17/17 → aprobado; paridad Python–Remotion sobre 30 manifiestos con planos válidos e inválidos → aprobado; `tsc --noEmit` → aprobado; `check_skill` → aprobado. Ocho cuadros de prueba y un render técnico de 24.4 s sin audio (1080×1920, H.264) revisados por la IA → aprobado técnicamente. Render con voz, música y subtítulos reales, y `anchor-beats` sobre una narración real → no ejecutado: no hay todavía una producción de MILLA con voz aprobada. Aprobación estética de Emi → no ejecutado.
- Pendiente: primer video real de pizarra con planos; decidir si se portan el duo, las etiquetas y el sello de remate.

## 2026-11-11 · Vox Studio 0.11.0 y MILLA Video Studio 1.2.0: voz con ritmo, segunda voz, foto real, pizarra, lecciones para todos los espacios y auditoría

- Agente: Claude Code (sesión en la nube), con un subagente revisor independiente para la auditoría
- Solicitud: Emi, 11/11/2026: que lo aprendido valga para todos los espacios salvo su espíritu; decir más lento los cambios de tema, hacer pausas y usar expresiones humanas; preparar una segunda voz que opine para un video polémico futuro; usar bien Apify y Kie; aplicar todas las mejoras a los videos de pizarra o motion; «documenta, audita e implementa».
- Cambios en Vox Studio: (1) Voz: marcas `[pausa]`, `[pausa larga]` y expresiones (`[ríe]`, `[suspira]`…) en la narración; `cambio_tema` (respiro de 0.55 s y escena 10 % más lenta); narración por tramos con `previous_text`/`next_text`; segunda voz `voz_comentario` por espacio (candidata, modelo `eleven_v3`) con escenas `voz: "comentario"` y subtítulos en caja invertida con «OPINIÓN». (2) Imágenes: plano `imagen` con `foto_real` y `credito`; respaldo a la versión de 960 px cuando Wikimedia limita el original; regla de decidir cada plano entre código, Apify y Kie. (3) `estilo: "pizarra"`. (4) Tabla de anchos reales de Anton en el titular. (5) `aprender` avisa de que por espacio solo va el espíritu; lecciones de Castorena que eran de oficio se guardaron como generales. (6) Los trazos de punta redonda ya no dejan un punto antes de dibujarse. (7) Auditoría independiente: 12 fallas confirmadas y 3 plausibles, corregidas con prueba (ver TECNICA.md §2).
- Cambios en MILLA Video Studio 1.2.0: nueva referencia `references/narrative-motion.md` (candidata) con lo que se adopta de Vox Studio y lo que no; manual regenerado. El compositor de MILLA no se modificó.
- Archivos: `skills/vox-studio/{SKILL.md,CATALOGO.md,TECNICA.md,NARRATIVA.md}`, `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/plantilla/guion.ejemplo.json`, `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `espacios/README.md`, `espacios/APRENDIZAJES.md`, `espacios/*/perfil.json`, `skills/milla-video-studio/{SKILL.md,references/narrative-motion.md}`, `skills/milla-video-studio/assets/remotion-template/{package.json,package-lock.json}`, `tools/build_manual.py`, `MANUAL_COMPLETO.md` y este registro.
- Verificación: pruebas de vox-studio 56/56 → aprobado; pruebas de milla-video-studio 43/43 → aprobado; `tsc --noEmit` → aprobado; `check_skill` de ambas skills → aprobado. Voz en real: pausas con `eleven_multilingual_v2` y risa con `eleven_v3` devuelven tiempos por palabra → aprobado; narración real de 4 tramos con dos voces (240 caracteres) y de 4 tramos con dos cambios de tema (811 caracteres) → aprobado. Prueba de dos voces rendida: 19.61 s, −14.10 LUFS, sin avisos → aprobado técnicamente. Apify: búsqueda real y descarga de una foto de Wikimedia Commons (CC BY-SA 4.0, ProtoplasmaKid) con licencia leída de su ficha → aprobado. Cuadros de prueba en personal, MILLA y PAN, y en estilo pizarra → aprobado. Render final de `pagos-digitales-v4` con las correcciones de la auditoría → en curso al registrar. Kie: no se generó nada nuevo; sus modelos de video se revisaron solo en fuentes de terceros → no ejecutado. Escucha de Emi de la segunda voz, de las pausas y del cambio de tema → no ejecutado.
- Pendiente: que Emi elija por oído la voz que opina; su decisión sobre usar la foto CC BY-SA (obliga a dar crédito y a compartir igual la obra derivada); portar las piezas a la plantilla de MILLA si lo pide; referencias de X; medir retención y envíos al publicar.

## 2026-11-11 · Vox Studio 0.10.0: narrativa investigada y más motion con código

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: «aprende todo lo que hicimos»; poner más elementos explicando a la par de las imágenes; generar piezas con motion hecho con código; aprender storytelling viral tras investigar, analizar y razonar. Calificó el video aprobado con un 10.
- Cambios: (1) `skills/vox-studio/NARRATIVA.md`: investigación con fuentes y grado de certeza (señales de Instagram y TikTok, principios de Mayer, Berger y Milkman sobre lo que se comparte, visionado sin sonido, oficio de gancho y bucle, estilo Vox), análisis de por qué funcionó el video aprobado y reglas de guion, imagen y difusión. (2) Planos nuevos dibujados con código: `flujo`, `linea` (línea de tiempo) y `barras`; añadidos a cualquier plano: `apunte` (nota a mano anclada) y `etiquetas` sobre la imagen. (3) Guion: `bucle` (pregunta abierta y escena que la responde) y avisos nuevos (guion sin bucle, gancho sin segundo plano, plano quieto más de 4.5 s). (4) Muestra `productions/castorena/pagos-digitales-v3` con las piezas nuevas, misma voz e imágenes: sin gasto. El video aprobado no se tocó. (5) Seis lecciones nuevas, entre ellas el proceso completo que llevó al video aprobado.
- Archivos: `skills/vox-studio/{NARRATIVA.md,SKILL.md,CATALOGO.md,TECNICA.md}`, `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/plantilla/guion.ejemplo.json`, `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas de vox-studio 50/50 → aprobado; `tsc --noEmit` → aprobado; `check_skill` → aprobado. Cuadros de prueba de flujo, barras, línea de tiempo, etiquetas y apunte → aprobado. Render de la muestra: 56.09 s, −14.09 LUFS, pico −2.19 dBTP, un aviso de imagen (0.5 % bajo la descripción de TikTok, escena 08) → aprobado técnicamente con ese aviso; tira de 35 cuadros revisada por la IA → aprobado. La línea de tiempo solo se probó en un cuadro, no en un render completo → no ejecutado. Las reglas de narrativa salen de fuentes generales; no hay datos propios de retención ni envíos → no ejecutado. Opinión de Emi sobre la muestra → no ejecutado.
- Pendiente: que Emi diga si la muestra mejora o no al video aprobado; medir retención y envíos al publicar; referencias de X que mencionó; probar las piezas en Anton.

## 2026-11-11 · Vox Studio 0.9.1: primer video aprobado (Castorena)

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026, tras ver el corte con planos: «ESTÁ PERFECTO».
- Cambios: se registra la aprobación del video de pagos digitales como referencia del espacio Castorena (skill, `MARCA.md` y aprendizajes). El compositor sigue como candidato en personal, MILLA y PAN.
- Archivos: `skills/vox-studio/SKILL.md`, `espacios/castorena/{MARCA.md,aprendizajes.md}` y este registro.
- Verificación: pruebas de vox-studio 48/48 → aprobado; `check_skill` → aprobado. Visto bueno de Emi sobre el MP4 → aprobado (no detalló voz, música ni efectos por separado). Publicación en redes → no ejecutado: no se pidió.
- Pendiente: referencias de X que Emi mencionó; aviso de la escena 08 bajo la descripción de TikTok; probar los planos en Anton.

## 2026-11-11 · Vox Studio 0.9.0: planos dentro de la escena (guion visual)

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026, al ver el primer video de Castorena: «solo generas una imagen estática»; pidió más imágenes, efectos y storytelling, y recordó que el mismo video es para WhatsApp, LinkedIn, TikTok y X.
- Cambios: (1) `planos` por escena: `imagen`, `cita` (recorte del documento con la frase subrayada), `lista` (palomeada o tachada), `calendario`, `dato` (cifra que cuenta, con tachado) y `duo`; cada plano entra con el tiempo real de su palabra ancla (`en`) y el anterior sale de cuadro; `remate_en` ancla el sello; sonido al entrar cada plano. (2) `validar` comprueba planos y anclas y avisa de escenas largas con una sola imagen; `catalogar` y `armar` consideran todas las imágenes de la escena. (3) Corte suelto de Castorena rehecho con 20 planos en 8 escenas, misma voz (sin costo de narración) y dos imágenes nuevas. (4) Tres lecciones nuevas.
- Archivos: `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/plantilla/guion.ejemplo.json`, `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/vox-studio/{SKILL.md,CATALOGO.md,TECNICA.md}`, `biblioteca/`, `espacios/APRENDIZAJES.md`, `espacios/castorena/aprendizajes.md` y este registro.
- Verificación: pruebas de vox-studio 48/48 → aprobado; `tsc --noEmit` → aprobado; `check_skill` → aprobado. Citas de los arts. 13 y 16 copiadas del texto del DOF consultado en esta sesión → aprobado. Render: 56.09 s, H.264 1080×1920, −14.08 LUFS, pico −2.12 dBTP; un aviso de imagen (0.5 % bajo la descripción de TikTok en la escena 08) → aprobado técnicamente con ese aviso. Tira de 35 cuadros y cuadros sueltos de cada tipo de plano revisados por la IA → aprobado. Los sonidos de entrada de plano no están en la auditoría de audio → no ejecutado. Escucha y visto bueno de Emi → no ejecutado. Los «recursos de X» que Emi mencionó no estaban en la sesión ni en el repositorio → no ejecutado.
- Pendiente: que Emi comparta esas referencias; su opinión del corte nuevo; probar los planos en Anton (personal, MILLA, PAN), que no se han rendido.

## 2026-11-11 · Vox Studio 0.8.5: Castorena en corte suelto

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026, tras recibir los dos cortes del primer video semanal: «hazlos todos sueltos», para no producir varias versiones.
- Cambios: el espacio `castorena` pasa a un solo video por tema en corte suelto: `perfil.json` (tono de tú con ironía y remates, cierre «OPINA», voz a velocidad 1.15), `MARCA.md` y la skill; `sonido.py` ya no trata a Castorena como espacio sobrio (propone música `ironia`, efectos de chiste y remates); solo MILLA conserva esa restricción. La identidad visual no cambia.
- Archivos: `espacios/castorena/{perfil.json,MARCA.md,aprendizajes.md}`, `skills/vox-studio/scripts/{sonido.py,test_vox.py}`, `skills/vox-studio/SKILL.md` y este registro.
- Verificación: pruebas de vox-studio 45/45 → aprobado; guion del corte suelto existente sigue válido → aprobado. Ningún render nuevo → no ejecutado.
- Pendiente: comentarios de Emi sobre el corte suelto ya entregado (voz, música, efectos, chistes).

## 2026-11-11 · Vox Studio 0.8.4: tildes del titular en Gelasio y primer video semanal de Castorena

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: video semanal de DOF y SJF para Castorena, estilo Vox, en dos cortes (sobrio y suelto); aprobó los guiones («Está bien») antes de producir.
- Cambios: (1) En Gelasio la tilde de una palabra resaltada quedaba fuera del resaltador (papel sobre papel, casi invisible en «ÚNICA» y «HÁBIL») y la etiqueta tapaba la de «DÍA»: el resaltador sube 0.17 em en palabras acentuadas y el titular baja 44 px cuando hay etiqueta y tilde en la primera línea. (2) Producción privada `productions/castorena/pagos-digitales-{sobrio,suelto}` (Ley de Economía Digital para Pagos Digitales y Electrónicos, DOF 4/11/2026; flashes P./J. 220/2026 y A.I. 20/2025). (3) Ocho recortes catalogados en `biblioteca/castorena/` y siete lecciones nuevas.
- Archivos: `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/scripts/test_vox.py`, `skills/vox-studio/{SKILL.md,TECNICA.md}`, `biblioteca/`, `espacios/APRENDIZAJES.md`, `espacios/castorena/aprendizajes.md` y este registro.
- Verificación: pruebas de vox-studio 45/45 → aprobado; `tsc --noEmit` → aprobado. Texto de la ley cotejado con dof.gob.mx (arts. 13, 15, 16 y transitorio tercero) → aprobado; las dos tesis se tomaron del reporte de Emi, sin abrir el SJF → no ejecutado. Render final: sobrio 61.87 s y suelto 56.09 s, H.264 1080×1920, −14.09 LUFS, pico −2.0 dBTP; sobrio sin avisos; suelto con un aviso (0.5 % de contenido bajo la descripción de TikTok en la escena 08) → aprobado técnicamente con ese aviso. Hojas de fotogramas y recortes a tamaño real revisados por la IA → aprobado. Escucha y visto bueno de Emi → no ejecutado.
- Pendiente: comentarios de Emi sobre voz, música, efectos y chistes; medir Anton con el mismo método de anchos; corregir el aviso de la escena 08 del corte suelto si Emi publica en TikTok.

## 2026-11-11 · Vox Studio 0.8.3: acentos y márgenes del titular, llamado de cierre por video

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: primer video semanal de Castorena (DOF y SJF) en dos cortes; la auditoría de sus fotogramas encontró dos fallas de la plantilla.
- Cambios: (1) la entrada `mordidas` dejaba un recorte permanente que cortaba los acentos de las mayúsculas de la primera línea («DIA HABIL») y lo que saliera del ancho; ya no deja recorte al terminar. (2) El titular en Gelasio se mide con el ancho real de cada letra (tabla `ANCHOS`), no con una media: cuatro líneas de estos guiones medían entre 877 y 997 px para 870 px útiles. (3) `cierre` en el guion sustituye el llamado del espacio solo en ese video (hasta 16 letras).
- Archivos: `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/vox-studio/{SKILL.md,TECNICA.md}` y este registro.
- Verificación: pruebas de vox-studio 45/45 → aprobado; `tsc --noEmit` → aprobado; anchos medidos con fontTools sobre `gelasio-latin-700-normal.woff2` → aprobado. Render de los dos cortes con la corrección → en curso al registrar. Anton (personal y MILLA) no cambia: conserva la media por letra → no ejecutado ningún render de esos espacios.
- Pendiente: revisar la hoja de fotogramas del nuevo render; medir Anton con el mismo método.

## 2026-11-11 · Vox Studio 0.8.2: velocidad de la voz

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: primer video semanal de Castorena (DOF y SJF) en dos cortes. La voz salió lenta: 75 s para 142 palabras, con escenas de 9 a 12 s.
- Cambios: `voz_velocidad` en el guion o `voz.velocidad` en el perfil (0.7 a 1.2) se envía a ElevenLabs como `voice_settings.speed`; 1.0 no se envía ni altera la huella de las voces ya pagadas; la velocidad distinta de 1.0 entra en la huella, así que cambiarla vuelve a narrar.
- Archivos: `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/vox-studio/{SKILL.md,TECNICA.md}` y este registro.
- Verificación: pruebas de vox-studio 44/44 → aprobado. Narración real con velocidad 1.15 en los dos cortes: 61.9 s y 56.1 s (antes 75.1 s y 61.7 s) → aprobado. Render de los dos cortes → en curso al registrar; escucha de Emi → no ejecutado.
- Pendiente: entregar los dos MP4 a Emi, guardar sus comentarios como aprendizajes.

## 2026-11-10 · Vox Studio 0.8.1: paquete para claude.ai

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: tener la skill actualizada en Claude para solo llamarla.
- Cambios: `tools/empaquetar_vox.py` genera `dist/vox-studio.zip` (fuera de git) con la skill y una copia de `espacios/` dentro, enlaces ajustados y validado con `ia/check_skill.py`; `vox.py` usa los espacios empaquetados cuando existen; la skill explica qué hace en claude.ai y qué solo en Claude Code.
- Archivos: `tools/empaquetar_vox.py`, `skills/vox-studio/scripts/vox.py`, `skills/vox-studio/SKILL.md`, `.gitignore` y este registro.
- Verificación: paquete generado (92 KB, 34 archivos), descomprimido en limpio: `vox.py espacios` y `validar` del ejemplo → aprobado; pruebas de vox-studio 43/43 → aprobado. Subida a claude.ai → no ejecutado: solo puede hacerla Emi desde la configuración de la app.
- Pendiente: que Emi suba el .zip; fusionar este cambio a `main`.

## 2026-11-10 · Vox Studio 0.8.0: auditoría de imagen, titular en bloque, referencia técnica y control previo al commit

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: fusionar a `main`; comprobar el audio en cada video; castorena.com.mx es su despacho; «Perfecto» a que las pruebas de Vox Studio corran antes de cada commit; seguir mejorando y documentar todo de forma técnica.
- Cambios: (1) Reglas comunes, con confirmación expresa de Emi: `ia/politica.json` añade dos controles previos al commit (pruebas de Vox Studio al tocar `skills/vox-studio/` o `espacios/`, con comprobación de dependencias, y `check_skill` de su SKILL.md); `ia/REGLAS.md` regenerado. (2) `render` audita la imagen (`out/auditoria-video.json`): formato del archivo, contenido bajo la interfaz de TikTok y cuadros vacíos; al estrenarla detectó contenido bajo los botones de la derecha en tres escenas y se corrigió con un margen derecho de 900 px en esa franja. (3) Titular en bloque: cada línea llena el ancho útil. (4) Codificación con CRF 16, JPEG 95 y BT.709. (5) `skills/vox-studio/TECNICA.md` documenta formato, línea de tiempo, composición, cadena de audio, imágenes, auditorías y costos con los valores del código. (6) Castorena: despacho confirmado; regla de pedir la escucha de Emi en cada video.
- Archivos: `ia/politica.json`, `ia/REGLAS.md`, `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/{SKILL.md,TECNICA.md}`, `espacios/castorena/{perfil.json,MARCA.md,aprendizajes.md}`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: `python3 ia/test_guard.py` → aprobado; pruebas de vox-studio 43/43 → aprobado; pruebas de milla-video-studio → aprobado; `tsc --noEmit` → aprobado; demo 2 reconstruido sin gasto: 20.97 s, H.264 1080×1920 30 fps, −14.04 LUFS, pico −2.36 dBTP, 0 % de contenido en zonas tapadas, sin avisos de audio ni de imagen → aprobado técnicamente; hoja de fotogramas revisada por la IA → aprobado. Escucha de Emi del demo: «están bien» (10/11/2026).
- Pendiente: primer video real (Emi lo pedirá en una sesión nueva); nombre y @ de TikTok.

## 2026-11-10 · Vox Studio 0.7.0: cierre, ritmo, oficio del guion y guía de TikTok

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 10/11/2026: confirmar que las mejoras están documentadas y en la skill; auditar y mejorarla para que los videos queden bien.
- Cambios: cierre automático al terminar la voz (sello con el llamado del espacio y flecha a comentarios; 1.5 s de cola); pulso del recorte a media escena en escenas de más de 5 s; `validar` emite avisos de oficio no bloqueantes (gancho, escenas largas, duración total, escenas sin imagen, cifras sin fuente, keywords repetidos) y `armar` avisa de escenas de más de 7 s en la voz real; `render` entrega `out/hoja-tiktok.png` con las zonas que tapa la interfaz de TikTok. `cierre` añadido a los cuatro perfiles.
- Archivos: `skills/vox-studio/scripts/{vox.py,test_vox.py}`, `skills/vox-studio/plantilla/src/Vox.tsx`, `skills/vox-studio/{SKILL.md,CATALOGO.md}`, `espacios/*/perfil.json`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: se comprobó que `plantilla/src/` es idéntica a la del demo (todas las mejoras viven en la skill); pruebas 42/42 → aprobado; `tsc --noEmit` → aprobado; demo 2 reconstruido sin gasto: 20.97 s, −14.04 LUFS, pico −2.36 dBTP, sin avisos de audio; transiciones revisadas cuadro por cuadro y hoja con guía de TikTok revisada: todo el contenido dentro de la zona visible → aprobado. Escucha de Emi → no ejecutado.
- Pendiente: los mismos de la versión 0.6.0.

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
