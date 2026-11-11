---
name: vox-studio
description: "Producir shorts verticales 9:16 estilo documental-collage (tipo Vox) con Remotion para los espacios de Emi (personal, MILLA, Castorena, PAN/Acción Juvenil), cada uno por separado. Usar al pedir un short, video explicativo o video estilo Vox, al cambiar la marca de un espacio o al auditar y corregir animaciones, recortes, transiciones o subtítulos. Pregunta siempre la opinión de Emi antes del guion, aprende de cada video e informa los saldos al entregar."
metadata:
  version: "0.12.0"
  release_date: "2026-11-11"
  language: "es-MX"
---

# Vox Studio

Compositor propio. Primer video aprobado por Emi el 11/11/2026 (Castorena, pagos digitales, versión con planos: «ESTÁ PERFECTO»); es la referencia de ese espacio. En personal, MILLA y PAN sigue siendo **candidato**: ningún video suyo tiene aprobación. No sustituye a [MILLA Video Studio](../milla-video-studio/SKILL.md); para contenido jurídico de MILLA siguen valiendo sus reglas de investigación, derechos y revisión.

## Espacios separados

Cada marca vive en [su carpeta](../../espacios/README.md) y no se mezcla: `espacios/<espacio>/perfil.json` (colores, tipografía, voz, tono), `MARCA.md` (identidad investigada y sus fuentes), `aprendizajes.md` e `ideas.md`. Las producciones van en `productions/<espacio>/<tema>/`, privadas; `proyecto` se niega a crearlas en otro lugar. Antes de trabajar un espacio, leer su `MARCA.md`: Castorena y PAN tienen límites propios (visto bueno del despacho; no hablar a nombre del partido ni usar su logotipo sin autorización).

## Antes de escribir un guion

1. Leer lo aprendido: `$V aprendizajes --espacio E`. Son reglas vigentes, no sugerencias.
2. Preguntar a Emi, en cada video y sea cual sea el tema: **¿cuál es tu postura?**, qué quiere criticar o defender y qué chiste o referencia le gustaría. Se guarda en `opinion_emi`; el validador rechaza un guion sin ella.
3. Investigar el tema en fuentes verificables y poner la fuente en pantalla (`fuente`) junto a cada dato.
4. Leer [NARRATIVA.md](NARRATIVA.md): qué hace que un video se vea completo y se comparta, con sus fuentes, y las reglas de guion e imagen que salen de ahí. Declarar en el guion el `bucle` (qué pregunta deja abierta el gancho y qué escena la responde).

## Voz del guion

Crítico, con postura, teórico cuando ayude y con humor puntual (un chiste cada 2 o 3 escenas, nunca a costa del dato), ajustado al tono del espacio. Gancho en la primera frase; la pantalla debe entenderse en silencio. De 4 a 9 escenas, cada una contada con varios planos (ver abajo). Un solo video sirve a WhatsApp, LinkedIn, TikTok y X: vertical, con subtítulos, fuente en pantalla y todo dentro de la zona segura. El `keyword` refuerza, no repite la narración: hasta 3 líneas y palabras de 16 letras o menos. La última escena narra `cta_pregunta`, una pregunta que divida opiniones. Campos y ejemplo: [guion.ejemplo.json](plantilla/guion.ejemplo.json).

`validar` añade avisos de oficio (⚠) que no bloquean pero deben atenderse o justificarse: gancho de más de 14 palabras, escena de más de 22 palabras sin cambio de plano, video fuera de 55–200 palabras (unos 20–75 s), escenas sin nada que ver, cifras sin fuente y keywords que arrancan igual. `armar` avisa además de cualquier escena que dure más de 7 s en la voz real.

## Planos: contar la historia, no ilustrarla (siempre)

Una escena con un solo recorte quieto no cuenta nada: Emi lo rechazó en el primer video de Castorena (11/11/2026). Cada escena de más de unas 12 palabras lleva `planos`: de 2 a 5 cosas que se ven una tras otra, cada una entrando justo cuando la voz dice su palabra ancla (`en`). El primero abre la escena; el anterior sale de cuadro cuando entra el siguiente. Tipos:

