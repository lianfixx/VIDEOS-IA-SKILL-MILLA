# Cambios

## 2026-11-11 · Espacio pan: voz nueva (Diego, candidata) y auditoría de sincronía de ¡ACCIÓNate!

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: «cambia la voz y audita que esté todo perfecto sincronizado».
- Cambios: `espacios/pan/perfil.json` pasa de Daniel Virgen (hyped) a Diego - Cálida y Conversacional (`4rOzDieCbHQQyo9tzqZv`, mexicano, joven) con `speed` 1.07, `stability` 0.45 y `style` 0.2; la eligió quien produce entre las voces mexicanas de la cuenta porque Emi pidió una natural y conversacional. Queda como candidata hasta que Emi la escuche. La producción privada ¡ACCIÓNate! se volvió a narrar y a sincronizar con `sync.py` (cada golpe visual atado a su palabra).
- Archivos: `espacios/pan/{perfil.json,aprendizajes.md}`, `espacios/APRENDIZAJES-PIZARRA.md` y este registro.
- Verificación: voz en el MP4 desfasada 3 ms de la toma → aprobado; subtítulos entre 30 ms después y 90 ms antes que la voz en 16 inicios de frase → aprobado; 24 golpes visuales comprobados en cuadros del MP4 antes y después de su palabra → aprobado; `render` → sin avisos (−14.31 LUFS, pico −1.52 dBTP, 47.53 s); QR leído en tres cuadros → aprobado; pruebas de vox-studio y pizarra-studio → aprobado. Cómo suena la voz → no verificable por una IA.
- Pendiente: que Emi escuche a Diego y diga si se queda como voz del espacio; el espacio personal sigue con Daniel Virgen.

## 2026-11-11 · Vox Studio 0.9.1 y Pizarra Studio 0.3.1: ritmo de la voz ajustable por espacio

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026, tras escuchar ¡ACCIÓNate!: auditar con todo lo aprendido en el otro estilo y hacer la voz más natural, humana, fluida y motivadora, porque hablaba rapidísimo.
- Motivo y evidencia: la entrega de la voz estaba fija en el código (sin ritmo); la primera toma midió 18.2 letras por segundo hablando.
- Cambios: `vox.py` lee `voz.ajustes` del perfil (`speed` 0.7–1.2, `stability`, `style`, `similarity_boost`, `use_speaker_boost`), rechaza claves desconocidas y mete los ajustes propios en la huella de la narración (`firma_voz`), de modo que cambiarlos vuelve a narrar y los perfiles sin ajustes conservan su caché. `pizarra.py` usa la misma huella. Perfil `pan`: `speed` 0.84, `stability` 0.45, `style` 0.15 (candidato). Producción privada ¡ACCIÓNate! rehecha con guion más hablado, respiros entre ideas y animación atada a las palabras de la voz nueva; escena del título en dorado para no caer en el «azul pleno con mayúsculas blancas» que `MARCA.md` pide evitar.
- Archivos: `skills/vox-studio/{SKILL.md,TECNICA.md,scripts/vox.py,scripts/test_vox.py}`, `skills/pizarra-studio/{SKILL.md,scripts/pizarra.py}`, `espacios/pan/{perfil.json,aprendizajes.md}`, `espacios/APRENDIZAJES-PIZARRA.md` y este registro.
- Verificación: pruebas de vox-studio 52/52 y de pizarra-studio 21/21 → aprobado; voz nueva real: 14.8 letras/s en la toma (antes 18.2), 47 s con los respiros → medido; `render` → sin avisos (−14.43 LUFS, pico −2.21 dBTP, 48.93 s); `revisar` → 6 hallazgos corregidos; QR leído en tres cuadros → aprobado. Cómo suena la voz → no verificable por una IA.
- Pendiente: que Emi escuche la voz; si aún la siente acelerada, el siguiente paso es elegir otra voz para el espacio (decisión suya). Los ajustes de `pan` quedan como candidatos.

## 2026-11-11 · ¡ACCIÓNate! (pan): segunda versión con acabado motion y dos aprendizajes

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026, tras la primera entrega: «recuerda hacerlo estilo motion también, muy profesional».
- Cambios: la producción privada `productions/pan/accionate-14nov` se rehízo con el mismo guion, voz y datos aprobados: títulos cinéticos, escenas en azul y marino, tarjetas, cámara, contador del apoyo y transiciones de barras y círculo; la primera versión se conserva junto a ella. Al repositorio solo entran dos aprendizajes.
- Archivos: `espacios/APRENDIZAJES-PIZARRA.md`, `espacios/pan/aprendizajes.md` y este registro.
- Verificación: `qa` → revisado; `render` → sin avisos (−14.38 LUFS, pico −2.24 dBTP, 38.73 s); `revisar` → 5 hallazgos corregidos; QR leído en cuatro cuadros del cierre → aprobado; `cierre` → sin gasto nuevo (voz reutilizada).
- Pendiente: que Emi vea y escuche; el video no está aprobado.

