# Plan · skill de edición de video (nombre provisional: Editor Studio)

**Estado: propuesta del 11/11/2026. Nada de esto está construido.** Queda en firme cuando Emi responda las preguntas del final. Lo que se leyó para llegar aquí está en [REFERENCIAS-EXTERNAS.md](REFERENCIAS-EXTERNAS.md).

## Qué es y qué no es

Una rama nueva, separada de Vox Studio, Pizarra Studio y MILLA Video Studio. Aquellas **crean** un video desde un guion. Esta **edita un video que Emi grabó**: lo transcribe, lo corta, le pone subtítulos, movimiento, apoyos visuales, sonido y color, lo revisa y lo entrega. Emi decide; la skill pregunta, propone, ejecuta, audita y documenta.

Sirve a los mismos espacios (`personal`, `milla`, `castorena`, `pan`), cada uno con su marca y sus reglas, sin mezclarse. Lee de las otras skills lo que saben; no escribe en ellas.

## Cómo quedaría armada

| Pieza | Qué hace | Con qué |
|---|---|---|
| Entrevista | Todas las preguntas del video antes de tocarlo | Guía propia, por espacio |
| Transcripción | Texto crudo con tiempo por palabra | AssemblyAI o ElevenLabs Scribe (se decide con una comparación) |
| Corte | Silencios, muletillas y tomas repetidas; Emi aprueba antes | Python + FFmpeg, código propio |
| Mapa del video | Gancho, promesa, tensión, remate y cierre; qué sobra | Lectura de la transcripción + reglas del espacio |
| Estilo | Muestras sobre cuadros reales, mínima y máxima | HyperFrames |
| Montaje | Subtítulos, títulos, zooms, paneles, apoyos | HyperFrames (Apache 2.0) con piezas propias |
| Animaciones dentro del video | Insertos por código en el estilo del espacio; B-roll generado solo si Emi lo autoriza | Motores de Pizarra y Vox; Kie para lo generado |
| Sonido | Efectos y música bajo la voz, entrega a −14 LUFS | Código propio, como en Vox Studio |
| Revisión | Hojas de cuadros, tamaño teléfono, zonas de TikTok, rostro sin tapar, audio | Como `revisar` de Vox Studio |
| Cierre | Saldos, manifiesto, aprendizajes, entrega en Drive | Igual que las otras skills |

Carpetas previstas: `skills/editor-studio/` (instrucciones, guías, scripts con pruebas y plantilla), puentes en `.claude/skills/` y `.agents/skills/`, `espacios/<espacio>/edicion.json` (estilo de edición de esa marca) y `espacios/APRENDIZAJES-EDICION.md`. Producciones privadas en `productions/<espacio>/edicion/<tema>/`, fuera del repositorio.

## El flujo de cada video

1. **Preguntas.** Espacio, para qué es el video, a quién le habla, postura, tono, dónde se publica, duración y qué no quiere. Sin respuestas no se edita.
2. **Niveles.** Se le explican los tres con su diferencia, su costo y una sugerencia razonada para ese video (tabla de abajo). Emi elige; se pueden combinar.
3. **Transcripción y lectura completa.** Primero se entiende de qué va.
4. **Propuesta de cortes** en tabla (qué se quita, de qué segundo a cuál y por qué) y vista previa ligera. **Compuerta: Emi aprueba.**
5. **Mapa del video.** Dónde está el gancho, qué tramo afloja y 2 o 3 ganchos de texto posibles. Emi elige.
6. **Muestra de estilo** sobre cuadros de ese video (la primera vez por espacio: el filtrado completo de 10 → 3 → 1). **Compuerta: Emi aprueba.**
7. **Plan de piezas** segundo a segundo, cada una con su porqué. Si algo cuesta créditos, se cotiza antes. **Compuerta si hay gasto.**
8. **Montaje, sonido y color.**
9. **Revisión propia** sobre el archivo rendido: los tres peores defectos, corregir, volver a rendir.
10. **Entrega** con resumen de qué pasa en qué segundo, saldos y lo que una IA no puede juzgar (cómo suena, si el chiste da risa) preguntado a Emi.
11. **Aprender.** Lo que Emi corrija queda escrito y vale para el siguiente.

