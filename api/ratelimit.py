import hashlib
import logging

from fastapi import HTTPException, Request

import config
from rag import db

log = logging.getLogger("chatbot")


def client_ip(request: Request) -> str:
    ip = request.headers.get("x-real-ip", "").strip()
    if not ip:
        forwarded = request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip() if forwarded else ""
    if not ip and request.client:
        ip = request.client.host
    return ip or "unknown"


def _hit(bucket: str, window_seconds: int, limit: int) -> bool:
    res = db().rpc(
        "kb_rate_limit_hit",
        {"p_bucket": bucket, "p_window_seconds": window_seconds, "p_limit": limit},
    ).execute()
    return bool(res.data)


def enforce_rate_limit(request: Request) -> None:
    raw = (config.RATE_LIMIT_SALT + client_ip(request)).encode()
    ip_hash = hashlib.sha256(raw).hexdigest()[:16]

    # (bucket, цонхны секунд, хязгаар, Retry-After, мессеж)
    checks = [
        (f"ip-min:{ip_hash}", 60, config.RATE_LIMIT_PER_MIN, 60,
         "Хэт олон хүсэлт илгээлээ. Түр хүлээгээд дахин оролдоно уу."),
        (f"ip-day:{ip_hash}", 86400, config.RATE_LIMIT_PER_DAY, 3600,
         "Өнөөдрийн хязгаарт хүрлээ. Маргааш дахин оролдоно уу."),
        ("global-day", 86400, config.RATE_LIMIT_GLOBAL_PER_DAY, 3600,
         "Үйлчилгээ түр ачаалалтай байна. Дараа дахин оролдоно уу."),
    ]

    try:
        for bucket, window, limit, retry_after, message in checks:
            if not _hit(bucket, window, limit):
                raise HTTPException(
                    status_code=429,
                    detail=message,
                    headers={"Retry-After": str(retry_after)},
                )
    except HTTPException:
        raise
    except Exception:
        log.exception("rate limit алдаа")
        raise HTTPException(status_code=503, detail="Түр алдаа гарлаа. Дахин оролдоно уу.")