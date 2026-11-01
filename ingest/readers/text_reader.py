import re
from pathlib import Path

from .clean import clean_text
from .models import Section

# "[ГАРЧИГ]" эсвэл "# Гарчиг" хэлбэрийн мөр
HEADING_RE = re.compile(r"^\s*(?:\[(.+?)\]|#{1,3}\s+(.+?))\s*$")


def read_text(path: Path) -> list[Section]:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    text = clean_text(raw)
    if not text:
        return []

    sections: list[Section] = []
    heading: str | None = None
    buffer: list[str] = []

    def flush():
        body = clean_text("\n".join(buffer))
        if body:
            sections.append(Section(text=body, heading=heading))
        buffer.clear()

    for line in text.split("\n"):
        match = HEADING_RE.match(line)
        if match:
            flush()
            heading = (match.group(1) or match.group(2)).strip()
        else:
            buffer.append(line)

    flush()
    return sections