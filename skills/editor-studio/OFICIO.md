# Oficio: los criterios y los números

Lo que aquí se dice vale mientras Emi no diga otra cosa. Lo que él corrija se anota con `aprender` y manda.

## Cortes

| Ritmo | Silencio que se toca | Aire que queda a cada lado | Para |
|---|---|---|---|
| `apretado` | desde 0.30 s | 0.08 s | solo si Emi lo pide |
| `natural` (por defecto) | desde 0.55 s | 0.16 s (0.24 s tras un punto) | casi todo |
| `minimo` | desde 1.20 s | 0.30 s | discursos, entrevistas, Castorena |

- El silencio se mide en el audio: todo lo que quede 16 dB bajo la mediana de la voz, en ventanas de 10 ms. Un ruido de menos de 60 ms no parte un silencio.
- Con ruido o música de fondo fuertes (menos de 12 dB bajo la voz) el audio ya no deja ver las pausas: el umbral sube con el piso de ruido, se suman las pausas que marca la transcripción y `cortes` lo avisa. Esa vista previa se escucha con más cuidado.
- Una frase repetida con otras frases en medio puede ser énfasis y no una toma repetida: sale como `dudoso` y dice qué frases se irían.
- Los cortes valen para la transcripción con la que se propusieron: si se vuelve a transcribir, se repite `cortes`. Si se vuelve a cortar, se repiten `rostro` y `armar`; `render` se niega a mezclar una voz nueva con una imagen vieja.
- Cada corte cae en cuadro exacto y lleva 6 ms de fundido de audio. Nunca dentro de una palabra: la transcripción manda sobre la energía.
- Dos cortes separados por menos de 0.25 s sin palabra en medio son uno solo: dejar una rebanada de ambiente suena a tropiezo.
- El video arranca pegado a la voz y termina con medio segundo de cola.
- **Muletillas.** Sonidos de relleno («eh», «mmm») se proponen siempre. Las palabras que a veces dicen algo («este», «pues», «bueno», «o sea») salen como `dudoso`: se lee la frase y se decide. Emi pidió quitar casi todas; se dejan las que dan naturalidad o sostienen el ritmo de una frase.
- **Tomas repetidas y arranques en falso.** Gana la última completa. Son propuestas: se leen las dos y, si la primera estaba mejor dicha, se propone esa.
- **Groserías.** No se cortan: se tapan con un tono y en subtítulos se ve la inicial con asteriscos. «Güey», «pinche» y similares son modismo: salen como `avisar` y se le pregunta a Emi por espacio (`decidir --censura 0=tapar`).
- Tras cortar, `cortar` comprueba la duración exacta y que ningún empalme caiga en plena voz. Cualquier aviso se escucha.
- Si la transcripción es aproximada (viene de SRT o de frases), solo se proponen silencios; lo demás se marca a mano con `decidir --quitar 12.4~18.9 --motivo "…"`.

## El mapa del video (antes del plan)

Con la transcripción completa leída se escribe, para uno mismo y para enseñárselo a Emi:

- **Gancho** (0 a 3 s): ¿la primera frase da una razón para quedarse? Si no, se le proponen dos o tres ganchos de texto en pantalla, o mover al inicio una frase fuerte que dijo después.
- **Promesa**: qué va a obtener quien se quede.
- **Desarrollo**: las ideas, una por tramo. Lo que se repite o se desvía se propone como corte.
- **Giro o remate**: el momento que se va a recordar.
- **Cierre**: una pregunta que divida opiniones o un llamado concreto.

## Subtítulos: se razonan, no se preguntan

| Espacio y contexto | Modo | Aspecto | Por qué |
|---|---|---|---|
| personal, reel rápido | `karaoke`, 2–3 palabras, mayúsculas | contorno, palabra activa en el acento | ritmo y lectura sin sonido |
| personal, vlog o historia | `karaoke`, 3–4 palabras, sin mayúsculas | contorno | más calma |
| milla, explicación | `karaoke`, 3–4 palabras, sin mayúsculas | caja | se lee como información, no como grito |
| castorena | `frase`, hasta 6 palabras | sobrio, con serif | institucional; nada se ilumina |
| pan, crítica con datos | `karaoke`, 2–3 palabras, mayúsculas | contorno | énfasis |
| entrevista o varias voces | `frase` | sobrio o caja | no marear cuando cambian de voz |
| YouTube horizontal | `frase`, 5–7 palabras | caja, abajo | costumbre del formato |