## 2026-11-11 · Primer video real de Pizarra Studio (¡ACCIÓNate!, espacio pan): aprendizajes

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: video pizarra del evento ¡ACCIÓNate! (sábado 14 de noviembre, El Tenayo) para el grupo de WhatsApp, la Lic. Rafaela y la Lic. Laura Luja, y también TikTok y X.
- Cambios: entrevista completa (17 respuestas), resumen y storyboard aprobados por Emi; producción privada en `productions/pan/accionate-14nov` (fuera de git): estilo minimal, 9:16, 38.7 s, voz del espacio, música «energía» y efectos por código, QR nuevo al formulario del flyer. Al repositorio solo entran tres aprendizajes.
- Archivos: `espacios/APRENDIZAJES-PIZARRA.md`, `espacios/pan/aprendizajes.md` y este registro.
- Verificación: `qa` (32 cuadros) → revisado; `render` → sin avisos (−14.37 LUFS, pico −2.31 dBTP); `revisar` → 5 hallazgos corregidos y anotados en `out/revision.json`; el QR del cuadro final se lee y lleva al formulario → aprobado; `cierre` → 675 caracteres de ElevenLabs, Kie sin gasto. Formulario de registro en sí → no abierto.
- Pendiente: que Emi vea y escuche el video y dé su opinión; el video no está aprobado.

## 2026-11-11 · Vox Studio 0.9.0 y Pizarra Studio 0.3.0: mejoras tomadas de cuatro referencias de X

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: leer y analizar cuatro publicaciones de X y, si algo mejora las skills de video, implementarlo todo, auditar a fondo y corregir.
- Cambios: análisis completo en `docs/REFERENCIAS-EXTERNAS.md` (qué se adoptó, qué ya estaba y qué se descartó con motivo). Vox Studio: `funcion` obligatoria por escena (primera gancho, última cierre, al menos una opinión); `ganchos_propuestos` y `gancho_elegido`; una cifra sin `fuente` en su escena es error; el tempo de la música se ajusta ±8 % a los cambios de escena; aviso de audio plano; resortes distintos para titular, recorte y rótulo; los recortes ya no cruzan el titular al entrar (`sube`, sello desde 1.25×); línea de fuente legible; comandos `revisar` (hojas de transiciones y de tamaño teléfono + `out/revision.json`) y `referencia`; `cierre` exige la revisión del render actual; `out/manifiesto.json`. Pizarra Studio: `revisar`, la misma exigencia en `cierre`, manifiesto, función por escena en el storyboard y tempo ajustado.
- Archivos: `docs/REFERENCIAS-EXTERNAS.md`, `skills/vox-studio/{SKILL.md,CATALOGO.md,TECNICA.md,plantilla/guion.ejemplo.json,plantilla/src/Vox.tsx,scripts/vox.py,scripts/sonido.py,scripts/test_vox.py}`, `skills/pizarra-studio/{SKILL.md,scripts/pizarra.py,scripts/test_pizarra.py}`, `espacios/APRENDIZAJES.md` y este registro.
- Verificación: pruebas de vox-studio 49/49 y de pizarra-studio 21/21 → aprobado; `tsc --noEmit` → aprobado; demo 2 reconstruido sin gasto y rendido tres veces: sin avisos de audio ni de imagen; la hoja de transiciones nueva mostró dos fallas reales (recorte sobre el titular, fuente ilegible en teléfono) → corregidas y comprobadas en el render siguiente; `cierre` sin revisión → rechazado, con revisión firmada → aprobado; `revisar` en una producción de pizarra → aprobado. Los videos adjuntos a las publicaciones no se vieron; el repositorio de «475 videos» no se pudo verificar (el enlace es un Discord).
- Pendiente: formatos 1:1 y 16:9 en Vox Studio (propuesto, sin hacer); que Emi vea y escuche; fusionar a `main`.

