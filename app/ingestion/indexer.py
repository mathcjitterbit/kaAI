import os
from opensearchpy import OpenSearch
from dotenv import load_dotenv

load_dotenv()

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
OPENSEARCH_USE_SSL = os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    use_ssl=OPENSEARCH_USE_SSL,
    verify_certs=OPENSEARCH_USE_SSL,
)

INDEX_NAME = "knowledge"

INDEX_MAPPING = {
    "settings": {
        "index": {
            "knn": True
        }
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 1024
            }
        }
    }
}

def create_index_if_not_exists():
    if not client.indices.exists(index=INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)

def index_document(text, embedding):
    create_index_if_not_exists()
    doc = {
        "text": text,
        "embedding": embedding
    }
    client.index(index=INDEX_NAME, body=doc)