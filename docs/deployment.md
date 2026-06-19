# Deployment

Esta app esta preparada para desplegarse en Streamlit Community Cloud.

## Opcion recomendada: Streamlit Community Cloud

1. Publica el repositorio en GitHub como publico.
2. Entra a Streamlit Community Cloud con la cuenta vinculada a GitHub.
3. Crea una nueva app desde el repositorio.
4. Usa estos valores:
   - Repository: `diego1615/youtube-briefing-tfm`
   - Branch: `main`
   - Main file path: `app.py`
5. En `Secrets`, agrega:

```toml
YOUTUBE_API_KEY = "tu_api_key_de_youtube_data_api"
YOUTUBE_FORCE_IPV4 = "true"
OLLAMA_ENABLED = "false"
```

6. Guarda y espera el build.
7. Copia la URL publica en:
   - `README.md`
   - `docs/entrega-tfm.md`
   - Formulario de entrega del TFM

## Variables necesarias

| Nombre | Obligatoria | Descripcion |
| --- | --- | --- |
| `YOUTUBE_API_KEY` | Si | API key restringida a YouTube Data API v3 |
| `YOUTUBE_FORCE_IPV4` | No | Evita demoras en redes donde Python intenta IPv6 hacia Google antes de IPv4 |
| `OLLAMA_ENABLED` | No | Activa/desactiva el modulo generativo local. En cloud se recomienda `false` |
| `OLLAMA_BASE_URL` | No | URL de Ollama local. Default: `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | No | Modelo de completion de Ollama. Default: `qwen3.5:4b` |

## IA generativa local

El modulo generativo usa Ollama local. Para demo local:

```bash
ollama serve
ollama pull qwen3.5:4b
.venv/bin/streamlit run app.py
```

En Streamlit Community Cloud normalmente no existe un servicio local de Ollama, por eso el despliegue publico puede dejar `OLLAMA_ENABLED = "false"`. La app sigue cumpliendo el flujo principal con busqueda, metadata, transcripciones y resumen extractivo.

## Verificacion posterior

- Abrir la app publicada.
- Probar la pestana `Resumen` con una URL de YouTube.
- Probar la pestana `Noticias` con una busqueda simple.
- En local, probar `Generar briefing con IA` con Ollama activo.
- Confirmar que no se imprime la API key en pantalla.
- Confirmar que la URL publica queda documentada antes de entregar.

## Alternativas

Tambien se puede desplegar en Render, Railway, Hugging Face Spaces o cualquier plataforma compatible con apps Python/Streamlit. En ese caso, el comando de inicio debe ser:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```