- Un grupo a la vez. Se corta en pausa de 0.25 s, en punto o al llegar al máximo. Entre grupos encadenados el cambio es instantáneo; solo hay entrada tras una pausa real.
- Zona `pecho` por defecto; `abajo` si el encuadre lo pide. Ninguna pieza de texto usa esa franja.
- Los signos se quitan, pero el punto y la coma entre cifras se quedan: «3.5%» y «$1,500.00» salen tal cual.
- Durante un zoom la cara ocupa más cuadro: el validador lo tiene en cuenta al colocar un texto.
- Se corrigen a mano los nombres propios que el reconocimiento escriba mal (en `palabras_limpio.json`).
- La razón del estilo se escribe en `plan.json → subtitulos.razon`.

## Piezas

Cada una se ancla a lo que se oye: `"ancla": {"palabra": "contrato", "n": 1, "desfase": -0.1}` (la n-ésima vez que se dice), `{"palabra": "…", "al_final": true}` o, con transcripción aproximada, `{"t": 12.4}`. Duración con `dura` o con `hasta` (otra ancla).

| Pieza | Nivel | Campos | Límite |
|---|---|---|---|
| `titulo` | 1 | `texto` (con `*acento*`) | 42 letras |
| `rotulo` | 1 | `texto`, `sub` | 34 |
| `fuente` | 1 | `texto` | 60 |
| `foto` | 1 (pantalla) · 2 (tarjeta) | `archivo`, `origen_descripcion`, `pie`, `modo` | — |
| `cierre` | 1 | `texto` | 22 |
| `zoom` | 2 | `z` de 1.04 a 1.20, `modo` `punch` o `push` | no en el cuadro de un corte |
| `sello` | 2 | `texto` | 14 |
| `dato` | 2 | `cifra`, `etiqueta`, `fuente` | sin fuente no pasa |
| `barra` | 2 | — | — |
| `panel` | 2 | `titulo`, `items` (hasta 4) o `imagen` | nada más en pantalla mientras dura |
| `barrido` | 2 | — | 0.5 s |
| `detras` | 3 | `texto` | 12; pide `recorte` |
| `inserto` | 3 | `archivo`, `origen` | generado: cotizado y aprobado |
| `sticker` | 3 | `archivo` (WebM con transparencia), `origen`, `esquina` (`abajo-izq`, `abajo-der`, `arriba-izq`, `arriba-der`) | nunca sobre la cara ni sobre los subtítulos |
| `particulas` | 3 | — | una cada 25 s |

El `id` de cada pieza lleva minúsculas, números y guiones, empieza por letra y no repite nombres del motor (`cam`, `subs`, `g1`, `rc…`): un id mal escrito apagaría todas las animaciones, así que el validador lo rechaza.

Zonas de texto: `arriba` (sobre la cabeza, si hay sitio), `torso` (entre la cara y los subtítulos) y `medio` (solo si no hay cara ahí). El validador mide dónde está el rostro en ese tramo, ajusta la zona y avisa; si no cabe, es error: se mueve la pieza de segundo, se acorta, o se usa una foto o un panel.

Reglas que el validador también cumple: un `barrido` solo va sobre un corte (su centro cae en un empalme) y apaga los subtítulos mientras pasa; un renglón de `panel` no pasa de 32 letras; una `foto` en tarjeta no tapa la cara; como mucho dos `detras` por video; un título que no cabe legible se rechaza en vez de encogerse. Los subtítulos llevan un solo tamaño en todo el video. En los espacios de movimiento `sobrio` los títulos van en altas y bajas, sin sombras duras, sin giros y sin flecha.

