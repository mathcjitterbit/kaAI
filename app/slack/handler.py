import os
import hmac
import hashlib
import time
from fastapi import Request, HTTPException
from dotenv import load_dotenv

from app.services.embedding import generate_embedding
from app.services.retrieval import retrieve_context
from app.services.llm import generate_answer

load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")


def verify_slack_signature(request_body: bytes, timestamp: str, signature: str) -> bool:
    """Verify Slack request authenticity using signing secret."""
    if abs(time.time() - float(timestamp)) > 300:
        return False

    base_string = f"v0:{timestamp}:{request_body.decode('utf-8')}"
    expected = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


async def handle_slack_event(request: Request) -> dict:
    body_bytes = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    if SLACK_SIGNING_SECRET and not verify_slack_signature(body_bytes, timestamp, signature):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")

    payload = await request.json()

    # Slack URL verification challenge (required on first setup)
    if payload.get("type") == "url_verification":
        return {"challenge": payload["challenge"]}

    event = payload.get("event", {})

    # Only respond to direct messages or app mentions, not to bot messages
    if event.get("type") not in ("message", "app_mention"):
        return {"ok": True}

    if event.get("bot_id"):
        return {"ok": True}

    question = event.get("text", "").strip()
    channel = event.get("channel")

    if not question or not channel:
        return {"ok": True}

    answer = _ask(question)
    return {"channel": channel, "answer": answer}


def _ask(question: str) -> str:
    embedding = generate_embedding(question)
    context = retrieve_context(embedding)
    return generate_answer(question, context)


