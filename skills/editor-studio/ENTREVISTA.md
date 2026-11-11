# Entrevista: lo que se le pregunta a Emi antes de cada video

Todas las preguntas van **en un solo mensaje**, numeradas, con opciones y con una sugerencia marcada. Si responde «lo sugerido», vale. Lo que ya está en el perfil del espacio no se vuelve a preguntar: se le dice qué se va a usar y se le da la oportunidad de cambiarlo. Sus respuestas se guardan con sus palabras en `brief.json → respuestas_emi`.

## Antes de grabar (escaleta)

Si Emi todavía no graba, `$E escaleta $D` crea la hoja. Se le pregunta:

1. **Postura.** ¿Qué defiendes o qué criticas? ¿Qué te molesta del tema?
2. **A quién le hablas** y qué quieres que haga después (comentar, escribir, compartir, pensar).
3. **Ganchos.** Se le proponen tres distintos (una pregunta, una afirmación que incomoda, un dato) y elige uno. El gancho es lo que más pesa en que el video se vea; no se decide por él.
4. **Remate.** ¿Hay un chiste, una referencia o una frase tuya que quieras meter?
5. **Apoyos reales.** ¿Tienes capturas, documentos o fotos que enseñar?
6. **Duración** que te acomoda para este tema.

Se le entrega la estructura (gancho, promesa, desarrollo, giro, cierre), consejos de encuadre (vertical, plano medio, ojos en el tercio superior, aire abajo para subtítulos) y los datos que necesitan fuente.

## Con el video ya grabado

| # | Clave en `brief.json` | Pregunta |
|---|---|---|
| 1 | `para_que` | ¿Para qué es este video? (informar, opinar, vender una asesoría, convocar, entretener) |
| 2 | `a_quien` | ¿A quién le hablas? |
| 3 | `postura` | ¿Cuál es tu postura? Se respeta en la edición: qué se subraya y qué no |
| 4 | `tipo_de_video` | Opinión, explicación, vlog, evento, clip de podcast, entrevista, anuncio, tutorial |
| 5 | `donde_se_publica` | TikTok y Reels (9:16) · YouTube (16:9) · X · varios |
| 6 | `duracion_objetivo` | ¿Hay un tope? ¿Prefieres que se quede completo o que se apriete? |
| 7 | `nivel_elegido` | Se le enseña `$E niveles $D` (los tres, su diferencia y la sugerencia) y elige. Puede combinar: «2, con el gancho en 3» |
| 8 | `musica` | ¿Música? Se le sugiere una opción según el tono: ninguna · una pista suya · compuesta con código (Vox) · Suno. Si quiere, se le enseñan dos y elige |
| 9 | `humor` | ¿Cabe humor aquí? ¿Cuál? ¿Hay algún remate que quieras? |
| 10 | `quienes_salen` | ¿Quién sale a cuadro? |
| 11 | `permiso_de_quienes_salen` | Si sale alguien más: ¿dio su permiso para publicarse? Sin permiso no se entrega |
| 12 | `que_no_quiere` | ¿Algo que no quieras ver en esta edición? |
| 13 | `cierre` | ¿Con qué cierra? Se le proponen dos o tres llamados que estén funcionando esa semana (ver `cerebro/tendencias/`) y el del perfil del espacio |

Obligatorias para seguir (el validador se niega sin ellas): 1, 2, 3, 4, 5, 7, 8 y 10; y la 11 siempre que salga a cuadro alguien además de Emi. En el plan debe constar que la música se le preguntó (`sonido.musica.preguntado_a_emi: true`).

## Lo que se le pregunta después, con material delante

- **Cortes**: con la tabla y la vista previa. Las tomas repetidas y las muletillas dudosas, una por una.
- **Modismos fuertes** («güey», «pinche»): ¿se quedan o se tapan en este espacio?
- **Estilo**: con la muestra. La primera vez en cada espacio, el filtrado completo ([OFICIO.md](OFICIO.md#filtrar-el-estilo)).
- **Gasto**: si algo cuesta créditos, cuánto y para qué, antes de generarlo.
- **Al entregar**: lo que una IA no puede juzgar (cómo suena, si el ritmo se siente natural, si el chiste da risa).

## Lo que no se le pregunta

Lo que se puede razonar con el perfil del espacio y el video delante: posición y tamaño de los subtítulos, dónde cabe un título sin tapar la cara, qué efecto de sonido va con cada pieza. Eso se propone ya resuelto, con su razón, y él corrige si quiere.

## Palabras que usa esta skill, en claro

| Palabra | Qué quiere decir |
|---|---|
| Crudo | El video tal como salió de la cámara, sin tocar |
| Gancho | Lo primero que se ve y se oye: la razón para no deslizar |
| Corte, empalme | Lo que se quita; el punto donde quedan unidas dos partes |
| Muletilla | «eh», «este», «o sea»… |
| Pieza | Cualquier cosa que se pone sobre el video: un título, un zoom, una foto |
| Ancla | La palabra dicha a la que se amarra una pieza para que entre justo ahí |
| Panel | La cámara se hace chica y deja sitio a una lista |
| Inserto, B-roll | Imagen o animación que tapa a quien habla mientras se le sigue oyendo |
| Compuerta | Un punto donde se detiene todo hasta que Emi dice que sí |
| Muestra | Unos cuadros del video ya con el estilo, para aprobarlo antes de rendir |
| Render | El archivo de video final |
| LUFS | La medida del volumen que piden TikTok, Reels y YouTube (−14) |
