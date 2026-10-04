# Validación de la versión 1.0.1

Fecha: 4 de octubre de 2026. Este informe separa pruebas locales, comprobaciones documentales, mediciones sobre referencias recuperadas y revisiones todavía pendientes.

## Resultado de los controles

| Control | Resultado | Alcance real |
|---|---:|---|
| Validación estructural de la skill | Aprobada | Nombre, frontmatter y estructura reconocibles por el validador local de Skills |
| Pruebas Python | 43/43 | Manifiesto, rutas, paridad con Remotion, voz/ID/modelo, Kie/Fish simulados, estados, secretos y FFmpeg sintético |
| Pruebas del compositor | 16/16 | Timeline, precisión por frame, transiciones, diagramas, medios, subtítulos, SFX y zonas seguras |
| Prueba cruzada Python → Remotion | Aprobada | Un manifiesto final aceptado por Python pasa el validador JavaScript y ambos exponen las mismas siete familias |
| TypeScript | Aprobado | `tsc --noEmit` sobre la plantilla Remotion |
| Inicialización real | Aprobada | `init-project` copió una producción autocontenida; sus pruebas npm y validación en borrador pasaron |
| Escaneo preventivo de secretos | 0 hallazgos en 30 textos de la skill y 43 del repositorio | Excluye binarios, dependencias e historial y no prueba ausencia absoluta |
| Llamadas pagadas | 0 | Kie/Fish se probaron con respuestas simuladas; no se comprobaron claves, saldo ni calidad remota |
| Render del compositor nuevo | Bloqueado por el entorno | El bundle compiló; Chrome no pudo descargarse por timeout del proxy y falló la consulta de interfaces. No existe un render estético aprobado de esta plantilla |

Comandos reproducibles desde la raíz del repositorio:

```bash
python3 -m unittest discover -s skills/milla-video-studio/scripts -p 'test_*.py'
python3 skills/milla-video-studio/scripts/milla.py secret-scan .
cd skills/milla-video-studio/assets/remotion-template
npm ci
npm test
npm run typecheck
```

`npm ci` necesita acceso al registro de paquetes. Un entorno que ya tenga el lockfile instalado puede ejecutar solo las dos últimas órdenes. La validación local de una skill personal pertenece al mecanismo de Skills de cada plataforma y no se simula con una prueba casera.

## Referencias audiovisuales recuperadas

Los MP4 no se publican en este repositorio. Se midieron con `inspect-video --luminance`; los informes JSON sí se conservan, con nombre, SHA-256, versiones de FFmpeg, parámetros, resultados y límites:

| Referencia e informe | SHA-256 del MP4 | Duración | Formato principal | LUFS | True peak | Negro | Mayor cambio de luminancia media |
|---|---|---:|---|---:|---:|---:|---:|
| [Personas físicas V2](audits/personas-fisicas-v2.json) | `dbee266154c20c28b5e33804a1419fab433aa2ca3fb372f72abba94964e19126` | 50.20 s | 1080×1920, 30 fps, H.264/AAC | −16.04 | −1.67 dBTP | 0 | 10.789 a ~44.0 s |
| [Beneficios boutique V3](audits/beneficios-boutique-v3.json) | `27370f0b061f1762251c0dc2147a448f7300135d5054b3412993f57907dd427c` | 55.10 s | 1080×1920, 30 fps, H.264/AAC | −16.14 | −2.00 dBTP | 0 | 11.831 a ~1.9 s |

Ambos informes permanecen en `needs_human_review`. `freezedetect` señaló 17 y 13 inicios de bajo movimiento; también puede marcar pausas o animación sutil, por lo que no demuestra congelamientos defectuosos. Los dos usan `yuvj420p`; Personas físicas V2 además contiene audio a 96 kHz. El auditor los señala frente al perfil de salida `yuv420p`/48 kHz sin afirmar que el archivo sea ilegible.

`blackdetect` usó duración mínima 0.03 s, `pix_th=0.10` y `pic_th=0.98`; `freezedetect`, −50 dB y 0.5 s. La luminancia media localiza candidatos a cortes: no es un umbral médico ni una certificación contra destellos. La hoja de contacto de Personas físicas V2 sirvió para orientar continuidad, pero no equivale a revisar todos los fotogramas. La voz V3 de beneficios sigue pendiente de aprobación expresa de la dirección creativa.

## Casos de regresión cubiertos

- El hash se calcula sobre el mismo `public/<path>` que Remotion abre; un archivo señuelo en la raíz no puede validarlo.
- `init-project` copia el lockfile, código y pruebas, crea `public/assets`/`public/audio` y nunca sobrescribe un destino.
- Python y Remotion rechazan las tres transiciones nombradas pero no implementadas, escenas o medios que el componente no puede mostrar, tiempos subframe y combinaciones que invaden zonas seguras.
- ChatGPT Image, partículas, logos o marcas de agua declaradas, Kie sin procedencia generada y fotografía real sin derechos.
- Cambio de voz/narración intentando conservar una muestra antigua, salida Fish con extensión falsa y narración con ID o motor diferente.
- Reenvío ciego tras timeout, carrera entre procesos y modelo Kie alternativo sin razón documentada.
- Reutilización de imágenes por ID, ruta o hash; traversal, URL, segmentos ambiguos y symlinks fuera de la producción.
- Diagramas con nodos superpuestos, karaoke no verificado, texto distinto del cue y SFX fuera de frame.
- MP4 técnico que exige revisión humana aunque sus mediciones terminen.

## Pendientes del flujo completo

1. Elegir y aprobar una muestra real de Fish por `reference_id` y motor; la V3 no resuelve este punto.
2. Probar una llamada real y acotada de Kie y Fish con claves nuevas, saldo revisado y gasto autorizado.
3. Producir un piloto desde `init-project` hasta la entrega con activos y derechos trazables.
4. Renderizar en un entorno con navegador autorizado y revisar todos los frames críticos, voz, música, SFX y subtítulos.
5. Confirmar licencias de música, imágenes reales, fuentes y logo usados en ese piloto.
6. Comparar el piloto con la referencia aprobada en teléfono y registrar aprobación o correcciones.

La versión 1.0.1 demuestra coherencia local entre inicialización, validadores y compositor. No demuestra aún calidad de proveedores externos, equivalencia exacta con el montaje histórico ni aprobación estética del compositor nuevo.
