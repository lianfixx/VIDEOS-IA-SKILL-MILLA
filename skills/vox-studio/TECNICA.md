# Vox Studio: referencia técnica

Cómo está hecho cada video, con los números reales del código. Si un valor cambia en `scripts/vox.py`, `scripts/sonido.py` o `plantilla/src/Vox.tsx`, se cambia aquí en el mismo commit.

## 1. Formato de salida

| Parámetro | Valor | Dónde |
|---|---|---|
| Lienzo | 1080×1920, 30 fps | `armar_video` |
| Video | H.264, `yuv420p`, CRF 16, BT.709; cuadros intermedios JPEG calidad 95 | `rendir` |
| Audio | AAC 192 kbps, 48 kHz, estéreo | `masterizar` |
| Duración | narración + 1.5 s de cola (`COLA`) | `armar_video` |
| Navegador de render | `/usr/local/bin/chrome-headless-shell` o `VOX_NAVEGADOR` | `rendir` |

El archivo sale con más calidad de la que TikTok conserva a propósito: la plataforma vuelve a comprimir y una fuente limpia aguanta mejor.

## 2. Línea de tiempo

1. La narración completa se envía en **una sola petición** a ElevenLabs (`/with-timestamps`): una toma continua suena mejor que escenas pegadas.
2. La alineación por carácter se agrupa en palabras (`palabras_desde_alineacion`).
3. Las palabras se reparten entre escenas **contando palabras** del guion, no caracteres: si el proveedor normaliza comillas o espacios, los límites no se corren. Si el total no coincide, se aborta.
4. Cada escena empieza 0.12 s antes de su primera palabra. `frame = round(segundos × 30)`. La suma de duraciones es exactamente el total.
5. Una escena de menos de 24 frames se rechaza; una de más de 7 s genera aviso.
6. `armar` reconstruye todo esto desde `estados/voz.json` sin volver a pagar la voz, mientras texto, voz y modelo no cambien (huella SHA-256).

## 3. Composición

**Zona segura de TikTok** (px): texto e imágenes dentro de x 90–960, y 230–1440. De y 760 hacia abajo el borde derecho se recorta a x 900 (`DER_BAJO`) porque ahí están los botones.

**Distribución vertical de una escena**

| Franja (y) | Contenido |
|---|---|
| 222–232 | barra de avance |
| 252–312 | rótulo (`kicker`) y fuente del dato |
| 326 → fin del titular | titular en bloque |
| fin del titular + 62 → 1265 (1150 con nota) | recorte, dato o foto, con semitono, cinta y rayos |
| 1188–1250 | nota manuscrita con flecha |
| 1320–1440 | subtítulos; al terminar la voz, el cierre |

**Titular en bloque.** El texto se parte en líneas de hasta 11 caracteres (máximo 3). Cada línea crece hasta llenar 870 px: `tamaño = 870 / (letras × ancho_medio)`, con `ancho_medio` 0.47 para Anton y 0.64 para Gelasio, tope por línea y sin que una línea supere 1.7 veces a la menor. Una palabra de hasta 16 letras siempre cabe. El resaltado es una caja del color de acento con la palabra en color papel; si la palabra lleva mayúscula con tilde o Ñ, la caja sube 0.13 del tamaño de letra para cubrirla, y cada línea se pinta encima de la siguiente.

**Cámara.** Las escenas viven en un lienzo continuo, separadas 2400 px en vertical y ±620 px en horizontal, con giros de −3°, 2.5°, −2° y 3.5°. En `viaje` la cámara se mueve con un resorte (amortiguación 26, rigidez 140), sale 9 frames antes del corte y retrocede un 14 % a mitad del trayecto. Dentro de cada escena hay una deriva de zoom de 1.00 a 1.05 que se funde con la de la escena anterior para que no haya salto.

**Transiciones.** `viaje` (cámara), `barrido` (dos paneles inclinados cruzan en 16 frames y la cámara cambia tapada) y `rasgado` (panel con borde dentado baja en 16 frames). Lo automático evita repetir la anterior y la que el guion fije para la siguiente.

