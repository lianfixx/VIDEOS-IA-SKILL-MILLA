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

Priorizar Kie con `nano-banana-2-lite`; comprobar contrato y disponibilidad actuales según [connections.md](connections.md). Si falla, evaluar otro modelo Nano Banana/Kie compatible y registrar el motivo. No cambiar de proveedor en silencio.

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
