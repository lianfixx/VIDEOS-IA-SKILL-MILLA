# Aprendizajes de los videos estilo pizarra

Se leen antes de cada video de Pizarra Studio y se amplían después de cada entrega y de cada comentario de Emi (`pizarra.py aprender "..."`). Las lecciones que valen para cualquier video están en `APRENDIZAJES.md`.

- 2026-11-11 · Emi: en pizarra siempre se le hacen todas las preguntas antes de empezar; él decide y quien produce orquesta. Regla: `render` no entrega sin entrevista completa y storyboard aprobado.
- 2026-11-11 · Emi: propuestas creativas sí, pero naturales y humanas, que no se vean hechas por IA. Regla: un foco por escena, personaje que actúa, texto como él habla.
- 2026-11-11 · Prueba técnica: el sello cayó sobre la cara del personaje, y los pies y el cierre quedaron bajo la zona que tapa TikTok. Regla: en vertical nada debajo de y=1440; revisar la hoja de `qa` completa.
- 2026-11-11 · Prueba técnica: los golpes del dibujo tienen picos muy altos y el video no llegaba a −14 LUFS. Regla: `render` ya limita esos picos antes de mezclar y repone la ganancia midiendo.
- 2026-11-11 · Prueba técnica: la música compuesta a ojo quedó más corta que el video. Regla: `musica` sin `--segundos` mide la duración real del video.
- 2026-11-11 · El personaje de fábrica del motor es la mascota de Claude. Regla: no usarlo en los espacios de Emi salvo que él lo pida.
- 2026-11-11 · Emi (preferencias permanentes): estilo y música se le preguntan en cada video; sin personaje; voz del espacio. Regla: guardadas en `PREFERENCIAS-PIZARRA.json`; las dos primeras nunca se dan por sabidas.
- 2026-11-11 · Revisión independiente: 15 fallas corregidas. Las que más importan al producir: la voz no se paga sin entrevista aprobada; los cuadros de `qa` usan la misma línea de tiempo que el render; `musica` va antes de `qa`; si la voz dura más que el video o el video sobra, la auditoría avisa.
- 2026-11-11 · Primer video real en minimal (¡ACCIÓNate!, pan). El motor pone los subtítulos en y≈1575, bajo la zona que tapa TikTok. Regla: en la copia del proyecto subirlos a y≈1355-1440 y a 40 px, y dejar el contenido por encima de y=1340.
- 2026-11-11 · Un título con *énfasis* a media palabra se parte en dos («¡ACCIÓN ate!») y un texto con progreso 0 deja una raya suelta. Regla: palabras bicolor se dibujan a mano midiendo el ancho; no llamar al título hasta que empiece.
