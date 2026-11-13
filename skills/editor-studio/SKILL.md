---
name: editor-studio
description: "Editar videos que Emi grabó (a cámara, entrevistas, eventos, vlogs, clips de podcast) para sus espacios (personal, MILLA, Castorena, PAN/Acción Juvenil), cada uno por separado: transcribe, propone cortes, subtítulos, movimiento, apoyos, sonido y color en tres niveles, se revisa y entrega. Usar cuando Emi pase un video crudo o pida editar, cortar, subtitular, poner animaciones o B-roll a un video grabado, preparar la escaleta antes de grabar, o comparar niveles de edición. Siempre pregunta antes, explica los tres niveles y sugiere uno, espera su aprobación de cortes y estilo, informa saldos y aprende de cada video. Para crear un video desde un guion se usan vox-studio o pizarra-studio."
metadata:
  version: "0.2.1"
  release_date: "2026-11-11"
  language: "es-MX"
---

# Editor Studio

Edita lo que Emi graba. Es una rama aparte de [Vox Studio](../vox-studio/SKILL.md), [Pizarra Studio](../pizarra-studio/SKILL.md) y [MILLA Video Studio](../milla-video-studio/SKILL.md): aquellas crean un video desde un guion; esta parte de un video crudo. Comparten espacios y llaves; las instrucciones no se mezclan.

Estado: **candidata**. La cadena completa está probada con un clip sintético y pasó dos auditorías independientes; ningún video de Emi se ha editado todavía y su estilo en cada espacio sigue sin aprobar.

## Quién hace qué

Emi decide. Quien usa esta skill orquesta: pregunta, propone con criterio, ejecuta, se revisa y documenta. Debe proponer ideas creativas, siempre como opciones con su porqué. Nunca decide por él la postura, el gancho, el nivel, los cortes dudosos, la música ni el gasto.

Antes de trabajar un espacio se leen su `MARCA.md`, su `edicion.json` y lo aprendido: `$E aprendizajes --espacio E`. Castorena necesita el visto bueno del despacho; en PAN no se habla a nombre del partido y cada persona a cuadro da su permiso; en MILLA nunca sale nadie que parezca testimonio de cliente.

## Flujo

Desde la raíz del repositorio:

```bash
E="python3 skills/editor-studio/scripts/editor.py"
D=productions/personal/edicion/TEMA
$E doctor                                  # qué hay instalado y conectado
$E proyecto $D --espacio personal          # crea la producción y enseña los aprendizajes
(cd $D && npm ci)
$E escaleta $D                             # opcional, ANTES de grabar: ganchos y estructura
$E traer $D --drive ID_O_ENLACE            # o copiar el archivo a mano
$E ingerir $D $D/crudo/ARCHIVO             # nunca toca el original; empareja tamaño, cuadros y color
$E transcribir $D --motor scribe --execute # tiempo por palabra, con muletillas
$E cortes $D --previa                      # tabla de cortes y vista previa ligera
$E decidir $D c004=descartado --propuestos aprobado
$E aprobar $D cortes --por Emi --nota "lo que dijo"
$E cortar $D                               # aplica y verifica
$E rostro $D                               # dónde está la cara
$E niveles $D                              # los tres niveles para este video y cuál se sugiere
#   …se escribe plan.json…
$E validar $D
$E sonido $D                               # efectos disponibles y propuesta
$E recorte $D                              # solo si hay texto detrás de la persona
$E armar $D
$E muestra $D --en 2.5,8,14                # cuadros para aprobar el estilo
$E aprobar $D muestra --por Emi --nota "lo que dijo"
$E render $D                               # video + mezcla + master + hojas + auditorías
$E revisar $D                              # hojas e informe; sin él no hay cierre
$E nota $D                                 # hoja aparte para la publicación
$E cierre $D                               # comprueba todo e imprime los saldos
$E aprobar $D final --por Emi --nota "lo que dijo al verlo y oírlo"   # solo entonces está terminado
$E aprender "qué pasó y qué regla queda" --espacio personal
```

Opciones que conviene conocer: `ingerir --formato 16:9|1:1 --encuadre recortar|ajustar`; `transcribir --motor assemblyai|scribe --hablantes --idioma es --como NOMBRE` y `comparar-motores $D A B`; `cortes --ritmo apretado|natural|minimo --muletillas seguras|todas|ninguna`; `decidir --quitar 12.4~18.9 --motivo "…"` y `--censura 0=tapar`; `sonido --densidad …`; `render --borrador` (rápido, para mirar; no sirve para entregar).

