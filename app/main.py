from fastapi import FastAPI, Request
from app.services.embedding import generate_embedding
from app.services.retrieval import retrieve_context
from app.services.llm import generate_answer
from app.slack.handler import handle_slack_event

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/query")
async def query(q: str):
    query_embedding = generate_embedding(q)
    context = retrieve_context(query_embedding)
    answer = generate_answer(q, context)

    return {"answer": answer}

@app.post("/slack/events")
async def slack_events(request: Request):
    return await handle_slack_event(request)
