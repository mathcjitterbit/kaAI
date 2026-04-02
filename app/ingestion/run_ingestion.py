import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.ingestion.loader import load_pdf
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import generate_embedding
from app.ingestion.indexer import index_document

def run(path):
    text = load_pdf(path)
    chunks = chunk_text(text)

    for chunk in chunks:
        if not chunk.strip():
            continue
        embedding = generate_embedding(chunk)
        index_document(chunk, embedding)

    print("Ingestion complete")

if __name__ == "__main__":
    run("docs/test.pdf")