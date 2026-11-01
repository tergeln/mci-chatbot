from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Section:
    """Файлын нэг логик хэсэг: PDF-ийн нэг хуудас, Word-ийн нэг гарчгийн доорх
    агуулга, JSON-ийн нэг бичлэг гэх мэт."""
    text: str
    page: int | None = None        # PDF-ийн хуудасны дугаар
    heading: str | None = None     # Word-ийн гарчиг, JSON-ийн түлхүүр
    meta: dict = field(default_factory=dict)


@dataclass
class LoadedDoc:
    path: Path
    doc_type: str                  # pdf | docx | json | txt | md
    content_hash: str              # файл өөрчлөгдсөн эсэхийг мэдэх SHA-256
    sections: list[Section]