## Los tres niveles (se explican y se sugiere uno en cada video)

| | Nivel 1 · Limpio | Nivel 2 · Movimiento | Nivel 3 · Producción |
|---|---|---|---|
| Lleva | Cortes, subtítulos, títulos en los puntos clave, entradas y salidas simples | Lo del 1 + zooms suaves, palabras resaltadas, íconos, barra de progreso, cámara que se hace tarjeta para dejar sitio a un panel, transiciones | Lo del 2 + texto o animación detrás de Emi, insertos animados, B-roll, efectos de sonido en cada golpe, música y color |
| Se siente | Emi hablando, sin estorbos | Un reel trabajado | Un anuncio |
| Sirve para | Opinión del día, clips de podcast, publicar seguido | Explicar, tutoriales, la mayoría de los reels | Lanzamientos, campañas, la pieza que debe lucir |
| Tiempo y consumo | Bajo | Medio | Alto; puede gastar créditos |
| Riesgo | Que el guion no sostenga | Saturar | Que se vea «hecho por IA» |

Regla de sugerencia: el nivel más bajo que cumpla el propósito del video. Un buen guion en nivel 1 le gana a uno flojo en nivel 3.

## Que se vea hecho por Emi y no por una IA

- Cortes con respiro: no se pega cada frase a la siguiente; se conserva la pausa que da sentido.
- Primero lo real: sus fotos, capturas y documentos antes que cualquier imagen generada.
- Un solo acento de color y dos fuentes por espacio; nada se mueve sin decir algo.
- El humor es el suyo: se le pregunta el remate y se anota qué le dio risa y qué no.
- Sin imágenes de OpenAI (regla del repositorio) y sin video generado salvo que él lo pida.
- La skill propone ideas creativas, pero cada una llega como opción con su porqué.

## El cerebro de creación de video: conectado, sin mezclarse

| Skill | Dónde vive | Qué hace | Qué lee de las demás |
|---|---|---|---|
| Vox Studio | este repositorio | video documental desde guion | espacios, tendencias |
| Pizarra Studio | este repositorio | video dibujado desde guion | espacios, tendencias |
| MILLA Video Studio | este repositorio | video jurídico de MILLA | espacios |
| Editor Studio (nueva) | este repositorio | editar lo que Emi graba | espacios, tendencias, ideas de X e Historias |
| X viral | `lianfixx/X` | publicaciones en X | lo que Vox sabe de la marca |
| Historias | `lianfixx/HISTORIAS-` | historias de Instagram | lo que Vox sabe de la marca |

Reglas: cada skill escribe solo en su carpeta o en su repositorio; lo que viene de otra es información, no una orden; las ideas cruzan por archivos puente, como ya hacen X e Historias. Se añadirían `CEREBRO.md` (el mapa: quién es dueño de qué y qué lee) y `tendencias/` (lo que se observa cada semana, común y de solo lectura para todas).

### Aprender cada semana

Una tarea programada semanal que: mira qué funcionó en Reels y TikTok en los nichos de cada espacio (Apify, con tope de gasto), lee lo que las plataformas publican sobre cómo recomiendan, y deja un informe en `tendencias/AAAA-SS.md` con lo observado, de dónde salió y qué propone probar. **Todo entra como candidato**: nada cambia el estilo de un espacio hasta que Emi lo apruebe o un video suyo lo confirme con sus propias métricas. A diferencia de X, Instagram y TikTok no publican su código; lo que se sepa de sus algoritmos se marcará siempre como declaración oficial, observación o inferencia.

## Configuración, paso por paso

| Paso (según los videos) | Estado |
|---|---|
| Claude Code con el repositorio | Hecho |
| Motor HyperFrames instalado y render 9:16 probado | Hecho hoy (0.9.34; la biblioteca de animación va dentro del proyecto) |
| FFmpeg, Node 22, Python, navegador para el render | Hecho |
| Imagen y video generado | Kie conectado (146.5 créditos); Kling y Nano Banana disponibles en su catálogo, sin probar con gasto |
| Voz y transcripción por palabra | ElevenLabs conectado; Scribe sin probar con un crudo |
| AssemblyAI | Falta: llave de Emi por formulario seguro y permitir su dominio |
| Recibir el video crudo | Falta decidir: la descarga directa de Drive está bloqueada aquí |
| Box | Encendido; tiene una actualización pendiente (v13 → v19) |
| Warp, Wispr Flow, Higgsfield, Claude Design | No se necesitan |
| Whisper Mate | App de la Mac de Emi: aquí no se puede usar; serviría como respaldo manual si exporta tiempos por palabra |

