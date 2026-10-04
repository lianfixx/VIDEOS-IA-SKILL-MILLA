# Validación de la versión 1.0.0

Fecha: 4 de octubre de 2026. Este informe distingue pruebas locales, comprobaciones documentales, mediciones sobre referencias recuperadas y revisiones todavía pendientes.

## Resultado de los controles

| Control | Resultado | Alcance real |
|---|---:|---|
| Validación estructural de la skill | Aprobada | Nombre, frontmatter y estructura reconocibles por el validador local de Skills |
| Pruebas Python | 35/35 | Manifiesto, seguridad de rutas, voz ligada a muestra/ID/modelo, Kie/Fish simulados, estados, secretos y auditoría FFmpeg sintética |
| Pruebas del compositor | 13/13 | Línea de tiempo, solapamientos, transiciones, diagramas, fotos con derechos, subtítulos por palabra y zonas seguras |
| TypeScript | Aprobado | `tsc --noEmit` sobre la plantilla Remotion |
| Escaneo preventivo de secretos de la skill | Sin hallazgos en 30 textos | Excluye binarios, dependencias e historial; no garantiza ausencia absoluta |
| Llamadas pagadas | 0 | Los adaptadores Kie/Fish se probaron con respuestas simuladas; no se comprobaron claves, saldo ni calidad remota |
| Render del compositor nuevo | Bloqueado por el entorno | El bundle compiló; Chrome no pudo descargarse por timeout del proxy y el entorno falló al consultar interfaces. No existe un render estético aprobado de esta plantilla |

## Referencias audiovisuales recuperadas

Los dos MP4 se midieron nuevamente con el `inspect-video` incluido. Ambos informes conservan estado `needs_human_review` porque una medición no reemplaza ver y escuchar el archivo completo.

| Archivo | Duración | Formato | LUFS integrados | True peak | Negro detectado | Mayor cambio de luminancia media |
|---|---:|---|---:|---:|---:|---:|
| Personas físicas V2 | 50.20 s | 1080×1920, 30 fps, H.264/AAC | −16.04 | −1.67 dBTP | 0 intervalos | 10.789 a ~44.0 s |
| Beneficios boutique V3 | 55.10 s | 1080×1920, 30 fps, H.264/AAC | −16.14 | −2.00 dBTP | 0 intervalos | 11.831 a ~1.9 s |

`blackdetect` usó duración mínima 0.03 s, `pix_th=0.10` y `pic_th=0.98`; `freezedetect` usó −50 dB y 0.5 s. Esta última heurística marcó tramos de poco cambio en ambos videos; también marca pausas y animaciones sutiles, así que no demuestra congelamientos defectuosos. Los cambios de luminancia son localizadores de cortes, no un umbral de seguridad contra destellos.

Se extrajo una hoja de contacto de Personas físicas V2 para orientar la continuidad visual. No se presenta como revisión de cada fotograma. La voz V3 de beneficios sigue pendiente de aprobación expresa de Emi.

## Casos de regresión cubiertos

- ChatGPT Image o proveedor visual prohibido.
- Partículas, logos de terceros o marcas de agua declaradas.
- Fotografía real sin fuente, derechos o licencia.
- Cambio simultáneo de voz y narración intentando conservar una muestra antigua aprobada.
- Uso de la voz final con ID o motor distinto de la muestra.
- Reenvío ciego tras timeout de un POST y carrera entre dos procesos.
- Modelo Kie de respaldo sin explicar por qué falló Lite.
- Reutilización de imágenes por ID, ruta o hash.
- Recorrido de rutas, URL remota en assets o salida mediante symlink.
- Transiciones repetidas, cuota reducida sin justificación, huecos y último cuadro sin cubrir.
- Diagrama con nodos superpuestos o relaciones inválidas.
- Imagen + diagrama + body ocupando la misma zona.
- Karaoke con tiempos inventados, solapados o texto distinto del cue.
- MP4 técnico que exige revisión humana aun cuando las mediciones terminan.

## Pendientes antes de llamar verificado al flujo completo

1. Elegir y aprobar una muestra real de Fish por ID y motor; la V3 no resuelve este punto.
2. Probar una llamada real y acotada de Kie y Fish con claves nuevas, saldo revisado y gasto autorizado.
3. Producir un video piloto desde el manifiesto hasta la entrega con activos trazables.
4. Renderizar la plantilla en un entorno con navegador autorizado y revisar todos los frames críticos, voz, música, SFX y subtítulos.
5. Confirmar licencia comercial de música, imágenes reales, fuentes y logo usados en esa producción.
6. Comparar el piloto con la referencia aprobada en teléfono y registrar aprobación o correcciones.

La versión 1.0.0 acredita que el método, los validadores y la base de composición son coherentes y están probados localmente. No acredita todavía que la nueva plantilla reproduzca exactamente el montaje anterior ni que un proveedor externo produzca la calidad deseada con una cuenta concreta.
