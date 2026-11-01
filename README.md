# mci-chatbot

Magic Code AI-ийн (www.mci.mn) онлайн сургалт, вебсайт хөгжүүлэлт, мерчийн RAG чатбот "Magi".

Stack: Python, FastAPI, Gemini, Supabase pgvector, React.

## Бүтэц
- `api/`: чатын API (FastAPI, Vercel дээр Root Directory = `api`)
- `ingest/`: PDF, DOCX, JSON, TXT/MD файлыг мэдлэгийн санд ачаалах
- `evals/`: үнэлгээний асуултууд ба ажиллуулах скрипт
- `widget/`: React чат компонент (эх хувь; сайт `mci-web/src/components/ChatWidget/` руу хуулж ашигладаг)
- `knowledge/`: мэдлэгийн сангийн эх файлууд (`course/`, `web/`, `merch/`, `general/` хавтсаар ангилна)

## Тохиргоо
`.env.example`-ийг root дээр `.env` болгон хуулж утгуудаа оруулна. `api/` ба `ingest/` тус бүр өөрийн `.venv`-тэй:

```
cd api && python -m venv .venv && .venv/bin/pip install -r requirements.txt
cd ingest && python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## Мэдлэгийн сан шинэчлэх
`ingest/` дотроос:

```
.venv/bin/python ingest.py --dry-run           # хэсэглэлтийг харах, DB-д хүрэхгүй
.venv/bin/python ingest.py                     # өөрчлөгдсөн файлуудыг ачаалах
.venv/bin/python ingest.py --prune --dry-run   # knowledge/-аас устгасан файлуудыг жагсаах
.venv/bin/python ingest.py --prune             # тэдгээрийг DB-ээс устгах
.venv/bin/python search_test.py "асуулт"       # хайлтын оноог шалгах
```

Embedding: `gemini-embedding-001`, 1536 хэмжээс. API ба ingest-д ижил байх ёстой. Солиход бүх файлыг `--force`-оор дахин ачаална.

## API локал дээр
```
cd api && .venv/bin/uvicorn main:app --port 8000 --reload
```

## Үнэлгээ
Root-оос, `api/.venv`-ээр:

```
api/.venv/bin/python evals/run_evals.py                 # зөвхөн хайлт: MIN_SIMILARITY босгыг хэмжинэ
api/.venv/bin/python evals/run_evals.py --full          # локал бүтэн шалгалт
api/.venv/bin/python evals/run_evals.py --url https://magiccode-chatbot.vercel.app   # production
```

Мэдлэгийн санд контент нэмэх бүрд `evals/cases.jsonl`-д кейс нэмж, босгыг дахин хэмжинэ.

## Deploy (Vercel)
- Root Directory: `api`
- Заавал: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `ALLOWED_ORIGINS=https://www.mci.mn,https://mci.mn`, `CONTACT_TEXT`, `RATE_LIMIT_SALT`
- `DEBUG_RETRIEVAL`-ийг production дээр тохируулахгүй
- Deployment Protection (Vercel Authentication) унтраалттай байх ёстой
- Сайт талд: `VITE_CHAT_API_URL=<API хаяг>`

## Мэдэгдэж буй дутагдал
Supabase-ийн схем (`kb_sources`, `kb_chunks`, `kb_match_chunks`, `kb_rate_limit_hit`) repo-д ороогүй. Шинэ Supabase дээр суулгахын тулд одоогийн сангаас SQL-ийг экспортлон `sql/` руу нэмэх шаардлагатай.