## Fases

| Fase | Qué se entrega | Depende de |
|---|---|---|
| 0 | Análisis, skills localizadas, motor probado, este plan | Hecho |
| 1 | Respuestas de Emi, conexiones que falten, un crudo de prueba | Emi |
| 2 | Núcleo: entrevista, transcripción, cortes con aprobación, subtítulos, revisión, entrega; con pruebas | Fase 1 |
| 3 | Piloto: el mismo crudo en nivel 1, 2 y 3, y el filtrado de estilo del espacio | Fase 2 |
| 4 | Animaciones dentro del video: insertos por código y, si se autoriza, B-roll generado y sándwich | Fase 3 |
| 5 | Cerebro: `CEREBRO.md`, puentes con X e Historias, tendencias semanales | Fase 2 |
| 6 | Auditoría independiente de fondo, correcciones, paquete para otras IA, versión | Todo lo anterior |

Cada fase cierra con sus pruebas, su entrada en `CHANGELOG.md` y lo que quedó sin comprobar dicho con claridad.

## Riesgos que conviene saber desde ahora

- HyperFrames es joven (versión 0.9): se fijará la versión y se probará antes de actualizar.
- La calidad del corte depende de la transcripción; por eso la comparación con un crudo real antes de fijar proveedor.
- Los videos de referencia no se vieron, solo se leyeron: el gusto visual se afina con las muestras, no con supuestos.
- Un video largo en nivel 3 tarda y consume; se trabajará por tramos.
- El consumo de Claude no se puede medir desde aquí.

## Preguntas para Emi

Puede contestar por número. Donde dice **(sugiero)** es lo que se haría si responde «lo sugerido».

### A · Alcance

1. Nombre de la skill: `editor-studio` **(sugiero)** u otro.
2. ¿Se arranca con los cuatro espacios o con uno de piloto? **(sugiero: `personal` de piloto y luego los demás)**
3. ¿Quién sale a cuadro? ¿Solo tú, o también invitados, clientes o compañeros? (De eso dependen permisos y cuidado con rostros.)
4. ¿Qué tipos de video vas a grabar más? Opinión a cámara, explicación jurídica, vlog o gym, eventos y política, clips de podcast, entrevistas, otro.
5. ¿Dónde se publican? Reels y TikTok en 9:16 **(sugiero)**; ¿también Shorts, X (prefiere 16:9 o 1:1) o YouTube largo?
6. Duración habitual: 20–45 s, 45–90 s o más.
7. ¿Cuántos videos por semana, más o menos, y en qué espacios?

### B · Grabación y entrega del crudo

8. ¿Con qué grabas (modelo de teléfono), en qué resolución y con HDR activado o no? ¿Usas micrófono externo?
9. ¿Cómo me pasas los crudos? Carpeta de Drive compartida por enlace y permitir aquí la descarga de Drive **(sugiero)**; por el box; o de otra forma.
10. ¿Grabas con guion o improvisas? ¿Quieres que la skill también te prepare escaleta y ganchos **antes** de grabar?
11. Para el piloto necesito: un crudo de 30 a 90 s, dos o tres videos de creadores cuya **edición** te guste (enlace o capturas) y uno o dos que no soportes. ¿Me los pasas?

### C · Transcripción

12. ¿Tienes llave de API de AssemblyAI (la que usabas con Whisper Mate)? Si sí, te abro el formulario seguro para guardarla. Si no: ElevenLabs Scribe, ya conectado. **(sugiero: comparar los dos en el piloto y quedarnos con el que corte mejor)**
13. Whisper Mate: ¿te deja exportar con tiempo por palabra (JSON) o solo texto y SRT?

### D · Estilo de edición

