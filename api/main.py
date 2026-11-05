import logging
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
import rag
from ratelimit import enforce_rate_limit

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("chatbot")

app = FastAPI(title="Business Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=1000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    history: list[Message] = Field(default_factory=list, max_length=6)
    business: Literal["course", "web", "merch"] | None = None
    lang: Literal["mn", "en"] = "mn"


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    enforce_rate_limit(request)   # try-аас ГАДНА: 429 алдааг 502 болгож хуурахгүй

    question = req.message.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Асуулт хоосон байна")
    try:
        return rag.answer_question(question, req.history, req.business, req.lang)
    except Exception:
        log.exception("chat алдаа")
        raise HTTPException(
            status_code=502,
            detail="Түр алдаа гарлаа. Дахин оролдоно уу.",
        )