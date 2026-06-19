from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, List


STOPWORDS = {
    "a",
    "al",
    "algo",
    "ante",
    "antes",
    "as",
    "asi",
    "be",
    "but",
    "by",
    "como",
    "con",
    "de",
    "del",
    "desde",
    "do",
    "does",
    "el",
    "en",
    "entre",
    "era",
    "es",
    "esa",
    "ese",
    "eso",
    "esta",
    "este",
    "esto",
    "for",
    "ha",
    "han",
    "has",
    "have",
    "he",
    "in",
    "is",
    "it",
    "la",
    "las",
    "lo",
    "los",
    "mas",
    "me",
    "mi",
    "no",
    "of",
    "on",
    "or",
    "para",
    "pero",
    "por",
    "que",
    "se",
    "si",
    "sin",
    "su",
    "sus",
    "that",
    "the",
    "their",
    "this",
    "to",
    "un",
    "una",
    "was",
    "we",
    "were",
    "with",
    "y",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def split_sentences(text: str) -> List[str]:
    clean = normalize_text(text)
    if not clean:
        return []
    parts = re.split(r"(?<=[.!?])\s+", clean)
    sentences = [part.strip() for part in parts if len(part.strip()) > 20]
    if sentences:
        return sentences
    return [clean]


def tokenize(text: str) -> List[str]:
    return [
        token.lower()
        for token in re.findall(r"\b[\w-]{3,}\b", text)
        if token.lower() not in STOPWORDS and not token.isdigit()
    ]


def summarize_text(text: str, *, max_sentences: int = 5, max_chars: int = 1600) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ""
    if len(sentences) <= max_sentences:
        return _limit_chars(" ".join(sentences), max_chars)

    frequencies = Counter(tokenize(" ".join(sentences)))
    if not frequencies:
        return _limit_chars(" ".join(sentences[:max_sentences]), max_chars)

    max_frequency = max(frequencies.values())
    weights = {word: count / max_frequency for word, count in frequencies.items()}

    scored = []
    for index, sentence in enumerate(sentences):
        tokens = tokenize(sentence)
        if not tokens:
            continue
        score = sum(weights.get(token, 0) for token in tokens) / math.sqrt(len(tokens))
        scored.append((score, index, sentence))

    selected = sorted(scored, reverse=True)[:max_sentences]
    selected_indexes = sorted(index for _, index, _ in selected)
    summary = " ".join(sentences[index] for index in selected_indexes)
    return _limit_chars(summary, max_chars)


def bullet_summary(text: str, *, max_sentences: int = 5, max_chars: int = 1600) -> List[str]:
    summary = summarize_text(text, max_sentences=max_sentences, max_chars=max_chars)
    return split_sentences(summary)


def extract_keywords(text: str, *, limit: int = 8) -> List[str]:
    counts = Counter(tokenize(text))
    return [word for word, _ in counts.most_common(limit)]


def combine_texts(texts: Iterable[str]) -> str:
    return "\n".join(normalize_text(text) for text in texts if normalize_text(text))


def _limit_chars(text: str, max_chars: int) -> str:
    clean = normalize_text(text)
    if len(clean) <= max_chars:
        return clean
    trimmed = clean[: max_chars - 1].rsplit(" ", 1)[0].strip()
    return f"{trimmed}..."

