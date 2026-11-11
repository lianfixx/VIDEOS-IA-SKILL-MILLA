# Narrativa, ritmo y motion compartidos con Vox Studio

Estado: **candidato** en MILLA (reglas desde la 1.2.0; planos animados en el compositor desde la 1.3.0). Emi pidió el 11/11/2026 que las mejoras logradas en Vox Studio se apliquen también a los videos de pizarra o motion, y que lo aprendido en un espacio valga para todos salvo su espíritu. Aquí queda qué se adopta y qué no. Ningún video de MILLA se ha producido todavía con estas reglas; la primera producción las confirma o las corrige.

## Qué se adopta tal cual

Reglas de método, sin cambiar el estándar de MILLA (Kie Nano Banana Lite, Fish, sin partículas, sin ChatGPT Image):

1. **Narrativa.** Leer [NARRATIVA.md de Vox Studio](../../vox-studio/NARRATIVA.md) antes del guion: gancho con consecuencia para quien mira, bucle abierto declarado (qué pregunta abre y qué escena la responde), evidencia antes que explicación, una idea por escena, cierre con disyuntiva. Trae sus fuentes y su grado de certeza.
2. **Guion visual.** Cada escena larga se cuenta con varios planos que entran con la palabra que los nombra, no con una imagen quieta. Algo cambia en pantalla cada 2 a 4 segundos.
3. **El código se suma; no sustituye.** Emi lo precisó el 11/11/2026: pidió agregar piezas hechas con código junto a las imágenes, no reemplazarlas. Cada escena conserva sus imágenes y los planos van a su lado o debajo.
4. **Explicar a la par.** Lo que explica va junto a lo explicado y al mismo tiempo: etiquetas sobre la imagen, apuntes al lado, cita de la norma subrayada. Coincide con la regla 2 de esta skill (diagramas exactos con código).
5. **De dónde sale cada imagen.** Código para lo que se explica; Apify para instituciones, lugares, documentos y hechos reales, con licencia y crédito; Kie para objetos y situaciones.
6. **Ritmo de la voz.** Pausa antes del remate y tras la cifra que debe pesar; al cambiar de tema, respiro y más despacio; redactar como se habla. Con Fish se logra con puntuación y tomas por tramo; las marcas `[pausa]` y `cambio_tema` son de la herramienta de Vox Studio.
7. **Un video, cuatro redes.** Un solo corte vertical que se entienda sin sonido, con fuente en pantalla; versiones por red solo si Emi las pide.
8. **Proceso.** Guion completo a Emi antes de gastar; cuadros de prueba de cada pieza antes del render completo; tira de cuadros y recortes a tamaño real del titular en la revisión final.

## Qué no se adopta sin decisión de Emi

- El **tono suelto** con remates y música irónica es el espíritu de Castorena; MILLA conserva el suyo.
- La **segunda voz que opina** es candidata y se reserva para un video polémico que Emi pida.
- La voz de ElevenLabs de Vox Studio no sustituye la preferencia de MILLA por Fish.

## Qué código existe y dónde

Hay dos formas de hacer video en este repositorio y las dos tienen ya las piezas animadas:

- **Vox Studio** (collage): `skills/vox-studio/plantilla/src/Vox.tsx`, con `planos` anclados a palabras.
- **Pizarra estilo motion** (esta skill): `assets/remotion-template/src/MillaVideo.tsx`, con `beats` por escena desde la 1.3.0: cita subrayada, lista, calendario, cifra, línea de tiempo, barras, imagen y nota, más `anchor-beats` para tomar los tiempos de la voz real. Ver [renderizado](rendering.md#planos-dentro-de-la-escena-beats). El flujo de cajas con flechas ya existía aquí como `diagram`.

No se portaron a la pizarra, porque dependen del estilo de recortes de Vox: el duo de dos recortes, las etiquetas sobre una imagen y el sello de remate. La voz por tramos, las pausas `[pausa]` y la segunda voz son de la herramienta de Vox Studio (ElevenLabs); aquí la voz sigue siendo Fish y su ritmo se logra con puntuación y tomas por tramo.
