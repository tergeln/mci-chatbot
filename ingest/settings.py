import os
from pathlib import Path

from dotenv import load_dotenv

# ingest/ → нэг түвшин дээш = төслийн root
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} олдсонгүй. {ROOT / '.env'} файлаа шалгана уу.")
    return value