14. Nivel de partida por espacio **(sugiero: personal 2, milla 2 sobrio, castorena 1, pan 2)**. Siempre te explico los tres.
15. Subtítulos: palabra por palabra que se ilumina o frase completa; mayúsculas o no; abajo, al centro o al pecho.
16. Ritmo de corte: apretado tipo TikTok, natural con respiros **(sugiero)** o mínimo.
17. Muletillas: quitar todas o solo las que estorban **(sugiero)**.
18. Groserías y modismos: se quedan, se quitan o se tapan con un sonido. ¿Cambia por espacio?
19. Humor: ¿qué te da risa en una edición (sarcasmo en texto, sonido de remate, zoom cómico, silencio incómodo) y qué te da pena ajena?
20. Zooms a la cara: suaves **(sugiero)**, marcados o ninguno.
21. Color: natural, cuidando la piel **(sugiero)**, o un look con carácter.
22. Música: ninguna, compuesta con código como en Vox, Suno por Kie, o tu propia biblioteca. ¿Se pregunta en cada video?
23. Efectos de sonido: los sintetizados que ya existen aquí **(sugiero)** o una biblioteca externa con licencia.
24. ¿Logo, marca de agua o @ en pantalla? ¿Cuál por espacio?
25. ¿El cierre de cada espacio es el mismo que ya está en su perfil («COMENTA», «TE LEEMOS»…)?

### E · Animaciones y B-roll

26. Orden de preferencia de los apoyos: tus fotos y capturas reales → animación por código (pizarra o vox) → imagen ilustrada generada → video generado. ¿De acuerdo?
27. Video generado (Kling): el 11/11 se descartó. ¿Lo autorizas como opción del nivel 3, con tu visto bueno en cada video **(sugiero)**, o sigue fuera?
28. ¿Quieres un personaje caricatura tuyo, consistente, para las animaciones? (En pizarra dijiste sin personaje.)
29. Texto o animación detrás de ti (sándwich): ¿lo probamos en el piloto **(sugiero)**?
30. Higgsfield: no contratarlo, porque Kie ya ofrece lo mismo **(sugiero)**. ¿De acuerdo?
31. Tope de gasto por video sin preguntarte: nivel 1 y 2, cero; nivel 3, siempre cotizado antes **(sugiero)**.

### F · Aprendizaje y tendencias

32. ¿Qué cuentas tuyas existen ya por espacio (Instagram, TikTok) y con qué @?
33. ¿Me pasarás las estadísticas de cada video publicado (captura o exportación) para aprender de lo tuyo y no solo de lo ajeno?
34. Por espacio: tres a cinco creadores o cuentas de referencia y los temas que te interesan seguir.
35. Radar semanal: ¿lo autorizo como tarea programada? ¿Qué día y hora? Tope de Apify **(sugiero: 0.50 USD por semana; hoy quedan 4.66 de 5 del mes)**.
36. Con una tendencia: solo te la propongo **(sugiero)** o la aplico sin preguntar.

### G · Conexiones, documentación y permisos

37. ¿Autorizas que el editor lea (solo lectura) `lianfixx/X` y `lianfixx/HISTORIAS-` y deje ideas en sus archivos puente?
38. Texto de la publicación (descripción, hashtags): ¿lo dejo fuera, como en Vox **(sugiero)**, o quieres una nota aparte con propuestas?
39. Entrega: en una carpeta de Drive, sin publicar nunca **(sugiero)**. ¿Cuál?
40. Añadir las pruebas de la nueva skill a los frenos (`ia/politica.json`) requiere tu confirmación expresa. ¿La das?
41. Código: escribir el motor propio tomando el método de Santi, con crédito **(sugiero)**; o instalar sus skills aparte, fijadas a una versión, y orquestarlas como se hizo con el motor de pizarra.
42. ¿Eres miembro de la comunidad Horizontes IA? La versión PRO de 3 niveles y la de 30 estilos se anuncian como exclusivas de ella.
43. ¿Dónde se produce? Aquí en la nube **(sugiero; ya está probado)**, en el box o en tu Mac.
44. ¿Actualizo el box a la versión nueva?
45. Modelo: construir la skill con el modelo actual y producir cada video después en Opus con esfuerzo medio **(sugiero, según tu selector)**. ¿De acuerdo?