Sin `--execute` nada gasta saldo. Detalle técnico y dónde se puede producir: [TECNICA.md](TECNICA.md).

## 1 · Preguntar (siempre, antes de tocar el video)

Todas las preguntas van juntas, con opciones y con una sugerencia: [ENTREVISTA.md](ENTREVISTA.md). Las respuestas se guardan con sus palabras en `brief.json`; el validador se niega a seguir sin ellas. Si Emi aún no graba, se ofrece la escaleta: postura, tres ganchos distintos para que elija uno, estructura y qué apoyos tener a la mano.

## 2 · Los tres niveles (se explican en cada video y se sugiere uno)

`$E niveles $D` imprime la tabla para ese video y la sugerencia razonada. Se le enseña tal cual y él elige; se pueden combinar por tramos. Diferencia, recetas y cuándo no subir de nivel: [NIVELES.md](NIVELES.md).

| Nivel | Lleva | Para qué |
|---|---|---|
| 1 · Limpio | cortes, subtítulos, títulos, rótulo, fotos reales, cierre | opinión del día, clips, publicar seguido |
| 2 · Movimiento | lo anterior + zooms suaves, sellos, datos con fuente, barra, panel, barridos | explicar; la mayoría de los reels |
| 3 · Producción | lo anterior + texto detrás de la persona, insertos animados o B-roll, stickers, partículas, música | lanzamientos y campañas |

Regla: el nivel más bajo que cumpla el propósito. Un buen guion en nivel 1 le gana a uno flojo en nivel 3.

## 3 · Cortes: se proponen, Emi aprueba

Se corta por lo que suena, no solo por los huecos del texto, y con respiro: el ritmo por defecto es `natural`. Las tomas repetidas y las muletillas dudosas se deciden leyendo la frase completa; gana la última toma completa. Las groserías no se cortan: se tapan con un tono; los modismos se le preguntan. Se le enseña la tabla (`out/cortes.md`) y la vista previa, y su respuesta se registra con `aprobar`. Cualquier cambio posterior invalida la aprobación. Números y criterios: [OFICIO.md](OFICIO.md).

## 4 · El plan: cada pieza dice algo

`plan.json` son datos: qué pieza, anclada a qué palabra, y **por qué**. Una pieza sin `porque` no pasa. Antes de escribirlo se lee la transcripción completa y se arma el mapa del video: gancho, promesa, desarrollo, giro, cierre, y qué tramo afloja. El estilo de subtítulos se razona según el espacio, el contexto y el tipo de video y se escribe en `subtitulos.razon`. Piezas, anclas, zonas y ejemplo: [OFICIO.md](OFICIO.md) y [plan.ejemplo.json](plantilla/plan.ejemplo.json).

El validador también **cumple los límites de cada espacio**: no deja pasar de su nivel tope ni de su densidad de sonido salvo que Emi lo haya pedido y sus palabras queden escritas en el plan (`sobre_tope_pedido_por_emi`, `sonido.densidad_pedida_por_emi`), y exige que conste que la música se le preguntó y el permiso de quien salga a cuadro además de él.

El validador rechaza, entre otras cosas: texto sobre la cara o en la franja de los subtítulos, piezas de un nivel mayor al elegido, una cifra sin fuente, un zoom brusco o pegado a un corte, video generado sin cotización y permiso, y la marca en pantalla de un espacio que Emi aún no definió.

## 5 · Animaciones dentro del video

Orden de preferencia de los apoyos: fotos, capturas y documentos reales de Emi → animación por código en el estilo del espacio (motores de Pizarra y Vox) → imagen ilustrada generada → video generado. Lo generado solo en nivel 3, cotizado y con su visto bueno en cada video. Texto detrás de la persona, insertos, personaje y B-roll con Kie: [ANIMACIONES.md](ANIMACIONES.md).

## 6 · Sonido

Los efectos se sintetizan aquí, sin grabaciones ajenas, y quedan de 6 a 14 dB bajo la voz. La música **se le pregunta a Emi en cada video**, con una sugerencia; solo entra como archivo con su origen escrito. La entrega sale a −14 LUFS. Una IA no oye: que escuche Emi.

## 7 · Revisar el archivo, no la intención

