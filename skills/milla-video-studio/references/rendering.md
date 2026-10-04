# Compositor Remotion: plantilla nueva

Esta es una implementación original reutilizable, construida para este paquete. **No es el código original recuperado de los Shorts ni un render aprobado por Emi.** Traduce el estándar a controles editables; cada video necesita su propia dirección visual, escucha y revisión. No contiene imágenes comerciales, narración, pistas musicales, claves ni API de generación.

## Preparación

1. Copiar `assets/remotion-template/` a la carpeta de trabajo del proyecto; mantener el original como plantilla. Excluir `node_modules/`, `out/` y medios de cualquier repositorio público.
2. Instalar Node.js 22 o posterior y ejecutar `npm ci`. Las dependencias quedan fijadas por `package-lock.json`; Remotion y sus paquetes usan la misma versión exacta, `4.0.532`.
3. Ejecutar `npm run typecheck` y `npm test`. Revisar la licencia vigente de Remotion según tamaño de empresa y tipo de uso; instalar el paquete no otorga automáticamente derechos para cualquier operación comercial.
4. Colocar los medios aprobados en `public/`, conservando las rutas de `project.json`. Si un asset dice `assets/casa.png`, debe existir `public/assets/casa.png`. Nunca poner secretos en `public/`.
5. Abrir `npm run studio` para inspeccionar. El demo predeterminado es silencioso, tipográfico y técnico, deliberadamente sin subtítulos inventados.

## Entrada: el mismo project.json

Pasar el manifiesto como objeto directo, sin envolverlo en otra propiedad:

```bash
npm run render -- --props=project.json
```

Produce `out/review.mp4` para revisión. El CLI oficial permite elegir otro nombre de salida:

```bash
npx remotion render src/index.ts MillaVideo out/corte-01.mp4 --props=project.json --codec=h264 --audio-codec=aac --pixel-format=yuv420p
npx remotion still src/index.ts MillaVideo out/portada-candidata.png --props=project.json --frame=90
```

No confundir una portada candidata con una portada aprobada. Seleccionar el frame por el contenido real y comprobarlo a tamaño de teléfono. En la primera ejecución Remotion puede necesitar descargar Chrome Headless Shell; si la red está bloqueada, informar la limitación y usar un navegador local autorizado mediante `--browser-executable`, sin evadir restricciones.

| Campo | Contrato del compositor |
|---|---|
| `schema_version` | `1` |
| `output` | `width:1080`, `height:1920`, `fps:30`, `durationSeconds` positivo |
| `assets` | IDs únicos, `path` relativo a `public/`, `kind`; imágenes con `provider:"kie"` |
| `scenes` | Array ordenado; cada escena tiene `id`, `start`, `end`, `asset_ids`, `title`, `transition` |
| `scene.asset_ids` | Cero a tres imágenes; todas se muestran con `contain`, centradas; no se repiten entre escenas |
| `scene.title` | Hasta 74 caracteres; título editorial, no transcripción automática |
| `scene.kicker`, `scene.body` | Opcionales, hasta 48 y 145 caracteres; no sustituir subtítulos |
| `scene.theme` | `ivory` o `navy`; paleta fija marfil `#F6F0E4`, azul `#172636`, dorado `#D6A72C` |
| `scene.transition` | `family` implementada y `durationSeconds` de solapamiento entrante |
| `scene.diagram` | Nodos y aristas nativos exactos, descritos abajo |
| `subtitleCues` | Opcional; `{start,end,text}` con tiempos medidos sobre la narración final; nunca generados por reparto de palabras |
| `subtitlesVerified` | Debe ser `true` si existen cues; declaración no sustituye escucha y evidencia |
| `subtitleCues[].words` | Opcional; `{start,end,text}` absoluto por palabra, obtenido del audio real, mismo texto que el cue |
| `wordTimestampsVerified` | `true` obligatorio si hay palabras temporizadas; habilita palabra activa dorada, sin alterar tamaño ni posición |
| `audio.voice`, `audio.music` | IDs de assets de tipo `audio`, ambos comienzan en t=0; preparar silencios o un montaje de audio si se necesitan otros tiempos |
| `audio.sfx` | `{asset_id,start,volume?,duration?}`; eventos separados, sincronizados con acciones concretas |
| `audio.voiceVolume`, `audio.musicVolume` | Ganancia entre 0 y 1; defaults 1 y 0.14; no equivalen a LUFS |
| `branding` | `name`, `footer` opcionales; no inventar dominio ni CTA |

