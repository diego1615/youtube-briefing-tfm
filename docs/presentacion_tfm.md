# Presentacion TFM - YouTube Briefing

Este archivo resume el contenido de la presentacion editable subida a Google Slides:

https://docs.google.com/presentation/d/1lYlGqyycLlqZ9CUEBBYMQoiovi4FByi_Wa1CkFtQew4

## Slides

1. YouTube Briefing TFM
   - App para convertir busquedas y videos de YouTube en briefings accionables.
   - Enfoque: datos oficiales, transcripciones publicas, reproduccion embebida e IA generativa local con Ollama.

2. Problema y oportunidad
   - Buscar informacion en videos consume tiempo.
   - Los resultados de YouTube necesitan contexto, comparacion y sintesis.
   - El proyecto reduce friccion para investigacion y seguimiento de noticias con sintesis generativa local.

3. Flujo del producto
   - Ingreso de una URL o busqueda por tema.
   - Obtencion de metadata, transcripcion publica y resultados relacionados.
   - Resumen local, seleccion de videos y briefing generativo.

4. Funcionalidades principales
   - Analisis por URL.
   - Busqueda de noticias por tema.
   - Resumen extractivo y keywords.
   - Briefing generativo con Ollama: hallazgos, comparacion, sesgos y recomendacion.
   - Tabla comparativa, seleccion de resultados y reproduccion de videos dentro de la app.

5. Arquitectura tecnica
   - Streamlit como interfaz.
   - YouTube Data API para busqueda y metadata.
   - `youtube-transcript-api` para transcripciones publicas.
   - Ollama local para IA generativa sin proveedor externo.
   - Modulos Python separados para cliente, transcripciones, resumen e IA.

6. Demo funcional
   - Configurar API key.
   - Analizar una URL.
   - Buscar noticias.
   - Activar `Reproducir en la app`.
   - Generar briefing con IA local.

7. Salida generativa
   - Resumen ejecutivo.
   - Hallazgos principales.
   - Comparacion entre videos seleccionados.
   - Riesgos, sesgos y recomendacion de uso.

8. Reproduccion embebida
   - Toggle `Reproducir en la app` en cada resultado.
   - Video visible dentro de Streamlit sin abrir YouTube en otra pestana.
   - Carga solo el reproductor elegido para mantener la busqueda rapida.

9. Cumplimiento de consigna
   - README completo con descripcion, stack, instalacion, ejecucion, estructura y funcionalidades.
   - Repositorio publico en GitHub con CI y tests automatizados.
   - Slides actualizadas y enlazadas desde la documentacion.
   - Despliegue y video marcados como pendientes operativos hasta tener URL final.
   - Usuario y contrasena: no aplica porque la app no tiene login.

10. Entrega y proximos pasos
   - Repositorio, documentacion, checklist, guia de video y CI preparados.
   - Proximos pasos: publicar despliegue, grabar video final y completar el formulario con URLs definitivas.
