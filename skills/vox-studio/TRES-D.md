# 3D, sombreadores, Blender y ComfyUI: cuándo sí y cuándo no

Cuatro recursos disponibles por decisión de Emi (11/11/2026). Ninguno es el estilo: son acentos. Se usan cuando explican algo mejor que un recorte plano, y cada uso se justifica por escrito (`porque`). Si la frase no sale, no se usa.

## Primero la pregunta, después la herramienta

| Lo que la escena necesita mostrar | Recurso | Costo |
|---|---|---|
| Un sujeto, una persona, un objeto con carácter | Recorte de imagen (`imagen`, Kie) | 4 a 5.5 créditos |
| Una cifra sola | `dato` (recuadro) | nada |
| Cantidades que se comparan (2 a 5 valores reales) | `objeto3d: barras` | nada; unos segundos de horno |
| Dinero, acumulación, «se junta» | `objeto3d: monedas` o `moneda` | nada |
| Un paquete, un producto genérico, «lo que hay dentro» | `objeto3d: caja` | nada |
| Alcance mundial o territorial | `objeto3d: globo` | nada |
| Una foto real que debe convivir con el papel | `tratamiento: semitono` o `duotono` | nada |
| Un objeto que necesita luz y material de verdad, texto con volumen, o un modelo 3D que Emi tiene | `blender` | minutos de CPU |
| Una imagen que Kie no puede dar (estilo entrenado, control fino de composición) y Emi tiene servidor | `comfy` | el del servidor de Emi |

Orden de preferencia cuando dos sirven: el más simple. Recorte antes que 3D del compositor; 3D del compositor antes que Blender; Kie antes que ComfyUI.

## Señales de que NO va

- Es para «que se vea más pro». Eso no es una razón.
- Más de una de cada tres escenas en 3D: `validar` avisa. El video deja de parecer papel y empieza a parecer render.
- Un objeto 3D que solo gira de adorno, sin dato ni idea detrás.
- Acabado `real` de Blender en un espacio de ilustración (personal, MILLA): rompe la unidad visual. `real` es para los espacios con estilo de foto (Castorena, PAN) y solo si el objeto lo pide.
- En `castorena`: nada de monedas saltando ni cajas girando. Si acaso, barras sobrias o un duotono.
- Barras con valores inventados o sin `fuente`: el validador las rechaza. Unas barras son un dato.

## 1. 3D dentro del compositor (`objeto3d`)

Three.js con sombreado de dos tonos en los colores del espacio y contorno de tinta. `render` lo hornea aparte y lo pega en el video (ver «Cómo se rinde»); no hay que generar nada a mano.

```json
{"id": "03", "funcion": "dato", "narracion": "...", "keyword": "...", "fuente": "INEGI, 2025",
 "objeto3d": {"tipo": "barras", "valores": [12, 19, 31], "resaltar": 2,
              "porque": "la diferencia entre los tres años se entiende de un vistazo con altura"}}
```

Tipos: `moneda`, `monedas` (`valores[0]` = cuántas, entero de 2 a 8; tres si se omite), `barras` (2 a 5 valores; `resaltar` = índice desde 0 de la barra en color de acento, por defecto la última), `caja`, `globo`. Ocupa el lugar del recorte: no se combina con `imagen_archivo`, `dato` ni `secuencia`.

## 2. Sombreadores de imprenta (`tratamiento`)

Para que una foto o un recorte realista se vea impreso en el mismo papel que lo demás.

- `semitono`: trama de puntos a 45° en tinta sobre papel. Para fotos documentales, retratos de prensa, archivo.
- `duotono`: sombras en tinta, medios tonos en el acento, luces en papel. Para dar unidad de marca a una foto.

Se añade a una escena que ya tiene `imagen_archivo`: `"tratamiento": "semitono"`. Una foto real (`foto_real`) conserva su marco blanco y deja de pasarse a grises; si es la imagen de la portada, la portada también sale tratada. No usar en ilustraciones: ya están en estilo y la trama las ensucia.

## 3. Blender (`blender`)

Render aparte, con fondo transparente, que entra al video como un recorte más (o como secuencia que gira).

```bash
$V blender-instalar                      # una vez por máquina; descarga unos 430 MB
$V blender --dir $D --perfil personal --tipo texto --texto "73%" --out public/img/cifra.png \
   --porque "la cifra es el gancho y necesita peso físico en pantalla"
$V blender --dir $D --perfil castorena --tipo modelo --modelo mazo.glb --acabado real --giro 48 \
   --out public/seq/mazo --porque "el objeto real del despacho, visto por todos sus lados"
```

