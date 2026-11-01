import hashlib
from pathlib import Path

from .docx_reader import read_docx
from .json_reader import read_json
from .models import LoadedDoc, Section
from .pdf_reader import read_pdf
from .text_reader import read_text

SUPPORTED = {
    ".pdf": ("pdf", read_pdf),
    ".docx": ("docx", read_docx),
    ".json": ("json", read_json),
    ".txt": ("txt", read_text),
    ".md": ("md", read_text),
}


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_document(path: Path) -> LoadedDoc:
    ext = path.suffix.lower()
    if ext not in SUPPORTED:
        raise ValueError(f"{path.name}: дэмжигдэхгүй төрөл ({ext})")
    doc_type, reader = SUPPORTED[ext]
    return LoadedDoc(
        path=path,
        doc_type=doc_type,
        content_hash=file_hash(path),
        sections=reader(path),
    )


__all__ = ["SUPPORTED", "load_document", "LoadedDoc", "Section"]