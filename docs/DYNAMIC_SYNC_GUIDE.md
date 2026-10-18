# Dynamic source synchronization — v0.2

## Source of truth
- `data/source_docs/`: human-authored DOCX/PDF drafts, not a live database.
- `data/documents/`: draft JSON and offline fixtures, not the production authority.
- Main backend PostgreSQL / authorized backend API: authoritative approved course/service/policy data.
- `rag` schema: derived chunks and vectors; never directly edit business prices here.

## Change flow
1. Admin edits a course/service in the main backend.
2. Backend commits change, increments version, writes a durable outbox event in the same transaction.
3. A worker publishes an event with `event_id`, `source_type`, `source_id`, `version` (or the chatbot polls `updated_at` with a cursor for MVP).
4. Chatbot worker fetches the full approved record using a service credential, validates schema and time validity, computes content hash.
5. If changed, chunk by section and embed with BGE-M3. Stage new chunks as inactive; atomically activate only after all embeddings are ready.
6. On archive/unpublish, immediately filter record out at query time, then clean up vectors asynchronously.
7. On errors, retry with backoff; deduplicate by `event_id` and ignore older versions. Reconcile periodically.

## Important
- Compose build/redeploy is NOT needed for content changes. Do not bake JSON into Docker image for production.
- `docker compose` config and GitHub Actions secrets are not database sync mechanisms.
- Main backend owns business writes; chatbot uses read-only service API and dedicated `rag` schema role.
- Price, availability, enrollment state and user-specific status come from live backend tools, not embeddings.
- Use `approved` and valid-time filters in all production retrieval; `draft`/`test_only` only in isolated dev.
- Invalidate public FAQ cache by source/version; do not cache PII or mutable price/status.
- Deploying the chatbot service independently requires internal network/API authentication and TLS.

## Contracts
See `contracts/source_document.example.json` and `contracts/source_event.example.json`.

## Initial implementation tasks
A: schema + content hashing + ingestion worker + version-aware chunk replacement.
B: backend read API + outbox/polling adapter + authentication + API contract tests.
Both: test create/update/archive, duplicate events, failures and stale versions.