El esquema global puede conservar más datos de investigación, licencias, hashes, aprobaciones y entrega. El renderizador consume únicamente los campos anteriores. La validación Python del proyecto es la responsable de integridad de archivos y evidencia; la validación de render comprueba estructura y tiempos, **no detecta visualmente un logo ni escucha una voz**.

## Solapamientos sin huecos

`start` y `end` son segundos absolutos del video; `end` es exclusivo. Todos los tiempos se convierten por `Math.round(segundos * 30)`. Los cues se aplican sobre ese mismo reloj.

Ejemplo: escena A `start:0,end:4.4`; escena B `start:4,end:8.4,transition:{family:"wipe",durationSeconds:0.4}`. A permanece detrás hasta que B ocupa el cuadro por completo. No restar otra vez el solapamiento a la duración total.

Reglas comprobadas antes de renderizar:

- La primera escena comienza en frame 0 y tiene transición de duración 0.
- Cada escena siguiente avanza en inicio y final; su transición dura al menos dos frames y menos que la propia escena.
- La escena anterior llega como mínimo a `inicio de la siguiente + solapamiento`.
- La última escena llega exactamente a la duración total. No se desvanece hacia un cuadro vacío.
- Fondo marfil permanente; las capas entrantes se componen encima de la anterior.
- Usar cuatro familias como perfil normal cuando existan cinco o más cambios. Una reducción explícita requiere `quality.transition_variety_rationale`; en piezas con menos de cinco cambios no se fuerza la cuota de cuatro. Nunca repetir una familia en dos cambios consecutivos.

Familias implementadas: `wipe` (revelado horizontal), `push` (desplazamiento horizontal), `mask` (revelado vertical), `depth` (perspectiva y profundidad), `pan` (entrada vertical), `zoom` (escala) y `fade` (mezcla). `circle`, `ring`, partículas y flashes no existen en esta plantilla.

`match-cut`, `object-reveal` y `diagram-morph` requieren una coreografía diseñada para los recursos específicos; se rechazan en vez de simular otra transición con el mismo nombre. Añadirlas como mejora versionada exige implementarlas, probarlas y comparar el render. La profundidad actual es 2.5D CSS; no equivale a una escena 3D con geometría y luces físicas.

## Diagramas exactos

Los textos y las relaciones se componen con SVG nativo, no dentro de imágenes de IA:

```json
{
  "nodes": [
    {"id":"documentos","label":"Documentos","x":22,"y":30},
    {"id":"opciones","label":"Opciones","x":78,"y":70}
  ],
  "edges":[{"from":"documentos","to":"opciones"}]
}
```

`x/y` son porcentajes dentro del diagrama, entre 15 y 85. Máximo seis nodos, etiquetas de hasta 28 caracteres y aristas dirigidas con referencias válidas. Las animaciones dibujan las relaciones ya declaradas, no infieren causalidad. Mantener pocos nodos; revisar cruces, espaciado y legibilidad. Con imagen y diagrama juntos, preferir dos o tres nodos y etiquetas muy cortas. Una relación jurídica incorrecta seguirá siendo incorrecta aunque el SVG sea válido.

La combinación de imagen + diagrama + `body` se rechaza porque excedería las zonas inferiores. Mover la explicación a otro plano o mantenerla en la narración; no encoger textos para forzarla. El validador también rechaza nodos cuyas cajas se superponen.

## Audio, texto y medios

