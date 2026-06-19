# YouTube Briefing TFM

Aplicacion de Streamlit para buscar videos/noticias en YouTube, analizar una URL puntual y generar un briefing rapido con metadata oficial, transcripciones publicas cuando existen y resumenes extractivos locales.

Este repositorio esta preparado como Trabajo Final de Master de Desarrollo con IA.

## Entrega TFM

- Repositorio GitHub: `https://github.com/diego1615/youtube-briefing-tfm`
- Despliegue: pendiente de publicar en Streamlit Community Cloud o servicio equivalente.
- Slides: [Google Slides](https://docs.google.com/presentation/d/1SBayRuDCST3UX4fHH7AEZlcQVAinGpAd1kvxJv6BoEE)
- Guia para video explicativo: [`docs/video-guia.md`](docs/video-guia.md)
- Checklist de entrega: [`docs/entrega-tfm.md`](docs/entrega-tfm.md)
- Usuario y contrasena de prueba: no aplica, la app no tiene login.

## Descripcion general

YouTube Briefing resuelve una necesidad frecuente: encontrar videos recientes sobre un tema, filtrar resultados y construir una primera lectura rapida sin abrir decenas de pestanas. La app combina la API oficial de YouTube con un flujo de resumen local para apoyar investigacion, seguimiento de noticias y revision de contenido audiovisual.

El proyecto demuestra integracion con APIs externas, manejo de variables de entorno, interfaz web con Streamlit, normalizacion de datos, extraccion de transcripciones publicas y pruebas automatizadas.

## Stack tecnologico

- Python 3.9+
- Streamlit
- YouTube Data API v3
- `youtube-transcript-api`
- Pandas
- `python-dotenv`
- `unittest`
- GitHub Actions para CI

## Funcionalidades principales

- Analisis por URL de YouTube.
- Extraccion robusta de `video_id` desde URLs largas, cortas, shorts, embeds y directos.
- Consulta de metadata oficial con `videos.list`.
- Busqueda de videos/noticias por tema con `search.list`.
- Filtros por region, idioma, fecha, orden y categoria de noticias.
- Lectura de transcripciones publicas cuando estan disponibles.
- Resumen extractivo local a partir de transcripcion o metadata.
- Extraccion de keywords principales.
- Tabla comparativa de resultados.
- Resumen de videos seleccionados desde una busqueda.
- Setup asistido para Google Cloud y API key de YouTube.

## Estructura del proyecto

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
|-- .env.example
|-- .streamlit/
|   |-- config.toml
|   `-- secrets.toml.example
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- docs/
|   |-- deployment.md
|   |-- entrega-tfm.md
|   |-- presentacion_tfm.md
|   `-- video-guia.md
|-- scripts/
|   |-- bootstrap.sh
|   `-- configure_youtube_cloud.sh
|-- src/
|   |-- summarizer.py
|   |-- transcripts.py
|   `-- youtube_client.py
`-- tests/
    |-- test_summarizer.py
    `-- test_youtube_client.py
```

## Instalacion local

Requisitos:

- Python 3.9 o superior.
- Una API key de YouTube Data API v3.
- Opcional: Google Cloud CLI (`gcloud`) para automatizar la creacion de la API key.

Setup rapido:

```bash
scripts/bootstrap.sh
```

Ese comando crea `.venv`, instala dependencias y copia `.env.example` a `.env` si todavia no existe.

Setup manual:

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Luego edita `.env`:

```bash
YOUTUBE_API_KEY=tu_api_key_de_youtube_data_api
```

## Configuracion de Google Cloud

Si ya tienes `gcloud` instalado y autenticado:

```bash
scripts/configure_youtube_cloud.sh
```

El script crea un proyecto, habilita `youtube.googleapis.com`, crea una API key restringida a YouTube Data API y la guarda en `.env`.

Si `gcloud` no esta instalado en macOS:

```bash
brew install --cask google-cloud-sdk
scripts/configure_youtube_cloud.sh
```

Tambien puedes pegar una API key en la barra lateral de la app y presionar "Guardar API key local".

## Ejecucion

```bash
.venv/bin/streamlit run app.py
```

La app abre por defecto en:

```text
http://localhost:8501
```

## Tests

```bash
.venv/bin/python -m unittest discover -s tests
```

Los tests cubren extraccion de IDs de YouTube, formateo de duraciones y utilidades del resumen local.

## Despliegue

La opcion recomendada para esta app es Streamlit Community Cloud.

Resumen:

1. Publicar este repositorio en GitHub como publico.
2. Crear una app en Streamlit Cloud apuntando a `app.py`.
3. Configurar el secret:

```toml
YOUTUBE_API_KEY = "tu_api_key_de_youtube_data_api"
```

4. Copiar la URL publica del despliegue en esta documentacion y en el formulario de entrega.

Guia detallada: [`docs/deployment.md`](docs/deployment.md).

## Seguridad y secretos

- `.env` esta ignorado por git y no debe subirse al repositorio.
- `.streamlit/secrets.toml` esta ignorado por git.
- Para despliegue se debe usar el gestor de secretos del proveedor.
- La API key deberia estar restringida a YouTube Data API y, si aplica, al dominio del despliegue.

## Limitaciones conocidas

- YouTube Data API no genera resumenes por si misma.
- `captions.list` y `captions.download` requieren OAuth; no permiten descargar cualquier caption publico solo con API key.
- `youtube-transcript-api` funciona como fallback practico, pero depende de que el video tenga transcripcion publica accesible.
- El resumen actual es extractivo y local; no usa un LLM externo.
- Las cuotas de YouTube Data API pueden limitar busquedas intensivas.

## Proximas mejoras

- Agregar resumen generativo opcional con un proveedor LLM.
- Guardar historico de busquedas.
- Exportar brief en Markdown/PDF.
- Ranking de resultados por relevancia propia combinando fecha, views, canal y keywords.
