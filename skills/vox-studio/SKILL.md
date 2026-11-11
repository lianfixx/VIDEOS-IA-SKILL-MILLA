---
name: vox-studio
description: "Producir shorts verticales 9:16 estilo documental-collage (tipo Vox) con Remotion para los espacios de Emi (personal, MILLA, Castorena, PAN/Acción Juvenil), cada uno por separado. Usar al pedir un short, video explicativo o video estilo Vox, al cambiar la marca de un espacio o al auditar y corregir animaciones, recortes, transiciones o subtítulos. Pregunta siempre la opinión de Emi antes del guion, aprende de cada video e informa los saldos al entregar."
metadata:
  version: "0.10.0"
  release_date: "2026-11-11"
  language: "es-MX"
---

# Vox Studio

Compositor propio, **candidato**: rinde y está probado técnicamente, pero ningún video suyo tiene todavía aprobación estética de Emi. No sustituye a [MILLA Video Studio](../milla-video-studio/SKILL.md); para contenido jurídico de MILLA siguen valiendo sus reglas de investigación, derechos y revisión.

## Espacios separados

Cada marca vive en [su carpeta](../../espacios/README.md) y no se mezcla: `espacios/<espacio>/perfil.json` (colores, tipografía, voz, tono), `MARCA.md` (identidad investigada y sus fuentes), `aprendizajes.md` e `ideas.md`. Las producciones van en `productions/<espacio>/<tema>/`, privadas; `proyecto` se niega a crearlas en otro lugar. Antes de trabajar un espacio, leer su `MARCA.md`: Castorena y PAN tienen límites propios (visto bueno del despacho; no hablar a nombre del partido ni usar su logotipo sin autorización).

## Antes de escribir un guion

1. Leer lo aprendido: `$V aprendizajes --espacio E`. Son reglas vigentes, no sugerencias.
2. Preguntar a Emi, en cada video y sea cual sea el tema: **¿cuál es tu postura?**, qué quiere criticar o defender y qué chiste o referencia le gustaría. Se guarda en `opinion_emi`; el validador rechaza un guion sin ella.
3. Investigar el tema en fuentes verificables y poner la fuente en pantalla (`fuente`) junto a cada dato. Una cifra en la narración sin `fuente` en su escena hace fallar la validación: un dato sin fuente no se publica.
4. Proponer a Emi **2 o 3 ganchos** distintos para ese tema (`ganchos_propuestos`) y anotar cuál eligió (`gancho_elegido`). El gancho es lo que más pesa en que el video se vea; no se decide por él.
5. Si Emi tiene una imagen o un video de referencia, `$V referencia ARCHIVO --dir $D` lo convierte en una hoja: se mira y se le dice qué se toma de ahí (ritmo, tipografía, transiciones) antes de seguir.

## Voz del guion

Crítico, con postura, teórico cuando ayude y con humor puntual (un chiste cada 2 o 3 escenas, nunca a costa del dato), ajustado al tono del espacio. Gancho en la primera frase; la pantalla debe entenderse en silencio. De 4 a 9 escenas, cada una con su `funcion` (para qué existe): `gancho`, `contexto`, `dato`, `giro`, `prueba`, `opinion`, `remate` o `cierre`. La primera es el gancho, la última el cierre y al menos una es `opinion`: la postura de Emi tiene que oírse, no solo guiar el guion. Si no se puede decir para qué está una escena, sobra. El `keyword` refuerza, no repite la narración: hasta 3 líneas y palabras de 16 letras o menos. La última escena narra `cta_pregunta`, una pregunta que divida opiniones. Campos y ejemplo: [guion.ejemplo.json](plantilla/guion.ejemplo.json).

`validar` añade avisos de oficio (⚠) que no bloquean pero deben atenderse o justificarse: gancho de más de 14 palabras, escena de más de 22 palabras sin cambio de plano, video fuera de 55–200 palabras (unos 20–75 s), escenas sin nada que ver, cifras sin fuente y keywords que arrancan igual. `armar` avisa además de cualquier escena que dure más de 7 s en la voz real.

## Música, efectos y remates (siempre)

En cada video, antes de producir: leer el guion completo, entender de qué va y a quién le habla, y decidir el diseño de sonido. `$V sonido $D/guion.json` da una propuesta de partida (ánimo de la música, efecto por escena y remates); revisarla con criterio contra el sentido de cada escena, no aceptarla a ciegas, y escribir la decisión en el guion:

- `musica.animo`: `tension`, `energia`, `serio`, `ironia` o `motivacion`. La pista se **compone con código** (`scripts/sonido.py`), original y a la medida exacta del video: sin proveedor, sin costo y sin licencias de terceros. Baja bajo la voz y sube al terminar la narración.
- `sonido` por escena: `boom`, `scratch`, `trombon`, `ding`, `redoble`, `suspenso`, `caja`, `error`. Son remates sintetizados aquí, no grabaciones ajenas. Uno por idea; repetido pierde la gracia.
- `remate` por escena (opcional, hasta 14 letras): sello que cae a media escena con su sonido, por ejemplo «PLOT TWIST» o «ASÍ NO». Exige `sonido` en esa escena y no va en la primera.
- En `milla` y `castorena`: música `serio`, sin remates de chiste. En `personal` es donde cabe el humor sonoro.

El validador rechaza un guion sin `musica.animo` o sin ningún `sonido`. Si hace falta un efecto, ánimo o remate visual que no existe, se programa en `sonido.py` o en `plantilla/src/Vox.tsx` con su prueba y se deja disponible para los videos siguientes. No usar audios ni imágenes de memes con derechos de terceros.

Cada video suena distinto: la pista y los efectos se **generan nuevos** con una semilla que sale de su propio texto (otra tonalidad, tempo, acordes y arreglo, siguiendo los cambios de escena). La voz manda: se normaliza a −16 LUFS, la música se coloca 17 LU por debajo y los efectos salen todos al mismo nivel, unos 6 dB bajo la voz. `render` audita el resultado y avisa si la música tapa la voz (menos de 12 LU por debajo), si un efecto suena por encima de la voz, si la sonoridad final sale de −14 ± 1 LUFS o el pico pasa de −1.5 dBTP, si el master tuvo que mover más de 4 dB, si falta un efecto o si hay silencios; el informe queda en `out/auditoria-audio.json`. Eso no sustituye al oído de Emi.

## Fotos reales con Apify

Solo para personas, lugares o hechos reales que no deben ilustrarse. `$V foto --consulta "..." --dir $D --execute` trae hasta 10 candidatas con su página de origen (cada búsqueda cuesta unos 0.06 USD: 0.005 de arranque, 0.05 por página de resultados y 0.0023 por foto, medido el 10/11/2026; tope 0.12 USD por defecto y la herramienta rechaza un tope que abortaría cobrando; filtro Creative Commons por defecto). Antes de usar una: abrir la página, confirmar qué muestra, autor y licencia; luego `$V foto-bajar --dir $D --indice N --out ... --licencia "licencia y autor" --execute`. El filtro de derechos solo orienta. En Wikimedia Commons la herramienta lee autor y licencia de la ficha (si su API limita, se abre la ficha y se pasa `--licencia`). Preferir dominio público, CC0 o CC BY; una CC BY-SA obliga a dar crédito en pantalla o en la descripción y a compartir igual la obra derivada: avisar a Emi antes de usarla. Nunca rostros que parezcan testimonio de cliente. Si la red del entorno bloquea el dominio de la foto, pedir a Emi que lo autorice.

## Biblioteca: reciclar solo lo que encaja

Al terminar un video, `$V catalogar $D` guarda sus recortes en `biblioteca/` con lo que muestran. Antes de generar una imagen, `$V biblioteca --buscar "..."`; se recicla (`$V reciclar ID --dir $D`) solo si, **al mirarla**, dice exactamente lo que la escena necesita. Ante la duda, imagen nueva. Lo que existe en código (ánimos, efectos, entradas, transiciones, estilos) está en [CATALOGO.md](CATALOGO.md); los números exactos de montaje, audio y auditoría, en [TECNICA.md](TECNICA.md).

## Cuándo no es esta skill

Si Emi pide un video estilo pizarra, pizarrón, whiteboard, dibujado a mano, acuarela, cuaderno o minimal, se usa [Pizarra Studio](../pizarra-studio/SKILL.md), que tiene sus propias instrucciones. Para recomendar entre estilos: [espacios/ESTILOS.md](../../espacios/ESTILOS.md).

## Solo video

Esta skill hace video y nada más: guion, imagen, voz, sonido, montaje, portada y su auditoría. No redacta ni programa publicaciones en X ni en ninguna red, y no mezcla instrucciones de otras skills. La skill de X de Emi (`lianfixx/X`) es independiente: puede dejar ideas de video en su propio repositorio (`puente/para-vox.md`) y aquí se toman solo como propuestas de tema para el espacio `personal`, preguntando igual la postura de Emi. El `handle` de un espacio es el @ de la red donde se publica el video; un @ de otra red va en `cuentas` y no se muestra en pantalla.

## Cierre

