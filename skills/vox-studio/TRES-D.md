# 3D, sombreadores, Blender y ComfyUI: el momento exacto de cada uno

Emi pidió tener estos recursos «cuando sea necesario, para eso hay que razonar» (11/11/2026). El primer demo los metió en cuatro de cinco escenas y a Emi **le gustó menos** que el anterior. Esta guía existe para que eso no vuelva a pasar.

## El principio

Lo que hace que estos videos se vean hechos por una persona es el **recorte ilustrado**: tiene trazo, carácter y humor. Un objeto 3D es más limpio y más frío. Cada vez que un 3D ocupa el lugar de un recorte, el video pierde algo de eso.

Por eso la respuesta por defecto es **no**. Lo normal es un video sin ninguno de estos recursos; a veces uno; nunca más de uno salvo que Emi lo pida. Y cuando se usa, es porque en ese segundo exacto **el movimiento es la idea**: algo que crece, que se acumula o que gira dice lo que la narración está diciendo, y un dibujo quieto no podría.

## Las cinco preguntas (en orden; al primer «no», recorte)

1. **¿Qué dice la voz en esa escena?** Solo hay tres cosas que el 3D explica mejor: una **comparación de cantidades**, una **acumulación** y un **objeto real que hay que ver por todos lados**. Si la frase habla de otra cosa (una persona, una emoción, una crítica, un chiste), va recorte.
2. **¿El movimiento es la idea?** Las barras suben *mientras* se dice «el triple»; las monedas se apilan *mientras* se dice «cada mes se suma». Si el objeto podría estar quieto y decir lo mismo, va recorte.
3. **¿Qué se pierde?** Si esa escena carga el humor, la crítica o la postura de Emi, se pierde demasiado: va recorte.
4. **¿Es el mejor momento del video para gastarlo?** Hay un solo 3D por video. Va donde el argumento depende de una magnitud, casi siempre la escena de `dato` o de `prueba`. Si hay dos candidatas, se queda la que más explica y la otra vuelve a recorte o a `dato`.
5. **¿Emi lo vio y lo eligió?** Antes de rendir el video se le enseña la escena de las dos formas (`comparar`, abajo). Si duda, gana la versión plana.

La respuesta a las preguntas 1 y 2 es el `porque` que el guion exige. Un `porque` que no menciona lo que dice la voz («se ve más dinámico», «llama la atención») no es una razón.

## El momento de cada recurso

| Recurso | Va cuando… | En qué escena | No va cuando… | En su lugar |
|---|---|---|---|---|
| **Barras 3D** | la voz compara 2 a 5 cantidades reales de la misma unidad y lo que importa es **la diferencia** | `dato`, `prueba` | hay una sola cifra; las cantidades se parecen (la mayor no llega a 1.3 veces la menor); no hay fuente | `dato` (la cifra en recuadro) |
| **Monedas 3D** | la voz describe dinero que **se acumula o se suma** y apilarlo es la idea | `dato`, `prueba`, `giro` | el dinero es solo el tema («es caro», «cobran de más») | recorte ilustrado (billete, cartera, mano) |
| **Globo 3D** | la idea es **«en todas partes»** y que gire lo dice | `contexto`, `dato` | se habla de un país o una ciudad concretos | recorte de mapa o de lugar |
| **Caja 3D** | casi nunca: solo si «un paquete cerrado» es la idea y no hay recorte que lo diga | `contexto`, `giro` | se puede ilustrar el producto real | recorte del producto |
| **Semitono / duotono** | hay una **foto real** (persona, documento, hecho) que debe convivir con el papel | cualquiera | la imagen es una ilustración: ya está en estilo y la trama la ensucia | la imagen tal cual |
| **Blender, modelo propio** | Emi tiene el modelo de un **objeto real** y verlo girar enseña algo que una foto no | `contexto`, `dato`, `prueba`, `giro` | solo adornaría; no hay modelo de Emi | foto real o recorte |
| **Blender, texto con volumen** | una cifra o palabra es el tema entero del video y Emi lo pide para la portada o el gancho | `gancho` | en cualquier otro caso: el titular y `dato` ya hacen ese trabajo y están en estilo | titular o `dato` |
| **Blender, acabado real** | espacios de foto (Castorena, PAN) y un objeto serio que debe verse verdadero | las de arriba | espacios de ilustración (personal, MILLA): rompe la unidad | acabado plano o recorte |
| **ComfyUI** | hace falta el mismo personaje o un estilo entrenado que Kie no conserva, y Emi tiene servidor | — | Kie lo resuelve | `imagen` (Kie) |

