from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.ollama_client import (
    OLLAMA_DEFAULT_BASE_URL,
    OLLAMA_DEFAULT_MODEL,
    OllamaError,
    choose_default_model,
    completion_model_names,
    generate_news_briefing,
    is_truthy_env,
    list_ollama_models,
)
from src.summarizer import bullet_summary, combine_texts, extract_keywords
from src.transcripts import TranscriptResult, fetch_public_transcript
from src.youtube_client import (
    YouTubeAPIError,
    extract_video_id,
    format_count,
    get_video_details,
    readable_date,
    search_news_videos,
)


SAMPLE_URL = "https://youtu.be/zYmH-59KakM?si=UpgLcoIAiU7Ogra4"
ENV_PATH = Path(__file__).resolve().parent / ".env"


st.set_page_config(
    page_title="YouTube Briefing",
    page_icon=":material/play_arrow:",
    layout="wide",
)


load_dotenv()


def app_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ytb-bg: #f7f8fa;
            --ytb-ink: #171717;
            --ytb-muted: #6b7280;
            --ytb-border: #e5e7eb;
            --ytb-accent: #d90429;
            --ytb-blue: #1d4ed8;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1180px;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        .ytb-note {
            border: 1px solid var(--ytb-border);
            border-left: 4px solid var(--ytb-accent);
            background: #fff;
            padding: 0.9rem 1rem;
            border-radius: 8px;
            color: var(--ytb-ink);
        }
        .ytb-small {
            color: var(--ytb-muted);
            font-size: 0.9rem;
        }
        .ytb-card {
            border: 1px solid var(--ytb-border);
            border-radius: 8px;
            padding: 1rem;
            background: #fff;
        }
        .ytb-title-link a {
            color: var(--ytb-ink);
            text-decoration: none;
        }
        .ytb-title-link a:hover {
            color: var(--ytb-blue);
            text-decoration: underline;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def markdown_link_text(text: str) -> str:
    return (
        str(text or "Sin titulo")
        .replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def save_api_key_to_env(api_key: str) -> None:
    clean_key = (api_key or "").strip()
    if not clean_key:
        return

    lines: List[str] = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    replaced = False
    next_lines = []
    for line in lines:
        if line.startswith("YOUTUBE_API_KEY="):
            next_lines.append(f"YOUTUBE_API_KEY={clean_key}")
            replaced = True
        else:
            next_lines.append(line)

    if not replaced:
        next_lines.append(f"YOUTUBE_API_KEY={clean_key}")

    ENV_PATH.write_text("\n".join(next_lines).strip() + "\n", encoding="utf-8")
    os.environ["YOUTUBE_API_KEY"] = clean_key


def secret_value(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or "")


def configured_api_key() -> str:
    env_key = os.getenv("YOUTUBE_API_KEY", "").strip() or secret_value("YOUTUBE_API_KEY")
    with st.sidebar:
        st.header("Configuracion")
        if env_key:
            st.success("API key cargada desde entorno/secrets.")
            entered = st.text_input("Reemplazar API key", type="password", value="")
            active_key = entered.strip() or env_key
        else:
            st.warning("Falta configurar YouTube Data API.")
            active_key = st.text_input("YouTube API key", type="password", value="").strip()

        if active_key and st.button("Guardar API key local", use_container_width=True):
            save_api_key_to_env(active_key)
            st.success("Guardada en .env. Reinicia la app si no se refleja de inmediato.")

        return active_key


def configured_ollama() -> Dict[str, object]:
    default_enabled = is_truthy_env(os.getenv("OLLAMA_ENABLED") or secret_value("OLLAMA_ENABLED"), True)
    default_base_url = (
        os.getenv("OLLAMA_BASE_URL", "").strip()
        or secret_value("OLLAMA_BASE_URL")
        or OLLAMA_DEFAULT_BASE_URL
    )
    default_model = os.getenv("OLLAMA_MODEL", "").strip() or secret_value("OLLAMA_MODEL") or OLLAMA_DEFAULT_MODEL

    with st.sidebar:
        st.divider()
        st.header("IA generativa")
        enabled = st.toggle("Usar Ollama local", value=default_enabled)
        base_url = st.text_input("Ollama URL", value=default_base_url)

        model_options: List[str] = []
        if enabled:
            try:
                model_options = cached_ollama_model_names(base_url)
            except OllamaError as exc:
                st.warning(str(exc))

        if model_options:
            selected_default = choose_default_model(model_options, default_model)
            model = st.selectbox(
                "Modelo Ollama",
                options=model_options,
                index=model_options.index(selected_default),
            )
        else:
            model = st.text_input("Modelo Ollama", value=default_model)

        st.caption("La IA local usa Ollama y no envia el briefing a servicios externos.")

    return {"enabled": enabled, "base_url": base_url, "model": model}


@st.cache_data(ttl=3600, show_spinner=False)
def cached_video_details(api_key: str, video_id: str) -> Dict:
    return get_video_details(api_key, video_id)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_transcript(video_id: str, languages: Tuple[str, ...]) -> TranscriptResult:
    return fetch_public_transcript(video_id, languages)


@st.cache_data(ttl=1800, show_spinner=False)
def cached_news_search(
    api_key: str,
    query: str,
    max_results: int,
    region_code: str,
    relevance_language: str,
    published_after_days: int,
    order: str,
    use_news_category: bool,
) -> List[Dict]:
    return search_news_videos(
        api_key,
        query,
        max_results=max_results,
        region_code=region_code,
        relevance_language=relevance_language,
        published_after_days=published_after_days,
        order=order,
        use_news_category=use_news_category,
    )


@st.cache_data(ttl=300, show_spinner=False)
def cached_ollama_model_names(base_url: str) -> List[str]:
    return completion_model_names(list_ollama_models(base_url))


@st.cache_data(ttl=900, show_spinner=False)
def cached_ai_news_briefing(
    base_url: str,
    model: str,
    query: str,
    results: Tuple[Tuple[str, str, str, str, str, str, str], ...],
) -> str:
    videos = [
        {
            "title": title,
            "channel_title": channel,
            "published_at": published,
            "duration": duration,
            "view_count": views,
            "description": description,
            "url": url,
        }
        for title, channel, published, duration, views, description, url in results
    ]
    return generate_news_briefing(base_url, model, query, videos)


def metadata_text(video: Dict) -> str:
    return combine_texts(
        [
            video.get("title", ""),
            video.get("channel_title", ""),
            video.get("description", ""),
        ]
    )


def source_text_for_summary(video: Dict, transcript: TranscriptResult) -> Tuple[str, str]:
    if transcript.ok:
        return transcript.text, "transcripcion publica"
    return metadata_text(video), "metadata del video"


def render_summary(text: str, max_sentences: int) -> None:
    bullets = bullet_summary(text, max_sentences=max_sentences)
    if not bullets:
        st.warning("No hay texto suficiente para resumir.")
        return
    for bullet in bullets:
        st.markdown(f"- {bullet}")


def render_video_metrics(video: Dict) -> None:
    views, likes, comments, duration = st.columns(4)
    views.metric("Views", format_count(video.get("view_count")))
    likes.metric("Likes", format_count(video.get("like_count")))
    comments.metric("Comentarios", format_count(video.get("comment_count")))
    duration.metric("Duracion", video.get("duration", "N/D"))


def render_video_panel(video: Dict, transcript: TranscriptResult, max_sentences: int) -> None:
    left, right = st.columns([0.38, 0.62], gap="large")
    with left:
        if video.get("thumbnail"):
            st.image(video["thumbnail"], use_container_width=True)
        st.video(video.get("url"))
    with right:
        title = markdown_link_text(video.get("title", "Sin titulo"))
        st.markdown(f'### [{title}]({video.get("url")})')
        st.caption(
            f'{video.get("channel_title", "Canal desconocido")} | {readable_date(video.get("published_at", ""))}'
        )
        render_video_metrics(video)

        source_text, source_name = source_text_for_summary(video, transcript)
        st.subheader("Resumen")
        st.caption(f"Fuente del resumen: {source_name}.")
        render_summary(source_text, max_sentences)

        keywords = extract_keywords(source_text, limit=10)
        if keywords:
            st.caption("Keywords: " + ", ".join(keywords))

    with st.expander("Descripcion"):
        st.write(video.get("description") or "Sin descripcion.")

    with st.expander("Transcripcion detectada"):
        if transcript.ok:
            language = transcript.language_code or transcript.language or "N/D"
            generated = "auto" if transcript.is_generated else "manual/no indicado"
            st.caption(f"Idioma: {language} | Tipo: {generated} | Segmentos: {len(transcript.segments)}")
            st.text_area("Texto", transcript.text, height=260)
        else:
            st.warning(transcript.error or "No hay transcripcion publica disponible.")


def video_summary_tab(api_key: str, languages: Tuple[str, ...], max_sentences: int) -> None:
    st.subheader("Resumen por URL")
    url = st.text_input("URL de YouTube", value=SAMPLE_URL)
    analyze = st.button("Analizar video", type="primary", use_container_width=False)

    if not analyze:
        return
    if not api_key:
        st.error("Agrega una YouTube API key para consultar metadata oficial.")
        return

    try:
        video_id = extract_video_id(url)
    except ValueError as exc:
        st.error(str(exc))
        return

    try:
        with st.spinner("Consultando YouTube Data API..."):
            video = cached_video_details(api_key, video_id)
        with st.spinner("Buscando transcripcion publica..."):
            transcript = cached_transcript(video_id, languages)
    except YouTubeAPIError as exc:
        st.error(str(exc))
        return

    render_video_panel(video, transcript, max_sentences)


def render_news_result_card(video: Dict) -> None:
    with st.container(border=True):
        image_col, text_col = st.columns([0.28, 0.72], gap="medium")
        with image_col:
            if video.get("thumbnail"):
                st.image(video["thumbnail"], use_container_width=True)
        with text_col:
            title = markdown_link_text(video.get("title", "Sin titulo"))
            st.markdown(
                f'**[{title}]({video.get("url")})**',
            )
            st.caption(
                f'{video.get("channel_title", "Canal desconocido")} | {readable_date(video.get("published_at", ""))} | {video.get("duration", "N/D")}'
            )
            description = video.get("description", "")
            if description:
                st.write(description[:320] + ("..." if len(description) > 320 else ""))
            st.caption(
                f'Views: {format_count(video.get("view_count"))} | Likes: {format_count(video.get("like_count"))}'
            )


def ai_result_signature(results: List[Dict]) -> Tuple[Tuple[str, str, str, str, str, str, str], ...]:
    return tuple(
        (
            str(item.get("title", "")),
            str(item.get("channel_title", "")),
            str(item.get("published_at", "")),
            str(item.get("duration", "")),
            str(item.get("view_count", "")),
            str(item.get("description", "")),
            str(item.get("url", "")),
        )
        for item in results[:8]
    )


def render_ai_news_brief(results: List[Dict], query: str, ollama_config: Dict[str, object]) -> None:
    with st.container(border=True):
        st.markdown("#### Brief generativo con IA local")
        st.caption("Usa un modelo local de Ollama para comparar resultados, detectar angulos y sugerir que mirar primero.")

        if not ollama_config.get("enabled"):
            st.info("Activa 'Usar Ollama local' en la barra lateral para generar este briefing.")
            return

        model = str(ollama_config.get("model") or "").strip()
        base_url = str(ollama_config.get("base_url") or OLLAMA_DEFAULT_BASE_URL).strip()
        if not model:
            st.warning("Configura un modelo de Ollama para generar el briefing.")
            return

        generate = st.button("Generar briefing con IA", type="secondary")
        if not generate:
            st.caption(f"Modelo configurado: `{model}`.")
            return

        try:
            with st.spinner(f"Generando briefing con {model} en Ollama..."):
                ai_brief = cached_ai_news_briefing(base_url, model, query, ai_result_signature(results))
        except OllamaError as exc:
            st.error(str(exc))
            st.info("Puedes iniciar Ollama con `ollama serve` o cambiar el modelo en la barra lateral.")
            return

        st.markdown(ai_brief)


def news_tab(api_key: str, languages: Tuple[str, ...], max_sentences: int, ollama_config: Dict[str, object]) -> None:
    st.subheader("Noticias desde YouTube")
    controls = st.columns([0.38, 0.16, 0.14, 0.16, 0.16])
    with controls[0]:
        query = st.text_input("Tema", value="noticias Uruguay")
    with controls[1]:
        region_code = st.text_input("Region", value="UY", max_chars=2)
    with controls[2]:
        relevance_language = st.text_input("Idioma", value="es", max_chars=5)
    with controls[3]:
        published_after_days = st.slider("Dias", 1, 30, 7)
    with controls[4]:
        max_results = st.slider("Resultados", 5, 25, 10, step=5)

    advanced = st.columns([0.24, 0.24, 0.52])
    with advanced[0]:
        order = st.selectbox("Orden", ["date", "relevance", "viewCount"], index=0)
    with advanced[1]:
        use_news_category = st.checkbox("Categoria noticias", value=True)

    search = st.button("Buscar noticias", type="primary")
    if search:
        if not api_key:
            st.error("Agrega una YouTube API key para buscar noticias.")
            return
        try:
            with st.spinner("Buscando en YouTube Data API..."):
                st.session_state["news_results"] = cached_news_search(
                    api_key,
                    query,
                    max_results,
                    region_code,
                    relevance_language,
                    published_after_days,
                    order,
                    use_news_category,
                )
        except YouTubeAPIError as exc:
            st.error(str(exc))
            return

    results = st.session_state.get("news_results", [])
    if not results:
        st.info("Busca un tema para ver videos recientes y armar un brief.")
        return

    brief_text = combine_texts(
        f'{item.get("title", "")}. {item.get("description", "")}' for item in results
    )
    with st.container(border=True):
        st.markdown("#### Brief rapido de resultados")
        st.caption("Resumen construido con titulos y descripciones de los resultados encontrados.")
        render_summary(brief_text, max_sentences=max_sentences)

    render_ai_news_brief(results, query, ollama_config)

    rows = [
        {
            "titulo": item.get("title", ""),
            "canal": item.get("channel_title", ""),
            "fecha": readable_date(item.get("published_at", "")),
            "views": item.get("view_count"),
            "url": item.get("url", ""),
        }
        for item in results
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("#### Resultados")
    for video in results:
        render_news_result_card(video)

    options = {f'{item.get("title", "Sin titulo")} | {item.get("channel_title", "")}': item for item in results}
    selected_labels = st.multiselect(
        "Videos para intentar resumir con transcripcion",
        options=list(options.keys()),
        max_selections=5,
    )
    if st.button("Resumir seleccionados") and selected_labels:
        for label in selected_labels:
            video = options[label]
            with st.expander(video.get("title", "Video"), expanded=True):
                with st.spinner("Buscando transcripcion publica..."):
                    transcript = cached_transcript(video["id"], languages)
                text, source_name = source_text_for_summary(video, transcript)
                st.caption(f"Fuente: {source_name}")
                render_summary(text, max_sentences=max_sentences)
                if not transcript.ok:
                    st.warning(transcript.error or "Sin transcripcion publica.")


def setup_tab() -> None:
    st.subheader("Notas tecnicas")
    st.markdown(
        """
        - `videos.list` trae metadata, estadisticas y duracion del video.
        - `search.list` trae resultados por query, region, idioma y fecha.
        - La API oficial de captions requiere OAuth y permisos; no alcanza solo con API key para bajar cualquier transcripcion publica.
        - El brief generativo usa Ollama local de forma opcional; no envia el contenido a APIs externas.
        - El resumen rapido sigue siendo local y extractivo para funcionar aunque Ollama no este activo.
        """
    )
    st.code("YOUTUBE_API_KEY=tu_api_key\nOLLAMA_BASE_URL=http://127.0.0.1:11434\nOLLAMA_MODEL=qwen3.5:4b", language="bash")
    st.markdown("#### Configuracion automatizada")
    st.code(
        "scripts/bootstrap.sh\nscripts/configure_youtube_cloud.sh\n.venv/bin/streamlit run app.py",
        language="bash",
    )
    st.markdown(
        "Docs: [videos.list](https://developers.google.com/youtube/v3/docs/videos/list) | "
        "[search.list](https://developers.google.com/youtube/v3/docs/search/list) | "
        "[captions.list](https://developers.google.com/youtube/v3/docs/captions/list)"
    )


def main() -> None:
    app_css()
    api_key = configured_api_key()
    ollama_config = configured_ollama()
    with st.sidebar:
        language_input = st.text_input("Idiomas de transcripcion", value="es,en")
        max_sentences = st.slider("Frases del resumen", 3, 10, 5)
        st.caption("Usa codigos separados por coma, por ejemplo: es,en,pt.")

    languages = tuple(
        item.strip().lower()
        for item in language_input.split(",")
        if item.strip()
    ) or ("es", "en")

    st.title("YouTube Briefing")
    st.markdown(
        """
        <div class="ytb-note">
        Pega una URL para obtener metadata oficial, intentar leer transcripcion publica y generar un resumen.
        Despues usa la misma conexion de YouTube Data API para buscar noticias recientes por tema.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_video, tab_news, tab_setup = st.tabs(["Resumen", "Noticias", "Setup"])
    with tab_video:
        video_summary_tab(api_key, languages, max_sentences)
    with tab_news:
        news_tab(api_key, languages, max_sentences, ollama_config)
    with tab_setup:
        setup_tab()


if __name__ == "__main__":
    main()