- `imagen`: otro recorte (`imagen_archivo`). Varias imágenes por escena, no una.
- `cita`: recorte del documento con la frase clave subrayada a mano (`texto` literal de la fuente, `resaltar`, `origen`). Es la fuente a la vista: úsala para la norma o la tesis que sostiene la escena.
- `lista`: de 2 a 4 `items` que se palomean (`marca: "si"`) o se tachan (`"no"`), cada uno con su propia ancla.
- `calendario`: `dias` que se tachan uno a uno, o `celdas` propias (`t`, `estado: tachado | marcado`) para plazos y cómputos.
- `dato`: cifra que cuenta hasta su valor, con `etiqueta` y, si se pide, `tachar`.
- `duo`: dos recortes frente a frente con una ficha en medio (`entre`: O, VS, +).
- `flujo`: de 2 a 4 `pasos` en cajas unidas por flechas que se dibujan (quién decide, qué sigue), con `nota` a mano opcional.
- `linea`: línea de tiempo de 2 a 4 `hitos` (`fecha`, `texto`); la línea baja hasta cada uno cuando la voz llega.
- `barras`: de 2 a 4 barras que crecen hasta su `valor`; exige `origen` de las cifras.

Cualquier plano puede llevar además un `apunte` (aclaración a mano con flecha, anclada a una palabra) y los de imagen, `etiquetas` que señalan una parte (`x`, `y` de 0 a 1). Y un plano de imagen puede llevar `junto`: una pieza de código (`dato`, `lista`, `calendario`, `barras`, `linea` o `flujo`) que entra a su lado con su palabra mientras la imagen se queda. Así la explicación va a la par de lo que se ve, no después.

**El código se suma; no sustituye.** Emi lo dejó claro el 11/11/2026: el video aprobado «ya estaba perfecto», pidió agregar cosas con código, no reemplazar las imágenes con él. La receta aprobada lleva imagen en cada escena; las piezas de código van al lado de la imagen o como plano adicional. Nunca se quita una imagen para poner un diagrama, y un video aprobado solo se toca para sumarle. `validar` avisa de cualquier escena que quede solo con código.

Antes de generar imágenes se escribe el guion visual: qué se ve en cada frase y por qué ese plano y no otro. Lo que se puede dibujar con código (cita, lista, calendario, cifra) no gasta créditos. `remate_en` hace caer el sello con su palabra. `validar` avisa de cada escena larga que se queda con una sola imagen, del gancho sin segundo plano y del guion sin `bucle`; `armar` avisa de cualquier plano quieto más de 4.5 s en la voz real. Los cambios de plano se prueban con cuadros sueltos (`npx remotion still … --frame=N --browser-executable=/usr/local/bin/chrome-headless-shell`) antes del render completo.

## Cómo lo dice la voz

La voz no lee: cuenta. Tres recursos, escritos en el guion:

- **Pausas**: `[pausa]` (medio segundo) o `[pausa larga]` (uno) dentro de la narración, antes del remate o después de una cifra fuerte. No se leen ni salen en subtítulos.
- **Cambio de tema**: `cambio_tema: true` en la escena que abre otro asunto (los flashes, un «por otro lado»). La voz respira 0.55 s y dice esa escena 10 % más despacio; se narra en un tramo propio.
- **Expresiones humanas**: redactar como se habla (muletillas medidas, autocorrecciones como «bueno, casi», preguntas al que mira). Las marcas `[ríe]`, `[suspira]`, `[carraspea]`, `[susurra]`, `[irónica]`, `[sorprendida]`, `[seria]`, `[emocionada]`, `[lento]` y `[duda]` solo las dice un modelo expresivo (`eleven_v3`, `eleven_v4`); con la voz clásica se omiten y `validar` lo avisa.

**Segunda voz (candidata)**: cada espacio tiene `voz_comentario`, la que opina, bromea y comenta, distinta de la que informa. Una escena con `voz: "comentario"` la usa; en pantalla sus subtítulos van en caja invertida con la etiqueta «OPINIÓN», para que opinión y dato no se confundan. Es para un video polémico cuando salga algo muy relevante y Emi lo pida: antes, él elige la voz por oído con una muestra.