- Tipos: `texto` (letras con volumen), `moneda`, `caja`, `modelo` (un `.glb`, `.gltf`, `.obj` o `.stl` que Emi proporcione; no se descargan modelos de terceros sin licencia comprobada).
- `--acabado plano` (por defecto): dos tonos con el color de la marca y contorno de tinta. `--acabado real`: materiales físicos y luz de estudio.
- `--out` siempre dentro de `public/`. Sin `--giro`: un archivo `.png` que se usa como `imagen_archivo` (`img/cifra.png`, sin el `public/`). Con `--giro N`: una carpeta con N cuadros a velocidad constante que cierran en bucle; en la escena, `"secuencia": {"carpeta": "seq/mazo", "cuadros": 48}`. Repetir el comando sobre la misma carpeta borra los cuadros anteriores.
- Un modelo con varias piezas o con nodo padre se centra y gira completo. En acabado `real` se respetan sus materiales; una pieza sin material recibe el color de acento.
- El texto usa la tipografía de Blender salvo que se pase `--fuente` con un archivo `.ttf` u `.otf`.
- El resultado se recorta a su contenido; los tiempos están más abajo.
- Cada uso queda en `estados/blender.json` con su `porque`.

## 4. ComfyUI (`comfy`)

ComfyUI necesita tarjeta gráfica y modelos de varios gigas. **Este entorno en la nube no tiene tarjeta gráfica**, así que aquí no se instala: la herramienta se conecta al servidor de ComfyUI que Emi tenga (su computadora o uno rentado).

```bash
export COMFY_URL=https://direccion-del-servidor     # y COMFY_TOKEN si lo protege una llave
# http solo se acepta si ComfyUI corre en la misma máquina: http://127.0.0.1:8188
$V comfy --dir $D --flujo flujos/retrato.json --out public/img/04.png \
   --porque "necesita el mismo personaje que el video anterior y Kie no lo conserva" --execute
```

- `--flujo` es el JSON que ComfyUI exporta con «Export (API)». Debe tener un nodo que guarde imagen (`SaveImage`). Sin `--execute` el comando solo comprueba servidor y flujo; no envía nada.
- Sin `COMFY_URL` el comando se detiene y lo dice; nunca simula un resultado.
- El dominio del servidor debe estar permitido en la red del entorno; si no, se le pide a Emi autorizarlo.
- Lo generado se revisa igual que una imagen de Kie y sigue las mismas reglas (sin logos ni texto inventado; en `milla`, nada de modelos de OpenAI).
- Estado: el cliente está probado contra un servidor simulado. **No se ha probado contra un ComfyUI real** porque Emi aún no tiene uno conectado.

## Cómo se rinde: el horno

El 3D del compositor y los sombreadores necesitan WebGL. Rendir todo el video con WebGL por software resultó inviable aquí (un video de 21 s no terminaba en 15 minutos), así que se **hornean aparte**:

1. `render` detecta las escenas con `objeto3d` o `tratamiento`.
2. Rinde cada una en una composición aparte (`Horno`, fondo transparente, `--gl=swangle`): el objeto como secuencia de PNG de 720 px, la foto tratada como un solo PNG de hasta 900 px.
3. A las secuencias les recorta el aire transparente (el mismo recorte para todos los cuadros, para que el objeto no cambie de tamaño).
4. Lo arma y lo comprueba en `out/` y solo entonces lo pasa a `public/horno/`, con una firma del pedido, los colores y el código que dibuja: si nada cambió, no se vuelve a hornear; si algo falló o salió vacío, no queda nada a medias. Lo horneado que ya ninguna escena pide se borra.
5. El video principal se rinde desde `src/data/_render.json`, donde esas escenas ya son imágenes. No usa WebGL.

`video.json` conserva el pedido original; `_render.json` es derivado y se regenera en cada render. Por eso se rinde siempre con `vox.py render`: Remotion directo sobre `video.json` deja esas escenas sin dibujar.

Los colores salen exactos: sin mapeo de tonos, la cara iluminada de un objeto es el color del espacio y la sombra es una sola banda más oscura; el sombreador escribe papel, tinta y acento tal como están en el perfil.

Tiempos medidos (4 núcleos, sin tarjeta gráfica): hornear 30 cuadros, 8 s; el demo de 21 s con dos objetos 3D, una foto tratada y dos piezas de Blender, 4 min 29 s en total. Blender: imagen de 1024 px en acabado plano, 6 s; secuencia de 24 cuadros de 640 px, 43 s en plano y 129 s en real.

## Revisión

Se revisan como cualquier escena: `revisar`, hoja de transiciones y hoja a tamaño teléfono. Un objeto 3D debe seguir leyéndose en el teléfono; si no, es demasiado detalle.
