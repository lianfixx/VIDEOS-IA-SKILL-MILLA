# MILLA Video Studio

Un método portable para producir videos de MILLA ABOGADOS: investigación, guion, conexiones, voz, imágenes, música, montaje y revisión. Incluye una skill, instrucciones para otras IAs, utilidades y un compositor nuevo.

**Empieza en [START_HERE.md](START_HERE.md).** Para dar todo el método a una IA que solo lee archivos, usa [MANUAL_COMPLETO.md](MANUAL_COMPLETO.md). No hace falta repetir la conversación.

## Qué conserva

Kie Nano Banana Lite como primera opción; Fish como voz preferente; marfil, navy y dorado; diagramas explicativos; transiciones y SFX variados; música adaptada; subtítulos superiores. Sin partículas, imágenes de ChatGPT, logos visibles Gemini, recortes con fondo, repetición mecánica ni promesas jurídicas.

La referencia editorial aprobada es el Short de personas físicas. La nueva voz de beneficios V3 **no se considera aprobada**: se elige mediante muestras antes de otra narración completa.

## Qué incluye

| Pieza | Función |
|---|---|
| [Skill](skills/milla-video-studio/SKILL.md) | Instrucciones operativas para un agente compatible |
| [Manual completo](MANUAL_COMPLETO.md) | Lectura portable para cualquier IA capaz de procesar el archivo |
| `scripts/milla.py` dentro de la skill | Diagnóstico, proyecto, validación, auditoría MP4 y escaneo preventivo de secretos |
| `scripts/providers.py` dentro de la skill | Kie Lite y Fish, simulación por defecto y estados para evitar reenvíos ciegos |
| `assets/remotion-template` dentro de la skill | Compositor original que `init-project` copia a cada producción |
| [Recapitulación](docs/RECAPITULACION.md) | Evolución, correcciones y evidencia disponible |
| [Mejoras](docs/MEJORAS.md) | Prioridades y criterios de aceptación |
| [Validación](docs/VALIDACION.md) | Qué se probó y qué sigue sin verificarse |

## Lo que significa instalar

Instalar transmite el método y el código. Cada usuario necesita sus cuentas, presupuesto y herramientas. Una IA sin terminal puede guiar paso a paso, pero no renderizar por leer un archivo. No se garantiza instalación nativa en Gemini, Grok, DeepSeek o Kimi: pueden usar el manual según sus capacidades.

La plantilla es nueva; el código exacto de los videos anteriores no se recuperó. Este paquete no contiene sus medios privados, claves ni transcripción cruda. Tampoco publica videos automáticamente en redes.

## Usarlo

Con un agente que puede leer este repositorio:

> Lee START_HERE.md y la skill MILLA Video Studio. Quiero un video sobre [tema] para [público]. Comprueba conexiones, conserva el estándar y ejecuta los pasos posibles. Guíame brevemente por lo que falte. Si necesitas cambiar la voz, presenta muestras antes de narrar todo.

En terminal, desde la raíz:

```bash
python3 skills/milla-video-studio/scripts/milla.py doctor
python3 skills/milla-video-studio/scripts/milla.py init-project ../produccion-milla --title "Tema del video"
```

Los resultados de `doctor` no prueban autenticación ni saldo. Los comandos a proveedores hacen simulación salvo `--execute`; ese indicador se usa solo con gasto autorizado.

## Mejorar y actualizar

Registrar el problema, su evidencia y el alcance; proponer cambio; probar regresiones; versionar. Una preferencia explícita tiene prioridad sobre un experimento. Ver [mejora continua](skills/milla-video-studio/references/improvement.md). No hay autoaprendizaje en segundo plano.

## Procedencia y derechos

Recapitulación de material disponible, no certificación de que se recuperó cada palabra del historial original. `video-vox` de santmun fue un antecedente; no se copió su código. Las marcas y contenidos audiovisuales de terceros conservan sus derechos. La publicación del método no transfiere licencias de voces, música, imágenes o marca MILLA. No se asigna una licencia general de código abierto sin decisión del titular.