## 2026-11-11 · Vox Studio 0.8.3 y Pizarra Studio 0.2.1: qué hacer si se llaman donde no se puede producir

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: actualizar el paquete de la skill para la app y añadir instrucciones por si la ejecuta mal o solo en Claude (sin terminal).
- Cambios: Vox Studio sustituye «Dónde funciona» por una tabla de situaciones (con todo, sin llaves, sin repositorio, app sin terminal, pedido de pizarra) con qué hacer y qué decirle a Emi, reglas de honestidad y un paquete de traspaso para continuar en Claude Code. Pizarra Studio añade la misma regla. El paquete para la app incluye ahora la guía de entrevista de pizarra (`pizarra/PIZARRA.md` y su ejemplo de brief).
- Archivos: `skills/vox-studio/SKILL.md`, `skills/pizarra-studio/SKILL.md`, `tools/empaquetar_vox.py` y este registro.
- Verificación: `ia/check_skill.py` de ambas skills → aprobado; paquete generado y descomprimido en limpio: `vox.py espacios`, `validar` del ejemplo y enlaces internos existentes → aprobado; pruebas de vox-studio y pizarra-studio → aprobado. Subida a la app → no ejecutado (solo puede hacerla Emi).
- Pendiente: que Emi sustituya la copia de la app; fusionar a `main`.

## 2026-11-11 · Pizarra Studio 0.2.0: revisión independiente (15 fallas) corregida

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: fusionar a `main` con la skill terminada antes del primer video.
- Cambios: `pizarra.py` reescrito con las 15 correcciones de una revisión independiente: (1) `voz --execute` exige entrevista aprobada y que Emi haya pedido la voz del espacio antes de gastar; (2) medición, cuadros de prueba y render usan la misma línea de tiempo (modo B con voz); (3) una cama sin sonido ya no satura la mezcla y la respuesta «sin efectos» apaga los efectos; (4) formato y duración del brief se interpretan antes de rendir y aceptan «horizontal 16:9», «45 a 60», «1:00», «1 minuto»; (5) aviso si la voz se corta o el video sobra; (6) en estilos la marca lleva estilo, sin mascota ni persona y subtítulos con tiempos reales; (7) respuestas que no son texto no cuentan; (8) `proyecto` se arma aparte, se renombra al final y solo acepta `productions/<espacio>/`; (9) el motor vive en `~/.cache/pizarra-studio/motor`, se rechaza si tiene archivos modificados y cada producción anota su commit; (10) se borran entregables anteriores al empezar y los temporales siempre; (11) la medición no ensucia `stills/`; (12) el navegador se busca en más rutas y solo se devuelve si existe; (13) import con mensaje claro si falta Vox Studio; (14) ejemplo y textos alineados con «sin personaje», `musica` antes de `qa`; (15) límites y tiempo máximo en `qa`, primera escena en 0, ganancia final calculada desde una sola fuente.
- Archivos: `skills/pizarra-studio/{SKILL.md,brief.ejemplo.json,scripts/pizarra.py,scripts/test_pizarra.py}`, `espacios/{ESTILOS.md,APRENDIZAJES-PIZARRA.md}`, `docs/VALIDACION.md` y este registro.
- Verificación: pruebas de pizarra-studio 19/19 → aprobado; flujo real completo con el motor reinstalado en su carpeta nueva (proyecto, voz desde caché sin gasto, música, cuadros, render de prueba: 22.8 s, −14.36 LUFS, pico −2.23 dBTP) → aprobado técnicamente, con el aviso esperado de que la escena de prueba no sigue a la voz; `render` sin entrevista → rechazado, como debe.
- Pendiente: primer video real; modo historia y render horizontal completo sin probar.

## 2026-11-11 · Pizarra Studio 0.1.2: los cinco estilos probados y duración medida en ambos motores

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: fusionar a `main`; dejar la skill terminada antes del primer video.
- Cambios: `musica` sin `--segundos` no sabía leer la duración en el motor de estilos (lo imprime distinto) y fallaba: `duracion_del_video` lee ambos formatos y no ensucia `stills/`; prueba añadida.
- Archivos: `skills/pizarra-studio/scripts/{pizarra.py,test_pizarra.py}`, `docs/VALIDACION.md` y este registro.
- Verificación: pruebas de pizarra-studio 14/14 → aprobado; cuadros reales de acuarela, acuarela viva, cuaderno (vertical) y minimal (horizontal) con la marca de Castorena, revisados como imagen → aprobado; render técnico completo del motor de estilos: 43.0 s, 1080×1920, −14.11 LUFS, pico −2.32 dBTP, sin avisos → aprobado técnicamente.
- Pendiente: integrar la revisión independiente del código (en curso); modo historia y render horizontal completo sin probar; primer video real.

