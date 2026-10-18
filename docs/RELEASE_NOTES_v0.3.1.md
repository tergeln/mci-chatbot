# v0.3.1 release notes

Merged the v0.2 dynamic architecture starter (contracts, SQL migration, Compose example, curated JSON, golden set) with the v0.3 local ingestion/security upgrade (DOCX/PDF extraction, section-based chunk staging, requirements, public/private directories, ignore rules).

**Not implemented:** BGE-M3 vectors, pgvector write pipeline, live backend event ingestion, automated approval, or a runnable Compose deployment.

**Security:** `data/generated/`, `data/source_docs/private/`, `data/documents/private/`, and local credentials are ignored. Public documents are not automatically safe; review before staging.

**Merge detail:** preserved the v0.2 `deploy/.env.example`; renamed v0.3's root `.env.example` to `deploy/.env.ingestion.example`. Combined both `.gitignore` rule sets.
