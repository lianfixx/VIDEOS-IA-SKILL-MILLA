# Referencias externas analizadas

Qué se tomó y qué se descartó de material de terceros, y por qué. Aquí se anota cada referencia que Emi pida analizar; lo adoptado vive en las skills, no en este documento.

## 11 de noviembre de 2026 · cuatro publicaciones de X sobre diseño de movimiento con código

Leídas completas por su texto (dos son artículos largos); los videos adjuntos no se vieron.

| Publicación | Qué es | Veredicto |
|---|---|---|
| @seeconvm, «What the Viral One-Prompt Videos Are Hiding» (2/10/2026) | Desmonta los videos «de un solo prompt»: detrás hay un brief largo, una carpeta de skills, llaves y muchas rondas de corrección | La más útil. Su tesis ya era la de este repositorio |
| @e1genqq, «How to Build an Automated Motion Design System» (13/10/2026) | Sistema para producir campañas en serie: datos separados del código, validación antes de rendir, control de calidad en cinco pasadas, variantes | Útil en control de calidad y validación; la parte de negocio no aplica |
| @e1genqq, lista de 20 repositorios (8/11/2026) | Herramientas libres: Remotion, FFmpeg, Three.js, Blender, ComfyUI, etc. | Casi todo relleno. El propio autor dice en su artículo: «no necesitas veinte repositorios» |
| @tivollem (8/11/2026) | Promete un repositorio con 475 videos y sus prompts | Sin verificar: el enlace lleva a un servidor de Discord, no a GitHub. No se entró |

### Adoptado

| Idea | De dónde | Cómo quedó |
|---|---|---|
| Cada escena necesita una razón de existir | @seeconvm, «State Lists» | Campo `funcion` obligatorio; primera `gancho`, última `cierre` y al menos una `opinion` |
| El gancho se elige, no se improvisa | ambas | `ganchos_propuestos` (2 o más) y `gancho_elegido` por Emi |
| Un dato inventado no se publica; rechazar la entrada mala antes de rendir | @e1genqq, «Validate Before Rendering» | Una cifra en la narración sin `fuente` en esa escena es error, no aviso |
| El sonido va en el mismo reloj que la imagen | ambas | El tempo de la música se ajusta ±8 % para que los cambios de escena caigan en pulso |
| Prueba «a ojos cerrados» | @seeconvm | La auditoría avisa si el audio es plano (rango menor de 1.5 LU). No sustituye a que Emi lo escuche |
| Cada clase de objeto con su física | @seeconvm, «Springs» | Titular firme, recorte con peso, rótulo seco; antes todo usaba el mismo resorte |
| Muestrear antes, durante y después de cada transición | @e1genqq, pasada 2 | `revisar` genera `hoja-transiciones.png` |
| Revisar a tamaño de teléfono | @e1genqq, pasada 3 | `revisar` genera `hoja-telefono.png` |
| No dar por bueno un video sin haber mirado el render; informe con segundos, hallazgos, arreglos y pendientes | ambas | `out/revision.json`; `cierre` se niega si falta o si es de un render anterior |
| Manifiesto de entrega | @e1genqq | `out/manifiesto.json`: huellas de guion, voz, música, imágenes, versión y ajustes |
| Una referencia visual vale más que una descripción | @seeconvm, «The Reference» | `referencia ARCHIVO` convierte la imagen o el video de Emi en una hoja para mirarla |
| Detenerse y preguntar si falta algo real | @seeconvm, «gates» | Compuertas explícitas en las skills |

Al estrenar la revisión de transiciones sobre el demo aparecieron dos fallas que las hojas anteriores no mostraban: un recorte que caía sobre el titular al entrar y la línea de fuente ilegible a tamaño teléfono. Las dos se corrigieron.

### Ya estaba

Render determinista cuadro por cuadro, datos separados del código, hoja de contacto, zonas seguras, música y efectos por código, entrevista antes de producir, espacios por marca, aprendizaje entre videos y la regla de no fingir un render.

### Descartado, con motivo

| Idea | Por qué no |
|---|---|
| Campaña de 18 variantes (3 ganchos × 3 formatos × 2 cierres) | Es para vender paquetes a clientes. Emi publica en sus propios espacios; multiplicar la voz por 3 triplica el gasto sin un fin |
| Formatos 1:1 y 16:9 en Vox Studio | Es una mejora real (X prefiere horizontal o cuadrado), pero exige rehacer la composición, no recortar. Queda propuesto, sin hacer. Pizarra Studio ya rinde en 16:9 |
| «Generar y calcar» con un modelo de video | Cuesta, y contradice la regla de no usar video generado donde se dice que todo es código |
| Three.js, sombreadores, Blender, ComfyUI, simulaciones | No sirven al estilo editorial de estos videos y empujan hacia el aspecto «hecho por IA» que Emi quiere evitar |
| Contenedor primero y texto después | Se probó en el recuadro del dato: llegaba vacío y se veía peor. Revertido |
| Skills oficiales de Remotion (`remotion-dev/skills`) | El repositorio existe; no se instaló para no mezclar instrucciones ajenas con las de estas skills. Sirve como consulta al modificar la plantilla |
| Precios, paquetes y venta del servicio | Fuera del alcance: aquí solo se hace video |
