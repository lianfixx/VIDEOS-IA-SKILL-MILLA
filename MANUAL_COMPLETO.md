# MILLA Video Studio · manual portable

Generado desde la skill; editar los originales y ejecutar tools/build_manual.py.
Este archivo transmite instrucciones. Para ejecutar se necesita la carpeta de código completa.


---

## Archivo: skills/milla-video-studio/SKILL.md

---
name: milla-video-studio
description: Producir, corregir, auditar y documentar videos cortos de MILLA ABOGADOS con Kie Nano Banana Lite, Fish Audio, música temática y Remotion. Usar al pedir un video, continuar producción, configurar conexiones, cambiar voz o imágenes, revisar un MP4 o mejorar el método VIDEOS IA. Guiar paso a paso y conservar el estándar sin partículas ni imágenes de ChatGPT.
---

# MILLA Video Studio

## Empezar por el resultado real

Leer [estándar vigente](skills/milla-video-studio/references/standard.md) y [flujo de producción](skills/milla-video-studio/references/workflow.md). Recuperar proyecto y estado antes de continuar. Distinguir **nuevo video**, **revisión** y **cambio del estándar**. No convertir un tema nuevo en una V2 del anterior.

Respetar instrucciones actuales y correcciones expresas posteriores por encima de documentos antiguos. No afirmar haber leído mensajes omitidos, usado un proveedor, escuchado una voz o auditado un MP4 sin evidencia. Personas físicas V2 es referencia editorial aprobada; la voz de beneficios V3 es candidata.

Detectar navegación, archivos, terminal, red, secretos configurados, proveedores, audio/video y persistencia. Elegir:
- **Ejecución:** producir y verificar con las capacidades autorizadas disponibles.
- **Asistencia:** avanzar guion, manifiesto y prompts; explicar una acción externa cada vez y pedir su resultado. No fingir conexiones o renders.
- **Reanudación:** comprobar hashes y tareas existentes; continuar desde el primer hito pendiente sin regenerar recursos recibidos.

Ejecutar `python3 scripts/milla.py doctor` desde la carpeta de la skill. Comprueba disponibilidad local, no autenticación ni saldo. Leer [conexiones](skills/milla-video-studio/references/connections.md) y [portabilidad](skills/milla-video-studio/references/portability.md).

## Reglas permanentes

1. Priorizar Kie `nano-banana-2-lite`; verificar contrato actual. Usar otro Nano Banana/Kie solo ante fallo o calidad insuficiente documentados. **Nunca ChatGPT Image**, tampoco como respaldo.
2. Construir diagramas exactos con código/vector. Usar Apify solo para realidad necesaria y verificar derechos. Un diagrama nativo no es generación de imágenes con ChatGPT.
3. Excluir partículas, logos visibles Gemini, marcas de agua, texto inventado, cuadros de fondo de recortes, halos y repetición como relleno. Revisar píxeles; un JSON no demuestra ausencia.
4. Variar transiciones, entradas y SFX. No usar círculo/anillo automático. Mantener solapamiento y cobertura continua del cuadro.
5. Preferir Fish, voz femenina mexicana, natural, conversacional, energética y motivadora. No seleccionar la primera disponible ni reutilizar la toma rechazada denominada “Mexicana”. Su ID exacto no se recuperó.
6. Si falta muestra aprobada para voz/modelo actuales, producir 2–3 muestras breves y pedir elección **después de entregar audios escuchables**. Aprovechar aprobaciones existentes; no pedirlas de nuevo sin cambio material. No clonar la referencia TikTok.
7. Investigar contenido jurídico en fuentes oficiales vigentes; registrar jurisdicción y límites. No prometer resultados ni superioridad automática de una firma boutique.
8. Elegir música específica para mensaje y SFX debajo de voz. Verificar derechos comerciales independientemente del pago al proveedor.
9. Sincronizar subtítulos superiores al **audio final**. No repartir palabras uniformemente para fingir alineación.
10. Revisar MP4 completo con imagen y sonido. Pruebas automáticas no certifican naturalidad, ausencia de todo logo ni seguridad frente a destellos.

## Ejecutar por hitos

1. Crear producción privada con `python3 scripts/milla.py init-project RUTA --title "Tema"`. Registrar objetivo, audiencia, plataforma, jurisdicción, CTA y presupuesto ya autorizado. Completar solo lo faltante.
2. Investigar y escribir guion, mapa de afirmaciones y storyboard. Leer [prompts](skills/milla-video-studio/references/prompts.md). Dar función explicativa a cada escena.
3. Configurar secretos fuera del chat/repositorio. Hacer solicitudes mínimas dentro del presupuesto. Registrar hash de petición y task ID. Tras timeout de POST, comprobar estado antes de reenviar.
4. Resolver voz, música, imágenes, recortes y tiempos. Conservar originales/derivados/hashes. Revisar cada recurso antes de montar. Guardar motivos de rechazo y aprobación.
5. Trabajar en la plantilla Remotion que `init-project` ya copió a la raíz de la producción, siguiendo [renderizado](skills/milla-video-studio/references/rendering.md). Es una base nueva, no código recuperado del video aprobado. Adaptar diagramas, tipografía y transiciones sin crear otra copia paralela.
6. Ejecutar `python3 scripts/milla.py validate RUTA/project.json`. `--allow-pending` solo revisa borradores; no convierte pendientes en aprobación. Renderizar storyboard y segmentos críticos antes del completo.
7. Masterizar y medir con [QA](skills/milla-video-studio/references/quality.md). Ejecutar `python3 scripts/milla.py inspect-video RUTA/video.mp4 --output RUTA/qa.json`. Corregir riesgos concretos, sin ciclos interminables.
8. Entregar MP4, portada, subtítulos, fuentes y resumen breve de cambios/mediciones/limitaciones. Conservar composición, lockfile, audios separados, manifiesto y estado en destino durable autorizado. No inferir publicación en redes.
9. Registrar retroalimentación en [mejora continua](skills/milla-video-studio/references/improvement.md), probar cambios y versionar sin borrar restricciones ni inventar aprobaciones.

## Explicar a la par

Comunicar en dos o tres frases: **resultado comprobado → siguiente acción → bloqueo concreto si existe**. Avanzar trabajo autorizado sin pedir confirmación en cada paso. No repetir “inicio” sin ejecutar. Si falta una elección perceptual, preparar muestras antes de preguntar. Estimar coste y límite antes de nuevas generaciones cuando no exista autorización suficiente; saldo disponible no equivale a gasto ilimitado.

## Persistir y compartir

Separar código reutilizable de `productions/`, claves y medios privados. Ejecutar `python3 scripts/milla.py secret-scan RUTA` antes de compartir; es ayuda, no prueba exhaustiva. No copiar el historial crudo a GitHub.

Guardar preferencias explícitas y mantener experimentos candidatos. Las mejoras requieren otra ejecución autorizada o una automatización solicitada: instalar no crea aprendizaje autónomo. Consultar [evidencia y límites](skills/milla-video-studio/references/evidence.md) antes de describir qué se recuperó y probó.


---

## Archivo: skills/milla-video-studio/references/standard.md

# Estándar operativo MILLA

Aplicar este perfil al producir o corregir videos de MILLA ABOGADOS. Separarlo del contenido específico de cada encargo para poder reutilizar el método con otras marcas.

## Índice

- Precedencia y aprobación
- Contenido y marca
- Imágenes y composición
- Movimiento y transiciones
- Voz, música y subtítulos
- Timeline, exportación y revisión

## Precedencia y aprobación

1. Aplicar la instrucción del encargo actual y las correcciones expresas más recientes.
2. Conservar las reglas aprobadas que sigan siendo compatibles.
3. Tratar los valores sugeridos como criterios adaptables, no como instrucciones del usuario.
4. Registrar conflicto, decisión y alcance; pedir una aclaración concreta solo si cambia materialmente el resultado.
5. Mantener aprobaciones separadas para guion, muestra vocal, recursos y video final.

Usar el Short de personas físicas aprobado como referencia editorial. El MP4 V3 de cinco beneficios fue entregado, pero su nueva voz no tiene aprobación explícita recuperada: mantenerla `pending`.

No reactivar partículas, ChatGPT Image ni la voz rechazada a partir del estándar antiguo. No convertir una entrega, una métrica correcta o una respuesta entusiasta sobre otra versión en aprobación del recurso actual.

La plantilla del paquete es una implementación nueva. No presentarla como el proyecto fuente exacto de los videos previos, que no se recuperó íntegramente.

## Contenido y marca

| Elemento | Aplicación |
|---|---|
| Marfil | `#F6F0E4`: fondo principal y espacio de lectura. |
| Azul marino | `#172636`: texto, estructura y bloques de contraste. |
| Dorado | `#D6A72C`: acentos y énfasis contenidos. |
| Carácter | Boutique, editorial, profesional, cercano y claro. |
| Tipografía | Usar fuentes legibles y con licencia; confirmar la familia si se requiere fidelidad exacta. |
| Identidad | Usar el logo autorizado; no inventar escudos, monogramas ni identificadores de otros canales. |

Definir público, problema, objetivo y acción esperada antes del guion. El rango 27–65 años pertenece al video de beneficios; no imponerlo a nuevos temas.

Investigar afirmaciones jurídicas con fuentes oficiales pertinentes, fecha y jurisdicción. Distinguir norma, interpretación, ejemplo y mensaje comercial. Explicar beneficios posibles de la asesoría sin prometer resultados ni superioridad automática por llamarse boutique.

Redactar un hook claro, desarrollo comprensible y cierre útil. Mostrar situaciones reconocibles y evitar miedo gratuito, grandilocuencia y lenguaje corporativo plano. Verificar datos de contacto antes de repetir un CTA anterior.

## Imágenes y composición

Priorizar Kie con `nano-banana-2-lite`; comprobar contrato y disponibilidad actuales según [connections.md](skills/milla-video-studio/references/connections.md). Si falla, evaluar otro modelo Nano Banana/Kie compatible y registrar el motivo. No cambiar de proveedor en silencio.

**No usar ChatGPT Image/ImageGen en este flujo.** La prohibición no impide construir diagramas exactos con código o vectores: estos son elementos explicativos, no fotografías sintéticas de respaldo.

Usar Apify únicamente cuando una fotografía o referencia real aporte algo necesario. Registrar procedencia y derechos; un resultado de búsqueda no concede licencia. Distinguir esos recursos de imágenes generadas por Kie.

Para cada recurso:

