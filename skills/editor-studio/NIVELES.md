# Los tres niveles

En **cada video** se le explican a Emi los tres, con su diferencia, y se le sugiere uno con su razón. `$E niveles $D` imprime la tabla para ese video.

## Qué lleva cada uno

| | Nivel 1 · Limpio | Nivel 2 · Movimiento | Nivel 3 · Producción |
|---|---|---|---|
| Piezas | `titulo`, `rotulo`, `fuente`, `foto` (pantalla), `cierre` | + `zoom`, `sello`, `dato`, `barra`, `panel`, `barrido`, `foto` (tarjeta) | + `detras`, `inserto`, `sticker`, `particulas` |
| Sonido | Ninguno o mínimo | Efectos en lo que pesa | Efectos en cada golpe; música si Emi la quiere |
| Algo nuevo en pantalla | Cada 9 s como mucho | Cada 5 s | Cada 3.5 s |
| Se siente | La persona hablando, sin estorbos | Un reel trabajado | Un anuncio |
| Sirve para | Opinión del día, clips de podcast, entrevistas, publicar seguido | Explicar, tutoriales, la mayoría de los reels | Lanzamientos, campañas, la pieza que debe lucir |
| Tiempo y consumo | Bajo | Medio | Alto |
| Créditos | Ninguno | Ninguno | Solo si hay imagen o video generado; se cotiza antes |
| Riesgo | Que el guion no sostenga | Saturar | Que se vea «hecho por IA» |

Los subtítulos y los cortes van en los tres.

## Cómo se sugiere

1. Se parte del nivel del espacio (`edicion.json → nivel_partida`): personal 2, milla 2, castorena 1, pan 2.
2. Si el tipo de video se sostiene con menos (clip de podcast, entrevista), se baja.
3. Si el tipo admitiría más (anuncio, lanzamiento), **no** se sube todo el video: se propone el nivel 3 solo en el gancho o en el cierre con `tramos`.
4. No se pasa del tope del espacio (`nivel_tope`: milla y castorena 2) salvo que Emi lo pida. El validador lo cumple: para pasar, sus palabras van en `plan.json → sobre_tope_pedido_por_emi`. Lo mismo con la densidad de sonido del espacio (`sonido.densidad_pedida_por_emi`).
5. Un video de más de dos minutos no va entero en nivel 3.

Regla de fondo: **el nivel más bajo que cumpla el propósito**. La sugerencia se dice con su porqué y Emi decide.

## Combinar

```json
"nivel": 2,
"tramos": [{"de": 0, "a": 3.5, "nivel": 3}, {"de": 41, "a": 46, "nivel": 3}]
```

Combinaciones que funcionan:

- Podcast o entrevista: nivel 1 y un zoom en las tres frases más fuertes (esas tres van en tramos de nivel 2).
- Explicación jurídica: nivel 2, con `panel` para los pasos y `barra`.
- Anuncio: nivel 3 en los tres primeros segundos y en el cierre; nivel 2 en medio.

## Cuándo no subir

- El video es flojo: la edición no lo salva. Se le dice a Emi y se le propone regrabar el gancho.
- El tema es serio (un asunto de cliente, una nota institucional): menos es más.
- El encuadre es muy cerrado: hay poco sitio para texto sin tapar la cara; el validador lo va a rechazar.
- Castorena: sin humor, sin efectos; un rótulo y subtítulos sobrios dicen más.

## Comparar niveles sobre el mismo crudo

Para el primer video de un espacio conviene enseñarle el mismo tramo en dos o tres niveles: se guarda una copia de `plan.json` por nivel, se arma cada una y se saca `$E muestra $D --en … --nombre n1`, `n2`, `n3`. Con las tiras lado a lado elige con los ojos, no con una descripción.
