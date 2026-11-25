# Prompts editables y dirección

Son plantillas de intención, no garantías. Sustituir variables con hechos confirmados. No enviar datos reales de clientes a proveedores por defecto.

## Guion

“Preparar Short sobre {tema} para {audiencia}, en {jurisdicción}, objetivo {objetivo}. Investigar fuentes oficiales y registrar afirmaciones verificables. Lenguaje hablado, breve y profesional. Abrir con situación reconocible; mostrar opciones y prevención. No prometer resultados. CTA confirmado: {cta}. Un recurso útil por idea, sin fijar artificialmente nueve escenas.”

## Kie · recorte

“Recurso editorial jurídico boutique: {concepto} mediante {situación}. Marfil #F6F0E4, navy #172636, dorado #D6A72C, luz suave, composición ópticamente centrada. Sujeto completo, margen de cámara, perspectiva coherente, contornos separables. Fondo uniforme {chroma distinto del sujeto}. Sin texto, firma, logo Gemini/proveedor, watermark, marco, tarjeta, partículas, polvo, chispas ni confeti. {Detalles concretos}. Preparar para separar capas y animar 2.5D.”

Encuadre: indicar en inglés un plano y un ángulo, uno de cada clase. Plano: `full body`, `medium shot from the waist up`, `close-up`, `extreme close-up of the hands` u objeto (firma, sello, documento). Ángulo: `eye-level` por defecto; `low-angle view` para autoridad o firmeza; `high-angle view` para quien queda rebasado; `top-down view` para documentos sobre escritorio; `three-quarter view` o `side profile`. La luz suave del prompt basta: no pedir contraluz, luz de borde, neón, rayos, silueta, destellos ni fondo desenfocado, porque dejan halo o derrame que el recorte no quita (regla 3). Si aparecen manos, añadir `anatomically correct hands with five fingers`; si el sujeto hace varias cosas, `doing only one simple action`.

Si se necesita escena con fondo completo, indicarlo. No fingir alfa generado. Mantener referencias autorizadas. Revisar anatomía y concepto. No enviar parámetros API que ese modelo no admite.

## Voz

“Femenina mexicana, adulta, cercana y segura. Explicar a una persona con intención conversacional, energía motivadora, cambios reales de emoción, pausas breves y énfasis en {palabras}. Sin anuncio rígido, infantilización ni lectura robótica. Pronunciar {glosario}.”

Aplicar dirección con controles realmente soportados; no pegarla en texto que TTS pronunciará. Probar muestras. No usar audio de TikTok para clonar identidad.

## Música

“Instrumental documental moderna para {tema}, emoción {arco}. Pulso compatible con voz, espacio en frecuencias medias, inicio con intención, crecimiento moderado y cierre resuelto. Sin voz ni melodía competidora. Duración útil {segundos} con margen de edición.”

Revisar licencia y escuchar. Si no hay derechos claros, elegir pista autorizada. No generar como prueba técnica sin presupuesto.

## Diagrama

Definir relaciones exactas con nodos/texto nativo y fuente de cada dato. Flechas explicativas, no ambiente. Asignar a cada corte una familia y razón: máscara para revelar documento, desplazamiento entre opciones, profundidad para jerarquía o transformación de un proceso. No insertar datos exactos dentro de imágenes generadas.