## 2026-11-11 · Pizarra Studio 0.1.1: preferencias permanentes de Emi y entorno

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026, respuestas a las preguntas de arranque: estilo «decidir en cada video», personaje «sin personaje», voz «la del espacio», música «preguntarme en cada video».
- Cambios: `espacios/PREFERENCIAS-PIZARRA.json` guarda sus respuestas permanentes y `proyecto` las escribe en el brief para no repetirlas; el estilo y la música se preguntan siempre. La skill cambia la regla del personaje (la vida la dan la mano, los objetos y la cámara). `espacios/ESTILOS.md` pasa de «punto de partida» a «sugerencia». Entorno `videos-ia-skill-milla`: el script de configuración instala el motor de pizarra con `pizarra.py instalar` (aprobado por Emi en la tarjeta).
- Archivos: `espacios/{PREFERENCIAS-PIZARRA.json,ESTILOS.md,APRENDIZAJES-PIZARRA.md}`, `skills/pizarra-studio/{SKILL.md,scripts/pizarra.py,scripts/test_pizarra.py}` y este registro.
- Verificación: pruebas de pizarra-studio 13/13 → aprobado; `pizarra.py instalar` ejecutado desde la carpeta donde arranca el script del entorno → aprobado; el script completo en un arranque nuevo → no ejecutado.
- Pendiente: primer video real; fusionar a `main`.

## 2026-11-11 · Pizarra Studio 0.1.0 (candidata): videos dibujados a mano con las mismas reglas

- Agente: Claude Code (sesión en la nube)
- Solicitud: Emi, 11/11/2026: analizar el video «Contraté a Claude como animador» y el material de Drive; cuando pida estilo pizarra, producirlo de esa forma, en un apartado propio, con los mismos espacios, la misma llave, entrevista completa siempre, todo documentado en GitHub y utilizable por cualquier IA; «tienes mi permiso para todo».
- Cambios: (1) Nueva skill `skills/pizarra-studio/` con `scripts/pizarra.py`: instala el motor público `santmun/video-pizarra` fijado al commit `dc6adc4` (no se copia su código: el repositorio no tiene licencia), crea producciones por espacio con la marca traducida al motor, controla la entrevista de 17 preguntas y las dos aprobaciones de Emi, narra con la voz del espacio y entrega tiempos por escena, compone música por código con rejilla de beats exacta, genera cuadros de prueba con guía de TikTok, rinde, mezcla (voz al frente, efectos con picos limitados), lleva a −14 LUFS midiendo y audita. Reutiliza voz, saldos, niveles, espacios y aprendizajes de Vox Studio. (2) `espacios/ESTILOS.md` (qué estilo proponer) y `espacios/APRENDIZAJES-PIZARRA.md`. (3) Vox Studio 0.8.2 remite a Pizarra Studio cuando el pedido es de pizarra. (4) Reglas comunes, con permiso expreso de Emi en este encargo: `ia/politica.json` añade dos controles previos al commit (pruebas y `check_skill` de Pizarra Studio); `ia/REGLAS.md` regenerado. (5) Entorno en la nube: se propone añadir la instalación del motor al script de configuración.
- Archivos: `skills/pizarra-studio/**`, puentes en `.claude/skills/` y `.agents/skills/`, `espacios/{ESTILOS.md,APRENDIZAJES-PIZARRA.md,README.md}`, `skills/vox-studio/SKILL.md`, `tools/empaquetar_vox.py`, `ia/politica.json`, `ia/REGLAS.md`, `README.md`, `docs/VALIDACION.md` y este registro.
- Verificación: pruebas de pizarra-studio 12/12 → aprobado; pruebas de vox-studio 43/43 y `ia/test_guard.py` → aprobado; prueba técnica real en pizarrón con la marca del espacio personal (voz de 212 caracteres, música por código, efectos): 22.8 s, 1080×1920, −14.39 LUFS, pico −2.31 dBTP, sin avisos → aprobado técnicamente; cuadros del motor de estilos con la marca de Castorena → aprobado. Fuente del análisis: transcripción y descripción del video de YouTube y texto del PDF de Drive (un manual de 19 páginas de la misma skill); la imagen del video no se vio.
- Pendiente: respuestas de Emi sobre estilo y personaje por espacio; primer video real con entrevista y storyboard aprobados; probar acuarela, acuarela viva, cuaderno, modo historia y formato horizontal; fusionar a `main`.

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
