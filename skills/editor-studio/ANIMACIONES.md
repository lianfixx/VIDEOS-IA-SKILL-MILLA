# Animaciones y apoyos dentro del video

Orden de preferencia, acordado con Emi el 11/11/2026: **lo real → animación por código → imagen ilustrada generada → video generado**. Se usan todos los recursos, cada uno en su momento y con su porqué.

## 1 · Lo real (cualquier nivel)

Fotos, capturas de pantalla, documentos y tomas de Emi. Van a `assets/` y entran como `foto` (pantalla completa o tarjeta) o dentro de un `panel`. Siempre con `origen_descripcion`. Si muestra a otra persona, un expediente o datos de alguien, se tapa lo sensible o no se usa.

## 2 · Animación por código (nivel 3, sin costo)

Un inserto de 2 a 6 s hecho con los motores que ya existen, en el estilo del mismo espacio:

- **Pizarra Studio** para explicar un proceso o una analogía dibujada.
- **Vox Studio** para un dato, un recorte o un titular en collage.

Se produce en su propia skill, con sus reglas, como una escena suelta sin voz, y el MP4 se copia a `assets/` de esta producción. Aquí entra como `inserto` con `"origen": "codigo-pizarra"` o `"codigo-vox"`. La voz de Emi sigue sonando debajo: el inserto no trae audio.

## 3 · Texto detrás de la persona (nivel 3, sin costo)

`detras` pone una palabra grande entre el fondo y quien habla. `$E recorte $D` recorta a la persona solo en esos tramos (entre 1 y 2 cuadros por segundo en este entorno: unos 25 s de trabajo por cada segundo de video, medido el 11/11/2026 con 1.5 s). Se lee mejor con la cabeza tapando entre un tercio y la mitad de la palabra: se revisa en la muestra y, si la tapa de más, se cambia la palabra o el segundo. Como mucho dos por video (el validador rechaza el tercero). Si la cabeza taparía más de la mitad de la palabra, el validador avisa: en encuadre cerrado casi nunca se lee. El recorte queda atado a su tramo y a su corte: si cambian, hay que repetir `recorte`.

## 4 · Imagen ilustrada generada (nivel 3, con costo)

Con Kie y `nano-banana-2-lite` (4 créditos por imagen, medido el 10/11/2026), en el estilo de imagen del espacio. Nunca imágenes de OpenAI. Entra como `foto` con su `origen_descripcion` («generada con Kie, prompt en estados/…»). Nunca un rostro que parezca cliente, testigo o persona real.

## 5 · Video generado (nivel 3, con costo y con el sí de Emi en cada video)

Autorizado por Emi el 11/11/2026 como opción, no como costumbre. Método (hoja de personajes → cuadro inicial → cuadro final → animación entre los dos):

1. **Plan de escenas** en tabla: segundo, frase, idea visual, dónde va (pantalla completa, sticker o detrás), duración y costo. Una escena por idea, con **una** acción clara que cuente lo que se dice; nada de «solo un zoom».
2. **Cotizar y aprobar**: `$E aprobar $D gasto --por Emi --creditos N --nota "…"`. Sin eso el validador no deja pasar un inserto generado.
3. **Consistencia**: primero una hoja del personaje o del estilo; se usa como referencia en todas las escenas.
4. **Generar** cuadro inicial y final con Kie; animar con Kling por Kie (catálogo leído el 11/11/2026: Kling 3.0 y 4.0, incluido cuadro inicial + final). Cámara fija, salvo un movimiento suave de la tabla de abajo con su porqué en el plan. Sin logos, sin marcas, sin texto dentro de la imagen. El prompt se escribe como dice «Cómo se escribe el prompt de cada clip».
5. **Transparencia**: lo que va como `sticker` se genera sobre verde plano y se recorta con el recorte de croma de Vox Studio; se entrega como WebM con transparencia.
6. Revisar cada clip (inicio, mitad y final) antes de montarlo: que la acción tenga sentido y nada se deforme. Si algo falla, se regenera con la corrección de esa falla, no con todas.

**Sin comprobar todavía**: ningún clip de Kling se ha generado desde este repositorio; su esquema exacto y su costo real se medirán en el primer uso autorizado y se anotarán aquí. Higgsfield no está contratado ni hace falta mientras Kie lo cubra.

### Cómo se escribe el prompt de cada clip

Vale para el cuadro inicial, el cuadro final y la animación. Los términos de cámara van en inglés, porque los modelos de imagen y video los interpretan con más precisión así; la escena puede ir en español. Orden fijo:

