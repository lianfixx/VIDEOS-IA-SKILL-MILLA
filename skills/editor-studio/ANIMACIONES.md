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

`detras` pone una palabra grande entre el fondo y quien habla. `$E recorte $D` recorta a la persona solo en esos tramos (entre 1 y 2 cuadros por segundo en este entorno: unos 25 s de trabajo por cada segundo de video, medido el 11/11/2026 con 1.5 s). Se lee mejor con la cabeza tapando entre un tercio y la mitad de la palabra: se revisa en la muestra y, si la tapa de más, se cambia la palabra o el segundo. Como mucho dos por video.

## 4 · Imagen ilustrada generada (nivel 3, con costo)

Con Kie y `nano-banana-2-lite` (4 créditos por imagen, medido el 10/11/2026), en el estilo de imagen del espacio. Nunca imágenes de OpenAI. Entra como `foto` con su `origen_descripcion` («generada con Kie, prompt en estados/…»). Nunca un rostro que parezca cliente, testigo o persona real.

## 5 · Video generado (nivel 3, con costo y con el sí de Emi en cada video)

Autorizado por Emi el 11/11/2026 como opción, no como costumbre. Método (hoja de personajes → cuadro inicial → cuadro final → animación entre los dos):

1. **Plan de escenas** en tabla: segundo, frase, idea visual, dónde va (pantalla completa, sticker o detrás), duración y costo. Una escena por idea, con **una** acción clara que cuente lo que se dice; nada de «solo un zoom».
2. **Cotizar y aprobar**: `$E aprobar $D gasto --por Emi --creditos N --nota "…"`. Sin eso el validador no deja pasar un inserto generado.
3. **Consistencia**: primero una hoja del personaje o del estilo; se usa como referencia en todas las escenas.
4. **Generar** cuadro inicial y final con Kie; animar con Kling por Kie (catálogo leído el 11/11/2026: Kling 3.0 y 4.0, incluido cuadro inicial + final). Cámara fija. Sin logos, sin marcas, sin texto dentro de la imagen.
5. **Transparencia**: lo que va como `sticker` se genera sobre verde plano y se recorta con el recorte de croma de Vox Studio; se entrega como WebM con transparencia.
6. Revisar cada clip (inicio, mitad y final) antes de montarlo: que la acción tenga sentido y nada se deforme.

**Sin comprobar todavía**: ningún clip de Kling se ha generado desde este repositorio; su esquema exacto y su costo real se medirán en el primer uso autorizado y se anotarán aquí. Higgsfield no está contratado ni hace falta mientras Kie lo cubra.

## Personaje caricatura de Emi

Emi lo quiere solo si queda perfecto. Procedimiento cuando lo pida: una foto suya de frente → hoja de personaje (frente, tres cuartos, perfil, tres gestos) en dos o tres estilos → él elige o descarta todo. Si no convence, no se usa. Hasta entonces, sin personaje.

## Cuándo no

- El momento ya se entiende con Emi hablando: una animación ahí estorba.
- En `milla` y `castorena`: lo real y, a lo más, un inserto sobrio. Sin stickers ni partículas.
- Si el recurso se nota más que la idea.
