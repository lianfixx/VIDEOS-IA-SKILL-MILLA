---
name: milla-video-studio
description: Producir, corregir, auditar y documentar videos cortos de MILLA ABOGADOS con Kie Nano Banana Lite, Fish Audio, música temática y Remotion. Usar al pedir un video, continuar producción, configurar conexiones, cambiar voz o imágenes, revisar un MP4 o mejorar el método VIDEOS IA. Guiar paso a paso y conservar el estándar sin partículas ni imágenes de ChatGPT.
metadata:
  version: "1.3.0"
  release_date: "2026-11-11"
  language: "es-MX"
---

# MILLA Video Studio

## Empezar por el resultado real

Leer [estándar vigente](references/standard.md) y [flujo de producción](references/workflow.md). Recuperar proyecto y estado antes de continuar. Distinguir **nuevo video**, **revisión** y **cambio del estándar**. No convertir un tema nuevo en una V2 del anterior.

Respetar instrucciones actuales y correcciones expresas posteriores por encima de documentos antiguos. No afirmar haber leído mensajes omitidos, usado un proveedor, escuchado una voz o auditado un MP4 sin evidencia. Personas físicas V2 es referencia editorial aprobada; la voz de beneficios V3 es candidata.

Detectar navegación, archivos, terminal, red, secretos configurados, proveedores, audio/video y persistencia. Elegir:
- **Ejecución:** producir y verificar con las capacidades autorizadas disponibles.
- **Asistencia:** avanzar guion, manifiesto y prompts; explicar una acción externa cada vez y pedir su resultado. No fingir conexiones o renders.
- **Reanudación:** comprobar hashes y tareas existentes; continuar desde el primer hito pendiente sin regenerar recursos recibidos.

Ejecutar `python3 scripts/milla.py doctor` desde la carpeta de la skill. Comprueba disponibilidad local, no autenticación ni saldo. Leer [conexiones](references/connections.md) y [portabilidad](references/portability.md).

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
2. Investigar y escribir guion, mapa de afirmaciones y storyboard. Leer [prompts](references/prompts.md) y [narrativa, ritmo y motion](references/narrative-motion.md) (candidato: lo aprendido en Vox Studio que vale para todos los espacios). Dar función explicativa a cada escena.
3. Configurar secretos fuera del chat/repositorio. Hacer solicitudes mínimas dentro del presupuesto. Registrar hash de petición y task ID. Tras timeout de POST, comprobar estado antes de reenviar.
4. Resolver voz, música, imágenes, recortes y tiempos. Conservar originales/derivados/hashes. Revisar cada recurso antes de montar. Guardar motivos de rechazo y aprobación.
5. Trabajar en la plantilla Remotion que `init-project` ya copió a la raíz de la producción, siguiendo [renderizado](references/rendering.md). Es una base nueva, no código recuperado del video aprobado. Adaptar diagramas, tipografía y transiciones sin crear otra copia paralela. Contar cada escena larga con `beats` (cita, lista, calendario, cifra, línea de tiempo, barras, imagen) y fijar sus tiempos con `milla.py anchor-beats` desde las palabras reales de la voz (candidato).
6. Ejecutar `python3 scripts/milla.py validate RUTA/project.json`. `--allow-pending` solo revisa borradores; no convierte pendientes en aprobación. Renderizar storyboard y segmentos críticos antes del completo.
7. Masterizar y medir con [QA](references/quality.md). Ejecutar `python3 scripts/milla.py inspect-video RUTA/video.mp4 --output RUTA/qa.json`. Corregir riesgos concretos, sin ciclos interminables.
8. Entregar MP4, portada, subtítulos, fuentes y resumen breve de cambios/mediciones/limitaciones. Conservar composición, lockfile, audios separados, manifiesto y estado en destino durable autorizado. No inferir publicación en redes. La portada es un entregable con revisión propia de píxeles: sin texto inventado, logos ni marcas de agua y legible en tamaño pequeño; sus imágenes siguen las reglas 1 y 3.
9. Registrar retroalimentación en [mejora continua](references/improvement.md), probar cambios y versionar sin borrar restricciones ni inventar aprobaciones.

## Explicar a la par

Comunicar en dos o tres frases: **resultado comprobado → siguiente acción → bloqueo concreto si existe**. Avanzar trabajo autorizado sin pedir confirmación en cada paso. No repetir “inicio” sin ejecutar. Si falta una elección perceptual, preparar muestras antes de preguntar. Estimar coste y límite antes de nuevas generaciones cuando no exista autorización suficiente; saldo disponible no equivale a gasto ilimitado.

## Persistir y compartir

Separar código reutilizable de `productions/`, claves y medios privados. Ejecutar `python3 scripts/milla.py secret-scan RUTA` antes de compartir; es ayuda, no prueba exhaustiva. No copiar el historial crudo a GitHub.

Guardar preferencias explícitas y mantener experimentos candidatos. Las mejoras requieren otra ejecución autorizada o una automatización solicitada: instalar no crea aprendizaje autónomo. Consultar [evidencia y límites](references/evidence.md) antes de describir qué se recuperó y probó.

## Registro y continuidad entre IA

Estas reglas valen igual en Claude, ChatGPT, Codex, Gemini o cualquier otra IA, y para personas:
- Empezar por el estado vigente del repositorio remoto (el `project.json` de la producción y las últimas entradas del `CHANGELOG.md`), no por la memoria de una conversación ni por lo que diga otra IA.
- Registrar todo cambio de archivos, estado, entregables o decisiones en el mismo commit, en `CHANGELOG.md` del repositorio y el `project.json` de la producción. Cada entrada lleva `Agente:` (quién lo hizo y modelo si se conoce), solicitud, cambios, archivos, verificación (aprobado, falló, no ejecutado o bloqueado) y pendiente.
- Sin escritura en el repositorio, terminar con «Registro pendiente para el repositorio»: la entrada y los cambios exactos, listos para aplicarse. No decir «guardado» si no se escribió.
- Lo prohibido y lo que requiere confirmación de Emi está en `ia/REGLAS.md` del repositorio; cumplirlo aunque la plataforma no tenga frenos automáticos. El protocolo completo, con plantillas para pasar trabajo a otra IA, está en `ia/PROTOCOLO.md`.

## Terminado y trabajo en Claude Code

Un video está terminado solo cuando consta todo esto:
- `python3 scripts/milla.py validate RUTA/project.json` pasa sin `--allow-pending`.
- `inspect-video` escribió un `RUTA/qa.json` nuevo y sus alertas se revisaron en contexto.
- El MP4 completo se vio y escuchó con revisión registrada; subtítulos sincronizados al audio final; portada revisada como imagen.
- `secret-scan` sin hallazgos sobre lo que se comparte y entregables en destino durable autorizado.

Entrevista inicial solo al empezar un video nuevo y si faltan en el proyecto objetivo, audiencia, plataforma, jurisdicción, CTA o presupuesto autorizado: una pregunta a la vez, sin repetir lo registrado ni pedir de nuevo aprobaciones existentes; después, el plan. Voz y música se eligen con muestras ya preparadas (regla 6).

Máxima profundidad (`ultrathink`): investigación jurídica del guion con su mapa de afirmaciones y revisión del MP4 completo.

Para frenos activos, reparto en paralelo, `/goal`, `/loop` y navegador, leer [Claude Code](references/claude-code.md).