1. **Escena**: quién, qué hace y dónde, en una o dos frases concretas. Una sola acción.
2. **Cámara**: un movimiento (o ninguno), un ángulo y un plano. Nunca dos de la misma clase: se contradicen y el clip sale confuso.
3. **Luz y acabado**: sí se pueden sumar.
4. **Correcciones**: solo las que hagan falta.
5. **Formato**, al final y el mismo del video que se edita: `vertical 9:16 framing for mobile`, `horizontal 16:9 widescreen framing` o `square 1:1 framing`.

**Movimiento.** Por defecto `static locked-off camera, no camera movement`. Un movimiento suave solo cuando el movimiento es la idea y su porqué queda en el plan de escenas que Emi aprueba en el paso 2:

| Cuando la idea es… | Movimiento | En el prompt |
|---|---|---|
| acercarse a lo que importa | acercamiento lento | `slow dolly in toward the subject, steady and smooth` |
| mostrar dónde ocurre | alejamiento lento | `slow dolly out, the frame widens to reveal the surroundings` |
| acompañar a alguien que camina | seguimiento lateral | `lateral tracking shot at the subject's walking pace` |
| recorrer un lugar o un documento | paneo | `slow horizontal pan, the camera pivots on a fixed point` |
| ir de abajo hacia arriba (de los pies a la cara, de la base a lo alto) | tilt | `slow tilt up, the camera pivots on a fixed point` |

**Ángulo** (por defecto, altura de ojos):

| Para decir… | Ángulo | En el prompt |
|---|---|---|
| neutral, de tú a tú | altura de ojos | `eye-level shot` |
| fuerza, autoridad | contrapicado | `low-angle shot looking up at the subject` |
| pequeñez, vulnerabilidad | picado | `high-angle shot looking down at the subject` |
| un escritorio, documentos, una mesa | cenital | `top-down overhead shot` |
| una conversación | sobre el hombro | `over-the-shoulder shot` |
| una silueta limpia, alguien que piensa | perfil | `side profile shot` |

**Plano**: `wide establishing shot` (ubica el lugar), `full shot, head to toe`, `medium shot from the waist up`, `close-up of the face`, `extreme close-up detail` (manos que firman, un sello, una pluma).

**Luz y acabado** que no delatan a una IA: `soft natural window light from one side`, `clean soft studio lighting`, `documentary style, natural available light`, y con personas `photorealistic, natural skin texture with pores, no artificial smoothing`. En lo que va como `sticker` sobre verde, solo luz pareja y suave: nada de contraluz, luz de borde, neón, reflejos, rayos de luz, siluetas, destellos de lente ni fondo desenfocado, porque dejan halo y derrame de color que el recorte no quita.

**Correcciones** (se añade la de la falla que apareció y se regenera):

| Falla | Se añade |
|---|---|
| hace varias cosas a la vez | `the subject performs only one simple action during the entire shot` |
| objetos que flotan o se mueven raro | `realistic physics, objects have weight and natural gravity` |
| manos o dedos de más | `anatomically correct hands with five fingers, natural hand movement` |
| la imagen tiembla o brinca | `smooth stabilized camera, no jitter, no sudden jumps` |
| aparecen letreros o letras | `no text, no subtitles, no captions, no logos, no watermarks` |
| el personaje cambia entre clips | `keep the exact same character from the reference image: same face, hairstyle, clothing and proportions`, junto con la hoja del paso 3 como imagen de referencia |

**No se usan**: tomas de dron, FPV, órbita de 360°, efecto vértigo, hyperlapse, momento congelado, cámara lenta, cámara en mano con temblor, neón, lente anamórfico ni acabado de animación 3D. Son la firma del video hecho con IA y Emi pidió que nada lo parezca (11/11/2026); varias además tiemblan o deforman. Tampoco se pide sonido: el inserto entra mudo y la voz de Emi sigue debajo.

Origen de estas tablas: el catálogo de códigos de cámara para Google Flow analizado el 25/11/2026, reescrito y filtrado con las reglas de esta skill (detalle en `docs/REFERENCIAS-EXTERNAS.md` del repositorio).

## Personaje caricatura de Emi

Emi lo quiere solo si queda perfecto. Procedimiento cuando lo pida: una foto suya de frente → hoja de personaje (frente, tres cuartos, perfil, tres gestos) en dos o tres estilos → él elige o descarta todo. Si no convence, no se usa. Hasta entonces, sin personaje.

## Cuándo no

- El momento ya se entiende con Emi hablando: una animación ahí estorba.
- En `milla` y `castorena`: lo real y, a lo más, un inserto sobrio. Sin stickers ni partículas.
- Si el recurso se nota más que la idea.