`voz` sin `--execute` enseña el plan: cuántos tramos, con qué voz y velocidad, y cuántos caracteres cuesta.

## De dónde sale cada imagen

En el guion visual, cada plano se decide entre tres fuentes:

- **Código** para lo que se explica, sumado a la imagen: cita, lista, flujo, línea de tiempo, barras, calendario, cifras. No cuesta y es exacto, pero no ocupa el lugar de una imagen.
- **Apify** para lo real: instituciones, edificios, lugares, documentos y hechos. Plano `imagen` con `foto_real: true` y `credito` a la vista. Un video que habla de instituciones reales sin ninguna foto real está incompleto.
- **Kie** para objetos y situaciones que no existen como foto libre. Un solo sujeto por prompt, sin superficies; croma magenta si hay vidrio, pantallas o verde; revisar cada recorte.

## Estilo pizarra o motion

`estilo: "pizarra"` en el guion hace el mismo video con la marca del espacio sobre cuadrícula blanca. Imágenes, narrativa, planos, voz, música, auditorías y saldos son los mismos: solo cambia el fondo.

## Música, efectos y remates (siempre)

En cada video, antes de producir: leer el guion completo, entender de qué va y a quién le habla, y decidir el diseño de sonido. `$V sonido $D/guion.json` da una propuesta de partida (ánimo de la música, efecto por escena y remates); revisarla con criterio contra el sentido de cada escena, no aceptarla a ciegas, y escribir la decisión en el guion:

- `musica.animo`: `tension`, `energia`, `serio`, `ironia` o `motivacion`. La pista se **compone con código** (`scripts/sonido.py`), original y a la medida exacta del video: sin proveedor, sin costo y sin licencias de terceros. Baja bajo la voz y sube al terminar la narración.
- `sonido` por escena: `boom`, `scratch`, `trombon`, `ding`, `redoble`, `suspenso`, `caja`, `error`. Son remates sintetizados aquí, no grabaciones ajenas. Uno por idea; repetido pierde la gracia.
- `remate` por escena (opcional, hasta 14 letras): sello que cae a media escena con su sonido, por ejemplo «PLOT TWIST» o «ASÍ NO». Exige `sonido` en esa escena y no va en la primera.
- En `milla`: música `serio`, sin remates de chiste. En `personal` y en `castorena` (corte suelto, por decisión de Emi del 11/11/2026: un solo video por tema, de tú, con remates) cabe el humor sonoro.

El validador rechaza un guion sin `musica.animo` o sin ningún `sonido`. Si hace falta un efecto, ánimo o remate visual que no existe, se programa en `sonido.py` o en `plantilla/src/Vox.tsx` con su prueba y se deja disponible para los videos siguientes. No usar audios ni imágenes de memes con derechos de terceros.

Cada video suena distinto: la pista y los efectos se **generan nuevos** con una semilla que sale de su propio texto (otra tonalidad, tempo, acordes y arreglo, siguiendo los cambios de escena). La voz manda: se normaliza a −16 LUFS, la música se coloca 17 LU por debajo y los efectos salen todos al mismo nivel, unos 6 dB bajo la voz. `render` audita el resultado y avisa si la música tapa la voz (menos de 12 LU por debajo), si un efecto suena por encima de la voz, si la sonoridad final sale de −14 ± 1 LUFS o el pico pasa de −1.5 dBTP, si el master tuvo que mover más de 4 dB, si falta un efecto o si hay silencios; el informe queda en `out/auditoria-audio.json`. Eso no sustituye al oído de Emi.

## Fotos reales con Apify

