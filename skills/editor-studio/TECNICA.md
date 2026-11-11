# Técnica

## Qué hace cada parte

| Parte | Archivo | Con qué |
|---|---|---|
| Base: espacios, red, saldos, FFmpeg | `scripts/comun.py` | biblioteca estándar |
| Transcripción | `scripts/transcripcion.py` | ElevenLabs Scribe, AssemblyAI o un archivo |
| Corte | `scripts/corte.py` | numpy + FFmpeg |
| Plan, validación y composición | `scripts/montaje.py` | — |
| Movimiento y aspecto | `plantilla/editor.js`, `plantilla/editor.css` | GSAP sobre HyperFrames |
| Sonido | `scripts/audio.py` | FFmpeg |
| Flujo y compuertas | `scripts/editor.py` | — |
| Pruebas | `scripts/test_editor.py` | sin red ni saldo |

El motor de render es [HyperFrames](https://github.com/heygen-com/hyperframes) (HeyGen, licencia Apache 2.0), fijado a la versión 0.9.34 en `plantilla/package.json`. Convierte HTML animado en video buscando cada cuadro, así que dos renders del mismo plan son iguales. Todo el código de esta skill es propio; el método se tomó de las referencias anotadas en `docs/REFERENCIAS-EXTERNAS.md`.

## Archivos de una producción

```
productions/<espacio>/edicion/<tema>/
  brief.json          respuestas de Emi, aprobaciones, saldo inicial
  crudo/              el original, sin tocar
  trabajo.mp4         mismo video, emparejado (tamaño, 30 c/s, color estándar)
  audio.wav           mono 16 kHz para medir y transcribir
  palabras.json       transcripción por palabra · transcripcion.txt para leerla
  cortes.json         propuesta, decisiones y aprobación
  limpio.mp4 · limpio.wav · palabras_limpio.json · cortes-aplicados.json
  rostro.json         dónde está la cara
  plan.json           la edición, como datos
  index.html          composición (la escribe `armar`; no se edita a mano)
  assets/             base.mp4, fotos, insertos, recortes, fuentes
  out/                muestras, FINAL.mp4, hojas, auditorías, revision.json, manifiesto.json, publicacion.md
```

## Reglas del motor que ya se cumplen (y hay que respetar al añadir piezas)

- La biblioteca de animación y las fuentes (Anton, Gelasio e Inter) van **dentro del proyecto** (`lib/`, `assets/fonts/`): el navegador del render no alcanza internet y así se ve igual en cualquier máquina.
- Una sola línea de tiempo pausada, registrada en `window.__timelines["main"]`. Sin `Date.now()`, sin azar sin semilla, sin relojes, sin repeticiones infinitas.
- Los videos llevan `class="clip"`, `data-start` y `data-duration`; no se les da reproducir. Se mueve su contenedor, nunca el video.
- No se animan `display` ni `visibility` con transición; se enciende y apaga con `tl.set`.
- El video base va mudo: la mezcla se hace fuera y se une al final. El motor avisa de «audio sin elemento»; es a propósito.
- El color del metraje se aplica con FFmpeg antes de componer, no con filtros CSS.
- Una pieza nueva necesita: su fila en `PIEZAS`, sus reglas en `validar`, su HTML en `armar_html`, su movimiento en `editor.js`, su estilo en `editor.css` y su prueba.

## Recibir los crudos

1. **Drive** (lo normal): Emi sube el archivo a `Editor Studio/<espacio>/crudos` y comparte el archivo o la carpeta con «cualquier persona con el enlace». `$E traer $D --drive ENLACE` lo baja. El entorno `videos-ia-skill-milla` permite `drive.google.com` y `drive.usercontent.google.com` desde el 11/11/2026.
2. Si el video no debe tener enlace abierto: se baja en el box con la sesión de Emi y se trabaja desde ahí lo que se pueda; o se produce en su Mac.

iPhone: graba en HEVC y, con HDR activado, en Dolby Vision. `ingerir` lo detecta y lo convierte a color estándar. Conviene grabar a 30 c/s y 4K o 1080p vertical; con micrófono externo la transcripción y los cortes mejoran.

## Transcripción

| Motor | Estado | Notas |
|---|---|---|
| ElevenLabs Scribe (`scribe`) | Conectado y probado el 11/11/2026 con un clip en español | Tiempo por palabra; conserva «eh» y tomas repetidas; marca eventos de audio; `--hablantes` separa voces |
| AssemblyAI (`assemblyai`) | Conectado y probado el 11/11/2026 con el mismo clip en español | Es el que recomiendan las referencias para cortar. Pide muletillas con `disfluencies`. La llave va en la cabecera `Authorization` sola, sin «Bearer»: con el prefijo, la subida de audio responde «Invalid API key» |
| Archivo (`--archivo`) | Probado con JSON, SRT y VTT | Para exportaciones de Whisper Mate u otra app. Con SRT o frases los tiempos son aproximados: sirven para subtítulos por frase, no para cortar muletillas |

Comparación del 11/11/2026 sobre el clip sintético de 27 s: los dos dieron 72 palabras, coinciden en 97 %, sus tiempos difieren 25 ms de mediana (75 ms en el peor décimo) y ambos conservaron el «eh» y la toma repetida. La única diferencia: AssemblyAI escribe los números con cifra («3», «8») y Scribe con letra. Con una voz sintética y limpia empatan; la diferencia que importa (voz baja, ruido, muletillas reales) solo se verá con un crudo de Emi.

Para decidir entre dos motores con un crudo real: `transcribir --como scribe`, `transcribir --motor assemblyai --como assemblyai` y `comparar-motores DIR scribe assemblyai`. El número no decide: se escuchan los cortes.

## Dónde producir

| Lugar | Para qué sirve | Límite |
|---|---|---|
| Nube (Claude Code, entorno `videos-ia-skill-milla`) | Todo. 4 núcleos, 15 GB. Medido: 19 s de video en nivel 2 se rinden en menos de un minuto en borrador | Solo alcanza los dominios permitidos |
| Box de Emi | Navegador con sus sesiones: bajar algo de una cuenta suya, subir a Drive, Flow Music | 2 núcleos y 3 GB: no rinde video |
| Mac de Emi | Si la nube no alcanza (crudos muy largos, material que no debe salir de su equipo) | `sh ia/instalar.sh`, Node 22, FFmpeg y `pip install numpy pillow 'opencv-python-headless<5'` |

Un video largo se trabaja por tramos de 5 a 10 minutos.

## Entregar

El MP4 se sube a `Editor Studio/<espacio>/entregas` con el conector de Drive y se le manda a Emi el archivo en la conversación. No se publica. La hoja `out/publicacion.md` va aparte.

## Costos medidos

| Qué | Costo | Medido |
|---|---|---|
| Transcribir 27 s con Scribe | no aparece en el contador de caracteres | 11/11/2026 (revisar el historial de ElevenLabs con un crudo real) |
| Imagen con `nano-banana-2-lite` | 4 créditos de Kie | 10/11/2026 |
| Cortes, subtítulos, montaje, sonido, recorte de persona, render | nada | — |
| Video generado con Kling | sin medir | — |

## Lo que una revisión independiente encontró y ya está corregido (11/11/2026)

Quince defectos, cada uno con su prueba de regresión en `test_editor.py` (clases `Auditoria` y `Cierre`) o `test_radar.py`: ids de pieza sin validar, cifras alteradas en subtítulos, `cierre` que no comprobaba que el archivo correspondiera a lo aprobado, tope del radar mal calculado, milisegundos leídos como segundos, sticker mal colocado, texto con zona «pantalla», silencios que se tragaban una palabra dicha en voz baja, pie de foto bajo los subtítulos, fuente Inter fuera del proyecto, censura que perdía su palabra, y varios errores que salían como traza. Quedó sin comprobar por esa revisión: un Dolby Vision real de iPhone, macOS, el ancho de Gelasio en mayúsculas y los motores de transcripción en vivo.

## Segunda auditoría independiente (11/11/2026): lo que encontró y ya está corregido

Tres revisores (flujo bajo estrés, imagen y sonido, guías y conexiones). Cada defecto tiene su prueba en `test_editor.py` (clases `Auditoria2` y `Compuertas2`).

- **Cortar agotaba la memoria** con un clip vertical de unos minutos (13 GB con 6 min). Ahora corta tramo por tramo y los une: memoria constante.
- **Voz nueva sobre imagen vieja** si se volvía a cortar después de armar: `render` y `validar` ahora lo detectan, igual que un mapa de rostro o un recorte de otro corte.
- **Voz adelantada** unos 270 ms cuando el audio del crudo arranca después que la imagen: `ingerir` conserva ese desfase. Si imagen y sonido duran distinto, trabaja hasta donde hay los dos.
- **Sin silencios con ruido de fondo**: ver Oficio.
- **Censura sobre otra palabra** si cambiaba la transcripción: los cortes quedan atados a su transcripción y la censura entra en la aprobación.
- **Imagen**: el panel cortaba su texto; un título largo se salía del cuadro; el azul de PAN no se leía; un zoom regresaba de golpe; la foto a pantalla parpadeaba; los renglones del panel aparecían, se apagaban y volvían; el cierre y el sello de Castorena no eran sobrios; los subtítulos cambiaban de tamaño.
- **Sonido**: los efectos se nivelaban por pico y sonaban hasta 7 dB más fuertes que la voz; cuatro efectos de ruido salían casi mudos por un filtro mal puesto.
- **Reglas que solo cumplía la prosa**: topes de nivel y de sonido por espacio, música preguntada, permiso de quien sale a cuadro, tipo de video.
- **Otras IA**: el paquete llevaba enlaces rotos y no había plantilla de traspaso; las guías de entrada no nombraban la skill.

Queda sin comprobar: un Dolby Vision real de iPhone, macOS, un video de más de 6 minutos de punta a punta, el sticker en un video a cámara (con la cara en plano medio apenas cabe) y, sobre todo, un video real de Emi.

## Si algo falla

- **«la palabra … no está en el video cortado»**: mira cómo quedó escrita en `palabras_limpio.json`, o ancla por segundo.
- **El render falla o sale en negro**: `npx hyperframes lint` dentro de la producción; casi siempre es un archivo que falta en `assets/`.
- **Voz e imagen desfasadas**: siempre se parte de `limpio.mp4`; nunca se recorta por fuera del flujo.
- **`rostro` no encuentra cara** (perfil, lentes oscuros, varias personas lejos): mira un cuadro y da la caja con `--caja x0,y0,x1,y1`.
- **Disco lleno**: borra `out/` de producciones viejas; los crudos son lo único que no se regenera.