- Asignar ID, función narrativa, origen, modelo cuando corresponda y hash del archivo.
- Rechazar logotipos visibles de Gemini, firmas del modelo, marcas de agua o texto inventado.
- Preferir una salida limpia y conservar atribuciones o metadatos obligatorios; no borrar marcas exigidas por licencia.
- Guardar original y derivado; verificar que un PNG realmente contiene el alfa necesario.
- Revisar bordes, cabello y huecos sobre fondos claros y oscuros; quitar chroma residual autorizado sin dejar parches.
- Evitar cuadros posteriores, halos, anatomía defectuosa y detalles que contradigan el mensaje.
- Mantener centrado óptico y márgenes seguros para subtítulos, sujeto, logo y CTA.
- Usar imágenes específicas y distintas; reutilizar un objeto dentro de una secuencia solo si tiene continuidad narrativa.

No afirmar ausencia de marcas por haber pasado OCR o por revisar una sola captura. Inspeccionar el recurso y su apariencia dentro del montaje.

## Movimiento y transiciones

**No incluir partículas.** Aplicar la restricción en prompts, activos, composición y revisión final.

Usar profundidad 2.5D/3D, parallax, capas, iluminación y cámara cuando refuercen la explicación. Mantener movimiento residual sutil si una entrada larga deja después una escena visualmente inerte; permitir pausas deliberadas cuando ayuden a leer.

Variar transiciones y entradas. El círculo/anillo no es el cambio predeterminado de cada imagen. Un círculo semántico dentro de un diagrama no está prohibido.

Tomar **cuatro o más familias** como referencia para una pieza con suficientes cambios. La plantilla actual implementa barrido (`wipe`), empuje (`push`), máscara (`mask`), profundidad (`depth`), paneo (`pan`), zoom y fundido (`fade`). Evitar repetir la misma familia en cambios consecutivos cuando haya una alternativa natural.

En una pieza breve con pocos cortes, reducir la cuota y registrar la razón; no alargar ni saturar el video para cumplir un número. `match-cut`, `diagram-morph` y `object-reveal` son ideas futuras que requieren coreografía e implementación propias: la base las rechaza y nunca debe declararlas para simular un efecto distinto.

Sincronizar cambios con ideas, voz y música. El intervalo histórico de 1.2–1.8 segundos es orientación, no obligación. La legibilidad y la comprensión prevalecen.

Solapar escenas hasta cubrir completamente la transición. Comprobar que máscaras oscuras o barridos no descubran un fondo vacío cuando termina el recurso anterior. Evitar flashes blancos y saltos bruscos no intencionados.

## Voz, música y subtítulos

Priorizar Fish. Separar el motor TTS (`model`) del identificador de voz (`reference_id`); registrar ambos y conservar la toma sin mezclar.

Buscar voz femenina, español mexicano, natural, cercana, profesional, energética y motivadora. Pedir intención conversacional, énfasis útil y pausas breves; evitar tono robótico o de locutora impostada. No añadir un requisito maternal que el usuario no estableció.

No reutilizar la voz denominada “Mexicana” en la primera entrega de beneficios. Recuperar su ID antes de usar esa etiqueta como bloqueo inequívoco. Mantener la voz V3 como candidata hasta una aprobación real.

Cuando se seleccione otra voz, generar una muestra de 10–15 segundos con texto del guion. Guardar `reference_id`, motor, parámetros, archivo y SHA-256. Registrar `voice.approval.status` como `pending`, `approved` o `rejected` y, al aprobar, quién y cuándo lo hizo.

Reutilizar una aprobación válida sin pedirla nuevamente si conserva voz y condiciones relevantes. Escuchar igualmente la nueva toma. Si no se puede reproducir audio, declarar esa limitación; no describirla como natural basándose en duración o metadatos.

Tomar referencias sociales para ritmo e intención, sin clonar identidades vocales no autorizadas. Priorizar una nueva actuación antes de acelerar una toma lenta; ajustar velocidad solo si conserva claridad y naturalidad.

Crear o seleccionar música acorde al arco del guion, con espacio para voz y cierre definido. Documentar proveedor, archivo y licencia; “generada” u “original” no acredita automáticamente uso comercial.

Usar SFX variados y precisos: acciones, documentos, énfasis y transiciones. Evitar repetir el mismo sonido por costumbre. Ajustar música y efectos para que ninguna palabra importante quede enmascarada.

Derivar subtítulos de la **toma final**. Recalcularlos al cambiar voz, pausas o velocidad. Ubicarlos arriba, con contraste, líneas breves y zona segura; verificar palabras, inicios, finales y acentos.

## Timeline, exportación y revisión

Construir el timeline desde voz final y unidades de sentido. Registrar por escena ID, inicio, fin, activos, texto, transición y duración de solapamiento. Registrar también música, SFX y cues de subtítulos.

Evitar huecos de cobertura y recursos duplicados por error. Revisar tiempos como segundos o fotogramas explícitos, sin mezclarlos. Aplicar fondos continuos durante cambios de escena.

Usar como referencia vertical 1080×1920 a 30 fps, video H.264 y audio AAC. Ajustar duración al mensaje: 50.15 o 55.10 segundos fueron resultados anteriores, no requisitos.

Apuntar a mezcla cercana a −16 LUFS, sin clipping y con margen de true peak; usar −2 dBTP como objetivo práctico ajustable, no garantía histórica. Distinguir dBTP de dBFS y guardar herramienta, comando y resultado.

Auditar el MP4 codificado: decodificación, duración, pistas, resolución, frecuencia, loudness, picos y posibles cuadros negros. Examinar transiciones y comparar audio con subtítulos. Interpretar detectores de congelamiento o luminancia en contexto.

No adoptar los valores históricos 10.78/11.86 como certificación de ausencia de destellos: faltan fórmula y escala originales. Una métrica de luminancia no sustituye revisión visual ni certificación de accesibilidad.

Completar revisión manual del video a tamaño móvil y escucha real. Revisar voz, legibilidad, logos, bordes, composición, ritmo, SFX, contacto y cierre. Si una comprobación no pudo ejecutarse, marcarla pendiente.

Entregar versión identificada, MP4, portada, manifiesto y evidencia disponible. Distinguir generado, comprobado técnicamente y aprobado por el usuario. No prometer perfección ni publicar en redes sin una instrucción que lo autorice.


---

## Archivo: skills/milla-video-studio/references/workflow.md

# Flujo guiado de producción

Ejecutar el trabajo autorizado hasta la entrega, explicando avances reales con frases breves. Consultar [standard.md](skills/milla-video-studio/references/standard.md) para criterios editoriales y [connections.md](skills/milla-video-studio/references/connections.md) para APIs y configuración. No presentar una simulación o un comando preparado como ejecución real.

## Índice

- Orientar y recuperar
- Preparar espacio y conexiones
- Investigar y cerrar el guion
- Seleccionar voz y producir activos
- Montar y revisar
- Entregar, reanudar y mejorar

## 1. Orientar y recuperar

Identificar si se solicita un video nuevo, corregir una capa, continuar una producción o instalar/configurar el flujo. Conservar el objetivo activo cuando el usuario diga “continúa”; no crear otro proyecto por inercia.

Recuperar brief, manifiesto, aprobaciones y archivos disponibles antes de generar. Si solo existe el MP4, usarlo como referencia y registrar que falta el fuente. No afirmar reconstrucción exacta.

Confirmar lo que cambia materialmente el trabajo: tema, público, objetivo, marca, formato, publicación prevista y restricciones. Resolver detalles rutinarios con criterio. No repetir preguntas ya contestadas ni pedir aprobación para cada operación reversible autorizada.

Dar una actualización inicial concreta: qué se recuperó, qué falta y cuál es el próximo resultado verificable. Durante operaciones largas, informar cambios y resultados; no encadenar anuncios de “inicio”.

## 2. Detectar capacidad real

| Entorno | Conducta |
|---|---|
| Terminal, archivos y APIs disponibles | Ejecutar los pasos autorizados, conservar resultados y comprobarlos. |
| Terminal disponible sin proveedor conectado | Preparar guion, manifest, montaje y pruebas locales mientras se guía la conexión faltante. |
| Solo chat o herramientas insuficientes | Guiar una acción por vez en el equipo del usuario y solicitar su resultado observable. Entregar archivos/comandos posibles sin afirmar ejecución. |
| Servicio bloqueado | Registrar causa y usar un respaldo permitido si ya está autorizado; no eludir controles ni inventar acceso. |

Leer la ayuda de los scripts y verificar versiones antes de utilizarlos. Desde la raíz de esta skill, ejecutar `python scripts/milla.py doctor` para diagnóstico local; este comando no prueba las cuentas ni su saldo.

## 3. Preparar espacio privado y estado

Crear una carpeta de producción privada fuera del repositorio público, por ejemplo `/ruta/privada/productions/<id>`. No usar los recursos privados como ejemplos del paquete instalable.

Inicializar sin sobrescribir: `python scripts/milla.py init-project /ruta/privada/productions/<id> --title "Título"`. Revisar los archivos creados antes de completarlos.

Separar guion, prompts, fuentes, estados de tareas, imágenes, audio, subtítulos, revisiones y entregas. Mantener nombres estables y versiones; conservar siempre la última entrega aprobada.

Usar `project.json` como manifiesto de montaje según el esquema incluido. Registrar metadatos adicionales en archivos privados asociados cuando el renderer no los consuma. No inventar campos que el validador interprete como evidencia.

Mantener como mínimo: ID y versión, brief, fuentes, decisiones, hashes, procedencia/licencias, motor y voz, muestra/aprobación, escenas, cues, mezcla, resultado de QA y tareas pendientes.

Registrar jobs con proveedor, modelo, hash de solicitud, task ID, estado, fechas y rutas de resultado. Guardar prompts sensibles y URLs firmadas solo en privado; excluirlos de commits y logs públicos.

## 4. Conectar un servicio por vez

1. Detectar si ya existe una conexión suficiente; reutilizarla sin solicitar otra clave.
2. Explicar una sola acción concreta en la pantalla o plataforma correcta.
3. Configurar secretos en el administrador de la plataforma o variables de entorno, nunca en el chat.
4. Verificar presencia de configuración sin mostrar valores.
5. Ejecutar una prueba mínima autorizada y registrar su resultado real.
6. Continuar con el siguiente servicio necesario; no exigir conexiones que el encargo no utiliza.