- Voz, música y SFX son capas independientes. La voz no se estira ni se acelera aquí. La música tiene una entrada corta y salida suave; no se repite automáticamente si es más corta que el montaje.
- Los niveles por defecto son puntos de partida. Medir y masterizar el MP4, con voz inteligible sobre música y efectos. Conservar stems para remasterizar sin regenerar narración ni imágenes.
- Los subtítulos van en la zona superior y fuera del título; máximo 85 caracteres por cue y sin solapamientos. Corregir manualmente cortes de frase y temporización tras escuchar el audio final.
- La palabra activa se resalta en dorado únicamente cuando el cue contiene `words` con tiempos reales y `wordTimestampsVerified:true`. Se verifica el mismo texto, el orden y la pertenencia al intervalo del cue. Sin esos datos se muestra la frase completa sin adivinar qué palabra se está diciendo. Registrar la procedencia de la alineación en la evidencia del proyecto.
- Las imágenes tienen márgenes y `object-fit:contain`. No añadir tarjetas detrás de los recortes; preparar alfa real antes del montaje. El centrado geométrico no garantiza centrado óptico: inspeccionar cada asset.
- Todos los movimientos dependen del número de frame. No usar `Math.random()`, reloj real, transiciones CSS temporales, GIF no controlado ni descargas externas durante un render.
- Esta base usa Arial/Helvetica/sans-serif. No reproduce una tipografía original cuya licencia/archivo no se haya recuperado. Para fijar la misma apariencia entre máquinas, incluir una fuente licenciada y carga bloqueante antes de renderizar; revalidar saltos de línea. `fontAssetId` se rechaza hasta implementar ese control.
- La plantilla solo renderiza imágenes estáticas, diagramas y audio. Los clips generados o de cámara requieren añadir un componente de video y su validación; no basta declarar un asset `video`.

## Validación antes de entregar

1. Ejecutar validador del proyecto con hashes, proveedores, derechos, selección vocal y presupuestos antes de consumir recursos.
2. Revisar frames de cada escena y **dentro de cada transición**, incluyendo primer y último frame.
3. Renderizar MP4 y revisarlo de principio a fin, con audio; una prueba del JSON no acredita calidad visual.
4. Medir con FFmpeg/ffprobe: resolución, fps, duración, cuadros negros, freeze sospechoso, mezcla LUFS y true peak. Analizar destellos con herramienta pertinente y revisión humana; diferencias medias de luminancia son solo un indicador.
5. Registrar prueba realizada, archivo evaluado, hash, resultado y limitaciones. No llamar aprobado al render por pasar tests técnicos.

## Fuentes primarias consultadas

Registro de implementación inicial (4 de octubre de 2026): instalación de dependencias completada, `npm run typecheck` aprobado y nueve pruebas de validación aprobadas. El intento de `remotion still` compiló el bundle, pero **no produjo imagen**: el entorno devolvió un timeout del proxy al descargar Chrome y `uv_interface_addresses` al consultar interfaces del sistema. Por ello no se acredita aquí un render visual, compatibilidad de audio extremo a extremo ni aprobación estética. No se modificaron controles del entorno para sortear el bloqueo.

Consulta: 4 de octubre de 2026. Documentación oficial; revalidar cambios cuando se actualice la versión.

- [calculateMetadata](https://www.remotion.dev/docs/calculate-metadata): dimensiones, fps, duración y validación previa a cada composición.
- [Audio](https://www.remotion.dev/docs/media/audio): componente actual recomendado, volumen, inicio y duración.
- [Render CLI](https://www.remotion.dev/docs/cli/render): `--props` como ruta JSON, códecs y salida.
- [Still CLI](https://www.remotion.dev/docs/cli/still): extracción de frames y ejecutable local de navegador.
- [random](https://www.remotion.dev/docs/random): evitar aleatoriedad no determinista entre procesos.
- [Licensing](https://www.remotion.dev/docs/licensing) y [licencia/precios](https://www.remotion.dev/license): condiciones por uso; todos los paquetes Remotion deben fijar la misma versión.
