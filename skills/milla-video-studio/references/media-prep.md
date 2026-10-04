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

Antes de mezclar, reunir originales y prueba de derechos conforme a [connections.md](connections.md). Crear `music-bed.wav` con duración suficiente para el corte y `sfx-timeline.wav` con los efectos situados en los eventos reales. Ambos comienzan en el cero de la composición. Si no hay SFX, usar una mezcla de dos entradas; no fabricar eventos para aparentar producción.

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
