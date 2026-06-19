# Guia para video explicativo

Objetivo: grabar un video corto con captura de pantalla mostrando el proyecto en funcionamiento.

Duracion sugerida: 5 a 7 minutos.

## Preparacion

1. Ejecutar la app:

```bash
.venv/bin/streamlit run app.py
```

2. Tener una API key cargada en `.env` o en la barra lateral.
3. Tener Ollama activo para mostrar IA generativa:

```bash
ollama serve
ollama pull qwen3.5:4b
```

4. Abrir `http://localhost:8501`.
5. Preparar una URL de YouTube para la demo.
6. Preparar una busqueda, por ejemplo `noticias Uruguay` o el tema elegido para el TFM.

## Guion sugerido

### 1. Presentacion del proyecto

"Hola, soy Diego y este es YouTube Briefing, mi Trabajo Final de Master. Es una aplicacion creada con Streamlit para buscar videos en YouTube, analizar metadata oficial, leer transcripciones publicas cuando estan disponibles y generar resumenes rapidos, incluyendo un briefing generativo con modelos locales de Ollama."

### 2. Problema

"La idea nace de una necesidad cotidiana: cuando buscamos informacion en YouTube, encontramos muchos videos, pero comparar resultados y extraer una primera conclusion lleva tiempo. La app ayuda a convertir esos resultados en un brief accionable."

### 3. Demo: resumen por URL

- Abrir la pestana `Resumen`.
- Pegar una URL de YouTube.
- Ejecutar `Analizar video`.
- Mostrar metadata, miniatura, metricas, resumen, keywords y transcripcion.
- Explicar que si no existe transcripcion publica, se resume la metadata.

### 4. Demo: busqueda de noticias

- Abrir la pestana `Noticias`.
- Buscar un tema.
- Mostrar filtros por region, idioma, dias, orden y categoria.
- Mostrar tabla de resultados.
- Activar `Reproducir en la app` en un resultado y mostrar que el video se reproduce embebido.
- Ejecutar `Generar briefing con IA`.
- Mostrar el resumen ejecutivo, hallazgos, comparacion de fuentes, sesgos y recomendacion de videos.
- Seleccionar uno o mas videos y ejecutar `Resumir seleccionados`.

### 5. Demo: reproduccion embebida

"Los resultados no obligan a salir a YouTube. Cada card tiene un toggle para reproducir el video dentro de la app. Esto ayuda a revisar fuentes, comparar contenidos y volver al briefing sin romper el flujo de investigacion."

### 6. Demo: IA generativa local

"La parte de IA generativa se ejecuta con Ollama en local. La app toma los resultados de YouTube y los transforma en un briefing ejecutivo: compara fuentes, marca posibles sesgos y recomienda que videos mirar primero. Esto evita enviar el contenido a un proveedor externo de LLM y mantiene la app usable incluso sin conexion a APIs generativas."

### 7. Arquitectura

"La app separa responsabilidades en modulos: `youtube_client.py` maneja la API oficial de YouTube, `transcripts.py` intenta obtener transcripciones publicas, `summarizer.py` genera resumenes extractivos locales y `ollama_client.py` encapsula la generacion con modelos locales."

### 8. Stack y buenas practicas

"El proyecto usa Python, Streamlit, YouTube Data API, Ollama, variables de entorno, tests unitarios y GitHub Actions. La API key no se sube al repositorio; se configura como `.env` local o secret en despliegue."

### 9. Limitaciones y mejoras

"YouTube Data API no genera resumenes, y las transcripciones no siempre estan disponibles. La IA generativa depende de tener Ollama corriendo en local; en un despliegue cloud se puede desactivar. Como mejora natural agregaria exportacion de briefs y ranking propio de resultados."

### 10. Cierre

"El proyecto queda documentado, con slides, instrucciones de despliegue y repositorio publico en GitHub."

## Checklist del video

- [ ] Se ve la pantalla durante toda la explicacion.
- [ ] Se muestra la app ejecutandose.
- [ ] Se muestra al menos una URL analizada.
- [ ] Se muestra una busqueda de noticias.
- [ ] Se muestra un video reproducido dentro de la app.
- [ ] Se muestra el briefing generativo con Ollama.
- [ ] Se explica la arquitectura.
- [ ] Se menciona que no hay login.
- [ ] Se menciona como se protegen los secretos.
- [ ] El video queda con URL publica para el formulario.