**Nunca**, sea cual sea el recurso: en la escena de `opinion` ni en la de `cierre`. Ese momento es de Emi, no de un objeto. Y los objetos del compositor tampoco en el `gancho`: el primer cuadro necesita un sujeto con carácter.

**Por espacio.** `personal` y `milla`: barras o monedas cuando el dato lo pide; fotos reales con semitono. `castorena`: sobrio; si acaso barras o un duotono, y Blender real solo con un objeto del despacho; nada que salte o gire de adorno. `pan`: barras para cifras públicas con fuente; duotono para fotos de archivo.

## Ejemplos razonados

| La voz dice | Decisión | Por qué |
|---|---|---|
| «Un juicio laboral tarda hoy 3 años; en 2019 tardaba 1.» | Barras `[1, 3]` | Dos cantidades, misma unidad, la diferencia es el punto. La barra crece cuando se oye «3 años». |
| «El 73 % nunca reclama.» | `dato` «73 %» | Una sola cifra: no hay nada que comparar. |
| «Cada quincena te descuentan 200. En un año son casi 5 mil.» | Monedas | La idea es la suma que crece; la pila sube con la frase. |
| «Los abogados cobran carísimo.» | Recorte | El dinero es el tema, no un proceso. Un recorte con carácter (y chiste) dice más. |
| «Esto pasa en todo el mundo.» | Globo, si es el contexto del video | Girar dice «en todas partes». |
| «En México pasa esto.» | Recorte | Un lugar concreto: el globo girando no añade nada. |
| «Yo creo que esto es un abuso.» | Recorte, siempre | Es la opinión de Emi. |
| Foto real de una sesión del Congreso | Semitono | Es fotográfica y debe convivir con el papel. |
| Ilustración de un mazo generada con Kie | Sin tratamiento | Ya está en estilo. |

Los ejemplos son para razonar; las cifras de un video real siempre salen de una fuente.

## Lo que el validador exige

- `objeto3d` y `secuencia` llevan `porque`; sin él, error.
- **Como mucho una escena con 3D por video.** Más, solo si Emi lo pidió: se escribe su pedido, con sus palabras y la fecha, en `excepcion_3d`. No se usa por iniciativa propia.
- Cada objeto, solo en las escenas de la tabla; ninguno en `opinion` ni `cierre`.
- Barras: 2 a 5 valores reales y `fuente`. Aviso si se parecen demasiado.
- Un solo tratamiento por video (no mezclar semitono y duotono). Aviso si se aplica a algo que no es `foto_real`.
- Aviso si la escena con 3D no dice cómo se vería en plano (`alternativa_plana`).

## Enseñárselo a Emi antes de rendir: `comparar`

```json
{"id": "03", "funcion": "dato", "narracion": "...", "keyword": "...", "fuente": "INEGI, 2025",
 "objeto3d": {"tipo": "barras", "valores": [1, 3], "resaltar": 1,
              "porque": "la voz compara 1 y 3 años: la diferencia se ve cuando la barra crece"},
 "alternativa_plana": {"dato": "x3"}}
```

```bash
$V comparar $D --escena 03     # out/comparacion-03.png: A con el recurso, B en plano
```

`alternativa_plana` es cómo se vería la escena sin 3D: `{"dato": "..."}` o `{"imagen_archivo": "img/..."}`. Si falta, unas barras se comparan contra su cifra en recuadro y una foto tratada contra la foto sin tratar. Se le enseña la hoja a Emi y se deja la que elija; su elección se guarda con `aprender`.

## Cómo se escribe cada uno

**Objetos del compositor.** `"objeto3d": {"tipo": ..., "valores": [...], "resaltar": n, "porque": "..."}`. Tipos: `moneda`, `monedas` (`valores[0]` = cuántas, entero de 2 a 8; tres si se omite), `barras` (2 a 5 valores; `resaltar` = índice desde 0 de la barra en color de acento, por defecto la última), `caja`, `globo`. Ocupa el lugar del recorte: no se combina con `imagen_archivo`, `dato` ni `secuencia`.

**Tratamientos.** `"tratamiento": "semitono"` (trama de puntos a 45° en tinta sobre papel; fotos documentales, prensa, archivo) o `"duotono"` (sombras en tinta, medios en el acento, luces en papel; unidad de marca) en una escena con `imagen_archivo`. Una foto real conserva su marco blanco; si es la imagen de la portada, la portada también sale tratada.

**Blender.**

```bash
$V blender-instalar                      # una vez por máquina; descarga unos 430 MB
$V blender --dir $D --perfil castorena --tipo modelo --modelo mazo.glb --acabado real --giro 48 \
   --out public/seq/mazo --porque "es el objeto real del despacho y verlo girar enseña el grabado del reverso"
```

