# DOCX/PDF ingestion & Git safety

## Quick start
1. Copy **public** documents to `data/source_docs/public/`, confidential documents to `data/source_docs/private/`.
2. `python -m pip install -r requirements-ingestion.txt`
3. `python scripts/ingest_documents.py --scope all`
4. Review staged `data/generated/{public,private}/*.json` and `*.chunks.jsonl` locally.
5. All imported docs start as `draft` and are NOT automatically published or inserted into PostgreSQL.

## Security
- `.gitignore` excludes `data/source_docs/private/`, `data/generated/`, and `.env` files. Never commit credentials or PII.
- `git check-ignore -v data/source_docs/private/secret.docx` verifies the ignore rule.
- `git ls-files data/source_docs/private data/generated` should return no paths.
- If a secret was already committed, `.gitignore` cannot remove history. Revoke/rotate it, untrack with `git rm --cached`, and clean history with appropriate tooling.
- Public docs may still contain confidential data: inspect and approve before committing.
- This parser extracts DOCX paragraphs/tables and PDF text; scanned PDFs, diagrams, images, and complex layouts need a separate extraction/review path. PDF `page` is available; DOCX page numbers are unknown.

## Dynamic synchronization design (next milestone)
Admin/backend changes → authenticated event or outbox → ingestion worker → validate + approve → content_hash diff → embeddings → transactional activation of new version → invalidate public FAQ cache. Do not rebuild Docker images for content changes. Keep source of truth in backend DB; the JSON files here are local staging, not authoritative production data.
