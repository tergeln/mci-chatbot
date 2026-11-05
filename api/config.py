import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")  


def require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} тохируулагдаагүй байна")
    return value


EMBED_MODEL = "gemini-embedding-001"   # ingest-тэй яг ижил байх ёстой
EMBED_DIMS = 1536

GEN_MODEL = os.getenv("GEN_MODEL", "gemini-3.5-flash-lite")
GEN_FALLBACK_MODEL = os.getenv("GEN_FALLBACK_MODEL", "gemini-3.8-flash")
MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", "0.60"))
TOP_K = int(os.getenv("TOP_K", "6"))
DEBUG_RETRIEVAL = os.getenv("DEBUG_RETRIEVAL") == "1"
CONTACT_TEXT = os.getenv("CONTACT_TEXT", "").strip()
CONTACT_TEXT_EN = os.getenv("CONTACT_TEXT_EN", "").strip() or "For details, please contact magiccodeai@gmail.com."

ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")
    if o.strip()
]


RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "10"))
RATE_LIMIT_PER_DAY = int(os.getenv("RATE_LIMIT_PER_DAY", "100"))
RATE_LIMIT_GLOBAL_PER_DAY = int(os.getenv("RATE_LIMIT_GLOBAL_PER_DAY", "3000"))
RATE_LIMIT_SALT = os.getenv("RATE_LIMIT_SALT", "")