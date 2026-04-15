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

def retrieve_context(query_embedding, k=5):

    search_body = {
        "size": k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": k
                }
            }
        }
    }

    response = client.search(index=INDEX_NAME, body=search_body)

    hits = response["hits"]["hits"]

    return [hit["_source"]["text"] for hit in hits]