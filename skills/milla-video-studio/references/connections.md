# Conexiones y proveedores

Verificación documental: 4 de octubre de 2026. Estos adaptadores se probaron con respuestas simuladas. **No se verificaron credenciales, saldo, calidad de voz ni generación real.** Un esquema documentado no acredita una conexión operativa.

## Índice

- Configuración inicial
- Imágenes Kie
- Voz Fish
- Fotografías reales con Apify
- Música
- Fotografías reales con Apify
- Descargas, errores y recuperación
- Fuentes y comprobaciones futuras

## Configuración inicial

1. Identificar si la IA tiene terminal y archivos. Si solo tiene chat, explicar un paso a la vez y entregar los comandos para el equipo del usuario. Leer una skill no concede conexiones ni capacidad de ejecutar.
2. Crear un directorio privado de proyecto fuera del repositorio. Guardar ahí guion, prompts, estados, medios y licencias. El código usa Python 3.9 o posterior y biblioteca estándar.
3. Crear claves nuevas en [Kie](https://kie.ai/api-key) y [Fish](https://fish.audio/app/api-keys). Configurarlas con el administrador de secretos de la plataforma o variables `KIE_API_KEY` y `FISH_API_KEY`. Nunca pedir claves por chat ni copiarlas a prompts, comandos con valores literales, GitHub o archivos públicos. Las claves antes compartidas por chat no son material reutilizable del paquete.
4. Consultar precio y saldo actuales. Definir el gasto máximo por proyecto y cuántos reintentos caben. Los scripts no calculan precios, no recargan cuentas y no autorizan gastos; `--execute` representa una ejecución previamente autorizada.
5. Ejecutar primero en seco. Explicar brevemente qué hará la siguiente acción y continuar con la autorización vigente. Una muestra de voz nueva requiere evaluación real antes de usarla en todo el montaje.

## Imágenes Kie

Modelo principal comprobado: **`nano-banana-2-lite`**. Endpoint: `POST https://api.kie.ai/api/v1/jobs/createTask`. Requiere `model`, `input.prompt` y `input.aspect_ratio`. El esquema permite `image_urls` opcional (hasta 10 URLs); el adaptador incluido mantiene la variante mínima de texto a imagen. No admite por suposición parámetros de otros modelos como `resolution`, `transparent_background` o `output_format`.

```bash
python scripts/providers.py --workspace /ruta/proyecto-privado kie-image \
  --prompt-file /ruta/proyecto-privado/prompts/escena-01.txt \
  --aspect-ratio 9:16 --state estados/imagen-01.json
```

Añadir `--execute` para crear la tarea real. Guarda primero el intento y, cuando se recibe, su ID. No reutilizar un archivo de estado para cobrar otra generación. Consultar una vez:

```bash
python scripts/providers.py --workspace /ruta/proyecto-privado kie-status \
  --state estados/imagen-01.json --execute
```

Si Lite falla, comprobar motivo, presupuesto y disponibilidad del siguiente modelo Kie aprobado. El adaptador no hace cambios silenciosos de modelo. Cada respaldo necesita su propio esquema comprobado.

**Marca visual:** rechazar recursos con logo Gemini o firmas visibles; preferir una nueva salida limpia. No equiparar esa revisión con eliminar toda identificación técnica: Google documenta SynthID en sus imágenes. Conservar procedencia y metadatos requeridos. No retirar marcas obligatorias ni firmas de terceros. Verificar alfa y bordes visualmente; PNG por sí solo no prueba transparencia.

## Voz Fish

Hay dos identificadores distintos: el header `model` selecciona el motor TTS; `reference_id` selecciona la voz. La documentación actual acepta `s1`, `s2-pro`, `s2.1-pro`, `s2.1-pro-free` y `drama-3-preview`. Un valor no reconocido puede caer en el motor predeterminado; el script lo impide validando la lista. No confundir una opción gratuita con licencia comercial universal o saldo de transcripción.

```bash
python scripts/providers.py --workspace /ruta/proyecto-privado fish-tts \
  --text-file /ruta/proyecto-privado/voz/muestra.txt \
  --reference-id ID_DE_VOZ_VERIFICADO --model s2.1-pro-free \
  --out voz/muestra.wav --state estados/voz-muestra.json
```

Tras comprobar la configuración y el gasto autorizado, añadir `--execute`. Produce WAV privado. No guarda claves ni texto en el estado; guarda motor, ID y hash. Separar la toma TTS del audio mezclado y de los subtítulos.

Para seleccionar una voz: `GET /model` permite filtrar idioma y `licensed=true`; `GET /model/{id}` devuelve título, muestras, disponibilidad y otros datos. La condición pública no equivale a derechos verificados. Revisar las muestras y generar 10–15 segundos con el guion real. Comparar naturalidad, acento mexicano, energía, pronunciación y ausencia de tono impostado. Guardar la elección y el audio aprobado; no declarar que una voz está aprobada por haberse generado.

S2 usa indicaciones entre corchetes como `[confident]` o `[empathetic]`; S1 emplea otra sintaxis. Usarlas con moderación y escuchar el resultado. No sustituir actuación por aceleración. No clonar a la persona de una referencia social sin autorización de su voz.

## Fotografías reales con Apify

Apify es opcional y sirve para **descubrir candidatos reales**, no para crear la imagen ni conceder licencia. El actor utilizado históricamente fue `automation-lab/google-images-scraper`, mantenido por un tercero. Antes de cada uso abrir su ficha, revisar desarrollador, fecha de actualización, precio, entrada y salida; un actor comunitario puede cambiar aunque conserve el nombre.

Flujo guiado y prudente:

1. Decidir si la escena necesita realidad verificable. Para conceptos abstractos preferir diagrama local; no buscar una foto por relleno.
2. Abrir [la ficha del actor](https://apify.com/automation-lab/google-images-scraper). Revisar precio y fijar un máximo pequeño de resultados en la interfaz. La ficha consultada el 4 de octubre de 2026 documenta `queries`, `maxResultsPerQuery`, `imageSize` y `language`; comprobar de nuevo el esquema visible antes de ejecutar.
3. Hacer una consulta concreta, con búsqueda segura y filtros de tamaño/tipo. Para una primera prueba usar 5–10 resultados. La interfaz debe mostrar el costo estimado o modelo de precio antes de iniciar; el saldo de la cuenta no equivale a autorización ilimitada.
4. Examinar `imageUrl`, dimensiones, título y, sobre todo, `sourceUrl`/`sourceDomain`. Abrir la página original. Google Images y el dataset son índices: no usar una miniatura ni asumir derechos por aparecer en resultados.
5. Elegir únicamente material propio, de dominio público comprobado o con licencia que cubra el uso concreto. Guardar fuente, autor si aplica, licencia, fecha de consulta y cualquier atribución. Rechazar marcas de agua, baja resolución, rostros que aparenten testimonio de cliente y páginas sin licencia clara.
6. Descargar desde la fuente autorizada, no desde una URL temporal de miniatura. Calcular hash, conservar original y registrar en el manifiesto como `provider: "real-photo"`, `source.type: "licensed"` o `"owned"`, `rights_confirmed: true`; si se usó Apify, agregar `discovery_provider: "apify"`.
7. Recortar solo cuando la licencia permita modificación. Revisar alfa/halos y el resultado dentro del MP4. El hallazgo del scraper nunca cambia los derechos originales.

Para automatizar más adelante, la API oficial inicia el actor mediante `POST /v2/acts/automation-lab~google-images-scraper/runs` y devuelve un `defaultDatasetId`; después se leen los items de ese dataset. Construir un adaptador solo tras fijar versión del esquema y límite de gasto. Usar autenticación en header/gestor de secretos según la documentación vigente; no incrustar el token en URLs, código, historial de terminal o GitHub. Este paquete no ejecuta Apify automáticamente para evitar una llamada de costo con un contrato comunitario cambiante.

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

## Fotografías reales con Apify

Usar solo cuando una persona, lugar o hecho real sea necesario. Para conceptos e ilustraciones se mantiene Nano Banana/Kie. Actor histórico identificado y localizado: [automation-lab/google-images-scraper](https://apify.com/automation-lab/google-images-scraper), mantenido por su autor en la comunidad; no asumir que es un servicio propio de Google o un actor mantenido por Apify.

1. Abrir su ficha, [Input](https://apify.com/automation-lab/google-images-scraper/input-schema), [Pricing](https://apify.com/automation-lab/google-images-scraper/pricing), permisos y versión/build actuales. Revalidar antes de una ejecución. El precio puede incluir inicio, páginas consultadas y resultados; un límite de imágenes no equivale a un límite total de gasto.
2. Conectar Apify por el conector disponible, su [MCP oficial](https://docs.apify.com/platform/integrations/mcp), o la consola. Para REST, configurar `APIFY_TOKEN` como secreto. No copiar el token al parámetro de una URL ni al repositorio. La frase comercial del actor «sin API key» no elimina la autenticación que necesita un cliente externo de Apify.
3. Preparar una consulta acotada. Este ejemplo refleja el esquema consultado, **no ejecuta el actor**:

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

4. Confirmar presupuesto previamente autorizado y permisos mínimos. Si se usa REST, comprobar la operación actual `POST /v2/actors/{actorId}/runs`, con el identificador `automation-lab~google-images-scraper`. Establecer `maxTotalChargeUsd` conforme al presupuesto y `restartOnError=false`; no elevar permisos para sortear un rechazo. El paquete no inicia runs de Apify automáticamente.
5. Guardar ID del run y `defaultDatasetId`. Consultar ese run hasta que termine; recuperar el dataset solo cuando corresponda. Un timeout de la conexión no demuestra que el run haya fallado. No volver a crear otro sin revisar el anterior.
6. Conservar `imageUrl` y `sourceUrl`, autor, licencia y fecha. Abrir la página original para verificar identidad, contexto y derechos de la imagen concreta. El filtro de Google/actor solo ayuda a encontrar candidatos: no concede autorización ni prueba que el etiquetado sea correcto. Si no se comprueba la licencia necesaria, buscar otro recurso.
7. Descargar el original autorizado, no una miniatura; revisar definición, encuadre y marcas. Mantener intacta la copia de origen, registrar cualquier recorte autorizado y preparar alfa según [media-prep.md](media-prep.md). No retirar firmas de terceros ni sustituir una foto histórica por una imagen inventada presentada como real.

Fuentes de operación: [ejecución en Store](https://docs.apify.com/actors/running/actors-in-store), [crear run y límites de cobro](https://docs.apify.com/api/v2/actors-runs-post), [input del autor](https://apify.com/automation-lab/google-images-scraper/input-schema). Se verificó documentación pública; no se probó el actor, su saldo o acceso con una cuenta.

## Descargas, errores y recuperación

Los estados guardan URLs firmadas en privado; la consola muestra solo conteos. Verificar el hostname del resultado en el archivo privado y autorizar exactamente ese CDN:

```bash
python scripts/providers.py --workspace /ruta/proyecto-privado download \
  --state estados/imagen-01.json --index 0 \
  --allow-host HOST_CDN_VERIFICADO --out imagenes/escena-01.png
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
