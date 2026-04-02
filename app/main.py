from fastapi import FastAPI
from app.services.embedding import generate_embedding
from app.services.retrieval import retrieve_context

app = FastAPI()

@app.post("/query")
async def query(q: str):
    query_embedding = generate_embedding(q)
    context = retrieve_context(query_embedding)
    answer = generate_answer(q, context)

    return {"answer": answer}