Solo para personas, lugares o hechos reales que no deben ilustrarse. `$V foto --consulta "..." --dir $D --execute` trae hasta 10 candidatas con su página de origen (cada búsqueda cuesta unos 0.06 USD: 0.005 de arranque, 0.05 por página de resultados y 0.0023 por foto, medido el 10/11/2026; tope 0.12 USD por defecto y la herramienta rechaza un tope que abortaría cobrando; filtro Creative Commons por defecto). Antes de usar una: abrir la página, confirmar qué muestra, autor y licencia; luego `$V foto-bajar --dir $D --indice N --out ... --licencia "licencia y autor" --execute`. El filtro de derechos solo orienta. En Wikimedia Commons la herramienta lee autor y licencia de la ficha (si su API limita, se abre la ficha y se pasa `--licencia`). Preferir dominio público, CC0 o CC BY; una CC BY-SA obliga a dar crédito en pantalla o en la descripción y a compartir igual la obra derivada: avisar a Emi antes de usarla. Nunca rostros que parezcan testimonio de cliente. Si la red del entorno bloquea el dominio de la foto, pedir a Emi que lo autorice.

## Biblioteca: reciclar solo lo que encaja

Al terminar un video, `$V catalogar $D` guarda sus recortes en `biblioteca/` con lo que muestran. Antes de generar una imagen, `$V biblioteca --buscar "..."`; se recicla (`$V reciclar ID --dir $D`) solo si, **al mirarla**, dice exactamente lo que la escena necesita. Ante la duda, imagen nueva. Lo que existe en código (ánimos, efectos, entradas, transiciones, estilos) está en [CATALOGO.md](CATALOGO.md); los números exactos de montaje, audio y auditoría, en [TECNICA.md](TECNICA.md).

## Solo video

Esta skill hace video y nada más: guion, imagen, voz, sonido, montaje, portada y su auditoría. No redacta ni programa publicaciones en X ni en ninguna red, y no mezcla instrucciones de otras skills. La skill de X de Emi (`lianfixx/X`) es independiente: puede dejar ideas de video en su propio repositorio (`puente/para-vox.md`) y aquí se toman solo como propuestas de tema para el espacio `personal`, preguntando igual la postura de Emi. El `handle` de un espacio es el @ de la red donde se publica el video; un @ de otra red va en `cuentas` y no se muestra en pantalla.

## Cierre

Cuando termina la voz cae un sello con el llamado del espacio (`cierre` en `perfil.json`: «COMENTA», «TE LEEMOS», «SU OPINIÓN», «OPINA») y una flecha hacia el botón de comentarios; el video dura 1.5 s más que la narración para que se lea. Un video puede cambiar el llamado solo para sí con `cierre` en el guion (hasta 16 letras), por ejemplo cuando un corte tutea en un espacio que habla de usted. Las escenas de más de 5 s reciben un pulso del recorte a la mitad.

## Portada

`render` deja también `out/portada.png` con el titular y el mejor recorte, en los colores y la tipografía del espacio. Por defecto toma la primera escena; se ajusta con `portada: {texto, resaltar, imagen_archivo}` en el guion. Revisarla como imagen: legible en tamaño pequeño y sin texto cortado.

## Flujo

Desde la raíz del repositorio:

```bash
V="python3 skills/vox-studio/scripts/vox.py"
D=productions/personal/TEMA
$V proyecto $D --perfil personal        # copia la plantilla, guarda el saldo inicial y muestra los aprendizajes
(cd $D && npm ci)
$V sonido $D/guion.json                 # propuesta de música, efectos y remates; decidir y escribirla en el guion
$V validar $D/guion.json
$V imagen --perfil personal --prompt-file $D/prompts/01.txt --out $D/originales/01.jpg --estado $D/estados/img-01.json --execute
$V recorte $D/originales/01.jpg $D/public/img/01.png
$V voz $D/guion.json --dir $D --execute # narra una vez y guarda la alineación
$V armar $D/guion.json --dir $D         # tras cambiar textos o imágenes: no vuelve a pagar la voz
$V render $D                            # render + portada + master + hoja de fotogramas
$V cierre $D                            # saldos: gastado y restante
$V catalogar $D                         # guarda los recortes en la biblioteca
```

Si la narración sale lenta para un short (más de 60 s o escenas de 9 s o más), `voz_velocidad` en el guion (0.7 a 1.2; también `voz.velocidad` en el perfil) pide a ElevenLabs otro ritmo; cambiarla vuelve a pagar la narración.

Sin `--execute` nada gasta saldo. Costos medidos el 10/11/2026: 4 créditos de Kie por imagen con `nano-banana-2-lite`, 5.5 con `seedream/5-lite-text-to-image`; la voz consume los caracteres de la narración.

