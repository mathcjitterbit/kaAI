from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
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