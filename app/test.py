from app.ingestion.embedder import generate_embedding
from app.services.retrieval import retrieve_context

query = "What is Jitterbit?"

embedding = generate_embedding(query)

results = retrieve_context(embedding)

print("RESULTS:")
for r in results:
    print("-", r)