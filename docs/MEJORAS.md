# Mejoras y prioridades

La mejora continua debe producir cambios comprobables, no promesas de calidad absoluta. Esta lista separa lo consolidado en la documentación de lo que aún necesita implementación, integración o validación con un video real.

Estados usados: **documentado** significa que existe una regla o especificación; **implementado** requiere código presente; **verificado** requiere una prueba y su resultado; **pendiente** significa que aún no puede darse por hecho. Un estado no implica el siguiente.

## 1. Mejoras ya realizadas en la documentación

| Prioridad | Mejora | Estado y alcance |
|---|---|---|
| P0 | Resolver preferencias contradictorias. | Documentado: cero partículas, exclusión de ChatGPT Image y variedad de transiciones prevalecen sobre propuestas antiguas. |
| P0 | Separar aprobación y entrega. | Documentado: personas físicas es referencia aprobada; la voz V3 de beneficios permanece como candidata. |
| P0 | Separar hechos y afirmaciones históricas. | Documentado: los resultados anteriores no se presentan como pruebas recién ejecutadas. |
| P0 | Proteger credenciales. | Documentado: no reproducir secretos del historial ni usarlos como ejemplos de configuración. |
| P0 | Reconocer el límite de recuperación. | Documentado: se recuperaron referencias finales, pero no el proyecto fuente exacto. La nueva plantilla es una implementación nueva. |
| P1 | Trazabilidad de decisiones. | Documentado en [RECAPITULACION.md](RECAPITULACION.md), con mensajes 194–267 y distinción de reglas sustituidas. |
| P1 | Recuperar el perfil cromático. | Documentado: `#F6F0E4`, `#172636` y `#D6A72C`, contrastados con el estándar recuperado. |
| P1 | Precisar el modelo de imagen. | Documentado: `nano-banana-2-lite` contrastado con documentación oficial. Su disponibilidad debe comprobarse al ejecutar. |
| P1 | Evitar falsas promesas de portabilidad. | Documentado: la skill no concede capacidades, cuentas ni permisos; el flujo contempla asistentes con distinta capacidad de ejecución. |
| P1 | Convertir errores anteriores en controles. | Documentado: voz, logos, chroma, solapamientos, audio, costos y persistencia tienen controles concretos. |

Esta tabla no certifica por sí sola adaptadores de API, renderizado, eliminación de marcas ni auditorías automáticas. Esas funciones requieren sus propias pruebas. Tampoco certifica que un proveedor mantenga indefinidamente el mismo nombre, precio o contrato.

## 2. Prioridades de implementación y validación

### P0 — Necesario antes de una producción de confianza

| Mejora | Criterio de aceptación | Situación |
|---|---|---|
| Registro de decisiones y aprobaciones | Cada voz, versión y regla tiene estado, evidencia y fecha; la V3 no aparece como aprobada sin decisión expresa de la dirección creativa. | Requiere verificar la implementación y mantenerla por producción. |
| Secretos y repositorio limpio | Variables de entorno o almacén de secretos; exclusiones adecuadas; revisión del diff y del historial antes de subir. Ninguna credencial real en fixtures o logs. | Control obligatorio en cada entrega. |
| Manifiesto de producción | Guarda brief, guion, recursos, modelo, tarea, procedencia, hashes, tiempos y versiones sin secretos. Distingue desconocido de inferido. | Requiere verificar implementación y uso efectivo. |
| Reanudación sin gasto duplicado | Una interrupción permite consultar tareas existentes y reutilizar activos válidos antes de crear otros. | Pendiente de prueba con adaptadores reales. |
| Voz reutilizable aprobada | Muestra breve con voice ID y parámetros; aprobación perceptual explícita antes de etiquetarla como referencia. | Pendiente: no consta aprobación de la voz V3. |
| Contenido jurídico sustentado | Fuentes oficiales fechadas, jurisdicción identificada y revisión de afirmaciones comerciales antes de generar. | Se ejecuta para cada guion; no se hereda de otro tema. |
| MP4 completo e íntegro | Archivo decodificable, duración y pistas correctas, sin recursos faltantes ni pérdida de audio. | Requiere ejecutar QA en cada entrega. |

### P1 — Mejoras de calidad con mayor impacto

