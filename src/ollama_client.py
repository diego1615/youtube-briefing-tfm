from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional


OLLAMA_DEFAULT_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_DEFAULT_MODEL = "qwen3.5:4b"
OLLAMA_REQUEST_TIMEOUT = (5, 120)
OLLAMA_MODEL_PREFERENCES = (
    "qwen3.5:4b",
    "llama3.2:3b",
    "qwen2.5:7b",
    "gemma3:4b",
)


class OllamaError(RuntimeError):
    """Raised when local Ollama cannot generate a response."""


THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


def normalize_base_url(base_url: str) -> str:
    clean_url = (base_url or OLLAMA_DEFAULT_BASE_URL).strip().rstrip("/")
    return clean_url or OLLAMA_DEFAULT_BASE_URL


def is_truthy_env(value: Optional[str], default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def list_ollama_models(base_url: str = OLLAMA_DEFAULT_BASE_URL) -> List[Dict[str, Any]]:
    import requests

    url = f"{normalize_base_url(base_url)}/api/tags"
    try:
        response = requests.get(url, timeout=(3, 10))
    except requests.RequestException as exc:
        raise OllamaError("No pude conectar con Ollama local. Verifica que `ollama serve` este activo.") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise OllamaError("Ollama devolvio una respuesta no-JSON.") from exc

    if not response.ok:
        message = data.get("error") or response.text[:300]
        raise OllamaError(f"Ollama devolvio un error: {message}")

    return list(data.get("models", []) or [])


def completion_model_names(models: Iterable[Dict[str, Any]]) -> List[str]:
    names: List[str] = []
    for model in models:
        name = str(model.get("name") or model.get("model") or "").strip()
        if not name:
            continue
        capabilities = model.get("capabilities") or []
        if capabilities and "completion" not in capabilities:
            continue
        names.append(name)
    return names


def choose_default_model(model_names: Iterable[str], preferred: str = OLLAMA_DEFAULT_MODEL) -> str:
    names = [name for name in model_names if name]
    if preferred in names:
        return preferred
    for candidate in OLLAMA_MODEL_PREFERENCES:
        if candidate in names:
            return candidate
    return names[0] if names else preferred


def video_line(video: Dict[str, Any], index: int) -> str:
    title = str(video.get("title") or "Sin titulo").strip()
    channel = str(video.get("channel_title") or "Canal desconocido").strip()
    published = str(video.get("published_at") or "Fecha no disponible").strip()
    duration = str(video.get("duration") or "Duracion no disponible").strip()
    views = str(video.get("view_count") or "Views no disponibles").strip()
    url = str(video.get("url") or "").strip()
    description = str(video.get("description") or "").replace("\n", " ").strip()
    if len(description) > 600:
        description = description[:600].rsplit(" ", 1)[0] + "..."

    return (
        f"{index}. Titulo: {title}\n"
        f"   Canal: {channel}\n"
        f"   Publicado: {published}\n"
        f"   Duracion: {duration}\n"
        f"   Views: {views}\n"
        f"   URL: {url}\n"
        f"   Descripcion: {description or 'Sin descripcion.'}"
    )


def build_news_brief_prompt(query: str, videos: Iterable[Dict[str, Any]], *, max_items: int = 8) -> str:
    selected = list(videos)[:max_items]
    lines = "\n\n".join(video_line(video, index + 1) for index, video in enumerate(selected))
    topic = (query or "busqueda en YouTube").strip()

    return f"""Eres un analista senior de investigacion audiovisual.
Tu tarea es convertir resultados de YouTube en un briefing ejecutivo accionable.

Tema buscado: {topic}

Resultados disponibles:
{lines}

Instrucciones:
- Escribe en espanol claro y profesional.
- Usa solo la informacion provista; no inventes datos, fuentes ni fechas.
- Si hay poca evidencia, dilo explicitamente.
- Diferencia hechos observables de interpretaciones.
- Prioriza utilidad para decidir que videos mirar primero.

Devuelve Markdown con estas secciones:
## Resumen ejecutivo
3 a 5 lineas sobre el panorama general.

## Hallazgos clave
5 bullets concretos.

## Comparacion de fuentes
Compara canales, angulos y posibles diferencias de enfoque.

## Senales de alerta o sesgos
Indica limites, sesgos potenciales, titulares exagerados o informacion faltante.

## Recomendacion de consumo
Orden sugerido de 3 videos para mirar primero, con razon breve.
"""


def generate_ollama_text(
    base_url: str,
    model: str,
    prompt: str,
    *,
    temperature: float = 0.2,
    num_predict: int = 900,
) -> str:
    import requests

    if not model:
        raise OllamaError("Falta configurar el modelo de Ollama.")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    try:
        response = requests.post(
            f"{normalize_base_url(base_url)}/api/generate",
            json=payload,
            timeout=OLLAMA_REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise OllamaError("No pude conectar con Ollama local. Verifica que `ollama serve` este activo.") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise OllamaError("Ollama devolvio una respuesta no-JSON.") from exc

    if not response.ok or data.get("error"):
        message = data.get("error") or response.text[:300]
        raise OllamaError(f"Ollama devolvio un error: {message}")

    text = clean_model_response(str(data.get("response") or ""))
    if not text:
        raise OllamaError("Ollama no devolvio texto para el briefing.")
    return text


def clean_model_response(text: str) -> str:
    return THINK_BLOCK_RE.sub("", text or "").strip()


def generate_news_briefing(
    base_url: str,
    model: str,
    query: str,
    videos: Iterable[Dict[str, Any]],
) -> str:
    prompt = build_news_brief_prompt(query, videos)
    return generate_ollama_text(base_url, model, prompt)
