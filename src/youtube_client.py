from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import parse_qs, urlparse


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
ISO_DURATION_RE = re.compile(
    r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$"
)


class YouTubeAPIError(RuntimeError):
    """Raised when YouTube Data API rejects or cannot fulfill a request."""


def extract_video_id(value: str) -> str:
    """Extract an 11-character YouTube video id from a URL or raw id."""
    raw = (value or "").strip()
    if VIDEO_ID_RE.match(raw):
        return raw

    parsed = urlparse(raw)
    host = parsed.netloc.lower().replace("www.", "")
    query = parse_qs(parsed.query)

    if "v" in query and query["v"]:
        candidate = query["v"][0]
        if VIDEO_ID_RE.match(candidate):
            return candidate

    path_parts = [part for part in parsed.path.split("/") if part]
    if host == "youtu.be" and path_parts:
        candidate = path_parts[0]
        if VIDEO_ID_RE.match(candidate):
            return candidate

    for marker in ("shorts", "embed", "live", "v"):
        if marker in path_parts:
            index = path_parts.index(marker) + 1
            if index < len(path_parts) and VIDEO_ID_RE.match(path_parts[index]):
                return path_parts[index]

    match = re.search(r"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])", raw)
    if match:
        return match.group(1)

    raise ValueError("No pude detectar un video_id valido en esa URL.")


def youtube_watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def thumbnail_url(snippet: Dict[str, Any]) -> str:
    thumbs = snippet.get("thumbnails", {}) or {}
    for key in ("maxres", "standard", "high", "medium", "default"):
        if key in thumbs and thumbs[key].get("url"):
            return thumbs[key]["url"]
    return ""


def parse_iso_duration_to_seconds(duration: str) -> int:
    match = ISO_DURATION_RE.match(duration or "")
    if not match:
        return 0
    parts = {key: int(value or 0) for key, value in match.groupdict().items()}
    return (
        parts["days"] * 86400
        + parts["hours"] * 3600
        + parts["minutes"] * 60
        + parts["seconds"]
    )


def format_duration(duration: str) -> str:
    seconds = parse_iso_duration_to_seconds(duration)
    if not seconds:
        return "N/D"
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_count(value: Any) -> str:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return "N/D"
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    if number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return str(number)


def _youtube_get(api_key: str, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    import requests

    if not api_key:
        raise YouTubeAPIError("Falta YOUTUBE_API_KEY.")

    request_params = {**params, "key": api_key}
    response = requests.get(
        f"{YOUTUBE_API_BASE}/{endpoint}",
        params=request_params,
        timeout=25,
    )

    try:
        data = response.json()
    except ValueError as exc:
        raise YouTubeAPIError("YouTube devolvio una respuesta no-JSON.") from exc

    if not response.ok or "error" in data:
        error = data.get("error", {})
        message = error.get("message") or response.text[:300]
        reasons = []
        for item in error.get("errors", []) or []:
            reason = item.get("reason")
            if reason:
                reasons.append(reason)
        suffix = f" ({', '.join(reasons)})" if reasons else ""
        raise YouTubeAPIError(f"Error de YouTube API: {message}{suffix}")

    return data


def get_video_details(api_key: str, video_id: str) -> Dict[str, Any]:
    data = _youtube_get(
        api_key,
        "videos",
        {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
        },
    )
    items = data.get("items", [])
    if not items:
        raise YouTubeAPIError("No encontre ese video en YouTube Data API.")
    return normalize_video(items[0])


def get_videos_details(api_key: str, video_ids: Iterable[str]) -> List[Dict[str, Any]]:
    ids = [video_id for video_id in video_ids if video_id]
    if not ids:
        return []
    data = _youtube_get(
        api_key,
        "videos",
        {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(ids[:50]),
        },
    )
    return [normalize_video(item) for item in data.get("items", [])]


def normalize_video(item: Dict[str, Any]) -> Dict[str, Any]:
    snippet = item.get("snippet", {}) or {}
    content = item.get("contentDetails", {}) or {}
    stats = item.get("statistics", {}) or {}
    video_id = item.get("id", "")
    if isinstance(video_id, dict):
        video_id = video_id.get("videoId", "")

    return {
        "id": video_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "channel_id": snippet.get("channelId", ""),
        "published_at": snippet.get("publishedAt", ""),
        "thumbnail": thumbnail_url(snippet),
        "duration": format_duration(content.get("duration", "")),
        "duration_seconds": parse_iso_duration_to_seconds(content.get("duration", "")),
        "view_count": stats.get("viewCount"),
        "like_count": stats.get("likeCount"),
        "comment_count": stats.get("commentCount"),
        "url": youtube_watch_url(video_id),
        "raw": item,
    }


def search_news_videos(
    api_key: str,
    query: str,
    *,
    max_results: int = 10,
    region_code: str = "UY",
    relevance_language: str = "es",
    published_after_days: Optional[int] = 7,
    order: str = "date",
    use_news_category: bool = True,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": order,
        "maxResults": max(1, min(max_results, 50)),
    }

    if region_code:
        params["regionCode"] = region_code.upper()
    if relevance_language:
        params["relevanceLanguage"] = relevance_language.lower()
    if published_after_days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=published_after_days)
        params["publishedAfter"] = cutoff.isoformat().replace("+00:00", "Z")
    if use_news_category:
        params["videoCategoryId"] = "25"

    data = _youtube_get(api_key, "search", params)
    search_items = data.get("items", [])
    ordered_ids = [
        item.get("id", {}).get("videoId", "")
        for item in search_items
        if item.get("id", {}).get("videoId")
    ]
    details_by_id = {video["id"]: video for video in get_videos_details(api_key, ordered_ids)}

    results: List[Dict[str, Any]] = []
    for item in search_items:
        video_id = item.get("id", {}).get("videoId", "")
        snippet = item.get("snippet", {}) or {}
        base = {
            "id": video_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "channel_id": snippet.get("channelId", ""),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail": thumbnail_url(snippet),
            "url": youtube_watch_url(video_id),
        }
        base.update(details_by_id.get(video_id, {}))
        results.append(base)

    return results


def readable_date(value: str) -> str:
    if not value:
        return "N/D"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return parsed.strftime("%Y-%m-%d %H:%M UTC")
