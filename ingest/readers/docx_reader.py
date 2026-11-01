from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from .clean import clean_text
from .models import Section


def _iter_blocks(doc):
    """Догол мөр ба хүснэгтийг баримт доторх жинхэнэ дарааллаар нь гаргана."""
    for child in doc.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, doc)
        elif child.tag.endswith("}tbl"):
            yield Table(child, doc)


def _table_lines(table: Table) -> list[str]:
    lines = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            value = clean_text(cell.text).replace("\n", " ")
            # нийлүүлсэн (merged) нүд давхардаж гардаг тул дараалсан адилыг алгасна
            if value and (not cells or cells[-1] != value):
                cells.append(value)
        if cells:
            lines.append(" | ".join(cells))
    return lines


def read_docx(path: Path) -> list[Section]:
    doc = Document(str(path))
    sections: list[Section] = []
    heading: str | None = None
    buffer: list[str] = []

    def flush():
        text = clean_text("\n".join(buffer))
        if text:
            sections.append(Section(text=text, heading=heading))
        buffer.clear()

    for block in _iter_blocks(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue
            style = block.style.name if block.style is not None else ""
            if style.startswith("Heading") or style == "Title":
                flush()
                heading = text
            else:
                buffer.append(text)
        else:
            buffer.extend(_table_lines(block))

    flush()
    return sections