| Mejora | Criterio de aceptación | Riesgo que resuelve |
|---|---|---|
| Prueba perceptual de voz | Revisar acento, intención, pausas, énfasis y pronunciación en una muestra y en el montaje final. | Una voz puede pasar LUFS y duración y aun así resultar desagradable. |
| Saneamiento y procedencia de imágenes | Original y derivado preservados, recorte inspeccionado sobre dos fondos, licencia/procedencia registradas. | Logo sobre objetos, halos, chroma y pérdida de trazabilidad. |
| Alineación a la toma final | Subtítulos y escenas se recalculan al sustituir la voz. Revisión de comienzos, finales y palabras clave. | Desfase después de regrabar o cambiar velocidad. |
| Transiciones por función | Matriz de familias y revisión de secuencias; sin círculos automáticos ni efectos repetidos por inercia. | Monotonía y saturación. |
| Continuidad temporal del render | Cobertura completa del cuadro durante transiciones y revisión de fotogramas cercanos al corte. | Destello al terminar demasiado pronto una escena. |
| Audio con mediciones separadas | Loudness integrado y true peak registrados con herramienta, versión y comando. Escucha de música y SFX bajo la voz. | Confusión dBFS/dBTP y mezcla que oculta el mensaje. |
| Revisión móvil y accesibilidad | Texto legible, contraste suficiente, zona segura y ritmo de lectura apropiado. No se presenta una prueba simple de luminancia como certificación médica o normativa. | Texto ilegible, interferencia con interfaz y falsa seguridad sobre destellos. |
| Archivo reproducible | Código, dependencias, manifiesto y activos autorizados disponibles; medios grandes fuera del Git ordinario cuando corresponda. | Pérdida de continuidad al limpiarse el espacio temporal. |

### P2 — Evolución después de validar el flujo básico

| Mejora futura | Condición para incorporarla |
|---|---|
| Integraciones intercambiables de voz e imágenes | Mantener prioridad y prohibiciones; pruebas de contrato y estados de error antes de habilitar cada proveedor. |
| Detección asistida de marcas y defectos | Medir falsos positivos y negativos. El detector ayuda a revisar; no autoriza afirmar ausencia total. |
| Presupuesto por producción y costo real por recurso | Leer precios vigentes y registrar consumo comprobado. Evitar estimaciones presentadas como cargos reales. |
| Previews económicos antes del render final | Validar voz, composición y sincronización sin regenerar activos ni pagar renders completos innecesarios. |
| Matriz de compatibilidad entre IA | Probar instalación, lectura y ejecución en cada plataforma; no inferir compatibilidad por usar Markdown. |
| Perfiles para otras marcas y audiencias | Mantener el núcleo común y separar identidad, tono, restricciones y aprobaciones de cada perfil. |
| Recuperación de fuentes originales | Incorporar solo archivos y metadatos encontrados; conservar diferencias frente a la plantilla nueva. |
| Accesibilidad ampliada | Añadir transcripción, subtítulos exportables y variantes de lectura cuando el encargo lo permita. |

## 3. Ciclo de mejora continua

1. Registrar la observación concreta: archivo, versión, segundo o fotograma y resultado esperado.
2. Clasificarla: error técnico, desacuerdo editorial, cambio de preferencia o capacidad faltante.
3. Proponer el cambio mínimo que la resuelve, indicando costo y efectos relevantes.
4. Aplicar el cambio en una versión nueva o rama; conservar la última entrega aprobada.
5. Ejecutar la comprobación relacionada con el fallo. No añadir pruebas que solo repitan la implementación.
6. Revisar el resultado perceptual cuando la mejora afecte voz, ritmo o diseño.
7. Registrar aprobación o rechazo y actualizar changelog, perfil o código según corresponda.

Una aprobación de contenido no aprueba automáticamente otra voz; una mejora técnica no permite reactivar una herramienta prohibida. Si una preferencia parece entrar en conflicto con una instrucción nueva, el conflicto se expone con una pregunta concreta después de avanzar lo posible.

## 4. Qué no se promete

- No se promete reconstrucción exacta del montaje anterior sin recuperar sus fuentes.
- No se promete instalación universal ni acceso automático a cuentas desde otra IA.
- No se promete aprendizaje autónomo ilimitado: los cambios quedan versionados y trazables.
- No se promete ausencia absoluta de defectos a partir de métricas aisladas.
- No se presenta generación de video como publicación automática en redes.
- No se completan datos faltantes —modelos, voces, tareas, permisos o resultados— con valores inventados.

El siguiente hito de calidad es producir una pieza de prueba con voz aprobada, recursos trazables, render reproducible y revisión documentada. Solo entonces podrá afirmarse que el flujo completo de esta nueva herramienta está verificado de principio a fin.
