from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
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