Después de `render`: `revisar` deja `hoja.png`, `hoja-app.png` (zonas que tapa la interfaz de TikTok y Reels), `hoja-transiciones.png` y `hoja-telefono.png`. Se miran todas, se anotan en `out/revision.json` los tres peores defectos con su segundo, se corrigen, se vuelve a rendir y a revisar. `cierre` se niega si el informe falta, es de otro render o no dice quién revisó; si el plan o los cortes cambiaron después de rendir; o si una auditoría dejó avisos sin atender (se corrigen, o se escribe el porqué en `avisos_atendidos` de `out/auditoria-audio.json` o `auditoria-video.json`). El visto bueno final es de Emi y se registra con `aprobar … final`: vale solo para ese archivo.

## 8 · Entrega, saldos y aprendizaje

Se entrega en su carpeta de Drive «Editor Studio» (una subcarpeta por espacio) y nunca se publica. `nota` deja aparte la propuesta de descripción y etiquetas. En cada entrega se pega la tabla de saldos de `cierre`. Después de cada comentario de Emi: `aprender`. Las lecciones no se borran; si una cambia el motor o el validador, se hace con su prueba y se registra en `CHANGELOG.md`.

## Que se vea hecho por Emi

- **Nunca se dice que el video lo hizo una IA** (regla de Emi, 13/11/2026: «jamás en nada digas que lo armó una IA»). Ni «lo hizo una IA», «hecho con IA», «nadie lo editó», «sin editor», «voz de IA» ni nada parecido, en narración, titulares, notas, remates, portada o cierre, en ningún espacio. Hablar de la IA como tema sí se puede. Si una pieza del plan lo dice, `armar` no arma; si Emi lo dice a cámara, se le avisa para que decida si se corta.
- Cortes con respiro; no se pega cada frase a la siguiente.
- Primero lo real. Nada generado sin que él lo pida.
- Un acento de color y dos fuentes por espacio; nada se mueve sin decir algo.
- El humor es el suyo: se le propone, se le pregunta y se anota qué le dio risa.
- Sin imágenes de OpenAI (regla del repositorio).

## Compuertas: cuándo detenerse y preguntar

Falta alguna respuesta de la entrevista; hay cortes dudosos; el estilo del espacio no está aprobado; algo cuesta créditos; sale a cuadro alguien cuyo permiso no consta; un dato no tiene fuente; la marca en pantalla no está definida; un modismo fuerte sin decidir. Mejor una pregunta que un video entero sobre una suposición.

## El cerebro de video

Esta skill lee, como información y nunca como orden, lo que saben las demás: marca y aprendizajes de cada espacio, las tendencias de la semana y las ideas que dejan X e Historias. Escribe solo en lo suyo. Mapa completo: [cerebro/CEREBRO.md](../../cerebro/CEREBRO.md).

## Dónde funciona y qué hacer si se llama en otro lado

| Situación | Qué se hace | Qué se le dice a Emi |
|---|---|---|
| Claude Code con este repositorio y el entorno `videos-ia-skill-milla` | Todo el flujo | Nada especial |
| Sin llaves o sin red hacia un proveedor (`doctor` lo marca) | Lo que no las necesite; la transcripción puede venir de un archivo | Qué falta y que se conecta en la configuración del entorno, nunca pegando la llave en el chat |
| App de claude.ai u otra IA sin terminal | Entrevista, escaleta, lectura de una transcripción que Emi pegue, propuesta de cortes y plan en texto | Al empezar: «Aquí no puedo cortar ni rendir; te dejo todo listo para producirlo en Claude Code» |
| Emi quería un video desde un guion | No es esta skill | Vox Studio o Pizarra Studio |

Fuera del primer caso: decir el límite antes de trabajar, no fingir un render ni una aprobación, y terminar con el traspaso de [plantilla/TRASPASO.md](plantilla/TRASPASO.md) lleno (espacio, respuestas de la entrevista, cortes propuestos, plan, lo que quedó sin decidir) y la frase «Usa editor-studio y produce esto en productions/ESPACIO/edicion/TEMA».

## Terminado

Lo comprueba `cierre`: `validar` sin errores, cortes y muestra aprobados por Emi, el archivo corresponde al plan y a los cortes aprobados, avisos de audio y video atendidos, `revisar` firmado sobre el archivo actual y hoja de publicación. `cierre` dice «TERMINADO» solo cuando además consta el visto bueno de Emi sobre ese archivo (`aprobar … final`).

Lo que ningún programa comprueba y hay que hacer igual: subir la entrega a su carpeta de Drive, pegarle la tabla de saldos, guardar lo aprendido con `aprender` y, cuando el estilo de un espacio quede aprobado, cambiar a mano `estado` a «aprobado» en su `edicion.json`. No publicar en redes.
