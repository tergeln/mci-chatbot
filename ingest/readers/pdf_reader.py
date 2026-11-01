from pathlib import Path

from pypdf import PdfReader

from .clean import clean_text
from .models import Section


def read_pdf(path: Path) -> list[Section]:
    reader = PdfReader(str(path))

    if reader.is_encrypted:
        # нууц үггүй (хоосон нууц үгтэй) хамгаалагдсан PDF-ийг нээх оролдлого
        if reader.decrypt("") == 0:
            raise ValueError(f"{path.name}: нууц үгтэй PDF, нээж чадсангүй")

    sections: list[Section] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            sections.append(Section(text=text, page=page_number))
    return sections