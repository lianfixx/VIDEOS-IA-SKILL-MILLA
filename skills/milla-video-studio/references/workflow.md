# Flujo guiado de producción

Ejecutar el trabajo autorizado hasta la entrega, explicando avances reales con frases breves. Consultar [standard.md](standard.md) para criterios editoriales y [connections.md](connections.md) para APIs y configuración. No presentar una simulación o un comando preparado como ejecución real.

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
