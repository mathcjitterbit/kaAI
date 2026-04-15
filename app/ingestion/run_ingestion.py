import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.ingestion.loader import load_pdf, load_pdf_from_s3, list_pdfs_in_s3
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import generate_embedding
from app.ingestion.indexer import index_document


def ingest_text(text: str, source_label: str):
    chunks = chunk_text(text)
    indexed = 0

    for chunk in chunks:
        if not chunk.strip():
            continue
        embedding = generate_embedding(chunk)
        index_document(chunk, embedding)
        indexed += 1

    print(f"[{source_label}] Ingested {indexed} chunks")


def run_local(path: str):
    text = load_pdf(path)
    ingest_text(text, path)
    print("Ingestion complete")


def run_s3(bucket: str, prefix: str = ""):
    keys = list_pdfs_in_s3(bucket, prefix)

    if not keys:
        print(f"No PDF files found in s3://{bucket}/{prefix}")
        return

    for key in keys:
        print(f"Processing s3://{bucket}/{key}...")
        text = load_pdf_from_s3(bucket, key)
        ingest_text(text, key)

    print("S3 ingestion complete")


if __name__ == "__main__":
    source = os.getenv("INGEST_SOURCE", "local")

    if source == "s3":
        bucket = os.getenv("S3_BUCKET")
        prefix = os.getenv("S3_PREFIX", "")

        if not bucket:
            print("Error: S3_BUCKET env var is required when INGEST_SOURCE=s3")
            sys.exit(1)

        run_s3(bucket, prefix)
    else:
        path = sys.argv[1] if len(sys.argv) > 1 else "docs/test.pdf"
        run_local(path)
