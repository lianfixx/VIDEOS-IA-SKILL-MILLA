# Referencias externas analizadas

Qué se tomó y qué se descartó de material de terceros, y por qué. Aquí se anota cada referencia que Emi pida analizar; lo adoptado vive en las skills, no en este documento.

## 11 de noviembre de 2026 · siete videos de Santiago Muñoz (Horizontes IA) sobre edición con IA y sus skills en GitHub

Pedido de Emi: analizar en orden cinco videos (tres de edición, dos de animaciones dentro de la edición) y dos de contexto, buscar cada skill en GitHub y unificarlas en una skill propia de edición. El plan y las preguntas están en [PLAN-EDITOR.md](PLAN-EDITOR.md); aquí queda qué se leyó y qué se toma.

**Cómo se leyeron.** YouTube está bloqueado desde este entorno; las transcripciones se obtuvieron con Apify (`streamers/youtube-scraper`, 0.03 USD): son los subtítulos automáticos de YouTube traducidos al inglés, leídos completos. **Los videos no se vieron**: lo que se dice de su imagen sale de lo que el autor describe al hablar y de los repositorios. El video de Warp no tiene subtítulos; de él solo se leyó la descripción. Los repositorios se clonaron en modo lectura y se leyeron sin ejecutar nada.

| # | Video (fecha, duración) | Qué enseña | Skill en GitHub (commit leído) |
|---|---|---|---|
| Editar 1 | «Claude Code Acaba de Destruir a los Editores de Video» (22/07/2026, 28:48) `RSomDkV2Aj0` | Construir un editor propio en cinco pasos: contexto, base limpia (transcribir, cortar, subtítulos), visuales en el segundo exacto, sonido, y empaquetarlo como skill | [`santmun/editor-tiktok`](https://github.com/santmun/editor-tiktok) 1.0.0 (`8e0b6fe`) |
| contexto | «Edita Videos con Claude Code (GRATIS)» (23/04/2026, 37:20) `M1UQzYaQl4Y` | Qué es HyperFrames y la arquitectura: la IA orquesta, el motor arma y las conexiones (transcripción, imagen, música, voz) aportan | [`santmun/intro-edit-pipeline-skill`](https://github.com/santmun/intro-edit-pipeline-skill) (`8a60185`) |
| contexto | «El stack que nadie te enseña para Claude Code» (19/06/2026, 17:31) `TfKqouIHPqw` | Dictado por voz (Wispr Flow), la terminal Warp y Claude Code | ninguna; no hace falta |
| Editar 2 | «Claude Design + Claude Code: mi edición…» (19/09/2026, 21:08) `oFYznV9EYPg` | Método de filtrado del estilo: 10 estilos en texto → cada uno dibujado en versión mínima y máxima sobre cuadros reales → elegir 3 → 5 escenas más → editar | no existe como repositorio público (es un método; la skill que replica un estilo concreto es de su comunidad de pago) |
| Editar 3 | «Convertí a Claude en mi editor de videos (nivel 1 vs nivel 3)» (1/11/2026, 21:07) `anrAaNvbp4M` | El mismo crudo editado en tres niveles: 1 subtítulos y textos; 2 movimiento; 3 3D, B-roll con IA, sonido y color | [`santmun/edicion-3-niveles`](https://github.com/santmun/edicion-3-niveles) 1.0.0 (`e6451f4`) y [`edicion-3-niveles-pro`](https://github.com/santmun/edicion-3-niveles-pro) (`2c6c253`) |
| Animación 1 | «Contraté a Claude como animador y esto pasó» (26/09/2026, 20:16) `5REPWhjX64A` | Videos animados 100 % con código, entrevista previa, voz y música opcionales; los 12 elementos de una animación | [`santmun/video-pizarra`](https://github.com/santmun/video-pizarra) (`dc6adc4`): **ya es el motor de Pizarra Studio** |
| Animación 2 | «Así Hago las Animaciones de Mis Videos» (24/10/2026, 14:34) `XlDeXK_DazI` | B-roll con personajes consistentes: hoja de personajes, cuadro inicial y final, animación con Kling, fondo verde quitado con código y «sándwich» (la animación pasa detrás de quien habla) | [`santmun/broll-animado`](https://github.com/santmun/broll-animado) (`147fe97`) |

Otros repositorios suyos leídos por ser del mismo oficio: `analisis-video` (Gemini mira el video; MIT), `color-grade-skill` (color por código), `videos-virales-skill` (radar de virales con Apify; MIT), `mega-editor-davinci` (método de brief y control de calidad; MIT) y `video-estilos-pro` (30 estilos por código).

### Licencias: se toma el método, no el código

`editor-tiktok`, `edicion-3-niveles`, `edicion-3-niveles-pro`, `broll-animado`, `video-pizarra`, `intro-edit-pipeline-skill` y `color-grade-skill` no traen archivo de licencia. `video-estilos-pro` dice «Exclusivo para miembros de la comunidad. No se redistribuye» y la versión PRO de 3 niveles se anuncia como exclusiva de su comunidad aunque el repositorio sea público. Por eso se sigue la misma regla que con el motor de pizarra: **su código, plantillas y sonidos no se copian a este repositorio**. Las ideas y los números de oficio sí se adoptan, escritos de nuevo y con el crédito aquí. HyperFrames, el motor que todos usan, es de HeyGen y tiene licencia Apache 2.0.

### Qué se propone adoptar (queda en firme cuando Emi responda el plan)

| Idea | De dónde | Cómo quedaría |
|---|---|---|
| Transcribir en crudo, con muletillas y tiempo por palabra; nunca cortar con un texto «limpio» | Editar 1 | Transcripción por palabra obligatoria antes de cortar |
| Cortar por la energía del audio y no solo por huecos del texto (umbral: mediana de la voz −16 dB, silencio mínimo 0.35 s, 0.10 s de aire por lado, fundido de 6 ms, corte en cuadro exacto) | `edicion-3-niveles` | Motor de corte propio con esos valores de partida, ajustables por espacio |
| En tomas repetidas gana la última completa; los cortes se enseñan en tabla y vista previa antes de aplicarse | Editar 1 | Compuerta: Emi aprueba los cortes |
| Volver a transcribir el resultado para comprobar que ningún corte cayó dentro de una palabra | `video-estilos-pro` (errores vividos) | Verificación automática tras cortar |
| Tres niveles, explicados y recomendados en cada video; se pueden combinar (2 en todo, 3 solo en el gancho) | Editar 3 | Regla de Emi: siempre presentar los tres, su diferencia y una sugerencia |
| Filtrado del estilo de lo general a lo particular, con variante mínima y máxima sobre cuadros reales | Editar 2 | Hoja de muestras antes del primer video de cada espacio |
| Cada pieza en pantalla significa algo de lo que se dice en ese segundo; se ancla a la palabra | los tres | Piezas ancladas a la transcripción; el validador rechaza una pieza sin motivo |
| No tapar la cara; zonas seguras (arriba 12 %, abajo 80 %, derecha 86 %) | Editar 2 y 3 | Medir dónde está el rostro y negarse a poner texto encima |
| Revisarse antes de enseñar: hoja de cuadros, los 3 peores defectos con su segundo, corregir y repetir | `edicion-3-niveles` | Igual que `revisar` en Vox Studio |
| Efectos de sonido 6 a 10 dB bajo la voz, con tope de pico y de RMS corto; entrega a −14 LUFS | `broll-animado`, `edicion-3-niveles-pro` | Auditoría de audio como la de Vox Studio |
| Zooms suaves con resorte y deriva, nunca de corte seco; no en el mismo cuadro de un corte | `editor-tiktok`, PRO | Pieza `zoom` con esas curvas |
| Hoja de personajes antes de generar; cuadro inicial + final para que el movimiento cuente la idea; un solo punto de aprobación antes de gastar | Animación 2 | Solo si Emi autoriza video generado (ver abajo) |
| Recorte de la persona para poner texto o animación detrás | PRO, Animación 2 | `hyperframes remove-background`, local y sin costo |

### Dudas y choques con decisiones anteriores de Emi

- **Video generado (Kling).** El 11/11/2026 se descartó «generar y calcar con un modelo de video» y Emi pidió que nada se vea hecho por IA. El B-roll animado de Animación 2 es exactamente eso. Se propone como opción del nivel 3, apagada por defecto y con su visto bueno en cada video.
- **Personaje caricatura.** En Pizarra Studio Emi eligió «sin personaje». Se pregunta de nuevo para la edición.
- **Higgsfield.** No hace falta contratarlo: Kie, ya conectado, ofrece Kling 3.0 y 4.0 (incluido cuadro inicial + final) y Nano Banana 2 Lite, según su documentación leída hoy. Sin probar con gasto real.
- **AssemblyAI.** Es lo que el autor recomienda para cortar. Aquí no hay llave y su dominio está bloqueado; ElevenLabs, ya conectado, tiene transcripción por palabra (Scribe). Se propone comparar los dos con el primer crudo de Emi.
- **Warp y Wispr Flow.** Son una terminal y un dictado. No se necesitan.
- **Claude Design.** Es una función de la app. Aquí la hoja de muestras se rinde con el propio motor.

### Comprobado hoy en este entorno

- HyperFrames 0.9.34 se instala con `npx` y rinde 9:16 sin pantalla: 2 s de 1080×1920 en 2.7 s. La biblioteca de animación (GSAP) debe ir **dentro del proyecto**: el navegador del render no alcanza `cdn.jsdelivr.net` y falla si se carga de internet.
- Bloqueados desde aquí: YouTube, AssemblyAI, OpenAI, Higgsfield, Pixabay, TikTok, Instagram y la descarga directa de Google Drive. Alcanzables: Kie, ElevenLabs, Apify, Google Fonts y la API de Gemini.
- Una de las skills ajenas trae una llave escrita en claro en su documentación. No se copió ni se usó.

## 11 de noviembre de 2026 · cuatro publicaciones de X sobre diseño de movimiento con código

Leídas completas por su texto (dos son artículos largos); los videos adjuntos no se vieron.

| Publicación | Qué es | Veredicto |
|---|---|---|
| @seeconvm, «What the Viral One-Prompt Videos Are Hiding» (2/10/2026) | Desmonta los videos «de un solo prompt»: detrás hay un brief largo, una carpeta de skills, llaves y muchas rondas de corrección | La más útil. Su tesis ya era la de este repositorio |
| @e1genqq, «How to Build an Automated Motion Design System» (13/10/2026) | Sistema para producir campañas en serie: datos separados del código, validación antes de rendir, control de calidad en cinco pasadas, variantes | Útil en control de calidad y validación; la parte de negocio no aplica |
| @e1genqq, lista de 20 repositorios (8/11/2026) | Herramientas libres: Remotion, FFmpeg, Three.js, Blender, ComfyUI, etc. | Casi todo relleno. El propio autor dice en su artículo: «no necesitas veinte repositorios» |
| @tivollem (8/11/2026) | Promete un repositorio con 475 videos y sus prompts | Sin verificar: el enlace lleva a un servidor de Discord, no a GitHub. No se entró |

### Adoptado

| Idea | De dónde | Cómo quedó |
|---|---|---|
| Cada escena necesita una razón de existir | @seeconvm, «State Lists» | Campo `funcion` obligatorio; primera `gancho`, última `cierre` y al menos una `opinion` |
| El gancho se elige, no se improvisa | ambas | `ganchos_propuestos` (2 o más) y `gancho_elegido` por Emi |
| Un dato inventado no se publica; rechazar la entrada mala antes de rendir | @e1genqq, «Validate Before Rendering» | Una cifra en la narración sin `fuente` en esa escena es error, no aviso |
| El sonido va en el mismo reloj que la imagen | ambas | El tempo de la música se ajusta ±8 % para que los cambios de escena caigan en pulso |
| Prueba «a ojos cerrados» | @seeconvm | La auditoría avisa si el audio es plano (rango menor de 1.5 LU). No sustituye a que Emi lo escuche |
| Cada clase de objeto con su física | @seeconvm, «Springs» | Titular firme, recorte con peso, rótulo seco; antes todo usaba el mismo resorte |
| Muestrear antes, durante y después de cada transición | @e1genqq, pasada 2 | `revisar` genera `hoja-transiciones.png` |
| Revisar a tamaño de teléfono | @e1genqq, pasada 3 | `revisar` genera `hoja-telefono.png` |
| No dar por bueno un video sin haber mirado el render; informe con segundos, hallazgos, arreglos y pendientes | ambas | `out/revision.json`; `cierre` se niega si falta o si es de un render anterior |
| Manifiesto de entrega | @e1genqq | `out/manifiesto.json`: huellas de guion, voz, música, imágenes, versión y ajustes |
| Una referencia visual vale más que una descripción | @seeconvm, «The Reference» | `referencia ARCHIVO` convierte la imagen o el video de Emi en una hoja para mirarla |
| Detenerse y preguntar si falta algo real | @seeconvm, «gates» | Compuertas explícitas en las skills |

Al estrenar la revisión de transiciones sobre el demo aparecieron dos fallas que las hojas anteriores no mostraban: un recorte que caía sobre el titular al entrar y la línea de fuente ilegible a tamaño teléfono. Las dos se corrigieron.

### Ya estaba

Render determinista cuadro por cuadro, datos separados del código, hoja de contacto, zonas seguras, música y efectos por código, entrevista antes de producir, espacios por marca, aprendizaje entre videos y la regla de no fingir un render.

### Adoptado después, con condiciones (decisión de Emi, 11/11/2026)

Three.js, sombreadores, Blender y ComfyUI se habían descartado por el riesgo de aspecto «render». Emi pidió tenerlos disponibles **para cuando hagan falta, razonando cada uso**. Quedaron así en Vox Studio 0.10.0: son acentos con los colores y el contorno de tinta del espacio, cada uso lleva un `porque` escrito y ComfyUI solo funciona con el servidor de Emi. El primer demo que los usó en cuatro de cinco escenas le gustó menos a Emi, y desde la 0.11.0 la regla es más estricta: por defecto no, como mucho uno por video, cada objeto solo en su momento del guion y Emi elige viendo la escena con y sin el recurso. Guía: `skills/vox-studio/TRES-D.md`.

### Descartado, con motivo

| Idea | Por qué no |
|---|---|
| Campaña de 18 variantes (3 ganchos × 3 formatos × 2 cierres) | Es para vender paquetes a clientes. Emi publica en sus propios espacios; multiplicar la voz por 3 triplica el gasto sin un fin |
| Formatos 1:1 y 16:9 en Vox Studio | Es una mejora real (X prefiere horizontal o cuadrado), pero exige rehacer la composición, no recortar. Queda propuesto, sin hacer. Pizarra Studio ya rinde en 16:9 |
| «Generar y calcar» con un modelo de video | Cuesta, y contradice la regla de no usar video generado donde se dice que todo es código |
| Simulaciones físicas y de partículas | No sirven al estilo editorial de estos videos y empujan hacia el aspecto «hecho por IA» que Emi quiere evitar |
| Contenedor primero y texto después | Se probó en el recuadro del dato: llegaba vacío y se veía peor. Revertido |
| Skills oficiales de Remotion (`remotion-dev/skills`) | El repositorio existe; no se instaló para no mezclar instrucciones ajenas con las de estas skills. Sirve como consulta al modificar la plantilla |
| Precios, paquetes y venta del servicio | Fuera del alcance: aquí solo se hace video |