Cuando termina la voz cae un sello con el llamado del espacio (`cierre` en `perfil.json`: «COMENTA», «TE LEEMOS», «SU OPINIÓN», «OPINA») y una flecha hacia el botón de comentarios; el video dura 1.5 s más que la narración para que se lea. Las escenas de más de 5 s reciben un pulso del recorte a la mitad.

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
$V render $D                            # render + portada + master + hojas + auditorías + manifiesto
$V revisar $D                           # transiciones y tamaño teléfono + informe; sin él no hay cierre
$V cierre $D                            # saldos: gastado y restante
$V catalogar $D                         # guarda los recortes en la biblioteca
```

Sin `--execute` nada gasta saldo. Costos medidos el 10/11/2026: 4 créditos de Kie por imagen con `nano-banana-2-lite`, 5.5 con `seedream/5-lite-text-to-image`; la voz consume los caracteres de la narración.

## Reglas

- **Imágenes naturales**: `--perfil E` toma el estilo del espacio (`estilo_imagen`: ilustración en personal y MILLA, foto en Castorena y PAN); también `--estilo ilustracion` (editorial pintada) o `foto`; `sticker` (cartoon) solo si Emi lo pide. Modelo `nano-banana-2-lite` primero; Seedream 5 Lite para lo más realista. Cualquier otro modelo exige añadir su esquema comprobado a `MODELOS_KIE`. GPT Image solo como último recurso documentado, nunca en `milla`, y hoy lo bloquea el freno de `ia/politica.json`: cambiarlo requiere confirmación expresa de Emi.
- El prompt describe solo el sujeto, sin mesas ni suelos; se genera sobre verde (o `--croma magenta` si el sujeto es verde) y se recorta en local. Revisar cada PNG antes de montar.
- Fotos reales (Apify) solo para personas, logos o hechos que no se pueden ilustrar, con derechos verificados; pedir el token a Emi cuando haga falta.
- Subtítulos: solo con los tiempos por palabra que devuelve el proveedor de voz.
- **Nada tiembla**: flotación lenta, rebotes amortiguados. Sin fades. Entradas y transiciones (`viaje`, `barrido`, `rasgado`) variadas; el validador rechaza repetir la anterior.
- Texto dentro de la zona segura de TikTok (x 90–960, y 230–1440).
- Música y efectos: siempre, compuestos con código (ver arriba). Música de terceros solo con derechos documentados.

## 3D, sombreadores, Blender y ComfyUI (solo cuando hace falta)

Están disponibles y **no son el estilo**: son acentos. Antes de usar uno se razona si explica algo mejor que un recorte plano, y esa razón se escribe en el guion (`porque`); si la frase no sale, no se usa. La guía completa, con la tabla de «qué necesita la escena → qué recurso», las señales de que no va y los comandos, está en [TRES-D.md](TRES-D.md). Resumen:

- `objeto3d` en una escena (`moneda`, `monedas`, `barras`, `caja`, `globo`): 3D dibujado con los colores del espacio y contorno de tinta. Sin costo. Las `barras` son un dato: exigen valores reales y `fuente`.
- `tratamiento` (`semitono`, `duotono`) sobre una foto o recorte realista, para que se vea impreso en el mismo papel.
- `$V blender ...`: objeto con luz y material de verdad, texto con volumen o un modelo 3D de Emi. Se instala una vez con `$V blender-instalar`.
- `$V comfy ...`: imagen desde el servidor de ComfyUI de Emi (`COMFY_URL`). Este entorno no tiene tarjeta gráfica: sin servidor, el comando se detiene y lo dice.

`validar` avisa si más de una de cada tres escenas lleva 3D. Orden de preferencia: lo más simple que sirva.

## Auditar y corregir

`render` deja `out/hoja.png` con el inicio, el cambio y la mitad de cada escena, y `out/hoja-tiktok.png` con las zonas que tapa la interfaz de TikTok sombreadas en rojo: ningún texto ni rostro debe quedar debajo. Mirarla siempre: recortes, encimados, textos cortados, transiciones. Corregir en `src/Vox.tsx` de la producción y, si la mejora sirve a todos, pasarla a `plantilla/` con su prueba. `render` imprime los avisos de `out/auditoria-audio.json` y `out/auditoria-video.json` (formato del archivo, contenido bajo la interfaz de TikTok, cuadros vacíos, niveles): se corrigen todos antes de entregar. Sin avisos significa en rango, no aprobado: **en cada video se le pide a Emi que escuche voz, música y efectos** y se guarda lo que diga. Lo que una IA no puede juzgar (cómo suena la voz, el ritmo, la gracia del chiste) se le pregunta a Emi con el MP4 delante.

## Revisar el render (obligatorio antes de cerrar)

Nunca se dice que un video quedó bien sin haber mirado el archivo rendido. Después de `render`:

1. `$V revisar $D` crea `out/hoja-transiciones.png` (cada cambio de escena: 6 y 3 cuadros antes, el corte, y 3, 6 y 12 después) y `out/hoja-telefono.png` (el video al tamaño en que se ve en un teléfono).
2. Mirar las dos. En las transiciones: texto encimado, algo que tapa el titular al entrar, elementos que saltan o desaparecen, un cuadro vacío. En el teléfono: todo lo que no se lea ahí, no se lee.
3. Anotar en `out/revision.json` cada `hallazgo` (segundo, problema, arreglo), los `pendientes` y `revisado_por`. Corregir primero los tres peores, volver a rendir y volver a revisar: la revisión solo vale para el render actual.
4. `cierre` se niega si falta el informe, si es de un render anterior o si no dice quién revisó.

Una IA puede revisar imagen; no puede oír. `visto_y_escuchado_por_emi` solo lo marca Emi.

## Compuertas: cuándo detenerse y preguntar

Se trabaja de corrido salvo en estos puntos, donde se para y se le pregunta a Emi: falta su postura o no eligió gancho; un dato no tiene fuente verificable; falta una imagen real (captura, logo, foto) que no debe inventarse; la referencia que dio no queda clara (se le enseña un cuadro de prueba antes de hacer todo el video); el gasto pasaría de lo ya autorizado. Mejor una pregunta que un video entero bien hecho sobre una suposición.

## Aprender de cada video (obligatorio)

Después de cada entrega y de cada comentario de Emi, guardar la lección: `$V aprender "qué pasó y qué regla queda"` para todos los espacios, o con `--espacio E` si es propia de una marca. Las lecciones no se borran. Si una lección cambia el compositor o el validador, hacer el cambio en `plantilla/` o `vox.py` con su prueba y registrarlo en `CHANGELOG.md`.

## Saldos (obligatorio en cada entrega)

Pegar a Emi la tabla completa de `$V cierre`: lo gastado en ese video y lo que queda en Kie, ElevenLabs y Apify. Un proveedor sin conexión se informa como «no conectado», nunca se estima. El consumo de Claude no se puede consultar desde aquí; decirlo así.

## Dónde funciona y qué hacer si se llama en otro lado

Lo primero, siempre: comprobar dónde se está. Hay terminal, este repositorio y llaves si `python3 skills/vox-studio/scripts/vox.py saldo` responde con cifras. Según el resultado:

| Situación | Qué se hace | Qué se le dice a Emi |
|---|---|---|
| Claude Code con este repositorio y el entorno `videos-ia-skill-milla` | Todo el flujo, hasta el MP4 | Nada especial |
| Claude Code sin las llaves (`saldo` dice «no conectado» o da error) | Guion, validación, música, montaje con lo que ya exista; no voz ni imágenes nuevas | Qué proveedor falta y que se conecta en la configuración del entorno, nunca pegando la llave en el chat |
| Claude Code en otra carpeta, sin el repositorio | Nada de producción | Que abra la sesión sobre `lianfixx/VIDEOS-IA-SKILL-MILLA` |
| App de claude.ai u otra IA sin terminal (skill subida como `.zip`) | Solo lo que no necesita ejecutar: preguntarle su postura, investigar, escribir el guion completo en el formato de `guion.ejemplo.json`, proponer música, efectos y prompts de imagen | Al empezar, en una frase: «Aquí no puedo generar voz, imágenes ni el video; te dejo el guion listo para producirlo en Claude Code» |
| Emi pide un video estilo pizarra | No es esta skill | Con el repositorio: usar Pizarra Studio. En la app: hacer la entrevista de `pizarra/PIZARRA.md` y entregar las respuestas para llevarlas a Claude Code |

Reglas para cualquier caso que no sea el primero:

- Decir el límite **antes** de trabajar, no al final. Nunca fingir un render, un saldo, una voz escuchada ni un archivo que no existe.
- No pedir llaves por chat ni escribirlas en ningún archivo.
- Terminar con un **paquete de traspaso** que Emi pueda pegar tal cual en Claude Code: (1) espacio, (2) `guion.json` completo y válido, (3) un prompt por imagen, (4) música y efectos elegidos, (5) lo que quedó sin decidir. Y la frase exacta para continuar: «Usa vox-studio y produce este guion en productions/ESPACIO/TEMA».
- Si Emi llamó a la skill por error (quería otra cosa, u otro estilo), decirlo en una línea y preguntar qué quería; no producir «por si acaso».
- Si no se puede leer `espacios/` (copia vieja o incompleta), avisar que la skill instalada está desactualizada y que la vigente está en `main` del repositorio.

El paquete para la app se genera con `python3 tools/empaquetar_vox.py` y lleva los espacios y la guía de entrevista de pizarra dentro.

## Terminado

`validar` sin errores, `render` completo, `revisar` hecho y `out/revision.json` firmado sobre el render actual, audio en rango, tabla de saldos entregada, aprendizajes guardados y visto bueno de Emi sobre el MP4. No publicar en redes sin que lo pida.
