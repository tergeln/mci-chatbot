import time

from google import genai
from google.genai import types

from settings import require

MODEL = "gemini-embedding-001"
DIMENSIONS = 1536          # kb_chunks.embedding vector(1536)-тай таарах ёстой
BATCH_SIZE = 50

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=require("GEMINI_API_KEY"))
    return _client


def _embed(texts: list[str], task_type: str) -> list[list[float]]:
    for attempt in range(6):
        try:
            result = _get_client().models.embed_content(
                model=MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=DIMENSIONS,
                ),
            )
            vectors = [e.values for e in result.embeddings]
            if len(vectors) != len(texts):
                raise RuntimeError("Embedding-ийн тоо оролтын тоотой таарсангүй")
            return vectors
        except Exception as e:
            message = str(e)
            retryable = any(
                key in message
                for key in ("429", "RESOURCE_EXHAUSTED", "500", "503", "UNAVAILABLE")
            )
            if not retryable or attempt == 5:
                raise
            wait = 5 * (2 ** attempt)   # 5, 10, 20, 40, 80 секунд
            print(f"  … түр алдаа, {wait} секунд хүлээгээд дахин оролдоно")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def embed_documents(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        vectors.extend(_embed(texts[i:i + BATCH_SIZE], "RETRIEVAL_DOCUMENT"))
    return vectors


def embed_query(text: str) -> list[float]:
    return _embed([text], "RETRIEVAL_QUERY")[0]