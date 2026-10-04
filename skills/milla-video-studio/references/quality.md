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