**Entradas.** `sello`, `desliza-izq`, `desliza-der`, `cae`, `desdobla`, `mordidas`; los recortes, además, `sube`. Nunca por opacidad. Resortes por clase de objeto: titular (amortiguación 26, rigidez 230, masa 0.8: cae firme), recorte (13, 150, 1: se pasa un poco y asienta), rótulo (200, 300, 0.6: seco). Un recorte entra de lado, desde abajo sin rebote hacia arriba, o como sello desde 1.25×, para no tapar el titular mientras llega.

**Movimiento continuo.** Nada vibra: el recorte flota con `sin(f/24) × 5 px` y gira ±0.7°; el grano del papel cambia cada 15 frames a 13 % de opacidad. Las escenas de más de 150 frames reciben un pulso de escala del 7 % a la mitad.

**Subtítulos.** Grupos de hasta 3 palabras o 18 caracteres (15 en serif), cortados en pausas de más de 0.35 s y en signos de cierre. La palabra dicha se marca con el acento; las que faltan van atenuadas. Tiempos: los reales de la voz, adelantados 0.04 s.

**Cierre.** A `finVoz + 0.15 s` cae un sello con el llamado del espacio y una flecha hacia el botón de comentarios.

## 4. Cadena de audio

| Paso | Valor | Función |
|---|---|---|
| Voz | normalizada a −16 LUFS en dos pasadas | `normalizar` |
| Música | compuesta a −20 dBFS RMS; ganancia calculada para quedar 17 LU bajo la voz | `_escribir_video` |
| Envolvente de música | ×2.6 en el primer medio segundo, nivel base durante la voz, ×3 al terminar | `Vox.tsx` |
| Efectos y remates | todos a −20 dBFS RMS, ganancia 0.8: unos 6 dB bajo la voz | `sintetizar_efectos` |
| Transiciones | papel, deslizar, golpe, pop, rasgar a ganancia 0.3 | `Vox.tsx` |
| Master | ganancia fija hasta −14 LUFS y limitador de picos | `masterizar` |

La música se genera con una semilla derivada del título y la narración: decide tonalidad (±3 semitonos), tempo (±6 %, y después `ajustar_bpm` busca, en pasos de 0.5 y dentro de ±8 %, el que deja los cambios de escena más cerca de un pulso), progresión (5 por modo) y patrón del arpegio; el arreglo baja en escenas alternas y sube al final. Los efectos se afinan a esa tonalidad.

## 5. Imágenes

- Prompt = sujeto + estilo del espacio + fondo de croma + «sin texto, logos ni marcas de agua». Solo el sujeto; sin mesas ni suelos.
- Recorte (`recortar_croma`): mide el color del fondo en el marco de la imagen, exige que al menos el 90 % del marco sea uniforme, elimina lo conectado al borde y los huecos casi idénticos al fondo, suaviza una franja de 3 px y le quita el derrame de color.
- El estado de cada tarea guarda la huella de prompt, aspecto y modelo: no se reutiliza para otra imagen ni se reenvía tras un fallo.
- Descargas solo desde los dominios de resultado de Kie; fotos reales con tope de 15 MB y verificación de que son imágenes.

## 5 bis. 3D, sombreadores y Blender

