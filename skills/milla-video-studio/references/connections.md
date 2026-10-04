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
2. Crear un directorio privado de proyecto fuera del repositorio. Guardar ahí guion, prompts, estados, medios y licencias. Los scripts base y el instalador usan Python 3.9 o posterior y biblioteca estándar. Los entornos opcionales de WhisperX y `rembg` se aíslan con Python 3.11 como indica [media-prep.md](media-prep.md).
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
