---
name: pizarra-studio
description: "Producir videos dibujados a mano estilo pizarra (pizarrón, acuarela, acuarela viva, cuaderno, minimal) para los espacios de Emi (personal, MILLA, Castorena, PAN/Acción Juvenil), cada uno por separado. Usar cuando Emi pida un video estilo pizarra, pizarrón, whiteboard, dibujado a mano, acuarela, cuaderno o minimal. Siempre entrevista a Emi con todas las preguntas antes de producir, espera su aprobación del storyboard, audita, informa saldos y aprende de cada video. Para el estilo vox o box se usa vox-studio."
metadata:
  version: "0.3.1"
  release_date: "2026-11-11"
  language: "es-MX"
---

# Pizarra Studio

Skill independiente de [Vox Studio](../vox-studio/SKILL.md): mismas reglas de fondo, mismos espacios y mismas llaves, **instrucciones separadas**. Si Emi pide estilo vox o box, se usa Vox Studio; si pide pizarra, pizarrón, whiteboard, dibujado a mano, acuarela, cuaderno o minimal, se usa esta. Si no queda claro, se le pregunta; la guía para recomendar está en [espacios/ESTILOS.md](../../espacios/ESTILOS.md).

El 3D, los sombreadores, Blender y ComfyUI de Vox Studio **no se usan aquí**: este estilo es trazo a mano y un render lo rompe. Si un video necesita un objeto 3D, es un video de Vox Studio.

Estado: **candidata**. La cadena completa está probada técnicamente; ningún video suyo tiene aún aprobación de Emi.

## Quién hace qué

Emi decide. Quien usa esta skill orquesta: pregunta, propone con criterio, produce, audita y documenta. Puede y debe proponer ideas creativas, pero nunca decide por él el tema, la postura, el gancho, el estilo ni el cierre.

## El motor y por qué no está aquí

