# Música de Flow Music: complemento opcional

**Decisión de Emi (11/11/2026):** escuchó el mismo demo con la música hecha con código (A) y con una pista de Flow Music (B) y dijo: «me gusta más la A, pero puedes complementar con la B». Por eso:

- **La música por defecto es la de código** (`scripts/sonido.py`): original, a la medida y ajustada a los cambios de escena.
- **Flow Music es un complemento.** Se usa cuando Emi la pide para un video, o cuando el género que el video necesita no existe en código (por ejemplo, instrumentos reales muy concretos). Se le propone, no se decide por él.

## Cuándo proponerla

| Situación | Música |
|---|---|
| Video normal de cualquier espacio | código |
| Emi pide «música de Flow» o un género que el código no tiene | Flow Music |
| Hay duda | código, y se le ofrece la otra |

Nunca las dos a la vez en el mismo video.

## Cómo entra al video

En el guion, además del ánimo:

```json
"musica": {"animo": "ironia",
           "archivo": "originales/musica/pista.wav",
           "origen": "Flow Music (Lyria 3.5), cuenta de Emi, generada el 11/11/2026"}
```

`armar` salta el silencio inicial de la pista, la corta a la duración del video, la cierra con un desvanecido de 0.7 s y la deja al mismo nivel que la de código (17 LU bajo la voz). Si la pista es más corta que el video, se detiene: no se estira ni se repite. `origen` es obligatorio: es el registro de derechos. Lo usado queda en `estados/musica.json` con su huella.

Límite conocido: una pista externa **no** se ajusta a los cambios de escena como la de código.

## Cómo se consigue la pista

Flow Music no tiene API oficial. Hay dos caminos, los dos con la suscripción de Emi y sin costo extra:

1. **Emi la genera** en flowmusic.app, la descarga y la deja en la carpeta de Drive «Vox Studio - Música (Flow Music)».
2. **La IA la genera en el box de Emi** (su computadora virtual), con su sesión ya iniciada. Probado el 11/11/2026:
   1. En el box, abrir una pestaña que no se cierre: `curl -s -X PUT "http://127.0.0.1:9222/json/new?https://www.flowmusic.app/session"` y anotar su `id`.
   2. Con las herramientas de navegador sobre esa pestaña: escribir el pedido en «Chat message» y pulsar «Send message» (Enter no envía). Pedido: instrumental, sin voz ni letra, ánimo, tempo, tonalidad, instrumentos, «deja espacio para la voz», «empieza en el primer pulso».
   3. Esperar cerca de un minuto. En la pista: «More options» → «Download» → «WAV». Queda en `~/Downloads` del box.
   4. Abrir otra pestaña en la carpeta de Drive y subirla: `node subir_drive.mjs TAB_ID RUTA` (`scripts/box/subir_drive.mjs`, se copia al box).
   5. Desde la sesión de trabajo, bajarla con el conector de Drive y guardarla en `originales/musica/` de la producción.

Si Flow Music pide iniciar sesión o aceptar condiciones, se le da a Emi el enlace de la pantalla del box y se espera: eso no se hace por él.

## Lo que se sabe y lo que no

- La pista pedida de 30 s salió de 2:56: la duración no se controla; se recorta.
- El control es por la página web: si Google cambia la pantalla, el paso 2 hay que ajustarlo.
- No se pudo leer cuántos créditos gasta cada pista ni cuántos quedan en el plan de Emi.
- Todo audio de Lyria lleva una marca de agua inaudible (SynthID) que lo identifica como generado con IA.
- La API de Gemini también ofrece Lyria, pero se cobra aparte de la suscripción; no está conectada.
