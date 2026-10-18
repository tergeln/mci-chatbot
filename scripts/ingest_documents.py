"""Local, safe document-to-JSON/chunks staging. No DB writes or API calls.
Usage: python scripts/ingest_documents.py [--scope public|private|all]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data' / 'source_docs'
OUT = ROOT / 'data' / 'generated'


def extract_docx(path: Path):
    from docx import Document
    document = Document(path)
    sections, heading, content = [], 'Ерөнхий мэдээлэл', []
    def flush():
        nonlocal content
        if content:
            sections.append({'heading': heading, 'page': None, 'content': '\n'.join(content).strip()})
            content = []
    for block in document.element.body:
        if block.tag.endswith('}p'):
            from docx.text.paragraph import Paragraph
            p = Paragraph(block, document)
            t = p.text.strip()
            if not t: continue
            if p.style and p.style.name.lower().startswith(('heading', 'гарчиг')):
                flush(); heading = t
            else: content.append(t)
        elif block.tag.endswith('}tbl'):
            from docx.table import Table
            table = Table(block, document)
            for row in table.rows:
                content.append(' | '.join(c.text.replace('\n', ' / ').strip() for c in row.cells))
    flush()
    return sections


def extract_pdf(path: Path):
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    return [{'heading': f'Хуудас {i}', 'page': i, 'content': page.extract_text().strip()}
            for i, page in enumerate(reader.pages, 1) if page.extract_text().strip()]


def chunk_sections(sections, max_chars=1300):
    for section in sections:
        # Split at paragraph boundaries; avoid silently losing very long paragraphs.
        paragraphs = section['content'].split('\n')
        buf = ''
        for paragraph in paragraphs:
            pieces = [paragraph[i:i+max_chars] for i in range(0, len(paragraph), max_chars)] or ['']
            for piece in pieces:
                if buf and len(buf) + len(piece) + 1 > max_chars:
                    yield section['heading'], section['page'], buf
                    buf = ''
                buf = (buf + '\n' + piece).strip()
        if buf: yield section['heading'], section['page'], buf


def process(path: Path, scope: str):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    doc_id = hashlib.sha256(str(path.relative_to(SRC)).encode()).hexdigest()[:16]
    sections = extract_docx(path) if path.suffix.lower() == '.docx' else extract_pdf(path)
    document = {
        'document_id': f'upload-{doc_id}', 'doc_type': 'unclassified', 'title': path.stem,
        'status': 'draft', 'version': digest[:12], 'content_hash': digest,
        'valid_from': None, 'valid_to': None, 'lang': 'mn', 'course_id': None,
        'source_name': path.name, 'scope': scope,
        'processed_at': datetime.now(timezone.utc).isoformat(), 'sections': sections
    }
    target = OUT / scope
    target.mkdir(parents=True, exist_ok=True)
    (target / f'{doc_id}.json').write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
    chunks = []
    for i, (heading, page, text) in enumerate(chunk_sections(sections), 1):
        chunks.append({'chunk_id': f'{doc_id}-{i:04d}', 'document_id': document['document_id'],
                       'text': f'{heading}\n{text}', 'content_hash': hashlib.sha256(text.encode()).hexdigest(),
                       'meta': {'source_name': path.name, 'page': page, 'heading': heading,
                                'version': document['version'], 'status': 'draft', 'scope': scope}})
    (target / f'{doc_id}.chunks.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in chunks), encoding='utf-8')
    print(f'OK {scope}/{path.name}: {len(sections)} sections, {len(chunks)} chunks')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scope', choices=['public', 'private', 'all'], default='all')
    args = ap.parse_args()
    scopes = ['public', 'private'] if args.scope == 'all' else [args.scope]
    count = 0
    for scope in scopes:
        for path in sorted((SRC / scope).rglob('*')):
            if path.is_file() and path.suffix.lower() in {'.docx', '.pdf'} and not path.name.startswith('~$'):
                try: process(path, scope); count += 1
                except Exception as e: print(f'ERROR {path.name}: {e}')
    print(f'Processed {count} documents. Staged only; not approved, embedded, or published.')

if __name__ == '__main__': main()
