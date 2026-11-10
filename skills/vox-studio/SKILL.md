---
name: vox-studio
description: "Producir shorts verticales 9:16 estilo documental-collage (tipo Vox) con Remotion para los perfiles de Emi (personal, MILLA, Castorena, Acción Juvenil). Usar al pedir un short, video explicativo o video estilo Vox, al cambiar un perfil de marca o al auditar y corregir animaciones, recortes o subtítulos. Pregunta siempre la opinión de Emi antes del guion."
metadata:
  version: "0.1.0"
  release_date: "2026-11-10"
  language: "es-MX"
---

# Vox Studio

Compositor propio, **candidato**: rinde y está probado técnicamente, pero ningún video suyo tiene todavía aprobación estética de Emi. No sustituye a [MILLA Video Studio](../milla-video-studio/SKILL.md); para contenido jurídico de MILLA siguen valiendo sus reglas de investigación, derechos y revisión.

## Antes de escribir un guion

1. Preguntar a Emi, en cada video y sea cual sea el tema: **¿cuál es tu postura?**, qué quiere criticar o defender y qué chiste o referencia le gustaría. Se guarda en `opinion_emi`; el validador rechaza un guion sin ella.
2. Elegir perfil en `espacios/<espacio>/perfil.json` (ver [espacios](../../espacios/README.md)): `personal`, `milla`, `castorena` o `pan`. Cada uno tiene colores, voz y tono propios; no mezclarlos.
3. Investigar el tema en fuentes verificables y poner la fuente en pantalla (`fuente`) cuando haya un dato.

## Voz del guion

Crítico, con postura, teórico cuando ayude y con humor puntual (un chiste cada 2 o 3 escenas, nunca a costa del dato). Gancho en la primera frase; la pantalla debe entenderse en silencio. De 4 a 9 escenas; el `keyword` refuerza, no repite la narración. Cierra con `cta_pregunta`: una pregunta que divida opiniones.

## Flujo

Desde la raíz del repositorio; las producciones viven en `productions/` (privadas, fuera de git).

```bash
V="python3 skills/vox-studio/scripts/vox.py"
$V proyecto productions/personal/TEMA --perfil personal     # copia la plantilla y sintetiza los SFX
cd productions/personal/TEMA && npm ci && cd -
$V validar productions/personal/TEMA/guion.json
$V imagen --prompt-file P.txt --out productions/personal/TEMA/originales/01.jpg --estado productions/personal/TEMA/estados/img-01.json --execute
$V recorte productions/personal/TEMA/originales/01.jpg productions/personal/TEMA/public/img/01.png
$V voz productions/personal/TEMA/guion.json --dir productions/personal/TEMA --execute
cd productions/personal/TEMA && npm run render -- --props=src/data/video.json && cd -
$V master productions/personal/TEMA/out/video.mp4 productions/personal/TEMA/out/final.mp4
```

Sin `--execute` nada gasta saldo. Costos medidos el 10/11/2026: 4 créditos de Kie por imagen; la voz consume los caracteres de la narración. Consultar `$V saldo` antes y después.

## Reglas

- Imágenes: Kie `nano-banana-2-lite` primero. Seedream para lo realista y cualquier otro modelo requieren añadir su esquema comprobado a `MODELOS_KIE`. GPT Image solo como último recurso documentado, nunca en el perfil `milla`, y hoy lo bloquea el freno de `ia/politica.json`: cambiarlo exige confirmación expresa de Emi.
- Los recortes se generan sobre verde y se quitan por croma local; revisar cada PNG antes de montar.
- Fotos reales (Apify) solo para personas, logos o hechos que no se pueden ilustrar, con derechos verificados; pedir el token a Emi cuando haga falta.
- Subtítulos: solo con los tiempos por palabra que devuelve el proveedor de voz. Si no hay alineación, no hay subtítulos.
- Sin fades. Variar la entrada entre escenas (el validador rechaza repetir la anterior).
- Texto dentro de la zona segura de TikTok (x 90–960, y 230–1440).
- Música: ninguna por defecto hasta documentar derechos; los SFX se sintetizan con FFmpeg.

## Auditar y corregir

Después de cada render: sacar una hoja de fotogramas (inicio, mitad de cada escena y cada cambio), mirarla y corregir en `src/Vox.tsx` de la producción; medir sonoridad. Las mejoras que sirvan para todos los videos se pasan a `plantilla/` con su prueba. Lo que una IA no puede juzgar (naturalidad de la voz, ritmo, gracia del chiste) se le pregunta a Emi con el MP4 delante.

## Saldos (obligatorio en cada entrega)

Al entregar cualquier video, ejecutar `$V cierre productions/ESPACIO/TEMA` y pegar a Emi la tabla completa: lo gastado en ese video y lo que queda en Kie, ElevenLabs y Apify. Un proveedor sin conexión se informa como «no conectado», nunca se estima. El uso de Claude no se puede consultar desde aquí; decirlo así.

## Terminado

`validar` sin errores, render completo, hoja de fotogramas revisada, audio cerca de −14 LUFS y visto bueno de Emi sobre el MP4. No publicar en redes sin que lo pida.
