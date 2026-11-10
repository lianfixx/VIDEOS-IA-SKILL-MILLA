# Aprendizajes de todos los videos

Se lee antes de cada guion y se amplía después de cada video (`vox.py aprender "..."`). Cada línea: fecha, qué pasó o qué dijo Emi, y la regla que queda. No se borran lecciones; si una cambia, se añade la nueva debajo.

- 2026-11-10 · Emi (demo 1): «las cosas tiemblan mucho». Regla: nada vibra; solo flotación lenta y continua, grano de papel discreto y rebotes amortiguados.
- 2026-11-10 · Emi (demo 1): quiere imágenes más naturales. Regla: estilo por defecto `ilustracion` (editorial pintada, proporciones reales) o `foto`; el cartoon de contorno grueso solo si él lo pide.
- 2026-11-10 · Emi (demo 1): pide más efectos y transiciones. Regla: alternar viaje de cámara, barrido de color y papel rasgado; nunca la misma transición dos veces seguidas.
- 2026-11-10 · Auditoría (demo 1): el audio salió a −27 LUFS. Regla: masterizar siempre a −14 LUFS antes de entregar.
- 2026-11-10 · Auditoría (demo 1): recortes pequeños y nota manuscrita encimada. Regla: revisar una hoja de fotogramas de cada escena antes de entregar.
- 2026-11-10 · Emi: en cada entrega, tabla de lo gastado y lo que queda en Kie, ElevenLabs y Apify (`vox.py cierre`).
- 2026-11-10 · Auditoría (demo 2): un prompt que menciona una superficie («sobre un escritorio») rompe el fondo plano y el recorte lo rechaza. Regla: describir solo el sujeto, «floating, product shot», sin mesas ni suelos.
- 2026-11-10 · Auditoría (demo 2): los huecos encerrados (perforaciones, asas) quedaban verdes. Regla: el recorte ya los quita; para sujetos verdes usar `--croma magenta`.
- 2026-11-10 · Auditoría (demo 2): la normalización de una pasada dejó −12.7 LUFS y pico −0.4. Regla: master en dos pasadas (ya integrado en `render`); comprobar que diga cerca de −14 LUFS y pico ≤ −1.5 dBTP.
- 2026-11-10 · Revisión de código: 15 fallas corregidas (salto de zoom, textos que desbordan, re-narración pagada, estado de imagen reutilizado). Regla: tras cada cambio de la plantilla, pruebas + render + hoja de fotogramas.
- 2026-11-10 · Emi: en cada video analizar de qué va y proponer música, efectos y remates tipo meme, hechos con código. Regla: `vox.py sonido` + criterio propio; el guion no pasa sin `musica.animo` y al menos un `sonido`.
- 2026-11-10 · Emi aprobó: subtítulos de Castorena en serif y portada automática por video (`out/portada.png`).
- 2026-11-10 · Emi: música, efectos y demás se generan nuevos y acordes a cada video; lo ya hecho se documenta para reciclar solo si de verdad queda. Regla: sonido con semilla propia por video; imágenes en `biblioteca/` y reciclaje únicamente tras mirarlas; piezas de código en `CATALOGO.md`.
- 2026-11-10 · Emi autorizó usar Apify para fotos reales. Regla: pocas candidatas, tope de gasto, fuente y licencia comprobadas antes de bajar.
- 2026-11-10 · Auditoría (Apify): un tope de 0.05 USD abortó la búsqueda y cobró igual. Regla: cada búsqueda cuesta ~0.06 USD; la herramienta ya exige un tope suficiente. Con 5 USD al mes alcanzan unas 80 búsquedas.
- 2026-11-10 · Auditoría (Apify): la primera foto real bajada es CC BY-SA 3.0 (Wikimedia Commons). Regla: comprobar la ficha siempre; BY-SA exige crédito y compartir igual, así que se avisa a Emi antes de usarla en un video.