- Tipos: `texto`, `moneda`, `caja`, `modelo` (un `.glb`, `.gltf`, `.obj` o `.stl` que Emi proporcione; no se descargan modelos de terceros sin licencia comprobada).
- `--acabado plano` (por defecto): dos tonos con el color de la marca y contorno de tinta. `--acabado real`: materiales físicos y luz de estudio.
- `--out` siempre dentro de `public/`. Sin `--giro`: un `.png` que se usa como `imagen_archivo` (`img/x.png`, sin el `public/`). Con `--giro N`: una carpeta con N cuadros a velocidad constante que cierran en bucle; en la escena, `"secuencia": {"carpeta": "seq/mazo", "cuadros": 48, "porque": "..."}`. Repetir el comando sobre la misma carpeta borra los cuadros anteriores.
- Un modelo con varias piezas o con nodo padre se centra y gira completo. En acabado `real` se respetan sus materiales; una pieza sin material recibe el color de acento.
- El texto usa la tipografía de Blender salvo que se pase `--fuente` con un `.ttf` u `.otf`.
- Cada uso queda en `estados/blender.json` con su `porque`.

**ComfyUI.** Necesita tarjeta gráfica y modelos de varios gigas. **Este entorno en la nube no tiene tarjeta gráfica**: la herramienta se conecta al servidor que Emi tenga.

```bash
export COMFY_URL=https://direccion-del-servidor     # y COMFY_TOKEN si lo protege una llave
# http solo se acepta si ComfyUI corre en la misma máquina: http://127.0.0.1:8188
$V comfy --dir $D --flujo flujos/retrato.json --out public/img/04.png \
   --porque "necesita el mismo personaje que el video anterior y Kie no lo conserva" --execute
```

- `--flujo` es el JSON de «Export (API)» y debe tener un nodo que guarde imagen. Sin `--execute` solo comprueba servidor y flujo.
- Sin `COMFY_URL` el comando se detiene y lo dice; nunca simula un resultado.
- El dominio del servidor debe estar permitido en la red del entorno; si no, se le pide a Emi autorizarlo.
- Lo generado sigue las reglas de cualquier imagen (sin logos ni texto inventado; en `milla`, nada de modelos de OpenAI).
- Estado: probado solo contra un servidor simulado. **No se ha probado contra un ComfyUI real.**

## Cómo se rinde: el horno

El 3D del compositor y los sombreadores necesitan WebGL. Rendir todo el video con WebGL por software resultó inviable aquí (un video de 21 s no terminaba en 15 minutos), así que se **hornean aparte**:

1. `render` detecta las escenas con `objeto3d` o `tratamiento`.
2. Rinde cada una en una composición aparte (`Horno`, fondo transparente, `--gl=swangle`): el objeto como secuencia de PNG de 720 px, la foto tratada como un solo PNG de hasta 900 px.
3. A las secuencias les recorta el aire transparente (el mismo recorte para todos los cuadros, para que el objeto no cambie de tamaño).
4. Lo arma y lo comprueba en `out/` y solo entonces lo pasa a `public/horno/`, con una firma del pedido, los colores y el código que dibuja: si nada cambió, no se vuelve a hornear; si algo falló o salió vacío, no queda nada a medias. Lo horneado que ya ninguna escena pide se borra.
5. El video principal se rinde desde `src/data/_render.json`, donde esas escenas ya son imágenes. No usa WebGL.

`video.json` conserva el pedido original; `_render.json` es derivado y se regenera en cada render. Por eso se rinde siempre con `vox.py render`: Remotion directo sobre `video.json` deja esas escenas sin dibujar.

Los colores salen exactos: sin mapeo de tonos, la cara iluminada de un objeto es el color del espacio y la sombra es una sola banda más oscura; el sombreador escribe papel, tinta y acento tal como están en el perfil.

Tiempos medidos (4 núcleos, sin tarjeta gráfica): hornear 30 cuadros, 8 s; un video de 21 s, unos 4 min 30 s en total. Blender: imagen de 1024 px en acabado plano, 6 s; secuencia de 24 cuadros de 640 px, 43 s en plano y 129 s en real.

## Revisión

Se revisan como cualquier escena: `revisar`, hoja de transiciones y hoja a tamaño teléfono. Un objeto 3D debe seguir leyéndose en el teléfono; si no, es demasiado detalle. Después de cada video con uno de estos recursos se le pregunta a Emi si le sumó, y la respuesta se guarda con `aprender`: esta guía se corrige con lo que él diga.