Para Kie y Fish, seguir los contratos y comandos de `connections.md`. No copiar credenciales expuestas en conversaciones anteriores a este paquete. No incluir valores reales en comandos, notebooks, capturas, commits ni reportes.

Comprobar precio, saldo y permisos actuales; distinguir TTS de transcripción y motor de voz. Respetar presupuesto y reintentos autorizados. No pedir permiso otra vez si el alcance ya está autorizado; consultar antes de contratar planes, recargar o ampliar gasto fuera de ese alcance.

Mantener separado costo estimado de cargo confirmado. Si no se conoce el precio, decirlo y acotar la prueba antes de lanzar un lote grande. No asumir que una opción gratuita permite todo uso comercial.

Ejecutar primero en seco cuando el adaptador lo admita. Añadir `--execute` únicamente para la operación real autorizada; la bandera no sustituye revisar destino, parámetros o derechos.

## 5. Investigar y cerrar el guion

Investigar fuentes oficiales y leer los pasajes relevantes. Guardar URL, título, fecha de consulta, jurisdicción, afirmación sustentada y límites. No citar normas por memoria si el contenido es jurídico o puede haber cambiado.

Definir estructura, beneficio para el espectador y CTA. Redactar para escuchar, con frases comprensibles y pronunciaciones de nombres o siglas. Evitar promesas jurídicas y datos de contacto no confirmados.

Estimar duración a partir de una lectura realista, sin forzar un número histórico. Preparar un storyboard con intención visual, recurso requerido y transición propuesta por bloque.

Avanzar con el guion autorizado; no añadir una aprobación rutinaria si el usuario ya pidió producirlo. Resolver antes de generar cualquier duda que altere hechos, voz elegida o una preferencia relevante.

## 6. Seleccionar la voz

Revisar si existe muestra aprobada con voice ID, motor, parámetros y archivo verificables. La voz V3 de beneficios no está aprobada por el mero hecho de haberse entregado; no reutilizar la voz previamente rechazada.

Si cambia la voz o falta una referencia aprobada, seleccionar candidatos adecuados y producir una muestra de 10–15 segundos del guion. Escucharla, conservarla y pedir una elección concreta solo cuando sea necesaria para fijar la voz.

Guardar aprobación como `pending`, `approved` o `rejected`, con muestra, hash y evidencia de quién/cuándo aprobó. No aprobar por cuenta del usuario. Continuar mientras tanto investigación, storyboard y preparación local compatibles.

Generar la narración completa con la voz aprobada y escucharla. Corregir actuación, pronunciación o pausas antes de montar; no sustituir una interpretación deficiente por aceleración agresiva.

## 7. Generar imágenes, música y SFX

Preparar un inventario de escenas únicas. Generar con Kie/Nano Banana Lite y el perfil visual; dejar diagramas exactos y tipografía fuera de las imágenes sintéticas.

Guardar el estado de cada solicitud antes de generar otra. Si el envío termina con timeout, tratarlo como resultado incierto y consultar el historial antes de volver a pagar. Consultar tareas pendientes por el mismo ID con intervalos y límite total.

Cuando un resultado esté listo, descargarlo a una ruta privada, comprobar tipo/tamaño y calcular hash. Validar host de descarga; no reenviar claves a CDN ni conservar una URL temporal como único respaldo.

Revisar cada recurso según el estándar. Registrar rechazo y causa; sustituir únicamente lo que falla. Verificar alfa, bordes, logos y composición antes de aprobar. Usar respaldos Kie con contrato comprobado, sin ChatGPT Image.

Seleccionar o generar música y SFX adecuados, con derechos documentados. Si una licencia no está clara, usar una alternativa verificable; no etiquetar como libre de derechos una pista por proceder de una IA.

## 8. Construir timeline y preview

Obtener o alinear la transcripción con el audio final. Corregir manualmente palabras, tiempos y pronunciaciones; recalcular después de cualquier edición de voz. No simular precisión palabra a palabra con duraciones uniformes.

Completar escenas, activos, cues, transiciones, música y SFX en el manifiesto. Mantener unidades explícitas y comprobar continuidad, solapamiento, activos existentes y duración de cierre.

Copiar la plantilla Remotion al espacio privado y seguir su documentación y scripts reales. Servir medios localmente para preview; no publicarlos ni incluirlos en un commit porque el renderer use una carpeta llamada `public`.

Validar el borrador: `python scripts/milla.py validate /ruta/privada/productions/<id>/project.json --allow-pending`. Esta opción permite pendientes de borrador, no incumplimientos de política ni una entrega final sin revisión.

Renderizar primero un preview o fotogramas de escenas y transiciones relevantes. Revisar composición, voz, subtítulos y cierre a tamaño móvil. Corregir la capa afectada antes del render completo.

## 9. Exportar y verificar

Validar sin `--allow-pending` cuando estén completos recursos y aprobaciones necesarias. No modificar campos de QA para hacer pasar una prueba que no se realizó.

Renderizar el MP4 completo; preparar mezcla y normalización según el estándar. Conservar voz, música y SFX separados. No normalizar repetidamente sin una medición que lo justifique.

Ejecutar `python scripts/milla.py inspect-video /ruta/privada/productions/<id>/entregas/final.mp4 --luminance --output /ruta/privada/productions/<id>/revisiones/qa-final.json` con una ruta de reporte nueva.

Interpretar los resultados: métricas y alertas no aprueban voz, marcas, legibilidad ni contenido jurídico. Revisar el MP4 codificado y escucharlo; anotar comprobaciones manuales, fallos reales y límites del entorno.

Si hay un fallo, corregirlo, crear otra versión y repetir las comprobaciones afectadas y la integridad final. No regenerar todos los activos válidos ni añadir pruebas sin un riesgo concreto.

## 10. Entregar, reanudar y mejorar

Entregar MP4 y portada con versión identificada, resumen de cambios, comprobaciones realizadas y pendientes relevantes. Guardar duraderamente fuente y medios autorizados según las capacidades de la plataforma; un enlace temporal no equivale a persistencia.

Mantener código y documentación reutilizables separados de producciones privadas. Antes de subir a un repositorio público, revisar archivos, licencias y diff; ejecutar `python scripts/milla.py secret-scan /ruta/del/paquete` y recordar que un escáner no garantiza ausencia de secretos.

No publicar videos en redes ni compartir datos de clientes por inferirlo de una autorización para subir la herramienta a GitHub. Conservar la audiencia del repositorio y el destino del video como decisiones distintas.

Al reanudar, leer manifiesto, checkpoint y jobs; verificar hashes y archivos presentes. Recuperar lo perdido desde almacenamiento autorizado antes de reconstruir. Mantener desconocidos como desconocidos y no inventar IDs o resultados.

Registrar cada mejora con observación, versión, cambio, prueba y aprobación pertinente. Actualizar código o perfil en su lugar correcto; preservar preferencias expresas. Concluir con estado real: preparado, generado, comprobado técnicamente o aprobado por el usuario.


---

## Archivo: skills/milla-video-studio/references/connections.md

# Conexiones y proveedores

Verificación documental: 4 de octubre de 2026. Estos adaptadores se probaron con respuestas simuladas. **No se verificaron credenciales, saldo, calidad de voz ni generación real.** Un esquema documentado no acredita una conexión operativa.

## Índice

- Configuración inicial
- Imágenes Kie
- Voz Fish
- Fotografías reales con Apify
- Música
- Descargas, errores y recuperación
- Fuentes y comprobaciones futuras

## Configuración inicial

