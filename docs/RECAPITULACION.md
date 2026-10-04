# Recapitulación del proyecto VIDEOS IA

Este documento conserva las decisiones que dieron origen al flujo y distingue las instrucciones de Emi, las propuestas del asistente y los resultados que todavía necesitan comprobarse. Sirve para continuar el trabajo sin repetir sus errores ni convertir una respuesta anterior en una aprobación inexistente.

## 1. Alcance y fuentes recuperadas

La recapitulación utiliza los mensajes visibles **194–267** del historial proporcionado, el estándar `MILLA-VIDEO-STANDARD.md` recuperado y leído íntegramente —129 líneas, versión v2 con fecha interna del 22 de julio— y la recuperación contextual del inicio del proyecto. Los números de mensaje son identificadores del fragmento recibido; no son enlaces ni fechas.

**El historial recibido contiene omisiones. No se dispone de una transcripción íntegra de toda la conversación original y no se afirma haberla leído.** Cuando el texto anterior reporta una generación, una medición o una revisión, se identifica como antecedente hasta contrastarlo con sus archivos o registros.

Material recuperado o identificado:

- Estándar maestro anterior, que permite recuperar el perfil visual y parte del método.
- MP4 del Short de personas físicas V2 y MP4 de cinco beneficios V3. Son referencias audiovisuales; no sustituyen sus proyectos editables.
- Antecedente de trabajo con [video-vox](https://github.com/santmun/video-vox), registrado el 21 de julio, y un flujo con Remotion, FFmpeg, ElevenLabs y Apify. Este antecedente contextual no prueba que todos los renders posteriores emplearan la misma versión o composición.
- Identificador actual `nano-banana-2-lite`, contrastado con documentación oficial de Kie durante la investigación de este repositorio.

**No se recuperó el proyecto fuente exacto de los MP4 aprobados.** La plantilla creada para este repositorio es una implementación nueva del método; no es el código original ni promete reproducir fotograma por fotograma el montaje anterior.

## 2. Cómo se resuelven las contradicciones

Una corrección expresa posterior de Emi prevalece sobre una preferencia anterior incompatible. Las reglas compatibles se conservan. Una propuesta del asistente no debe convertirse silenciosamente en una exigencia del usuario, y la entrega de una versión no equivale a su aprobación.

Orden práctico: instrucción del encargo actual → corrección expresa más reciente → criterio aprobado y compatible → valor predeterminado propuesto. La documentación antigua conserva valor histórico, pero no puede reactivar partículas, ChatGPT Image o una voz rechazada.

## 3. Evolución y trazabilidad

| Mensajes | Qué ocurrió | Efecto para el método actual |
|---|---|---|
| 194–197 | El asistente reportó la entrega y auditoría del primer Short de personas físicas. | Referencia de producción; sus mediciones históricas no son pruebas ejecutadas por este repositorio. |
| 198–201 | Emi aprobó el resultado y pidió conservar su espíritu en todos los videos; el asistente documentó un estándar. | Existe aprobación editorial del video de personas físicas. La adaptación razonada es obligatoria. |
| 202–207 | Emi pidió predominio de Kie, más naturalidad y energía vocal, música, imágenes, transiciones, diagramas, profundidad, VFX y SFX; aportó una referencia de TikTok. | Se consolida una explicación visual dinámica, sin que los efectos desplacen el contenido. Las partículas y ChatGPT Image mencionados aquí fueron sustituidos después. |
| 208–217 | Emi pidió aplicar las mejoras al video en curso. El asistente reportó nuevos recursos, música y voz mediante Kie/ElevenLabs. | Antecedente del enriquecimiento de V2, no configuración actual de voz. |
| 218–226 | Tras continuar y recibir el paquete, Emi lo aprobó con dos observaciones: quitar partículas y variar las animaciones para no repetir el círculo. | El video aprobado permanece como referencia, pero los siguientes deben respetar ambas correcciones. |
| 227–230 | Emi pidió Fish Studio y precisó Nano Banana Lite como motor principal, con otro modelo como respaldo si falla. | Fish es preferente para voz; Kie/Nano Banana Lite es prioritario para imágenes. No se reproducen credenciales del historial. |
| 231–238 | Emi encargó cinco beneficios de una firma boutique para público de 27–65 años, con investigación previa. Se propuso un enfoque de prevención y decisiones informadas. | Tema y audiencia pertenecen a ese encargo; no son restricciones universales. |
| 239–244 | Emi insistió en que comenzara la producción. Más tarde el asistente reportó recuperación del estándar y cierre del guion. | La herramienta debe producir avances comprobables y evitar cadenas de promesas de inicio. |
| 245–249 | Se reportaron nueve imágenes, voz Fish, música Kie/Suno, ajuste de cadencia y storyboard. | Antecedentes de procedencia y montaje; faltan los registros completos para reproducir las solicitudes. |
| 250–256 | Se reportaron correcciones de cámara y de un salto de luminancia, y se entregó el video de beneficios. | Justifica revisar el archivo codificado y los solapamientos. No constituye aprobación del usuario. |
| 257–262 | Emi rechazó la voz, prohibió imágenes generadas por ChatGPT y pidió ausencia del logo de Gemini. El asistente identificó distintivos en dos archivos y reportó su saneamiento. | ChatGPT Image queda fuera del flujo. La voz rechazada no se reutiliza. Se añade revisión explícita de marcas y recortes. |
| 263–267 | El asistente reportó otra narración y entregó la V3 de beneficios con imágenes saneadas. | **La V3 fue entregada; no consta aprobación posterior de su voz.** Debe conservarse como candidata, no como voz aprobada. |

## 4. Estándar vigente

### Contenido, marca y público

| Área | Regla | Aplicación |
|---|---|---|
| Espíritu | Conservar el nivel del Short aprobado y adaptar el método a cada necesidad. | Definir objetivo, público, mensaje y referencia antes de generar. |
| MILLA | Estética editorial boutique, profesional y clara. | Perfil separado del motor general para poder trabajar con otras marcas. |
| Colores | Marfil `#F6F0E4`, azul marino `#172636`, dorado `#D6A72C`. | Valores recuperados del estándar. No inventar fuentes, logo o variantes faltantes. |
| Narrativa | Cercanía, prevención, estrategia y decisiones informadas. | Evitar miedo innecesario, tono grandilocuente y publicidad corporativa plana. |
| Investigación | Investigar y razonar antes de producir contenido jurídico. | Fuentes oficiales pertinentes, jurisdicción y fecha; diferenciar hechos, interpretación y mensaje comercial. |
| Beneficios | Expresar capacidades posibles del servicio, sin superioridad automática ni promesas de resultados. | La etiqueta boutique no demuestra por sí sola calidad, rapidez, especialización o éxito. |
| Audiencia | Adecuar lenguaje, lectura y ritmo al encargo. | El rango 27–65 corresponde al video de beneficios; no se aplica a todos los futuros videos. |
| Contacto | CTA claro y pertinente. | Confirmar dominio, datos y oferta vigente antes de usarlos; no arrastrar datos de un copy anterior sin revisión. |

### Imágenes, diagramas y movimiento

| Área | Regla | Aplicación |
|---|---|---|
| Motor principal | Kie con Nano Banana Lite. | Usar el identificador verificado `nano-banana-2-lite`; comprobar disponibilidad y contrato de API antes de ejecutar. |
| Respaldo | Otro modelo Nano Banana/Kie si el principal falla o no cumple. | Registrar motivo y proveedor real; limitar reintentos y evitar cobros repetidos. |
| ChatGPT Image | Prohibido en este flujo por corrección expresa. | No reactivarlo como respaldo, complemento o solución a un bloqueo. |
| Realidad necesaria | Apify puede localizar fotografías reales o referencias. | Búsqueda no equivale a licencia de reutilización. Conservar procedencia y revisar derechos. |
| Recursos | Imágenes específicas para cada idea, coherentes y sin repeticiones innecesarias. | Inventario por escena; no regenerar recursos válidos al reanudar. |
| Marcas | Sin distintivo de Gemini, marcas de agua, firmas del modelo o texto extraño. | Inspeccionar originales, derivados y composición final; una detección automática no sustituye la revisión visual. |
| Recortes | Transparencia cuando corresponda, sin fondo rectangular, halo ni chroma residual. | Examinar bordes y huecos sobre fondos claros y oscuros. Conservar original y derivado. |
| Composición | Centrado óptico y márgenes seguros. | Comprobar imagen, texto, logo y CTA en formato móvil. |
| Diagramas | Explicaciones visuales claras, exactas y animables. | Pueden construirse con código o vectores; no deben depender de texto inventado dentro de una imagen generada. |
| Profundidad | Parallax, cámara, capas, iluminación y objetos 2.5D/3D cuando ayuden. | La selección tiene una función narrativa; no hay obligación de usar todos los efectos en cada escena. |
| Partículas | **Cero partículas.** | Prohibición en prompts, composición y revisión. |
| Transiciones | Variar familias y entradas; no usar siempre círculo o anillo. | El círculo deja de ser un efecto automático. Esto no prohíbe un círculo con función explicativa dentro de un diagrama. |
| Continuidad | Solapamientos fluidos, sin destellos ni cuadros vacíos. | La escena saliente debe cubrir el tiempo que necesita la entrante para reemplazarla. |
| Ritmo | Actividad visual ágil, sin atropellar voz ni saturar. | Ajustar a lectura y comprensión. No convertir un intervalo sugerido en obligación universal. |

### Voz, música, subtítulos y entrega

| Área | Regla | Aplicación |
|---|---|---|
| Proveedor de voz | Fish Studio preferente. | Verificar conexión y capacidades; no fingir una integración. |
| Interpretación | Femenina, español mexicano, cercana, natural, profesional, energética y motivadora. | Variación de intención, pausas y énfasis; evitar entonación impostada o robótica. |
| Voz rechazada | No reutilizar la voz denominada “Mexicana” en la primera entrega de beneficios. | Recuperar su identificador real cuando sea posible. El nombre por sí solo no garantiza identificarla. |
| Voz V3 | Candidata pendiente de aprobación. | Conservar audio y parámetros; si se cambia de voz, proponer una muestra breve antes de producir toda la narración. |
| Referencia | La referencia vocal orienta cadencia y energía. | No es autorización para clonar la identidad de otra persona. |
| Música | Adecuada al tema y al arco emocional. | Acompañar la voz, preparar el cierre y guardar procedencia/licencia. Que una pista sea generada no demuestra sus derechos comerciales. |
| SFX | Variados, sincronizados y relevantes. | No repetir el mismo sonido por inercia; evitar picos y competencia con la voz. |
| Subtítulos | Superiores, legibles y sincronizados. | Alinear con la toma final y revisar saltos de línea, contraste y zonas seguras. |
| Exportación | Referencia vertical 1080×1920, 30 fps, H.264/AAC. | Perfil configurable; duración según guion y audiencia. |
| Mezcla | Referencia cercana a −16 LUFS, sin saturación. | Medir loudness integrado y true peak por separado; documentar los comandos. |
| QA | Revisar el MP4 codificado. | Integridad, cuadros negros, transiciones, movimiento, marcas, subtítulos y escucha perceptual. |
| Entrega | MP4, portada y elementos necesarios para continuidad. | Identificar versión, estado de aprobación y limitaciones; conservar manifiesto y fuente disponible. |

## 5. Reglas antiguas que no deben reaparecer

- **Partículas:** solicitadas inicialmente, prohibidas después en los mensajes 223–226.
- **ChatGPT Image compatible:** alternativa inicial eliminada por los mensajes 257–259.
- **ElevenLabs como opción habitual:** antecedente técnico; Fish tiene prioridad desde 227–230.
- **Voz V3 “aprobada”:** no existe esa aprobación en el material recibido.
- **Tono maternal:** fue una interpretación del asistente de una frase con error tipográfico; no se consolida como exigencia.
- **Cuatro o nueve imágenes, ocho transiciones, 50.15 o 55.10 segundos:** cantidades de piezas concretas, no mínimos universales.
- **Cuatro familias de transición y ausencia de repeticiones consecutivas:** controles propuestos por el asistente para lograr variedad. Son valores ajustables, no una licencia para añadir efectos innecesarios.
- **Cambios principales cada 1.2–1.8 segundos:** propuesta de ritmo que debe ceder ante legibilidad y comprensión.
- **Colores o identificadores de otros canales:** no forman parte del perfil MILLA vigente.
- **Mantener siempre el mismo guion:** era una condición de ciertas correcciones del video existente, no de todos los nuevos encargos.

## 6. Errores previos convertidos en controles

| Problema observado en el historial | Control del método |
|---|---|
| Repetir que la producción comienza sin mostrar avances reales. | Estados verificables: preparado, solicitado, recibido, renderizado, medido y entregado. |
| Responder a un nuevo video como si fuera otra V2 del anterior. | Identificador de producción, brief y alcance de versión antes de actuar. |
| Tratar una entrega como aprobación. | Registro separado de aprobaciones, rechazos y candidatos. |
| Voz técnicamente válida pero desagradable para Emi. | Escucha perceptual y muestra cuando cambia la voz; las métricas no certifican naturalidad. |
| Ajustar una toma lenta principalmente con velocidad. | Priorizar nueva interpretación; usar cambios de velocidad solo si conservan naturalidad. |
| Logo visible sobre un elemento de la escena. | Revisar archivo original, recorte y composición; el chroma no es una prueba de ausencia de marcas. |
| Bordes y zonas interiores con chroma residual. | Revisar alfa sobre dos fondos y a escala de uso. |
| Cámara quieta después de la entrada. | Revisar la intención visual de toda la escena; evitar movimiento gratuito o castigar pausas deliberadas. |
| Destello al pasar a una escena oscura. | Comprobar solapamiento completo de máscara y escenas en los fotogramas del cambio. |
| Música genérica o de duración insuficiente. | Brief musical y cierre editado sin unión evidente. |
| TTS disponible, transcripción sin saldo. | Detectar cada capacidad por separado y disponer de alineación local si es viable. |
| Reintentos que pueden cobrar dos veces. | Guardar task IDs, parámetros y resultados; consultar trabajos existentes antes de recrearlos. |
| Pérdida de archivos temporales. | Persistir fuente, activos y manifiesto; usar Git para código y almacenamiento adecuado para medios. |
| Claves publicadas en el historial. | No copiarlas a documentación, ejemplos, logs ni commits; configurar secretos fuera del chat. |

## 7. Evidencia histórica y límites de la auditoría

Se reportaron nueve imágenes de Nano Banana 2 Lite, narración Fish, música Kie/Suno y un MP4 V3 de 55.10 segundos a 1080×1920 y 30 fps. También se reportaron mezcla alrededor de −16.1 LUFS, picos próximos a −2 y ausencia de cuadros negros. La recuperación del MP4 permite nuevas verificaciones, pero no prueba por sí sola qué API produjo cada activo.

Los mensajes anteriores alternan **dBFS y dBTP**: no son equivalentes y no deben mezclarse al redactar un informe nuevo. Los valores históricos de cambio de luminancia —10.78 o 11.86— carecen en este fragmento de fórmula, escala y comando reproducible. No se adoptan como umbral universal de ausencia de destellos ni como certificación de accesibilidad.

“Sin congelamientos” requiere distinguir un fallo de render de una pausa narrativa deliberada. “Sin marcas” requiere inspección visual, además de cualquier detector. Una selección de capturas no permite garantizar que cada fotograma está libre de defectos.

## 8. Qué falta para reproducir exactamente el original

| Elemento | Estado y consecuencia |
|---|---|
| Código y dependencias del montaje original | No recuperados. La nueva plantilla no es una restauración del fuente. |
| Guion y pronunciaciones finales por versión | El historial aporta narrativas propuestas, no un paquete exacto de guion y alineación. |
| Voice IDs, parámetros y audios separados | No documentados de forma completa. Falta identificar la voz rechazada y aprobar una voz reutilizable. |
| Música, SFX y licencias | No recuperados como paquete completo. El MP4 solo contiene la mezcla. |
| Imágenes originales y saneadas | Falta un inventario completo con hashes, procedencia y transformaciones. |
| Prompts y task IDs | No recuperados íntegramente; no se inventan para completar un manifiesto. |
| Timeline y movimiento | Falta composición original con duraciones, cámara, transiciones y solapamientos exactos. |
| Subtítulos y timestamps | Deben recuperarse o regenerarse desde la toma utilizada. |
| Fuentes y logo | Los colores están comprobados; faltan activos y licencias completos para asegurar reproducción exacta. |
| Logs y comandos de QA | No disponibles de forma íntegra. Las futuras mediciones deben generar evidencia nueva. |
| Historial completo de decisiones | Parcial. Las reglas recuperadas y las omisiones quedan identificadas. |

## 9. Uso por otras personas o IA

El método debe funcionar primero como documentación neutral. Una skill facilita su lectura en plataformas compatibles, pero instalar el mismo texto no concede terminal, MCP, acceso a cuentas, saldo ni capacidad de render a todas las IA. Cada asistente debe detectar sus capacidades y explicar la siguiente acción posible sin simular ejecuciones.

La guía de conexión avanza una pantalla o paso a la vez, con instrucciones breves. Las credenciales se configuran fuera del chat. El perfil MILLA aporta decisiones editoriales; cada nuevo usuario puede crear otro perfil sin alterar las reglas de Emi. Las mejoras se incorporan con propuesta, evidencia, revisión y changelog, conservando las preferencias explícitas y los estados de aprobación.

La autorización para documentar o subir esta herramienta a GitHub no equivale a publicar videos en redes sociales ni a distribuir activos comerciales o datos privados indiscriminadamente.