- **Horno.** Las escenas con `objeto3d` o `tratamiento` se rinden aparte en la composición `Horno` (720 px, fondo transparente, `--gl=swangle`) y entran al video como imágenes; el render principal no usa WebGL. `plan_horno` decide qué hornear y `hornear` lo guarda en `public/horno/<id>-<firma>` (la firma cubre el pedido, los colores, el tramo de cuadros y el código de `Tres.tsx` y `Root.tsx`); lo que ya está horneado no se repite. Todo se arma en `out/_horno*`, se comprueba (número de cuadros, que no esté vacío) y se mueve de una vez; una secuencia completa lleva la marca `.listo`. Lo que ya no pide ninguna escena se borra. `src/data/_render.json` es el derivado que se rinde; `video.json` conserva el pedido.
- **Secuencias.** Un objeto horneado dura `dur + 16` cuadros y no se repite en bucle; en la primera escena, que el compositor adelanta 60 cuadros, se hornea ese mismo tramo (`inicio` 52). Un giro de Blender sí va en bucle. El mismo recorte al contenido se aplica a todos los cuadros de una secuencia.
- **Materiales.** Compositor: `meshToonMaterial` sin mapeo de tonos, luz ambiente 0.35 + directa π − 0.35 (la cara iluminada da el color exacto del espacio; la sombra, el 73 % en lineal) y contorno por casco invertido en tinta. Sombreador: luminancia elevada a 0.55 antes de tramar; semitono a 45° con celda de 9 px; duotono tinta → acento → papel.
- **Blender.** Módulo `bpy` 5.3 con Cycles en CPU, vista «Standard» para que el color de marca salga exacto. `plano`: emisión + sombra de una banda y contorno Freestyle. `real`: material físico y tres luces de área. Cámara de 70 mm a la distancia que encierra el objeto. El giro fija el ángulo cuadro por cuadro (sin fotogramas clave) y cuelga del eje la raíz de cada pieza.
- **Límites del validador.** Una escena con 3D por video (`MAX_3D`); cada objeto solo en las funciones de `LUGAR_3D`; ninguno en `opinion` ni `cierre`; un solo tratamiento por video. `excepcion_3d` (el pedido de Emi, con fecha) levanta los dos primeros. `comparar` rinde el cuadro a tres cuartos de la escena con el recurso y con su `alternativa_plana`.
- **ComfyUI.** Cliente HTTP (`/prompt`, `/history`, `/view`) contra `COMFY_URL` (https, o http solo en la misma máquina); nunca se llama sin esa variable y lo que baja se verifica como imagen antes de guardarse.

## 6. Auditorías automáticas de `render`

| Informe | Qué mide | Avisa cuando |
|---|---|---|
| `out/auditoria-audio.json` | voz, música respecto a la voz, cada efecto respecto a la voz, sonoridad y pico finales, ganancia del master, rango dinámico, silencios | música a menos de 12 o más de 26 LU; efecto por encima de la voz o 16 dB por debajo; final fuera de −15 a −13 LUFS; pico sobre −1.5 dBTP; master de más de 4 dB; rango dinámico menor de 1.5 LU (audio plano); silencio de más de 1.2 s |
| `out/auditoria-video.json` | códec, tamaño, fps, formato de pixel, audio, duración; tinta en las zonas que tapa TikTok y en la zona útil, a tres cuartos de cada escena (la última, 6 cuadros antes del final, con el sello de cierre ya asentado) | formato distinto del esperado; más de 0.4 % de una zona tapada con contenido; menos de 6 % de tinta en la zona útil; primer cuadro casi vacío |
| `out/hoja.png`, `out/hoja-tiktok.png`, `out/portada.png` | para revisar con los ojos | — |
| `out/hoja-transiciones.png`, `out/hoja-telefono.png` (comando `revisar`) | cada corte en −6, −3, 0, +3, +6 y +12 cuadros; el video a 150 px de ancho | — |
| `out/revision.json` | segundos revisados, hallazgos con su arreglo, pendientes y quién revisó, atado a la huella del render | `cierre` se niega si falta, si es de otro render o si no está firmado |
| `out/manifiesto.json` | huellas de guion, voz, música e imágenes, versión de la skill y ajustes de render | — |

«Tinta» es todo pixel a más de 90 unidades RGB del color del papel; el grano y la viñeta no llegan a ese umbral.

## 7. Lo que ninguna auditoría automática decide

Si la voz suena natural, si la música gusta, si el chiste funciona y si el ritmo se siente bien. Eso se comprueba con Emi en cada video, con el MP4 delante.

## 8. Costos medidos (10/11/2026)

| Recurso | Costo |
|---|---|
| Imagen `nano-banana-2-lite` | 4 créditos de Kie |
| Imagen `seedream/5-lite-text-to-image` | 5.5 créditos de Kie |
| Búsqueda de fotos en Apify | ~0.06 USD (0.005 de arranque + 0.05 por página + 0.0023 por foto) |
| Voz | los caracteres que cobre ElevenLabs por la narración; se informa lo que su API reporta |
| Música, efectos, portada, render, 3D del compositor, sombreadores, Blender | sin costo de proveedor (tiempo de CPU) |
