# Magic Code AI Chatbot — Starter v0.3.1

This release **combines v0.2 and v0.3**. It is a staging starter, **not** a deployed chatbot or a live database sync.

## Where to put documents
- `data/source_docs/public/` — approved-to-share DOCX/PDF source documents (can be committed only after manual review).
- `data/source_docs/private/` — confidential DOCX/PDF documents (ignored by Git; do not commit).
- `data/documents/` — manually curated **draft** JSON documents from v0.2.
- `data/generated/{public,private}/` — automatically extracted JSON and chunk JSONL (ignored by Git).
- `data/golden_set/questions.jsonl` — 10 sample eval questions; expand to 150.
- `contracts/` — example backend source/event payloads.
- `migrations/001_rag_sync.sql` — database schema draft.
- `deploy/` — illustrative Compose/environment examples, not a runnable deployment.

## Quick start
```bash
python -m pip install -r requirements-ingestion.txt
python scripts/validate_documents.py
python scripts/ingest_documents.py --scope public
```

Outputs are placed under `data/generated/public/`. Files are staged with `status=draft`, not automatically approved or indexed. For local private processing, run `--scope private`. Do not use `--scope all` by default.

## Before every push
```bash
git status
git diff --cached --name-only
git ls-files data/source_docs/private data/generated
```

`.gitignore` does not remove already-tracked secrets. If secrets were committed, remove from tracking/history as appropriate and rotate credentials. Never place live credentials in YAML committed to Git.

## Scope and limits
- PDF text extraction requires selectable text; scanned PDFs need separate OCR.
- DOCX pages are `null` because pagination is not reliably available in python-docx.
- Basic heading/paragraph splitting can split very long paragraphs; review chunk quality.
- No BGE-M3 embedding, database writes, backend sync, approval workflow, or production deployment yet.
- The included DOCX is a research reference, **not** approved company policy.
- `data/documents/*.json` are draft examples and must be reviewed before publication.

See `docs/DATA_GUIDE.md`, `docs/DYNAMIC_SYNC_GUIDE.md`, and `docs/INGESTION_SECURITY.md`.
