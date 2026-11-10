---
name: vox-studio
description: "Producir shorts verticales 9:16 estilo documental-collage (tipo Vox) con Remotion para los espacios de Emi (personal, MILLA, Castorena, PAN/Acción Juvenil), cada uno por separado. Usar al pedir un short, video explicativo o video estilo Vox, al cambiar la marca de un espacio o al auditar y corregir animaciones, recortes, transiciones o subtítulos. Pregunta siempre la opinión de Emi antes del guion, aprende de cada video e informa los saldos al entregar."
metadata:
  version: "0.4.0"
  release_date: "2026-11-10"
  language: "es-MX"
---

# Vox Studio

Compositor propio, **candidato**: rinde y está probado técnicamente, pero ningún video suyo tiene todavía aprobación estética de Emi. No sustituye a [MILLA Video Studio](../milla-video-studio/SKILL.md); para contenido jurídico de MILLA siguen valiendo sus reglas de investigación, derechos y revisión.

## Espacios separados

Cada marca vive en [su carpeta](../../espacios/README.md) y no se mezcla: `espacios/<espacio>/perfil.json` (colores, tipografía, voz, tono), `MARCA.md` (identidad investigada y sus fuentes), `aprendizajes.md` e `ideas.md`. Las producciones van en `productions/<espacio>/<tema>/`, privadas; `proyecto` se niega a crearlas en otro lugar. Antes de trabajar un espacio, leer su `MARCA.md`: Castorena y PAN tienen límites propios (visto bueno del despacho; no hablar a nombre del partido ni usar su logotipo sin autorización).

## Antes de escribir un guion

1. Leer lo aprendido: `$V aprendizajes --espacio E`. Son reglas vigentes, no sugerencias.
2. Preguntar a Emi, en cada video y sea cual sea el tema: **¿cuál es tu postura?**, qué quiere criticar o defender y qué chiste o referencia le gustaría. Se guarda en `opinion_emi`; el validador rechaza un guion sin ella.
3. Investigar el tema en fuentes verificables y poner la fuente en pantalla (`fuente`) junto a cada dato.

## Voz del guion

Crítico, con postura, teórico cuando ayude y con humor puntual (un chiste cada 2 o 3 escenas, nunca a costa del dato), ajustado al tono del espacio. Gancho en la primera frase; la pantalla debe entenderse en silencio. De 4 a 9 escenas. El `keyword` refuerza, no repite la narración: hasta 3 líneas y palabras de 16 letras o menos. La última escena narra `cta_pregunta`, una pregunta que divida opiniones. Campos y ejemplo: [guion.ejemplo.json](plantilla/guion.ejemplo.json).

## Música, efectos y remates (siempre)

En cada video, antes de producir: leer el guion completo, entender de qué va y a quién le habla, y decidir el diseño de sonido. `$V sonido $D/guion.json` da una propuesta de partida (ánimo de la música, efecto por escena y remates); revisarla con criterio contra el sentido de cada escena, no aceptarla a ciegas, y escribir la decisión en el guion:

- `musica.animo`: `tension`, `energia`, `serio`, `ironia` o `motivacion`. La pista se **compone con código** (`scripts/sonido.py`), original y a la medida exacta del video: sin proveedor, sin costo y sin licencias de terceros. Baja bajo la voz y sube al terminar la narración.
- `sonido` por escena: `boom`, `scratch`, `trombon`, `ding`, `redoble`, `suspenso`, `caja`, `error`. Son remates sintetizados aquí, no grabaciones ajenas. Uno por idea; repetido pierde la gracia.
- `remate` por escena (opcional, hasta 14 letras): sello que cae a media escena con su sonido, por ejemplo «PLOT TWIST» o «ASÍ NO».
- En `milla` y `castorena`: música `serio`, sin remates de chiste. En `personal` es donde cabe el humor sonoro.

El validador rechaza un guion sin `musica.animo` o sin ningún `sonido`. Si hace falta un efecto, ánimo o remate visual que no existe, se programa en `sonido.py` o en `plantilla/src/Vox.tsx` con su prueba y se deja disponible para los videos siguientes. No usar audios ni imágenes de memes con derechos de terceros.

Cada video suena distinto: la pista y los efectos se **generan nuevos** con una semilla que sale de su propio texto (otra tonalidad, tempo, acordes y arreglo, siguiendo los cambios de escena). `render` audita el sonido y avisa si la música tapa la voz (menos de 12 LU por debajo), si la sonoridad o el pico se salen de rango, si falta un efecto o si hay silencios; el informe queda en `out/auditoria-audio.json`. Eso no sustituye al oído de Emi.

## Fotos reales con Apify

Solo para personas, lugares o hechos reales que no deben ilustrarse. `$V foto --consulta "..." --dir $D --execute` trae hasta 10 candidatas con su página de origen (tope de gasto por búsqueda, 0.10 USD por defecto; filtro Creative Commons por defecto). Antes de usar una: abrir la página, confirmar qué muestra, autor y licencia; luego `$V foto-bajar --dir $D --indice N --out ... --licencia "licencia y autor" --execute`. El filtro de derechos solo orienta. Nunca rostros que parezcan testimonio de cliente. Si la red del entorno bloquea el dominio de la foto, pedir a Emi que lo autorice.

