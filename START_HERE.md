# Empieza aquí

## Si quieres que una IA te guíe

1. Dale el enlace de este repositorio o adjunta `MANUAL_COMPLETO.md` si no puede abrirlo.
2. Indica tema, público y objetivo. Si quieres MILLA, ya tiene el perfil; no vuelvas a explicar todas las reglas.
3. Pídele que detecte herramientas y conexiones. Debe ejecutar lo disponible y explicar **solo el primer paso que falte**, con su propósito y resultado esperado.
4. Conecta tus propias cuentas en los sitios oficiales. Introduce claves en un gestor de secretos o campo local oculto, nunca en el chat.
5. Cuando la voz sea nueva, escucha muestras y elige. Después debe continuar hasta entregar archivos y evidencia, sin repetir “voy a empezar”.

Ejemplo:

> Usa MILLA Video Studio. Haz un video sobre prevenir problemas al firmar un contrato, dirigido a personas de 30 a 60 años en México. Investiga primero. Conserva la identidad y las exclusiones del estándar. Avanza y explícame brevemente cada hito; pregunta solo lo que de verdad cambie el resultado.

## Si usas Claude Code

Clona el repositorio en una carpeta de trabajo:

```bash
git clone https://github.com/lianfixx/VIDEOS-IA-SKILL-MILLA.git
cd VIDEOS-IA-SKILL-MILLA
python3 tools/install_skill.py --target claude
```

El instalador copia la skill completa a tu directorio de usuario de Claude y se niega a sobrescribir una instalación. Luego usa `/milla-video-studio`. No instala dependencias ni configura claves.

Para actualizar, ejecuta `git pull --ff-only`, revisa `CHANGELOG.md`, renombra la carpeta instalada como respaldo y vuelve a ejecutar el instalador. La negativa a sobrescribir es deliberada: evita mezclar una versión nueva con archivos locales antiguos.

Para instalar a una ruta compatible elegida por ti:

```bash
python3 tools/install_skill.py --destination /ruta/de/skills/milla-video-studio
```

Consulta las reglas del producto para esa ruta. ChatGPT Work usa su mecanismo de habilidades personales; no apuntes el instalador genérico a ubicaciones administradas sin seguir ese mecanismo.

## Si prefieres ejecución local

Necesitas Python 3.9+ para los scripts base y el instalador, además de FFmpeg/ffprobe, Node 22+ y npm. Los entornos opcionales de WhisperX y `rembg` usan Python 3.11 según `media-prep.md`. El método explica para qué sirve cada herramienta; no descargues instaladores de fuentes desconocidas. Ejecuta `doctor` y luego `init-project`: este último crea fuera del repositorio una producción autocontenida con Remotion, `project.json` y las carpetas `public/assets` y `public/audio`. Sigue `references/connections.md`, `media-prep.md` y `rendering.md` dentro de la skill.

Kie genera imágenes; Fish genera voz; música se verifica por contrato y derechos; Remotion compone; FFmpeg mide y masteriza. Apify es opcional para encontrar realidad necesaria, no una obligación ni una licencia de uso.

## Qué falta de las referencias antiguas

Se recuperó el estándar y los MP4 principales, pero no su proyecto exacto ni el ID de una voz Fish finalmente aprobada. El paquete propone una base reproducible nueva y registra esos vacíos. Si compartes después el historial completo o proyecto original, se puede incorporarlo sin sustituir las correcciones vigentes.

La aprobación de voz se resuelve durante producción con muestras. No hace falta entregar ninguna clave para leer, instalar o probar localmente el método.