## Reglas

- **Imágenes naturales**: `--perfil E` toma el estilo del espacio (`estilo_imagen`: ilustración en personal y MILLA, foto en Castorena y PAN); también `--estilo ilustracion` (editorial pintada) o `foto`; `sticker` (cartoon) solo si Emi lo pide. Modelo `nano-banana-2-lite` primero; Seedream 5 Lite para lo más realista. Cualquier otro modelo exige añadir su esquema comprobado a `MODELOS_KIE`. GPT Image solo como último recurso documentado, nunca en `milla`, y hoy lo bloquea el freno de `ia/politica.json`: cambiarlo requiere confirmación expresa de Emi.
- El prompt describe solo el sujeto, sin mesas ni suelos; se genera sobre verde (o `--croma magenta` si el sujeto es verde) y se recorta en local. Revisar cada PNG antes de montar.
- Fotos reales (Apify) solo para personas, logos o hechos que no se pueden ilustrar, con derechos verificados; pedir el token a Emi cuando haga falta.
- Subtítulos: solo con los tiempos por palabra que devuelve el proveedor de voz.
- **Nada tiembla**: flotación lenta, rebotes amortiguados. Sin fades. Entradas y transiciones (`viaje`, `barrido`, `rasgado`) variadas; el validador rechaza repetir la anterior.
- Texto dentro de la zona segura de TikTok (x 90–960, y 230–1440).
- Música y efectos: siempre, compuestos con código (ver arriba). Música de terceros solo con derechos documentados.

## Auditar y corregir

`render` deja `out/hoja.png` con el inicio, el cambio y la mitad de cada escena, y `out/hoja-tiktok.png` con las zonas que tapa la interfaz de TikTok sombreadas en rojo: ningún texto ni rostro debe quedar debajo. Mirarla siempre: recortes, encimados, textos cortados, transiciones. Corregir en `src/Vox.tsx` de la producción y, si la mejora sirve a todos, pasarla a `plantilla/` con su prueba. `render` imprime los avisos de `out/auditoria-audio.json` y `out/auditoria-video.json` (formato del archivo, contenido bajo la interfaz de TikTok, cuadros vacíos, niveles): se corrigen todos antes de entregar. Sin avisos significa en rango, no aprobado: **en cada video se le pide a Emi que escuche voz, música y efectos** y se guarda lo que diga. Lo que una IA no puede juzgar (cómo suena la voz, el ritmo, la gracia del chiste) se le pregunta a Emi con el MP4 delante.

## Aprender de cada video (obligatorio)

Después de cada entrega y de cada comentario de Emi, guardar la lección: `$V aprender "qué pasó y qué regla queda"`. **Vale para todos los espacios**: lo técnico, de oficio, de proceso o de narrativa que se aprende en una marca se aplica a las demás. Con `--espacio E` solo va el espíritu de esa marca (tono, público, voz, límites, aprobaciones). Toda mejora de la plantilla se prueba con cuadros en los cuatro espacios. Las lecciones no se borran. Si una lección cambia el compositor o el validador, hacer el cambio en `plantilla/` o `vox.py` con su prueba y registrarlo en `CHANGELOG.md`.

## Saldos (obligatorio en cada entrega)

Pegar a Emi la tabla completa de `$V cierre`: lo gastado en ese video y lo que queda en Kie, ElevenLabs y Apify. Un proveedor sin conexión se informa como «no conectado», nunca se estima. El consumo de Claude no se puede consultar desde aquí; decirlo así.

## Dónde funciona

En Claude Code con este repositorio la skill produce el video completo. Como skill personal de claude.ai (paquete de `python3 tools/empaquetar_vox.py`, que lleva los espacios dentro) sirve para guion, método y consulta: ahí no hay llaves ni render, así que se avanza el guion y se entrega para producirlo en Claude Code. No fingir un render ni un saldo que no se pudo consultar.

## Terminado

`validar` sin errores, `render` completo, hoja de fotogramas revisada, audio en rango, tabla de saldos entregada, aprendizajes guardados y visto bueno de Emi sobre el MP4. No publicar en redes sin que lo pida.