1. Identificar si la IA tiene terminal y archivos. Si solo tiene chat, explicar un paso a la vez y entregar los comandos para el equipo del usuario. Leer una skill no concede conexiones ni capacidad de ejecutar.
2. Crear un directorio privado de proyecto fuera del repositorio. Guardar ahí guion, prompts, estados, medios y licencias. Los scripts base y el instalador usan Python 3.9 o posterior y biblioteca estándar. Los entornos opcionales de WhisperX y `rembg` se aíslan con Python 3.11 como indica [media-prep.md](skills/milla-video-studio/references/media-prep.md).
3. Crear claves nuevas en [Kie](https://kie.ai/api-key) y [Fish](https://fish.audio/app/api-keys). Configurarlas con el administrador de secretos de la plataforma o variables `KIE_API_KEY` y `FISH_API_KEY`. Nunca pedir claves por chat ni copiarlas a prompts, comandos con valores literales, GitHub o archivos públicos. Las claves antes compartidas por chat no son material reutilizable del paquete.
4. Consultar precio y saldo actuales. Definir el gasto máximo por proyecto y cuántos reintentos caben. Los scripts no calculan precios, no recargan cuentas y no autorizan gastos; `--execute` representa una ejecución previamente autorizada.
5. Ejecutar primero en seco. Explicar brevemente qué hará la siguiente acción y continuar con la autorización vigente. Una muestra de voz nueva requiere evaluación real antes de usarla en todo el montaje.

## Imágenes Kie

Modelo principal comprobado: **`nano-banana-2-lite`**. Endpoint: `POST https://api.kie.ai/api/v1/jobs/createTask`. Requiere `model`, `input.prompt` y `input.aspect_ratio`. El esquema permite `image_urls` opcional (hasta 10 URLs); el adaptador incluido mantiene la variante mínima de texto a imagen. No admite por suposición parámetros de otros modelos como `resolution`, `transparent_background` o `output_format`.

```bash
python3 /ruta/a/milla-video-studio/scripts/providers.py --workspace /ruta/produccion kie-image \
  --prompt-file /ruta/produccion/research/prompt-escena-01.txt \
  --aspect-ratio 9:16 --state estados/imagen-01.json
```

Añadir `--execute` para crear la tarea real. Guarda primero el intento y, cuando se recibe, su ID. No reutilizar un archivo de estado para cobrar otra generación. Consultar una vez:

```bash
python3 /ruta/a/milla-video-studio/scripts/providers.py --workspace /ruta/produccion kie-status \
  --state estados/imagen-01.json --execute
```

Si Lite falla, comprobar motivo, presupuesto y disponibilidad del siguiente modelo Kie aprobado. El adaptador no hace cambios silenciosos de modelo. Cada respaldo necesita su propio esquema comprobado.

**Marca visual:** rechazar recursos con logo Gemini o firmas visibles; preferir una nueva salida limpia. No equiparar esa revisión con eliminar toda identificación técnica: Google documenta SynthID en sus imágenes. Conservar procedencia y metadatos requeridos. No retirar marcas obligatorias ni firmas de terceros. Verificar alfa y bordes visualmente; PNG por sí solo no prueba transparencia.

## Voz Fish

Hay dos identificadores distintos: el header `model` selecciona el motor TTS; `reference_id` selecciona la voz. La documentación actual acepta `s1`, `s2-pro`, `s2.1-pro`, `s2.1-pro-free` y `drama-3-preview`. Un valor no reconocido puede caer en el motor predeterminado; el script lo impide validando la lista. No confundir una opción gratuita con licencia comercial universal o saldo de transcripción.

```bash
python3 /ruta/a/milla-video-studio/scripts/providers.py --workspace /ruta/produccion fish-tts \
  --text-file /ruta/produccion/research/muestra-voz.txt \
  --reference-id ID_DE_VOZ_VERIFICADO --model s2.1-pro-free \
  --out public/audio/voice-sample.wav --state estados/voz-muestra.json
```

Tras comprobar la configuración y el gasto autorizado, añadir `--execute`. Produce WAV privado. No guarda claves ni texto en el estado; guarda motor, ID y hash. Separar la toma TTS del audio mezclado y de los subtítulos.

Para seleccionar una voz: `GET /model` permite filtrar idioma y `licensed=true`; `GET /model/{id}` devuelve título, muestras, disponibilidad y otros datos. La condición pública no equivale a derechos verificados. Revisar las muestras y generar 10–15 segundos con el guion real. Comparar naturalidad, acento mexicano, energía, pronunciación y ausencia de tono impostado. Guardar la elección y el audio aprobado; no declarar que una voz está aprobada por haberse generado.

S2 usa indicaciones entre corchetes como `[confident]` o `[empathetic]`; S1 emplea otra sintaxis. Usarlas con moderación y escuchar el resultado. No sustituir actuación por aceleración. No clonar a la persona de una referencia social sin autorización de su voz.

## Fotografías reales con Apify

Apify es opcional y sirve para **descubrir candidatos reales**, no para crear imágenes ni conceder licencias. Usarlo solo cuando una persona, lugar o hecho real sea necesario; para conceptos e ilustraciones se mantiene Nano Banana/Kie o un diagrama local. El actor identificado es [automation-lab/google-images-scraper](https://apify.com/automation-lab/google-images-scraper), mantenido por su autor en la comunidad. No asumir que es un servicio de Google ni un actor mantenido por Apify.

1. Abrir su ficha, [Input](https://apify.com/automation-lab/google-images-scraper/input-schema), [Pricing](https://apify.com/automation-lab/google-images-scraper/pricing), permisos y versión/build actuales. Revalidar antes de cada ejecución: un actor comunitario puede cambiar esquema y precio aunque conserve el nombre. El costo puede incluir inicio, páginas consultadas y resultados; un límite de imágenes no equivale por sí solo a un límite total de gasto.
2. Conectar Apify por el conector disponible, su [MCP oficial](https://docs.apify.com/platform/integrations/mcp), o la consola. Para REST, configurar `APIFY_TOKEN` como secreto y enviarlo mediante autenticación; no copiarlo a la URL, código, historial de terminal o repositorio. La frase comercial del actor «sin API key» se refiere a Google y no elimina la autenticación que necesita un cliente externo de Apify.
3. Preparar una consulta concreta y acotada. Para una primera prueba usar 5–10 resultados. Este ejemplo refleja el esquema consultado y **no ejecuta el actor**:

```json
{
  "queries": ["NOMBRE DEL LUGAR O HECHO REAL"],
  "maxResultsPerQuery": 10,
  "imageSize": "large",
  "imageType": "photo",
  "usageRights": "creative_commons",
  "safeSearch": "strict",
  "language": "es",
  "country": "mx"
}
```

4. Confirmar el presupuesto autorizado. La referencia REST vigente inicia una ejecución con `POST https://api.apify.com/v2/actors/{actorId}/runs`; para este actor, `{actorId}` es `automation-lab~google-images-scraper`. Fijar `maxTotalChargeUsd` de acuerdo con el presupuesto y `restartOnError=false`. El paquete no inicia runs de Apify automáticamente.
5. Guardar el ID del run y `defaultDatasetId` de la respuesta. Consultar ese mismo run hasta que termine y recuperar entonces los elementos del dataset. Un timeout no demuestra que el run haya fallado; revisar el anterior antes de crear otro.
6. Examinar `imageUrl`, dimensiones, título y, sobre todo, `sourceUrl`/`sourceDomain`. Abrir la página original y comprobar identidad, contexto y derechos de cada imagen. Google Images, el dataset y `usageRights` solo ayudan a localizar candidatos; no conceden autorización ni prueban que la etiqueta sea correcta.
7. Elegir únicamente material propio, de dominio público comprobado o con licencia que cubra el uso. Guardar fuente, autor, licencia, fecha y atribución; rechazar marcas de agua, baja resolución, rostros que aparenten testimonio de cliente y páginas sin licencia clara.
8. Descargar el original autorizado, no una miniatura. Calcular su hash, conservar la copia de origen y registrar `provider: "real-photo"`, `source.type: "licensed"` o `"owned"`, `rights_confirmed: true` y, cuando corresponda, `discovery_provider: "apify"`. Recortar solo si la licencia permite modificación y revisar el resultado dentro del MP4.

Fuentes de operación: [ejecución en Store](https://docs.apify.com/actors/running/actors-in-store), [crear run y límites de cobro](https://docs.apify.com/api/v2/actors-runs-post) e [input del actor](https://apify.com/automation-lab/google-images-scraper/input-schema). Se verificó documentación pública; no se probó el actor, su saldo ni el acceso con una cuenta.

## Música

La página actual de Kie/Suno describe el endpoint unificado y el wrapper `ai-music-api/generate`; también conserva un ejemplo V4 mientras el texto enumera V6. **Comprobar el contrato actual antes de ejecutar.** Por esa contradicción no se incluyó un envío automático de música.

Plantilla conceptual para instrumental — completar el modelo tras comprobar catálogo, esquema, precio y derechos:

```json
{
  "model": "ai-music-api/generate",
  "input": {
    "model": "MODELO_MUSICAL_VERIFICADO",
    "custom_mode": true,
    "instrumental": true,
    "title": "MILLA - mensaje del proyecto",
    "style": "Instrumental documental cálido, motivador, pulso contenido; espacio para voz y cierre definido"
  }
}
```

No enviar `duration` hasta comprobar que el modelo la admite. Producir una pista adaptada al arco del guion y conservar el original. Edición, loop y mezcla no constituyen evidencia de licencia.

**Derechos de uso:** los términos vigentes de Suno vinculan el uso comercial a las condiciones de acceso, plan y descarga permitida. Pagar créditos a Kie no demuestra por sí solo que ese canal transfiera tales derechos. Registrar proveedor, ID, fecha, plan/canal, licencia o confirmación contractual y archivo original. Si la cadena no está documentada, usar música propia o una alternativa con licencia verificable; no etiquetar automáticamente la pista como libre de derechos.

## Descargas, errores y recuperación

Los estados guardan URLs firmadas en privado; la consola muestra solo conteos. Verificar el hostname del resultado en el archivo privado y autorizar exactamente ese CDN:

```bash
python3 /ruta/a/milla-video-studio/scripts/providers.py --workspace /ruta/produccion download \
  --state estados/imagen-01.json --index 0 \
  --allow-host HOST_CDN_VERIFICADO --out public/assets/escena-01.png
```

Añadir `--execute` para descargar. Nunca envía la clave de Kie o Fish al CDN, rechaza redirecciones, rutas que salen del proyecto y destinos de red privados. No es un descargador para URLs arbitrarias ni un servicio público: el hostname debe proceder de una respuesta verificada y aprobarse por el operador. Hay un límite de 128 MiB por respuesta. Las comprobaciones DNS son preventivas; no sustituyen aislamiento de red frente a un servidor hostil.

| Situación | Acción |
|---|---|
| Tarea en espera o generación | Reconsultar el mismo ID; espaciar consultas con backoff y fijar un límite total. |
| Timeout al crear tarea | Conservar `submission_unconfirmed`; revisar el historial antes de volver a pagar. |
| 401/403 | Revisar clave y permisos privadamente; no reintentar en bucle. |
| 429 | Respetar límites y esperar; no crear duplicados. |
| Error de proveedor/modelo | Registrar categoría y evaluar un respaldo compatible dentro del presupuesto. |
| Resultado correcto | Descargar, calcular hash y guardar; una URL temporal no es un respaldo. |
| Voz o imagen rechazada | Conservar motivo y recurso rechazado en privado; corregir la capa, no regenerar el proyecto entero. |

Kie distingue tarea creada de tarea terminada. Su consulta reconoce `waiting`, `queuing`, `generating`, `success` y `fail`. Las páginas difieren entre caducidad de URL y retención de archivos; descargar inmediatamente evita depender de cualquiera de esos plazos. Para un servicio permanente, incorporar verificación HMAC y protección contra repetición de webhooks. El paquete local usa consultas individuales y no necesita un servidor público.

## Fuentes y comprobaciones futuras

- [Kie Nano Banana 2 Lite, esquema oficial](https://docs.kie.ai/market/google/nano-banana-2-lite.md).
- [Kie: alta de claves, tareas, límites y conservación](https://docs.kie.ai/1973359m0).
- [Kie: consulta unificada](https://docs.kie.ai/market/common/get-task-detail).
- [Kie: autenticación de webhooks](https://docs.kie.ai/common-api/webhook-verification).
- [Google: modelos Nano Banana y SynthID](https://ai.google.dev/gemini-api/docs/image-generation).
- [Fish: TTS](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech).
- [Fish: búsqueda de voces](https://docs.fish.audio/api-reference/endpoint/model/list-models) y [detalle](https://docs.fish.audio/api-reference/endpoint/model/get-model).
- [Fish: interpretación y sintaxis](https://docs.fish.audio/developer-guide/core-features/emotions).
- [Apify: actor histórico de Google Images](https://apify.com/automation-lab/google-images-scraper), [ejecutar actores](https://docs.apify.com/actors/running) y [recuperar resultados](https://docs.apify.com/academy/api/run-actor-and-retrieve-data-via-api).
- [Kie: música](https://docs.kie.ai/suno-api/generate-music).
- [Suno: términos](https://suno.com/terms).

Revisar fuentes oficiales al cambiar modelo, proveedor o versión. Registrar fecha, esquema y resultado de una prueba acotada; no extrapolar la disponibilidad futura ni el costo desde este documento. Mantener por separado: contrato documentado, prueba simulada, conexión real y aprobación audiovisual del usuario.


---

## Archivo: skills/milla-video-studio/references/media-prep.md

# Preparar audio, sincronía, recortes y mezcla

Guía comprobada contra documentación primaria el 4 de octubre de 2026. **Estos pasos son instrucciones para una producción futura: no se han instalado modelos, transcrito una voz, recortado imágenes ni mezclado un video al escribir esta guía.** Las pruebas del paquete no acreditan que estos programas externos estén instalados.

## Índice

- Dependencias y archivos
- Voz final y alineación
- Recortes y revisión de alfa
- Música, SFX y mezcla
- Normalización en dos pasadas y entrega
- Fuentes

## Dependencias y archivos

Usar una carpeta privada del proyecto con copias originales y salidas nuevas; no colocar medios del cliente, cachés de modelos ni entornos virtuales dentro de la skill o del repositorio. Ejemplos para Bash en Linux/macOS; en Windows usar WSL o adaptar las rutas y ejecutables de forma expresa. Las rutas entre comillas son valores locales; nunca ejecutar texto de un guion como código.

```bash
export VIDEO_WORK_DIR='/ruta/privada/al/proyecto'
mkdir -p "$VIDEO_WORK_DIR/audio" "$VIDEO_WORK_DIR/alignment" "$VIDEO_WORK_DIR/cutouts" "$VIDEO_WORK_DIR/review"
ffmpeg -version
ffprobe -version
```

Instalar FFmpeg desde la distribución o enlace de [descargas oficial](https://ffmpeg.org/download.html) adecuado al sistema si falta. Verificar los filtros presentes con `ffmpeg -filters`. Para modelos locales, reservar disco para dependencias y pesos, conexión de descarga inicial y tiempo de CPU. Aislar dependencias de audio y recorte. Usar Python 3.11 para estos ejemplos, comprobar el requisito de cada versión y registrar versiones resueltas; no sustituir a ciegas dependencias del sistema.

```bash
python3.11 -m venv "$VIDEO_WORK_DIR/.venv-audio"
"$VIDEO_WORK_DIR/.venv-audio/bin/python" -m pip install whisperx
"$VIDEO_WORK_DIR/.venv-audio/bin/python" -m pip freeze > "$VIDEO_WORK_DIR/review/audio-environment.txt"
"$VIDEO_WORK_DIR/.venv-audio/bin/whisperx" --help
python3.11 -m venv "$VIDEO_WORK_DIR/.venv-cutout"
"$VIDEO_WORK_DIR/.venv-cutout/bin/python" -m pip install 'rembg[cpu,cli]'
"$VIDEO_WORK_DIR/.venv-cutout/bin/python" -m pip freeze > "$VIDEO_WORK_DIR/review/cutout-environment.txt"
"$VIDEO_WORK_DIR/.venv-cutout/bin/rembg" i --help
```

Las primeras instalaciones resuelven versiones actuales; después de probarlas, fijarlas para el proyecto. Revisar licencias de los pesos por separado del código. Ninguna instalación requiere claves pagadas por sí misma. Las descargas pueden estar bloqueadas en entornos restringidos: reportar el bloqueo y usar un entorno autorizado, sin fingir resultados.

## Voz final y alineación

1. Aprobar la muestra real de Fish antes de producir la toma completa. El adaptador incluido solicita WAV mono de 16 bits a 44.1 kHz y exige extensión `.wav`; conservar el motor, `reference_id`, texto, parámetros y WAV original en privado. Verificar con `ffprobe` el archivo realmente recibido: la extensión por sí sola no prueba su formato.
2. Escuchar la toma completa. Corregir palabras, actuación o pausas antes de fijar tiempos. No compensar una voz rechazada acelerándola. Los cambios de velocidad o recortes posteriores obligan a alinear otra vez.
3. Preparar una copia mono para reconocimiento; mantener el original de alta calidad para la mezcla:

```bash
ffmpeg -nostdin -n -i "$VIDEO_WORK_DIR/audio/narration-approved.wav" \
  -map 0:a:0 -vn -ac 1 -ar 16000 -c:a pcm_s16le \
  "$VIDEO_WORK_DIR/audio/alignment-input.wav"
ffprobe -v error -show_entries format=duration:stream=codec_name,sample_rate,channels \
  -of json "$VIDEO_WORK_DIR/audio/alignment-input.wav"
```

4. Ejecutar reconocimiento y alineación local con WhisperX. Esta variante evita CUDA y diarización; el modelo `small` prioriza facilidad de CPU. Subir calidad si nombres o términos fallan. Descargar el modelo y el alineador requiere red inicial:

```bash
"$VIDEO_WORK_DIR/.venv-audio/bin/whisperx" \
  "$VIDEO_WORK_DIR/audio/alignment-input.wav" \
  --model small --language es --device cpu --compute_type int8 \
  --batch_size 4 --vad_method silero --output_format all \
  --output_dir "$VIDEO_WORK_DIR/alignment"
```

WhisperX usa alineación específica del idioma y entrega marcas por palabra. No requiere diarización para una narradora. El español está contemplado por sus modelos de alineación; un modelo descargado no garantiza exactitud de cada término.

5. Comparar el texto reconocido contra lo realmente pronunciado y el guion aprobado. Corregir errores de reconocimiento por segmento respetando los intervalos detectados. Si el audio omite o cambia una idea, corregir la voz; no ocultar el error escribiendo subtítulos distintos. Guardar el JSON corregido como `alignment/segments-corrected.json`, con `segments` y los campos `start`, `end`, `text`.
6. Recalcular tiempos con el texto corregido, sin inventar una distribución por número de palabras:

```python
import json, os
from pathlib import Path
import whisperx

root = Path(os.environ['VIDEO_WORK_DIR'])
source = json.loads((root / 'alignment/segments-corrected.json').read_text())
segments = source['segments']
assert segments and all(s['start'] < s['end'] and s['text'].strip() for s in segments)
audio = whisperx.load_audio(str(root / 'audio/alignment-input.wav'))
model, metadata = whisperx.load_align_model(language_code='es', device='cpu')
aligned = whisperx.align(segments, model, metadata, audio, 'cpu', return_char_alignments=False)
target = root / 'alignment/words-aligned.json'
with target.open('x', encoding='utf-8') as stream:
    json.dump(aligned, stream, ensure_ascii=False, indent=2)
```

Ejecutar ese bloque con el Python de `.venv-audio`. No añadir pausas ficticias para satisfacer una plantilla. Palabras sin tiempo, intervalos solapados impropios, cifras o nombres mal alineados pasan a revisión auditiva con forma de onda; documentar la corrección. Si ninguna herramienta puede alinear, marcar sincronía pendiente. Una estimación no se convierte en dato medido por guardarla en JSON.

Alternativa local de reconocimiento: instalar `faster-whisper` en otro entorno y usar `WhisperModel('small', device='cpu', compute_type='int8').transcribe(ruta, language='es', word_timestamps=True, vad_filter=True)`. Consumir el generador de segmentos y guardar los tiempos efectivamente devueltos. Sus marcas son una estimación del reconocimiento, no una prueba de alineación forzada contra el guion; escuchar y revisar antes del render final.

Para subtítulos superiores: agrupar palabras por unidad de sentido, evitar líneas demasiado largas y comprobar lectura en teléfono. Fijar diseño con los tiempos de la toma final; reproducir todas las entradas, cambios y cierre. Conservar SRT/JSON editable además del texto integrado en pantalla.

## Recortes y revisión de alfa

El modelo de imagen produce el recurso; rembg separa el sujeto, no crea una imagen alternativa. Trabajar sobre una copia autorizada. En el rembg documentado actualmente, el valor predeterminado es BRIA y sus pesos tienen condiciones comerciales propias; **elegir el modelo explícitamente**. El ejemplo usa `u2net`: comprobar su licencia y la de los pesos concretos antes del uso comercial.

```bash
"$VIDEO_WORK_DIR/.venv-cutout/bin/rembg" i -m u2net \
  "$VIDEO_WORK_DIR/originals/scene-01.png" "$VIDEO_WORK_DIR/cutouts/scene-01.png"
```

Si el borde necesita refinado, generar otra variante con `-a`; comparar y conservar la mejor. No usar eliminación de fondo para disimular una marca obligatoria o retirar una firma ajena. No reemplazar un modelo local por un backend cloud de rembg sin comunicar ese cambio de procesamiento.

Comprobar alfa y crear vistas de inspección sin modificar el original:

```python
import os
from pathlib import Path
from PIL import Image

root = Path(os.environ['VIDEO_WORK_DIR'])
im = Image.open(root / 'cutouts/scene-01.png')
assert 'A' in im.getbands(), 'No contiene canal alfa'
im = im.convert('RGBA')
alpha = im.getchannel('A')
lo, hi = alpha.getextrema()
assert lo < 255 and hi > 0, 'Recorte opaco o vacío'
assert alpha.getbbox(), 'Sujeto vacío'
for name, rgb in [('ivory', (247, 243, 234)), ('navy', (12, 29, 48)), ('magenta', (210, 30, 160))]:
    background = Image.new('RGBA', im.size, rgb + (255,))
    Image.alpha_composite(background, im).convert('RGB').save(root / f'review/scene-01-{name}.png')
print({'alpha_min': lo, 'alpha_max': hi, 'subject_bounds': alpha.getbbox()})
```

Ejecutar con `.venv-cutout`. La prueba solo acredita que hay alfa no trivial. Inspeccionar las tres vistas al 100%: pelo, manos, documentos, sombras, huecos, halos y residuos. Probar además el recorte sobre el fondo real del montaje. Mantener aire suficiente alrededor del sujeto y centrar ópticamente; no recortar una mano para forzar dimensiones. Rechazar logos visibles y texto inventado. Una imagen sin errores detectados no equivale a una garantía universal de calidad.

## Música, SFX y mezcla

Antes de mezclar, reunir originales y prueba de derechos conforme a [connections.md](skills/milla-video-studio/references/connections.md). Crear `music-bed.wav` con duración suficiente para el corte y `sfx-timeline.wav` con los efectos situados en los eventos reales. Ambos comienzan en el cero de la composición. Si no hay SFX, usar una mezcla de dos entradas; no fabricar eventos para aparentar producción.

Elegir un fragmento musical que acompañe el arco de la historia. Si hace falta unir partes, cortar por frase musical y aplicar un fundido cruzado; escuchar la unión. No estirar o repetir arbitrariamente hasta conseguir un archivo largo. Mantener entrada y cierre suaves. Los niveles y parámetros siguientes son puntos de partida, no valores aprobados ni una receta que garantice inteligibilidad.

Ejemplo parametrizado: crea la premezcla con narración, música y SFX; el valor `CUT_SECONDS` debe provenir del montaje aprobado, no de una duración estimada por el texto.

```python
import json, os, subprocess
from pathlib import Path

root = Path(os.environ['VIDEO_WORK_DIR'])
cut_seconds = float(os.environ['CUT_SECONDS'])
assert 1 <= cut_seconds <= 3600
audio = root / 'audio'
inputs = [audio / n for n in ('narration-approved.wav', 'music-bed.wav', 'sfx-timeline.wav')]
def duration(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    return float(json.loads(result.stdout)['format']['duration'])
assert duration(inputs[0]) <= cut_seconds + 0.02, 'El corte truncaría la voz'
assert all(duration(p) >= cut_seconds - 0.02 for p in inputs[1:]), 'Música/SFX no cubren el corte'
d = f'{cut_seconds:.6f}'
fade = f'{max(0, cut_seconds - 1):.6f}'
graph = (
    f'[0:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={d},asplit=2[v][sc];'
    f'[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={d},volume=0.16,afade=t=in:d=0.5,afade=t=out:st={fade}:d=1[m0];'
    '[m0][sc]sidechaincompress=threshold=0.025:ratio=6:attack=10:release=250[m];'
    f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={d},volume=0.35[s];'
    '[v][m][s]amix=inputs=3:duration=first:normalize=0[out]'
)
command = ['ffmpeg', '-nostdin', '-n']
for path in inputs:
    command.extend(['-i', str(path)])
command.extend(['-filter_complex', graph, '-map', '[out]', '-ar', '48000', '-c:a', 'pcm_s24le', str(audio / 'premix.wav')])
subprocess.run(command, check=True)
```

Escuchar en auriculares y altavoz de teléfono. Bajar música o SFX que cubran consonantes; no solucionar todo elevando la voz. Revisar que el ducking no produzca bombeo. Conservar pistas separadas: modificar una capa no debería obligar a regenerar recursos pagados.

## Normalización en dos pasadas y entrega

Objetivo editorial MILLA: alrededor de −16 LUFS integrados y techo prudente de −2 dBTP. No es una obligación universal de redes. Medir la premezcla, usar sus valores en la segunda pasada y verificar nuevamente el AAC del MP4 final. En el JSON de `loudnorm`, `input_tp` es true peak en dBTP; `volumedetect` informa pico de muestra en dBFS. No son intercambiables.

Este bloque usa rutas como argumentos de `subprocess`, nunca `shell=True`, y exige números medidos finitos; no pegar resultados de otro video:

```python
import json, math, os, re, subprocess
from pathlib import Path

root = Path(os.environ['VIDEO_WORK_DIR'])
source = root / 'audio/premix.wav'
target = root / 'audio/master.wav'
base = 'loudnorm=I=-16:LRA=11:TP=-2'
first = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', str(source), '-af', base + ':print_format=json', '-f', 'null', '-'], capture_output=True, text=True, check=True)
candidates = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', first.stderr, re.S)
assert len(candidates) == 1, 'Falta una medición inequívoca de loudnorm'
stats = json.loads(candidates[0])
fields = {'measured_I':'input_i', 'measured_LRA':'input_lra', 'measured_TP':'input_tp', 'measured_thresh':'input_thresh', 'offset':'target_offset'}
values = {key: float(stats[field]) for key, field in fields.items()}
assert all(math.isfinite(value) for value in values.values()), 'Audio vacío, silencioso o medición inválida'
with (root / 'review/loudnorm-pass1.json').open('x') as stream:
    json.dump(stats, stream, indent=2)
filter_value = base + ''.join(f':{key}={value:.6f}' for key, value in values.items()) + ':linear=true:print_format=json'
second = subprocess.run(['ffmpeg', '-nostdin', '-n', '-hide_banner', '-i', str(source), '-af', filter_value, '-ar', '48000', '-c:a', 'pcm_s24le', str(target)], capture_output=True, text=True, check=True)
with (root / 'review/loudnorm-pass2.log').open('x') as stream:
    stream.write(second.stderr)
```

Si las condiciones de escalado lineal no se cumplen, FFmpeg puede usar normalización dinámica; leer el resultado. No asumir éxito por haber solicitado `linear=true`. Escuchar y volver a medir. Integrar sin recomprimir la imagen únicamente si el MP4 visual ya tiene resolución, codec y duración correctos:

```bash
ffmpeg -nostdin -n -i "$VIDEO_WORK_DIR/render/visual.mp4" \
  -i "$VIDEO_WORK_DIR/audio/master.wav" -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart \
  "$VIDEO_WORK_DIR/render/final.mp4"
ffmpeg -nostdin -hide_banner -i "$VIDEO_WORK_DIR/render/final.mp4" \
  -map 0:a:0 -af 'loudnorm=I=-16:LRA=11:TP=-2:print_format=json' \
  -f null - 2> "$VIDEO_WORK_DIR/review/final-audio-measurement.log"
```

Comprobar duración de ambos flujos antes y después del mux. No usar `-shortest` para ocultar que voz y video no coinciden. Si el AAC supera el techo, ajustar el master y volver a codificar audio; conservar el resultado medido y el hash de ese MP4. Reproducir el archivo final completo y pasar la auditoría audiovisual de la skill. Una medición de volumen no evalúa actuación, pronunciación, sincronía ni saturación visual.

## Fuentes

- [FFmpeg: filtros de audio](https://ffmpeg.org/ffmpeg-filters.html), particularmente `loudnorm`, `amix`, `sidechaincompress`, `afade` y `atrim`.
- [FFmpeg: comandos y selección de flujos](https://ffmpeg.org/ffmpeg.html).
- [ffprobe: inspección de medios](https://ffmpeg.org/ffprobe.html).
- [Fish Audio: Text to Speech](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech), formatos, frecuencias de muestreo, header de modelo y `reference_id`.
- [WhisperX: instalación, CPU y alineación](https://github.com/m-bain/whisperX), [ejemplos](https://github.com/m-bain/whisperX/blob/main/EXAMPLES.md) y [alineador](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py).
- [Faster Whisper: instalación y marcas por palabra](https://github.com/SYSTRAN/faster-whisper).
- [rembg: instalación, CLI, modelos y licencias](https://github.com/danielgatis/rembg) y [U-2-Net](https://github.com/xuebinqin/U-2-Net).

Estas herramientas evolucionan: comprobar `--help`, versión, compatibilidad y licencia efectiva antes de instalar o ejecutar. Registrar qué etapas se realizaron de verdad y cuáles siguen pendientes.


---

## Archivo: skills/milla-video-studio/references/prompts.md

# Prompts editables y dirección

Son plantillas de intención, no garantías. Sustituir variables con hechos confirmados. No enviar datos reales de clientes a proveedores por defecto.

## Guion

“Preparar Short sobre {tema} para {audiencia}, en {jurisdicción}, objetivo {objetivo}. Investigar fuentes oficiales y registrar afirmaciones verificables. Lenguaje hablado, breve y profesional. Abrir con situación reconocible; mostrar opciones y prevención. No prometer resultados. CTA confirmado: {cta}. Un recurso útil por idea, sin fijar artificialmente nueve escenas.”

## Kie · recorte

“Recurso editorial jurídico boutique: {concepto} mediante {situación}. Marfil #F6F0E4, navy #172636, dorado #D6A72C, luz suave, composición ópticamente centrada. Sujeto completo, margen de cámara, perspectiva coherente, contornos separables. Fondo uniforme {chroma distinto del sujeto}. Sin texto, firma, logo Gemini/proveedor, watermark, marco, tarjeta, partículas, polvo, chispas ni confeti. {Detalles concretos}. Preparar para separar capas y animar 2.5D.”

Si se necesita escena con fondo completo, indicarlo. No fingir alfa generado. Mantener referencias autorizadas. Revisar anatomía y concepto. No enviar parámetros API que ese modelo no admite.

## Voz

“Femenina mexicana, adulta, cercana y segura. Explicar a una persona con intención conversacional, energía motivadora, cambios reales de emoción, pausas breves y énfasis en {palabras}. Sin anuncio rígido, infantilización ni lectura robótica. Pronunciar {glosario}.”

Aplicar dirección con controles realmente soportados; no pegarla en texto que TTS pronunciará. Probar muestras. No usar audio de TikTok para clonar identidad.

## Música

“Instrumental documental moderna para {tema}, emoción {arco}. Pulso compatible con voz, espacio en frecuencias medias, inicio con intención, crecimiento moderado y cierre resuelto. Sin voz ni melodía competidora. Duración útil {segundos} con margen de edición.”

Revisar licencia y escuchar. Si no hay derechos claros, elegir pista autorizada. No generar como prueba técnica sin presupuesto.

## Diagrama

Definir relaciones exactas con nodos/texto nativo y fuente de cada dato. Flechas explicativas, no ambiente. Asignar a cada corte una familia y razón: máscara para revelar documento, desplazamiento entre opciones, profundidad para jerarquía o transformación de un proceso. No insertar datos exactos dentro de imágenes generadas.


---

## Archivo: skills/milla-video-studio/references/rendering.md

# Compositor Remotion: plantilla nueva

Esta es una implementación original reutilizable, construida para este paquete. **No es el código original recuperado de los Shorts ni un render aprobado por la dirección creativa.** Traduce el estándar a controles editables; cada video necesita su propia dirección visual, escucha y revisión. No contiene imágenes comerciales, narración, pistas musicales, claves ni API de generación.

## Preparación

1. Crear una producción autocontenida con `python3 /ruta/a/milla-video-studio/scripts/milla.py init-project /ruta/produccion --title "Tema"`. El comando copia esta plantilla y crea el manifiesto sin sobrescribir destinos existentes. Mantener la plantilla instalada como fuente inmutable y la producción fuera de repositorios públicos.
2. Entrar en `/ruta/produccion`, instalar Node.js 22 o posterior y ejecutar `npm ci`. Las dependencias quedan fijadas por `package-lock.json`; Remotion y sus paquetes usan la misma versión exacta, `4.0.532`.
3. Ejecutar `npm run typecheck` y `npm test`. Revisar la licencia vigente de Remotion según tamaño de empresa y tipo de uso; instalar el paquete no otorga automáticamente derechos para cualquier operación comercial.
4. Colocar cada medio aprobado bajo `public/`, conservando su ruta exacta de `project.json`. Si un asset declara `"path":"assets/casa.png"`, el único archivo válido es `/ruta/produccion/public/assets/casa.png`. El validador Python calcula el SHA-256 de ese archivo y Remotion lo carga mediante `staticFile("assets/casa.png")`.
5. Validar desde cualquier directorio con `python3 /ruta/a/milla-video-studio/scripts/milla.py validate /ruta/produccion/project.json --allow-pending`; retirar `--allow-pending` antes del render completo. Después abrir `npm run studio` para inspeccionar. El demo predeterminado es silencioso, tipográfico y técnico, deliberadamente sin subtítulos inventados.

Contrato único de ubicación:

- `project.json`, `package.json`, `package-lock.json`, `src/` y `test/` viven en la raíz de la producción.
- `assets[].path` y `voice.approval.sample_path` son rutas POSIX relativas a `public/`; no deben empezar por `public/`. Se rechazan rutas absolutas, URLs, barras inversas, segmentos vacíos, `.` o `..`, controles y `%`, `?` o `#`.
- `public/assets/` contiene imágenes y `public/audio/` contiene muestra de voz, narración, música y SFX. No crear copias paralelas en `assets/` o `audio/` en la raíz: no son las que renderiza `staticFile()`.
- `delivery.video_path` es relativo a la raíz de la producción y normalmente apunta a `out/final.mp4`. Nunca poner secretos en `public/`.

## Entrada: el mismo project.json

Pasar el manifiesto como objeto directo, sin envolverlo en otra propiedad:

```bash
npm run render -- --props=project.json
```

Produce `out/review.mp4` para revisión. Tras aprobarla, renderizar el archivo declarado por defecto en `delivery.video_path` con:

```bash
npx remotion render src/index.ts MillaVideo out/final.mp4 --props=project.json --codec=h264 --audio-codec=aac --pixel-format=yuv420p
npx remotion render src/index.ts MillaVideo out/corte-01.mp4 --props=project.json --codec=h264 --audio-codec=aac --pixel-format=yuv420p
npx remotion still src/index.ts MillaVideo out/portada-candidata.png --props=project.json --frame=90
```

No confundir una portada candidata con una portada aprobada. Seleccionar el frame por el contenido real y comprobarlo a tamaño de teléfono. En la primera ejecución Remotion puede necesitar descargar Chrome Headless Shell; si la red está bloqueada, informar la limitación y usar un navegador local autorizado mediante `--browser-executable`, sin evadir restricciones.

| Campo | Contrato del compositor |
|---|---|
| `schema_version` | `1` |
| `output` | `width:1080`, `height:1920`, `fps:30`, `durationSeconds` positivo |
| `assets` | IDs únicos, `path` POSIX relativo a `public/`, `kind`; imágenes con `provider:"kie"`; Python verifica el mismo `public/<path>` que consume Remotion |
| `scenes` | Array ordenado; cada escena tiene `id`, `start`, `end`, `asset_ids`, `title`, `transition` |
| `scene.asset_ids` | Cero a tres imágenes; todas se muestran con `contain`, centradas; no se repiten entre escenas |
| `scene.title` | Hasta 74 caracteres; título editorial, no transcripción automática |
| `scene.kicker`, `scene.body` | Opcionales, hasta 48 y 145 caracteres; no sustituir subtítulos |
| `scene.theme` | `ivory` o `navy`; paleta fija marfil `#F6F0E4`, azul `#172636`, dorado `#D6A72C` |
| `scene.transition` | `family` implementada y `durationSeconds` de solapamiento entrante |
| `scene.diagram` | Nodos y aristas nativos exactos, descritos abajo |
| `subtitleCues` | Opcional; `{start,end,text}` con tiempos medidos sobre la narración final; nunca generados por reparto de palabras |
| `subtitlesVerified` | Debe ser `true` si existen cues; declaración no sustituye escucha y evidencia |
| `subtitleCues[].words` | Opcional; `{start,end,text}` absoluto por palabra, obtenido del audio real, mismo texto que el cue |
| `wordTimestampsVerified` | `true` obligatorio si hay palabras temporizadas; habilita palabra activa dorada, sin alterar tamaño ni posición |
| `audio.voice`, `audio.music` | IDs de assets de tipo `audio`, ambos comienzan en t=0; preparar silencios o un montaje de audio si se necesitan otros tiempos |
| `audio.sfx` | `{asset_id,start,volume?,duration?}`; eventos separados, sincronizados con acciones concretas |
| `audio.voiceVolume`, `audio.musicVolume` | Ganancia entre 0 y 1; defaults 1 y 0.14; no equivalen a LUFS |
| `branding` | `name`, `footer` opcionales; no inventar dominio ni CTA |

El esquema global puede conservar más datos de investigación, licencias, hashes, aprobaciones y entrega. El renderizador consume únicamente los campos anteriores. La validación Python del proyecto es la responsable de integridad de archivos y evidencia; la validación de render comprueba estructura y tiempos, **no detecta visualmente un logo ni escucha una voz**.

## Solapamientos sin huecos

`start` y `end` son segundos absolutos del video; `end` es exclusivo. Todos los tiempos se convierten por `Math.round(segundos * 30)`. Los cues se aplican sobre ese mismo reloj.

Ejemplo: escena A `start:0,end:4.4`; escena B `start:4,end:8.4,transition:{family:"wipe",durationSeconds:0.4}`. A permanece detrás hasta que B ocupa el cuadro por completo. No restar otra vez el solapamiento a la duración total.

Reglas comprobadas antes de renderizar:

- La primera escena comienza en frame 0 y tiene transición de duración 0.
- Cada escena siguiente avanza en inicio y final; su transición dura al menos dos frames y menos que la propia escena.
- La escena anterior llega como mínimo a `inicio de la siguiente + solapamiento`.
- La última escena llega exactamente a la duración total. No se desvanece hacia un cuadro vacío.
- Fondo marfil permanente; las capas entrantes se componen encima de la anterior.
- Usar cuatro familias como perfil normal cuando existan cinco o más cambios. Una reducción explícita requiere `quality.transition_variety_rationale`; en piezas con menos de cinco cambios no se fuerza la cuota de cuatro. Nunca repetir una familia en dos cambios consecutivos.

Familias implementadas: `wipe` (revelado horizontal), `push` (desplazamiento horizontal), `mask` (revelado vertical), `depth` (perspectiva y profundidad), `pan` (entrada vertical), `zoom` (escala) y `fade` (mezcla). `circle`, `ring`, partículas y flashes no existen en esta plantilla.

`match-cut`, `object-reveal` y `diagram-morph` requieren una coreografía diseñada para los recursos específicos; se rechazan en vez de simular otra transición con el mismo nombre. Añadirlas como mejora versionada exige implementarlas, probarlas y comparar el render. La profundidad actual es 2.5D CSS; no equivale a una escena 3D con geometría y luces físicas.

## Diagramas exactos

Los textos y las relaciones se componen con SVG nativo, no dentro de imágenes de IA:

```json
{
  "nodes": [
    {"id":"documentos","label":"Documentos","x":22,"y":30},
    {"id":"opciones","label":"Opciones","x":78,"y":70}
  ],
  "edges":[{"from":"documentos","to":"opciones"}]
}
```

`x/y` son porcentajes dentro del diagrama, entre 15 y 85. Máximo seis nodos, etiquetas de hasta 28 caracteres y aristas dirigidas con referencias válidas. Las animaciones dibujan las relaciones ya declaradas, no infieren causalidad. Mantener pocos nodos; revisar cruces, espaciado y legibilidad. Con imagen y diagrama juntos, preferir dos o tres nodos y etiquetas muy cortas. Una relación jurídica incorrecta seguirá siendo incorrecta aunque el SVG sea válido.

La combinación de imagen + diagrama + `body` se rechaza porque excedería las zonas inferiores. Mover la explicación a otro plano o mantenerla en la narración; no encoger textos para forzarla. El validador también rechaza nodos cuyas cajas se superponen.

## Audio, texto y medios

- Voz, música y SFX son capas independientes. La voz no se estira ni se acelera aquí. La música tiene una entrada corta y salida suave; no se repite automáticamente si es más corta que el montaje.
- Los niveles por defecto son puntos de partida. Medir y masterizar el MP4, con voz inteligible sobre música y efectos. Conservar stems para remasterizar sin regenerar narración ni imágenes.
- Los subtítulos van en la zona superior y fuera del título; máximo 85 caracteres por cue y sin solapamientos. Corregir manualmente cortes de frase y temporización tras escuchar el audio final.
- La palabra activa se resalta en dorado únicamente cuando el cue contiene `words` con tiempos reales y `wordTimestampsVerified:true`. Se verifica el mismo texto, el orden y la pertenencia al intervalo del cue. Sin esos datos se muestra la frase completa sin adivinar qué palabra se está diciendo. Registrar la procedencia de la alineación en la evidencia del proyecto.
- Las imágenes tienen márgenes y `object-fit:contain`. No añadir tarjetas detrás de los recortes; preparar alfa real antes del montaje. El centrado geométrico no garantiza centrado óptico: inspeccionar cada asset.
- Todos los movimientos dependen del número de frame. No usar `Math.random()`, reloj real, transiciones CSS temporales, GIF no controlado ni descargas externas durante un render.
- Esta base usa Arial/Helvetica/sans-serif. No reproduce una tipografía original cuya licencia/archivo no se haya recuperado. Para fijar la misma apariencia entre máquinas, incluir una fuente licenciada y carga bloqueante antes de renderizar; revalidar saltos de línea. `fontAssetId` se rechaza hasta implementar ese control.
- La plantilla solo renderiza imágenes estáticas, diagramas y audio. Los clips generados o de cámara requieren añadir un componente de video y su validación; no basta declarar un asset `video`.

## Validación antes de entregar

1. Ejecutar validador del proyecto con hashes, proveedores, derechos, selección vocal y presupuestos antes de consumir recursos.
2. Revisar frames de cada escena y **dentro de cada transición**, incluyendo primer y último frame.
3. Renderizar MP4 y revisarlo de principio a fin, con audio; una prueba del JSON no acredita calidad visual.
4. Medir con FFmpeg/ffprobe: resolución, fps, duración, cuadros negros, freeze sospechoso, mezcla LUFS y true peak. Analizar destellos con herramienta pertinente y revisión humana; diferencias medias de luminancia son solo un indicador.
5. Registrar prueba realizada, archivo evaluado, hash, resultado y limitaciones. No llamar aprobado al render por pasar tests técnicos.

## Fuentes primarias consultadas

Registro de implementación inicial (4 de octubre de 2026): instalación de dependencias completada, `npm run typecheck` aprobado y nueve pruebas iniciales. La revisión 1.0.1 amplió la suite a 16 pruebas e incorporó una prueba cruzada desde el validador Python. El intento de `remotion still` compiló el bundle, pero **no produjo imagen**: el entorno devolvió un timeout del proxy al descargar Chrome y `uv_interface_addresses` al consultar interfaces del sistema. Por ello no se acredita aquí un render visual, compatibilidad de audio extremo a extremo ni aprobación estética. No se modificaron controles del entorno para sortear el bloqueo.

Consulta: 4 de octubre de 2026. Documentación oficial; revalidar cambios cuando se actualice la versión.

- [calculateMetadata](https://www.remotion.dev/docs/calculate-metadata): dimensiones, fps, duración y validación previa a cada composición.
- [Audio](https://www.remotion.dev/docs/media/audio): componente actual recomendado, volumen, inicio y duración.
- [Render CLI](https://www.remotion.dev/docs/cli/render): `--props` como ruta JSON, códecs y salida.
- [Still CLI](https://www.remotion.dev/docs/cli/still): extracción de frames y ejecutable local de navegador.
- [random](https://www.remotion.dev/docs/random): evitar aleatoriedad no determinista entre procesos.
- [Licensing](https://www.remotion.dev/docs/licensing) y [licencia/precios](https://www.remotion.dev/license): condiciones por uso; todos los paquetes Remotion deben fijar la misma versión.


---

## Archivo: skills/milla-video-studio/references/quality.md

# QA técnico y perceptual

La aprobación combina mediciones, inspección visual completa y escucha. Ningún número demuestra naturalidad vocal, corrección jurídica, ausencia de logos o accesibilidad frente a destellos. Conservar versión, comando, parámetros y hash del archivo.

## Audio

1. Medir con `loudnorm=I=-16:TP=-2:LRA=11:print_format=json` sin producir audio.
2. Si requiere ajuste, usar mediciones de primera pasada para una segunda pasada de loudnorm. Conservar video con `-c:v copy` cuando solo cambia audio. Fijar AAC estéreo y frecuencia explícita.
3. Volver a medir el AAC dentro del MP4. En la salida JSON de `loudnorm`, `input_i` expresa loudness integrado en LUFS e `input_tp` expresa true peak en dBTP. El `max_volume` de `volumedetect` es pico de muestra en dBFS: no renombrarlo como dBTP ni compararlo directamente con el límite de true peak.
4. Escuchar con audífonos y altavoz pequeño: voz al frente, música con mesura, SFX sin sobresalto y final sin corte.

Objetivo editorial: −16 ±1 LUFS; true peak ≤−1.5 dBTP, preferentemente cerca de −2. Son decisiones de MILLA, no norma universal de redes. Corregir mezcla antes de depender de limitador. Un silencio previsto no es un error.

## Video

Comprobar ffprobe: 1080×1920, 30 fps, H.264, AAC estéreo, duración esperada, rotación y pixel format compatible. Decodificar completo. Inspeccionar primer/último cuadro y cada unión.

`blackdetect` detecta intervalos casi negros con parámetros definidos; no todo cuadro vacío marfil. `freezedetect` detecta poco cambio; no decide si una imagen estable es defecto. Revisar cada alerta en contexto.

La diferencia de luminancia media entre fotogramas localiza saltos; no tiene umbral universal y puede ocultar destellos locales o rojos. No usar cifras históricas 10.78/11.86 como certificado. Evitar estrobos y revisar transiciones; para cumplimiento especializado usar análisis específico adicional.

## Revisión visual y auditiva

- Inspeccionar cada recurso y el MP4 completo: esquinas, mesas, ropa y objetos por marcas.
- Revisar alfa/halos en claro y oscuro; bordes recortados, verdes internos y parches.
- Comprobar ausencia de partículas en código y render, no por nombres de archivo.
- Revisar texto, ortografía, jerarquía, contraste, tamaño móvil y márgenes frente a UI destino.
- Validar todas las relaciones del diagrama durante la animación.
- Confirmar recursos únicos, transiciones variadas y cobertura al cambiar de claro a oscuro.
- Comprobar subtítulos contra voz final; tiempos de palabra solo si existen y se revisaron.
- Escuchar la actuación: un nivel correcto no convierte una voz mala en aprobada.

## Informe

Separar `measured`, `human_review`, `user_approval` y `unverified`. El informe automático queda en `needs_human_review`. Solo una revisión efectuada puede cerrar ese estado. Expresar “no detectado con estos parámetros” cuando esa sea la evidencia; no declarar perfección.

Fuente técnica consultada 2026-10-04: https://ffmpeg.org/ffmpeg-filters.html (loudnorm, volumedetect, blackdetect, freezedetect, signalstats). El código fuente de `loudnorm` etiqueta su salida como dBTP; los criterios editoriales son propios.


---

## Archivo: skills/milla-video-studio/references/improvement.md

# Mejora continua verificable

El método mejora cuando se usa y registra retroalimentación. No existe aprendizaje autónomo permanente ni vigilancia de proveedores solo por instalar.

Después de cada producción registrar: versión, ID privado, problema observado, evidencia/hash, comentario relevante sin secretos, alcance (video/perfil/método), cambio propuesto, pruebas y estado candidato/aprobado/rechazado. Una corrección expresa del usuario actualiza su preferencia; una idea del agente requiere evidencia y decisión si modifica estilo o gasto. No pedir aprobación de nuevo para correcciones rutinarias ya autorizadas.

Mantener regresiones: “continúa” con render pendiente; nuevo tema confundido con V2; voz sin aprobar; Lite falla con tarea conocida; logo en esquina; partículas prohibidas después; máscara claro→oscuro; voz cambiada tras subtítulos; timeout y doble cobro; secreto antes de publicar.

Probar código con respuestas simuladas sin gasto; declararlas simuladas. Probar render y percepción aparte. Comparar mismo guion/muestra cuando sea viable, midiendo tiempo, coste y retrabajo además de calidad. Analytics necesita fuente y acceso autorizado.

Versiones: PATCH corrige sin romper interfaz; MINOR añade compatible; MAJOR requiere migración. Actualizar estándar, ejemplo, código, tests y guía juntos. Registrar cambios en el repositorio de distribución. No reescribir el pasado como aprobado ni bajar controles para hacer pasar pruebas. Mantener versión estable y opción de revertir.

Antes de generar comprobar contratos y disponibilidad que puedan haber cambiado. No reemplazar automáticamente una voz aprobada por un modelo nuevo. Las mejoras futuras se ejecutan en otra tarea autorizada o automatización expresamente solicitada.


---

## Archivo: skills/milla-video-studio/references/portability.md

# Portabilidad

La unidad portable es la carpeta con SKILL.md, referencias, scripts y plantillas. Leerla transmite el método. Ejecutar depende del entorno y permisos, no del nombre del modelo.

| Entorno | Uso | Condición |
|---|---|---|
| Agent Skills compatible | Instalar carpeta completa | Verificar ruta/mecanismo del producto |
| Claude Code | `.claude/skills/milla-video-studio/` o `~/.claude/skills/milla-video-studio/` | Invocar `/milla-video-studio`; mantener referencias relativas |
| ChatGPT Work con Skills | Instalación mediante habilidades personales | Comprobar que aparezca en Skills |
| Gemini, Grok, DeepSeek, Kimi u otro chat | Leer método y guiar acciones | No presumir instalación nativa, terminal, MCP ni render |
| Agente con terminal/red | Ejecutar scripts/compositor | Python, Node/npm, FFmpeg, dependencias y proveedores |
| Sin red | Preparar con fuentes existentes y medios locales | No afirmar investigación actual o generación remota |

Cada usuario conecta sus propias cuentas y guarda secretos fuera del chat. Instalar no instala un MCP ni entrega credenciales. Transferir proyectos con brief, estado, manifiesto, medios, fuentes y aprobaciones mediante canal autorizado. Una URL privada inaccesible no basta; adjuntar archivos si la IA no puede leerlos.

Prompt: “Lee SKILL.md y referencias. Detecta herramientas disponibles. Quiero {nuevo video/corrección} sobre {tema}. Conserva el estándar vigente. Ejecuta lo posible y guíame brevemente por la primera conexión faltante. No declares generación, revisión o aprobación sin evidencia.”

Fuentes consultadas 2026-10-04: https://agentskills.io/specification y https://code.claude.com/docs/en/skills. La tabla es condicional: no certifica soporte nativo en todas las apps mencionadas.


---

## Archivo: skills/milla-video-studio/references/evidence.md

# Procedencia y límites

## Recuperado

- Historial visible 194–267 y solicitud actual. Contiene aviso de omisión; no es exportación completa palabra por palabra.
- MILLA-VIDEO-STANDARD.md versión 2, 129 líneas leído íntegramente. Sus reglas que permiten ChatGPT Image están sustituidas por correcciones posteriores.
- MP4 de personas físicas V2 y beneficios boutique V3 recuperados. No se distribuyen públicamente por defecto.
- Contexto resumido refiere inicio con santmun/video-vox, Remotion, FFmpeg, ElevenLabs, Kie y Apify. No equivale a transcripción original.

## No recuperado

Composición exacta, lockfile original, pistas separadas, prompts completos, tareas originales, nueve assets saneados, tiempos de subtítulos, ID exacto de voz rechazada y muestra Fish expresamente aprobada después de V3.

Las utilidades y plantilla son nuevas, no restauración exacta ni diseño ya aprobado. Las medidas históricas no sustituyen mediciones nuevas. No copiar claves, transcripción cruda, URLs firmadas o datos de clientes a GitHub.

Referencia histórica: https://github.com/santmun/video-vox. Se reconoce sin redistribuir su código; público no implica licencia de reutilización.

## Aprobaciones

Personas físicas aprobado editorialmente; después se prohibieron partículas y círculo repetitivo. Fish preferente; toma llamada “Mexicana” rechazada. V3 entregada, sin aprobación perceptual posterior visible. Conservar estado pendiente hasta elección real.

Los parámetros técnicos son reproducibles; gusto por voz y estética requiere evaluación humana. No prometer perfección absoluta o ejecución universal.
