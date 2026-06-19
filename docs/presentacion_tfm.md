# Presentacion TFM - YouTube Briefing

Este archivo resume el contenido de la presentacion editable subida a Google Slides:

https://docs.google.com/presentation/d/1SBayRuDCST3UX4fHH7AEZlcQVAinGpAd1kvxJv6BoEE

## Slides

1. YouTube Briefing TFM
   - App para convertir busquedas y videos de YouTube en briefings rapidos.
   - Enfoque: datos oficiales, transcripciones publicas y resumen local.

2. Problema y oportunidad
   - Buscar informacion en videos consume tiempo.
   - Los resultados de YouTube necesitan contexto, comparacion y sintesis.
   - El proyecto reduce friccion para investigacion y seguimiento de noticias.

3. Funcionalidades principales
   - Analisis por URL.
   - Busqueda de noticias por tema.
   - Resumen extractivo y keywords.
   - Tabla comparativa y seleccion de resultados.

4. Arquitectura
   - Streamlit como interfaz.
   - YouTube Data API para busqueda y metadata.
   - `youtube-transcript-api` para transcripciones publicas.
   - Modulos Python separados para cliente, transcripciones y resumen.

5. Stack y buenas practicas
   - Variables de entorno y secrets.
   - Scripts de bootstrap y Google Cloud.
   - Tests automatizados.
   - CI con GitHub Actions.

6. Demo sugerida
   - Configurar API key.
   - Analizar una URL.
   - Buscar noticias.
   - Resumir videos seleccionados.

7. Limitaciones y evolucion
   - Cuotas de YouTube API.
   - Transcripciones no siempre disponibles.
   - Futuro: resumen generativo, exportacion y ranking propio.

8. Cierre
   - Entrega preparada con repo, docs, slides y guia de video.
   - Proximo paso: despliegue publico y grabacion final.
