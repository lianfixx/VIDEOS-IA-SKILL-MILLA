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
6. `armar` reconstruye todo esto desde `estados/voz.json` sin volver a pagar la voz, mientras texto, voz, modelo y velocidad no cambien (huella SHA-256).
7. Planos: cada plano del guion entra 4 frames antes del inicio real de su palabra ancla (`buscar_ancla`: primera coincidencia sin signos ni mayúsculas, posterior al plano anterior), con al menos 18 frames entre planos; `dur` llega hasta el siguiente plano o el fin de la escena. Los `items` de una lista usan su propia ancla o entran cada 9 frames. Al entrar un plano, el anterior sale de cuadro en 7 frames (desplazamiento, nunca opacidad). El primer plano usa el reloj adelantado de la escena para llegar ya compuesto.
8. Velocidad de la voz: `voz_velocidad` del guion o `voz.velocidad` del perfil, de 0.7 a 1.2 (`voice_settings.speed` de ElevenLabs); 1.0 no se envía y no altera la huella de las voces ya pagadas.

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

**Titular en bloque.** El texto se parte en líneas de hasta 11 caracteres (máximo 3). Cada línea crece hasta llenar 870 px: `tamaño = 870 / (letras × ancho_medio)`, con `ancho_medio` 0.47 para Anton y 0.64 para Gelasio, tope por línea y sin que una línea supere 1.7 veces a la menor. Una palabra de hasta 16 letras siempre cabe. En Gelasio el ancho de la línea se calcula con el ancho real de cada mayúscula (tabla `ANCHOS`, leída de la fuente), más 0.22 em por espacio y 0.16 em del resaltador: con la media por letra, líneas como «DOMINGO NO» o «ÚNICA FORMA» medían hasta 997 px y se salían del margen. La entrada `mordidas` no deja recorte al terminar: antes cortaba los acentos de las mayúsculas de la primera línea. En Gelasio la tilde de una mayúscula sube unos 0.3 em: el resaltador de una palabra acentuada empieza 0.17 em más arriba para cubrirla (si no, queda en color papel sobre papel) y, si la escena lleva etiqueta (`kicker`) y la primera línea tiene tilde, el titular baja 44 px para que la etiqueta no la tape.

**Cámara.** Las escenas viven en un lienzo continuo, separadas 2400 px en vertical y ±620 px en horizontal, con giros de −3°, 2.5°, −2° y 3.5°. En `viaje` la cámara se mueve con un resorte (amortiguación 26, rigidez 140), sale 9 frames antes del corte y retrocede un 14 % a mitad del trayecto. Dentro de cada escena hay una deriva de zoom de 1.00 a 1.05 que se funde con la de la escena anterior para que no haya salto.

**Transiciones.** `viaje` (cámara), `barrido` (dos paneles inclinados cruzan en 16 frames y la cámara cambia tapada) y `rasgado` (panel con borde dentado baja en 16 frames). Lo automático evita repetir la anterior y la que el guion fije para la siguiente.

**Entradas.** `sello`, `desliza-izq`, `desliza-der`, `cae`, `desdobla`, `mordidas`. Nunca por opacidad. Resorte general: amortiguación 18, rigidez 170, masa 0.8.

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

La música se genera con una semilla derivada del título y la narración: decide tonalidad (±3 semitonos), tempo (±6 %), progresión (5 por modo) y patrón del arpegio; el arreglo baja en escenas alternas y sube al final. Los efectos se afinan a esa tonalidad.

## 5. Imágenes

- Prompt = sujeto + estilo del espacio + fondo de croma + «sin texto, logos ni marcas de agua». Solo el sujeto; sin mesas ni suelos.
- Recorte (`recortar_croma`): mide el color del fondo en el marco de la imagen, exige que al menos el 90 % del marco sea uniforme, elimina lo conectado al borde y los huecos casi idénticos al fondo, suaviza una franja de 3 px y le quita el derrame de color.
- El estado de cada tarea guarda la huella de prompt, aspecto y modelo: no se reutiliza para otra imagen ni se reenvía tras un fallo.
- Descargas solo desde los dominios de resultado de Kie; fotos reales con tope de 15 MB y verificación de que son imágenes.

## 6. Auditorías automáticas de `render`

| Informe | Qué mide | Avisa cuando |
|---|---|---|
| `out/auditoria-audio.json` | voz, música respecto a la voz, cada efecto respecto a la voz, sonoridad y pico finales, ganancia del master, silencios | música a menos de 12 o más de 26 LU; efecto por encima de la voz o 16 dB por debajo; final fuera de −15 a −13 LUFS; pico sobre −1.5 dBTP; master de más de 4 dB; silencio de más de 1.2 s |
| `out/auditoria-video.json` | códec, tamaño, fps, formato de pixel, audio, duración; tinta en las zonas que tapa TikTok y en la zona útil, a tres cuartos de cada escena | formato distinto del esperado; más de 0.4 % de una zona tapada con contenido; menos de 6 % de tinta en la zona útil; primer cuadro casi vacío |
| `out/hoja.png`, `out/hoja-tiktok.png`, `out/portada.png` | para revisar con los ojos | — |

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
| Música, efectos, portada, render | sin costo de proveedor |
