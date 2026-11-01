import re
from dataclasses import dataclass

from readers.models import LoadedDoc

MAX_CHARS = 1000   # нэг хэсгийн зорилтот дээд урт (зөөлөн хязгаар)
OVERLAP = 150      # урт section хуваагдахад хөрш хэсгүүдийн давхцал

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    index: int
    content: str
    page: int | None
    meta: dict


def _split_long(unit: str, max_chars: int) -> list[str]:
    """Хэт урт мөрийг өгүүлбэрээр, хэрэв бас урт бол тэмдэгтээр хуваана."""
    if len(unit) <= max_chars:
        return [unit]
    parts: list[str] = []
    for sentence in SENTENCE_RE.split(unit):
        if len(sentence) <= max_chars:
            parts.append(sentence)
        else:
            parts.extend(
                sentence[i:i + max_chars] for i in range(0, len(sentence), max_chars)
            )
    return parts


def split_text(text: str, max_chars: int = MAX_CHARS, overlap: int = OVERLAP) -> list[str]:
    units: list[str] = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            units.extend(_split_long(line, max_chars))

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for unit in units:
        extra = len(unit) + (1 if current else 0)
        if current and current_len + extra > max_chars:
            chunks.append("\n".join(current))

            # өмнөх хэсгийн сүүлчийн мөрүүдээс давхцал авна
            tail: list[str] = []
            tail_len = 0
            for prev in reversed(current):
                if tail_len + len(prev) + 1 > overlap:
                    break
                tail.insert(0, prev)
                tail_len += len(prev) + 1
            current = tail
            current_len = sum(len(x) for x in current) + max(len(current) - 1, 0)
            extra = len(unit) + (1 if current else 0)

        current.append(unit)
        current_len += extra

    if current:
        chunks.append("\n".join(current))
    return chunks


def build_chunks(doc: LoadedDoc, title: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    for section in doc.sections:
        header = f"{title} › {section.heading}" if section.heading else title
        for piece in split_text(section.text):
            meta = {}
            if section.heading:
                meta["heading"] = section.heading
            meta.update(section.meta)
            chunks.append(
                Chunk(
                    index=len(chunks),
                    content=f"{header}\n{piece}",
                    page=section.page,
                    meta=meta,
                )
            )
    return chunks