## Biblioteca: reciclar solo lo que encaja

Al terminar un video, `$V catalogar $D` guarda sus recortes en `biblioteca/` con lo que muestran. Antes de generar una imagen, `$V biblioteca --buscar "..."`; se recicla (`$V reciclar ID --dir $D`) solo si, **al mirarla**, dice exactamente lo que la escena necesita. Ante la duda, imagen nueva. Lo que existe en código (ánimos, efectos, entradas, transiciones, estilos) está en [CATALOGO.md](CATALOGO.md).

## Portada

`render` deja también `out/portada.png` con el titular y el mejor recorte, en los colores y la tipografía del espacio. Por defecto toma la primera escena; se ajusta con `portada: {texto, resaltar, imagen_archivo}` en el guion. Revisarla como imagen: legible en tamaño pequeño y sin texto cortado.

## Flujo

Desde la raíz del repositorio:

```bash
V="python3 skills/vox-studio/scripts/vox.py"
D=productions/personal/TEMA
$V proyecto $D --perfil personal        # copia la plantilla, guarda el saldo inicial y muestra los aprendizajes
(cd $D && npm ci)
$V validar $D/guion.json
$V imagen --prompt-file $D/prompts/01.txt --out $D/originales/01.jpg --estado $D/estados/img-01.json --execute
$V recorte $D/originales/01.jpg $D/public/img/01.png
$V voz $D/guion.json --dir $D --execute # narra una vez y guarda la alineación
$V armar $D/guion.json --dir $D         # tras cambiar textos o imágenes: no vuelve a pagar la voz
$V sonido $D/guion.json                 # propuesta de música, efectos y remates (antes de validar)
$V render $D                            # render + portada + master + hoja de fotogramas
$V cierre $D                            # saldos: gastado y restante
$V catalogar $D                         # guarda los recortes en la biblioteca
```

Sin `--execute` nada gasta saldo. Costos medidos el 10/11/2026: 4 créditos de Kie por imagen con `nano-banana-2-lite`, 5.5 con `seedream/5-lite-text-to-image`; la voz consume los caracteres de la narración.

## Reglas

- **Imágenes naturales**: estilo `ilustracion` (editorial pintada) o `foto`; `sticker` (cartoon) solo si Emi lo pide. Modelo `nano-banana-2-lite` primero; Seedream 5 Lite para lo más realista. Cualquier otro modelo exige añadir su esquema comprobado a `MODELOS_KIE`. GPT Image solo como último recurso documentado, nunca en `milla`, y hoy lo bloquea el freno de `ia/politica.json`: cambiarlo requiere confirmación expresa de Emi.
- El prompt describe solo el sujeto, sin mesas ni suelos; se genera sobre verde (o `--croma magenta` si el sujeto es verde) y se recorta en local. Revisar cada PNG antes de montar.
- Fotos reales (Apify) solo para personas, logos o hechos que no se pueden ilustrar, con derechos verificados; pedir el token a Emi cuando haga falta.
- Subtítulos: solo con los tiempos por palabra que devuelve el proveedor de voz.
- **Nada tiembla**: flotación lenta, rebotes amortiguados. Sin fades. Entradas y transiciones (`viaje`, `barrido`, `rasgado`) variadas; el validador rechaza repetir la anterior.
- Texto dentro de la zona segura de TikTok (x 90–960, y 230–1440).
- Música y efectos: siempre, compuestos con código (ver arriba). Música de terceros solo con derechos documentados.

## Auditar y corregir

`render` deja `out/hoja.png` con el inicio, el cambio y la mitad de cada escena. Mirarla siempre: recortes, encimados, textos cortados, transiciones. Corregir en `src/Vox.tsx` de la producción y, si la mejora sirve a todos, pasarla a `plantilla/` con su prueba. Comprobar que el master diga cerca de −14 LUFS y pico ≤ −1.5 dBTP. Lo que una IA no puede juzgar (cómo suena la voz, el ritmo, la gracia del chiste) se le pregunta a Emi con el MP4 delante.

## Aprender de cada video (obligatorio)

Después de cada entrega y de cada comentario de Emi, guardar la lección: `$V aprender "qué pasó y qué regla queda"` para todos los espacios, o con `--espacio E` si es propia de una marca. Las lecciones no se borran. Si una lección cambia el compositor o el validador, hacer el cambio en `plantilla/` o `vox.py` con su prueba y registrarlo en `CHANGELOG.md`.

## Saldos (obligatorio en cada entrega)

Pegar a Emi la tabla completa de `$V cierre`: lo gastado en ese video y lo que queda en Kie, ElevenLabs y Apify. Un proveedor sin conexión se informa como «no conectado», nunca se estima. El consumo de Claude no se puede consultar desde aquí; decirlo así.

## Terminado

`validar` sin errores, `render` completo, hoja de fotogramas revisada, audio en rango, tabla de saldos entregada, aprendizajes guardados y visto bueno de Emi sobre el MP4. No publicar en redes sin que lo pida.
