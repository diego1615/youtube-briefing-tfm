from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence


@dataclass(frozen=True)
class TranscriptResult:
    video_id: str
    text: str
    segments: List[Dict[str, Any]]
    language: str = ""
    language_code: str = ""
    is_generated: Optional[bool] = None
    error: str = ""

    @property
    def ok(self) -> bool:
        return bool(self.text.strip()) and not self.error


def fetch_public_transcript(
    video_id: str,
    languages: Sequence[str] = ("es", "en"),
) -> TranscriptResult:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return TranscriptResult(
            video_id=video_id,
            text="",
            segments=[],
            error="Instala youtube-transcript-api para intentar leer transcripciones publicas.",
        )

    try:
        fetched = _fetch_preferred_transcript(YouTubeTranscriptApi, video_id, languages)
        segments = _coerce_segments(fetched)
        text = transcript_text(segments)
        return TranscriptResult(
            video_id=video_id,
            text=text,
            segments=segments,
            language=getattr(fetched, "language", "") or "",
            language_code=getattr(fetched, "language_code", "") or "",
            is_generated=getattr(fetched, "is_generated", None),
        )
    except Exception as exc:
        return TranscriptResult(
            video_id=video_id,
            text="",
            segments=[],
            error=f"No pude obtener transcripcion publica: {exc}",
        )


def _fetch_preferred_transcript(
    api_cls: Any,
    video_id: str,
    languages: Sequence[str],
) -> Any:
    languages_list = list(languages) or ["es", "en"]

    try:
        api = api_cls()
        if hasattr(api, "fetch"):
            return api.fetch(video_id, languages=languages_list)
    except Exception:
        pass

    if hasattr(api_cls, "get_transcript"):
        raw = api_cls.get_transcript(video_id, languages=languages_list)
        return RawTranscript(raw)

    api = api_cls()
    list_method = getattr(api, "list", None) or getattr(api_cls, "list_transcripts", None)
    if list_method is None:
        raise RuntimeError("Version de youtube-transcript-api no soportada.")

    transcript_list = list_method(video_id)
    try:
        transcript = transcript_list.find_transcript(languages_list)
    except Exception:
        transcript = next(iter(transcript_list))
    return transcript.fetch()


class RawTranscript:
    def __init__(self, rows: Iterable[Dict[str, Any]]):
        self.rows = list(rows)
        self.language = ""
        self.language_code = ""
        self.is_generated = None

    def __iter__(self):
        return iter(self.rows)

    def to_raw_data(self) -> List[Dict[str, Any]]:
        return self.rows


def _coerce_segments(fetched: Any) -> List[Dict[str, Any]]:
    if hasattr(fetched, "to_raw_data"):
        rows = fetched.to_raw_data()
    else:
        rows = list(fetched)

    segments: List[Dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            text = row.get("text", "")
            start = row.get("start", 0)
            duration = row.get("duration", 0)
        else:
            text = getattr(row, "text", "")
            start = getattr(row, "start", 0)
            duration = getattr(row, "duration", 0)

        clean = " ".join(str(text).replace("\n", " ").split())
        if clean:
            segments.append({"text": clean, "start": start, "duration": duration})

    return segments


def transcript_text(segments: Iterable[Dict[str, Any]]) -> str:
    return " ".join(segment.get("text", "") for segment in segments).strip()

