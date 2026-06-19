# Presentacion TFM - YouTube Briefing

Este archivo resume el contenido de la presentacion editable subida a Google Slides:

https://docs.google.com/presentation/d/1VQzKtFd933Ag5pfQCFwfAtKsr5ET4k8RjqWO7PEV_ag

## Slides

1. YouTube Briefing TFM
   - App para convertir busquedas y videos de YouTube en briefings accionables.
   - Enfoque: datos oficiales, transcripciones publicas, resumen local e IA generativa con Ollama.

2. Problema y oportunidad
   - Buscar informacion en videos consume tiempo.
   - Los resultados de YouTube necesitan contexto, comparacion y sintesis.
   - El proyecto reduce friccion para investigacion y seguimiento de noticias con sintesis generativa local.

3. Funcionalidades principales
   - Analisis por URL.
   - Busqueda de noticias por tema.
   - Resumen extractivo y keywords.
   - Briefing generativo con Ollama: hallazgos, comparacion, sesgos y recomendacion.
   - Tabla comparativa y seleccion de resultados.

4. Arquitectura
   - Streamlit como interfaz.
   - YouTube Data API para busqueda y metadata.
   - `youtube-transcript-api` para transcripciones publicas.
   - Ollama local para IA generativa sin proveedor externo.
   - Modulos Python separados para cliente, transcripciones, resumen e IA.

5. Stack y buenas practicas
   - Variables de entorno y secrets.
   - IA local opcional, desactivable en cloud.
   - Scripts de bootstrap y Google Cloud.
   - Tests automatizados.
   - CI con GitHub Actions.

6. Demo sugerida
   - Configurar API key.
   - Analizar una URL.
   - Buscar noticias.
   - Generar briefing con IA local.
   - Resumir videos seleccionados.

7. Limitaciones y evolucion
   - Cuotas de YouTube API.
   - Transcripciones no siempre disponibles.
   - Ollama local requiere demo en entorno propio o toggle desactivado en cloud.
   - Futuro: exportacion y ranking propio.

8. Cierre
   - Entrega preparada con repo, docs, slides y guia de video.
   - Proximo paso: despliegue publico y grabacion final.