Los videos se dibujan con el motor público [`santmun/video-pizarra`](https://github.com/santmun/video-pizarra) (SVG + GSAP para el pizarrón; canvas para los otros cuatro estilos; render cuadro por cuadro con un navegador). Ese repositorio no tiene licencia de redistribución, así que **su código no se copia a este repositorio**: se instala aparte, fijado al commit revisado, y esta skill lo orquesta.

```bash
P="python3 skills/pizarra-studio/scripts/pizarra.py"
$P instalar     # clona el motor en ~/.cache/pizarra-studio/motor (o PIZARRA_MOTOR) y comprueba dependencias
$P motor        # dice si el autor publicó algo nuevo; no se actualiza solo
```

Adoptar una versión nueva del motor exige leer el código nuevo, probar un render, cambiar `MOTOR_COMMIT` en `pizarra.py` y registrarlo en `CHANGELOG.md`. Su documentación de uso (API de escenas, modo historia, errores conocidos) está en la carpeta instalada, en `references/`: leerla antes de escribir escenas. El motor vive en una carpeta propia para que nadie lo actualice por su cuenta; `proyecto` se niega a usarlo si no está en el commit revisado o si tiene archivos modificados, y cada producción anota con qué versión se creó.

Funciona con cualquier IA que tenga terminal: todo son comandos de `pizarra.py`, Node, Python y FFmpeg.

**Si se llama donde no se puede producir** (app de claude.ai, otra IA sin terminal, una carpeta sin el repositorio, o `pizarra.py instalar` falla): decirlo en la primera respuesta, no al final. Ahí solo se hace la entrevista completa, la investigación, el guion y el storyboard, y se entrega un **paquete de traspaso** para Claude Code: el `brief.json` con las 17 respuestas (aprobaciones en `false` hasta que Emi las dé), el `guion.json` y el `STORYBOARD.md`, con la frase «Usa pizarra-studio y produce esto en productions/ESPACIO/TEMA». No fingir un render, ni marcar aprobaciones, ni pedir llaves por chat. Si Emi en realidad quería estilo vox o box, decirlo y pasar a Vox Studio.

## 1. Entrevista: todas las preguntas, siempre

No se produce nada sin entrevista completa. `$P entrevista DIR` lista lo que falta en `brief.json`. Son 17 respuestas; las que Emi ya dejó fijas en `espacios/PREFERENCIAS-PIZARRA.json` (hoy: **sin personaje** y **voz del espacio**) llegan respondidas y no se vuelven a preguntar. El **estilo** y la **música** se preguntan en cada video.

tema e idea única · **postura de Emi** · público · objetivo · fuentes · formato · duración · tono · estilo · personaje · voz · música · efectos · gancho · cierre · marca en pantalla · referencias.

Cómo preguntar:

- En tandas de hasta 4, cada una con una opción recomendada primero y el porqué en una línea. Sin repetir lo que Emi ya dijo en su mensaje; eso se anota tal cual.
- El **estilo** se pregunta enseñando el catálogo (`catalogo-estilos/` del motor) y la recomendación de `espacios/ESTILOS.md` para ese espacio.
- El **gancho** se pregunta con 2 o 3 propuestas concretas para ese tema, no en abstracto.
- La **postura** se pregunta con el tema delante: qué quiere criticar, defender o provocar, y qué chiste o referencia es suya.
- Lo único que permite saltarse preguntas es que Emi diga expresamente «hazlo directo». Entonces se decide por defecto y se anota cada decisión en `decidido_por_defecto`.

Se cierra con un **resumen en dos grupos**: lo que respondió y lo que se decidió por defecto. Solo cuando Emi lo aprueba se marca `aprobaciones.resumen: true`. Nunca marcar una aprobación que Emi no dio.

## 2. Investigar

Datos en fuentes verificables, cada cifra con su fuente; nada de cifras derivadas o inventadas. En `milla` y `castorena`, fuentes oficiales vigentes y sin prometer resultados. Si falta un dato, se le dice a Emi; no se rellena.

## 3. Storyboard y aprobación

`STORYBOARD.md` en la producción: por escena, **para qué existe** (gancho, contexto, dato, giro, prueba, opinión, remate o cierre), fondo, herramienta, texto en pantalla, qué se dibuja y qué le pasa (la acción) y transición de salida. Si no se puede decir para qué está una escena, sobra; y al menos una lleva la opinión de Emi. A Emi se le muestra una línea por escena. Solo con su visto bueno se marca `aprobaciones.storyboard: true`. `render` se niega a producir un entregable sin las dos aprobaciones, y `voz --execute` no gasta un solo carácter sin ellas ni si Emi no pidió la voz del espacio.

## 4. Flujo de producción

```bash
D=productions/personal/TEMA
$P proyecto $D --perfil personal --modo pizarron            # o --modo estilos --estilo acuarela|acuarela-viva|cuaderno|minimal
$P entrevista $D                                            # hasta que diga «completa y aprobada»
# escribir $D/guion.json: {"escenas": [{"id": "01", "narracion": "..."}]}  (solo si lleva voz)
$P voz $D --execute                                         # una sola toma; devuelve cuánto dura cada escena
# construir scenes.js (pizarrón) o video.js (estilos) con esas duraciones exactas
$P musica $D --animo energia                                # música original por código + rejilla de beats exacta (mide el video)
$P qa $D                                                    # cuadros de prueba + zonas que tapa TikTok, con la misma línea de tiempo del render
$P render $D                                                # render, mezcla, master, auditoría, manifiesto y copia ligera
$P revisar $D                                               # transiciones y tamaño teléfono + informe; sin él no hay cierre
$P cierre $D                                                # saldos: gastado y restante
```

`render --prueba` rinde un borrador técnico (`out/prueba.mp4`) sin exigir la entrevista; sirve para comprobar el sistema y **nunca es un entregable**.

La marca del espacio llega al motor sola: `proyecto` escribe `marca.js` desde `espacios/<espacio>/perfil.json`.

- **Pizarrón**: colores de la marca (este motor usa sus propias letras de trazo a mano). Se usa `bootVideo(construir, { ...window.MARCA, speed: 1 })`.
- **Estilos**: colores, tipografía, el estilo elegido, sin mascota ni persona, y subtítulos con los tiempos reales de la voz. En `video.js`: `import marca from './marca.js'` y `...marca` **después** de las claves de la plantilla y antes de `scenes`, para que la marca mande. El `format` se escribe a mano según la respuesta de Emi (`'9:16'` o `'16:9'`).

Con voz, cada escena dura exactamente lo que dice `tiempos.json` y se usa `speed: 1`; las transiciones no se ajustan al beat (la herramienta lo aplica igual en la medición, en `qa` y en el render). Sin voz, en el pizarrón las transiciones caen en los golpes de la música; en estilos eso solo ocurre si `video.js` declara `beats: 'audio/beats.json'`, y nunca se declara cuando hay voz porque desincroniza. Si Emi respondió «sin efectos», el render los apaga.

## 5. Que se vea hecho por una persona

- Un foco por escena: un texto grande y un elemento dibujado. La voz carga el resto.
- **Sin personaje** por decisión de Emi: la vida la dan la mano que escribe (plumón, gis, lápiz, pincel), los objetos que se dibujan y actúan (algo cae, se tacha, se sella, se compara) y la cámara. Si un video necesitara personaje, se le pregunta; nunca la mascota de fábrica del motor, que es la de Claude.
- Fondo, herramienta y composición distintos de una escena a otra; ninguna transición repetida seguida; transiciones de 0.4 a 0.8 s y motivadas por algo de la escena.
- Texto con la voz de Emi, como habla: frases cortas, concretas, con su opinión. Nada de «en este video te explico», ni listas de adjetivos, ni moralejas.
- Un dato abstracto se vuelve una comparación concreta que se ve (dos pilas, antes y después).
- Humor del espacio: en `personal` cabe el sarcasmo; en `pan`, la crítica con datos; en `milla` y `castorena`, sobriedad.
- Nombres de terceros, clientes o asuntos en curso no salen en pantalla sin permiso expreso.

## 6. Que funcione en TikTok

Gancho escrito en pantalla antes de 0.3 s. Una idea por escena, de 8 a 10 escenas para 60 s. Texto e imágenes dentro de x 90–960, y 230–1440 en vertical (la hoja de `qa` sombrea en rojo lo que tapa la interfaz). Cierre con una pregunta que divida opiniones. Viral no es exagerar: es que la primera frase prometa algo que el video cumple.

## 7. Auditar antes de entregar

1. `qa`: mirar **todos** los cuadros de `out/hoja.jpg`: texto cortado o encimado, dibujos tapando texto, escenas vacías, algo bajo las zonas rojas. Para cada transición, cuadros cada 0.2 s alrededor (`node render.mjs --stills ...`).
2. `render`: corregir todos los avisos de `out/auditoria.json` (formato, duración frente a lo pedido, voz que se corta o video que sobra, sonoridad −14 ± 1 LUFS, pico, música corta, silencios).
3. `revisar`: mirar `out/hoja-transiciones.png` (cada cambio de escena antes, durante y después) y `out/hoja-telefono.png` (tamaño real de un teléfono); anotar en `out/revision.json` cada hallazgo con su arreglo, los pendientes y quién revisó. Corregir los tres peores, volver a rendir y a revisar. `cierre` se niega si el informe falta o es de un render anterior.
4. Ver el MP4 completo. Lo que una IA no puede juzgar (cómo suena la voz, si el chiste funciona, si se siente natural) se le pregunta a Emi con el video delante, en cada video.

## 8. Entregar, saldos y aprendizaje

Se entrega `out/final-movil.mp4` (y dónde está el master), un resumen de 3 a 5 líneas, una propuesta de descripción con las fuentes, y la tabla de `cierre` con lo gastado y lo que queda en ElevenLabs, Kie y Apify. Después de cada entrega y de cada comentario de Emi: `$P aprender "qué pasó y qué regla queda"` (lecciones del estilo pizarra) o con `--espacio E` (propias de una marca). Antes de cada video se leen con `$P aprendizajes --espacio E`.

## Límites

- Solo video. No redacta ni programa publicaciones.
- Las reglas comunes del repositorio (`ia/REGLAS.md`) valen aquí: registro en `CHANGELOG.md` en el mismo commit, sin secretos, producciones fuera de git.
- Si el video dice que todo es código, no se usan imágenes generadas por IA en él.
- Música de terceros solo con derechos documentados; por defecto se compone con código.