Paletas de serie: una serie de videos puede llevar colores propios, aprobados por Emi, sin tocar la marca del espacio. Viven en `espacios/<espacio>/paletas.json` (con `aprobada_por_emi`) y se eligen con `"paleta": "nombre"` en `plan.json`. Primera: `ia-derecho` (personal, 13/11/2026): papel crema y acento naranja de la marca personal, tinta azul #0D1B2A y dorado #C8A96B tomados de Castorena.

Colores: sobre fondo oscuro se usa el acento de la marca solo si se lee (contraste de 4.5 o más); si no, entra su color de apoyo. Por eso en PAN la palabra activa y los resaltes van en dorado y no en azul.

Zona segura en 9:16: x de 90 a 960, y de 230 a 1440. Lo demás lo tapa la interfaz de TikTok y Reels.

## Movimiento

- Una sola cosa protagonista a la vez. Entradas de 0.3 a 0.6 s, salidas de 0.2 a 0.35 s.
- Zooms suaves hacia la cara: entran con desaceleración, derivan apenas y regresan sin golpe. Uno cada 4 a 8 s de cámara completa, en la palabra clave.
- Perfil por espacio (`edicion.json → movimiento`): `suave`, `energico` o `sobrio`.
- Nada tiembla ni rebota como caricatura. Nada se mueve sin decir algo.

## Sonido

- Voz a −16 LUFS; efectos de 6 a 14 unidades de sonoridad por debajo de la voz (8 por defecto), medidos por cómo suenan y no por su pico: un tono puro con el mismo pico que la voz se oye mucho más fuerte; música 18 LU bajo la voz; entrega a −14 LUFS con pico máximo de −1.5 dBTP.
- Efectos disponibles: `pop`, `clic`, `deslizar`, `golpe`, `subida`, `ding`, `papel`, `teclas`. Se sintetizan aquí. Uno por idea; el mismo cuatro veces seguidas pierde la gracia. `deslizar` y `subida` arrancan antes de la pieza y terminan en el golpe.
- Densidad por espacio: personal y pan `media`, milla `minima`, castorena `ninguna`.
- Música: decisión de Emi en cada video. Si la quiere, la pista entra como archivo en `assets/` con `origen` (de dónde salió y con qué derecho se usa). Para componerla con código o traerla de Flow Music se usa lo que ya documenta Vox Studio; aquí no se duplica.
- Bibliotecas externas de efectos: hoy no se usa ninguna. El radar semanal revisa novedades y licencias; un sonido ajeno solo entra con su licencia leída y anotada.

## Color

`natural` por defecto: contraste 1.04 y saturación 1.05, cuidando la piel. `ninguno` deja el video como viene. El HDR del iPhone se convierte a color estándar al ingerir; si no, sale lavado. Cualquier look con carácter se le enseña a Emi en una muestra antes.

## Filtrar el estilo

La primera vez en cada espacio (método de filtrado, de lo general a lo particular):

1. Con el video ya cortado, se proponen en texto de 6 a 10 direcciones de estilo que le queden a ese espacio y ese tipo de video.
2. Emi descarta; de las que queden se arma una muestra **mínima** y una **máxima** sobre cuadros reales (`muestra --nombre …`).
3. Elige hasta tres; con ellas se arman más escenas del mismo video.
4. Elige una. Se rinde el video, corrige lo que no le guste y, cuando diga que así, `edicion.json` del espacio pasa a `"estado": "aprobado"` con lo que eligió, y la lección se guarda con `aprender`.

## Revisión

Lista de `out/revision.json` (cada punto se contesta mirando las hojas): los 2 primeros segundos enganchan · todo se lee en teléfono · nada tapa la cara · nada bajo la interfaz de la app · solo colores y fuentes del espacio · cada pieza dice algo de lo que se oye · sin cuadros rotos ni vacíos · los subtítulos van con la voz · el último cuadro cierra · se ve hecho por una persona.

Los tres peores defectos, con su segundo, se corrigen primero; se vuelve a rendir y a revisar. La revisión solo vale para el archivo actual.
