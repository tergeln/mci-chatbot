# Magic Code AI Chatbot demo data v0.3.1
Эх сурвалж: хэрэглэгчийн илгээсэн FR0100–FR0199 шаардлагын текст.

## Анхааруулга
Бүх үнэ, сургалтын нэр, хэрэглэгч, төлбөр, захиалга, мэдээ нь ЗОХИОМОЛ TEST DATA. `test_only`/`demo_only` тэмдэглэгээтэй. Production-д нийтэлж, бодит төлбөр хийхэд ашиглахгүй.

## Хавтас
- `data/documents/*.json`: v0.3.1-ийн document schema-тай ойролцоо RAG knowledge docs (sections, doc_type, version, status).
- `data/fixtures/*.json`: API/UI mock өгөгдөл. Хувийн мэдээллийг public RAG-д индексэлж болохгүй.
- `data/golden_set/demo_questions.jsonl`: chatbot-ийн demo шалгах 8 асуулт.
- `requirements_traceability.json`: эх сурвалжийн FR дугаар бүр.

## Хэрэглэх
1. ZIP-ийг задлаад `data/documents` доторх файлуудыг өмнөх repository-д шууд дарж солихын өмнө backup хий.
2. Эдгээр demo documents-ийг `test_only`-г дэмждэг **тусдаа demo loader**-оор унш. Өмнөх validator нь `status`-ийн зөвшөөрөгдөх утгыг хязгаарласан бол schema-гаа тааруул.
3. `data/fixtures`-ийг зөвхөн local/mock API-д ашигла. `users`, `payments`, `orders`, `enrollments`-ийг public vector DB-д бүү индексэл.
4. Үнэ, эрх, төлбөрийн статусыг production-д backend API-аас ав.
5. Энэ ZIP нь ажиллаж буй FastAPI эсвэл LLM биш, demo JSON өгөгдлийн багц.

Шаардлагад бодит курс нэр, үнэ, холбоо барих хаяг, төлбөрийн данс, видео URL байхгүй. Иймээс зохиомол demo утга ашигласан.
