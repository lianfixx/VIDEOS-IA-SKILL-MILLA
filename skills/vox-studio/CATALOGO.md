# Catálogo de lo que ya existe

Todo lo de esta lista está programado y probado; se reutiliza tal cual. La música y los efectos **no se reciclan como archivo**: se generan nuevos para cada video. Lo que sí se recicla son las piezas de código y, si de verdad encajan, las imágenes de la [biblioteca](../../biblioteca/).

## Se genera nuevo en cada video

| Qué | Cómo cambia de un video a otro |
|---|---|
| Música | La semilla sale del título y la narración: cambian tonalidad (±3 semitonos), tempo (±6 %, y luego ajustado hasta ±8 % para que los cambios de escena caigan en pulso), progresión de acordes (5 por modo) y patrón del arpegio. El arreglo sigue los cambios de escena: escenas alternas más ligeras y final a pleno en todos los ánimos; barrido en cada corte y, salvo en `serio`, un golpe. Queda registrada en `estados/musica.json`. |
| Efectos | Mismo carácter, los ocho afinados a la tonalidad de la música de ese video y todos al mismo nivel (−20 dBFS RMS). |
| Voz, subtítulos | De la narración de ese guion, con tiempos reales. |
| Portada | Del titular y el recorte de ese video. |

## Ánimos de música (`musica.animo`)

| Ánimo | Tempo base | Para qué |
|---|---|---|
| `tension` | 92 bpm, menor | denuncia, misterio, dato incómodo |
| `energia` | 122 bpm, mayor | gym, retos, listas rápidas |
| `serio` | 78 bpm, menor, sin batería ni golpes | jurídico, institucional |
| `ironia` | 104 bpm, mayor, pizzicato | sarcasmo, absurdo, humor |
| `motivacion` | 110 bpm, mayor | superación, cierre con llamado |

Pista externa opcional (`musica.archivo` + `musica.origen`): Flow Music, solo cuando Emi la pide. Ver [FLOW-MUSIC.md](FLOW-MUSIC.md).

## Efectos (`sonido`) y remates (`remate`)

| Efecto | Qué es | Cuándo |
|---|---|---|
| `boom` | golpe grave | gancho, revelación |
| `scratch` | disco rayado | contradicción, «un momento» |
| `trombon` | trombón triste | fracaso, chiste a costa propia |
| `ding` | campanita | dato correcto, idea |
| `redoble` | ba dum tss | remate de chiste |
| `suspenso` | tan tan taaan | giro, pregunta incómoda |
| `caja` | caja registradora | dinero, costos, multas |
| `error` | zumbido de error | dato falso, lo que no hay que hacer |

El `remate` es un sello de hasta 14 letras que cae a media escena («PLOT TWIST», «ASÍ NO», «$$$»).

## Movimiento

- Entradas (`entrada`): `sello`, `desliza-izq`, `cae`, `desliza-der`, `desdobla`, `mordidas`. Los recortes usan además `sube` y nunca cruzan el titular.
- Física por clase: titular firme (sin rebote), recorte con peso (se pasa un poco y asienta), rótulo seco.
- Función de escena (`funcion`): `gancho`, `contexto`, `dato`, `giro`, `prueba`, `opinion`, `remate`, `cierre`.
- Transiciones (`transicion`): `viaje` (cámara sobre el lienzo), `barrido` (panel de color), `rasgado` (papel).
- Cierre: sello con el llamado del espacio y flecha a comentarios al terminar la voz. Pulso del recorte a media escena en escenas de más de 5 s.
- Detalles fijos: resaltador que se dibuja, rayos tras el recorte, semitono, cinta, nota manuscrita con flecha, barra de avance, subtítulos por palabra.

## Imágenes

- Estilos (`--estilo`): `ilustracion` (por defecto), `foto`, `sticker`.
- Modelos (`--modelo`): `nano-banana-2-lite` (4 créditos), `seedream/5-lite-text-to-image` (5.5 créditos).
- Fondo de recorte (`--croma`): `verde`, `magenta`, `ninguno`.
- Fotos reales: `foto` y `foto-bajar` (Apify), solo con fuente y licencia comprobadas.

## 3D y tratamientos (por defecto no; como mucho uno por video)

- Objetos 3D del compositor (`objeto3d.tipo`): `moneda`, `monedas`, `barras`, `caja`, `globo`.
- Tratamientos de imprenta (`tratamiento`): `semitono`, `duotono`.
- Blender (`blender --tipo`): `texto`, `moneda`, `caja`, `modelo`; acabados `plano` y `real`; imagen fija o giro (`secuencia`).
- ComfyUI (`comfy`): flujos exportados por Emi, con su servidor.

El momento exacto de cada uno, las cinco preguntas previas y la comparación con y sin (`comparar`): [TRES-D.md](TRES-D.md).

## Tipografías

Anton (titulares y subtítulos), Gelasio (Castorena), Caveat (notas a mano). Empaquetadas en local.

## Biblioteca de imágenes

`biblioteca/catalogo.json` lista cada recorte guardado: qué muestra, de qué video salió y cuántas veces se usó. `vox.py biblioteca --buscar "..."` lo consulta. **Reciclar solo si la imagen dice exactamente lo que la escena necesita**: se mira antes de usarla; si hay duda, se genera una nueva. No reciclar entre espacios distintos sin revisar que el estilo corresponda, ni repetir la misma imagen en videos seguidos del mismo espacio.

## Si falta algo

Un ánimo, efecto, entrada, transición o remate nuevo se programa en `scripts/sonido.py` o `plantilla/src/Vox.tsx`, con su prueba, y se añade a esta lista.
