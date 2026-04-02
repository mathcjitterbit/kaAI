# kaAI — Knowledge Agent AI

> Portuguese version: [README.md](README.md)

---

## What is this?

kaAI is an internal RAG (Retrieval-Augmented Generation) assistant that answers natural language questions about company documents.

The user asks a question, the system retrieves the most relevant passages from indexed documents, and an AI model generates a contextualized answer — without the user needing to open files or read lengthy documentation.

---

## How it works (overview)

```
User question
       |
       v
  Generate question embedding
       |
       v
  KNN search in OpenSearch  <──────────────────────┐
       |                                            |
       v                                    Ingestion Pipeline
  Retrieve relevant passages               (runs separately)
       |
       v
  Send question + passages to LLM
       |
       v
  AI-generated answer
```

1. The user sends a question via the API
2. The question is converted into a vector (embedding)
3. The system finds the K most semantically similar passages in OpenSearch using KNN search
4. The retrieved passages + original question are sent to Claude on AWS Bedrock
5. The model generates a response based exclusively on the retrieved context

---

## Ingestion pipeline architecture

Before answering questions, documents must be processed and indexed. This pipeline runs once per document (or whenever content is updated).

### Steps

**1. Loading (`loader.py`)**
Reads the PDF file from the `docs/` folder and extracts raw text from all pages using `pypdf`.

```
docs/file.pdf  →  plain text (string)
```

---

**2. Chunking (`chunker.py`)**
Splits the text into smaller overlapping blocks to preserve context across boundaries.

```
Full text  →  ["chunk 1...", "chunk 2...", ...]
```

- Default chunk size: **500 characters**
- Overlap between chunks: **50 characters**

Overlap ensures that important sentences near chunk boundaries are not lost.

---

**3. Embedding (`embedder.py`)**
Each chunk is converted into a high-dimensional numeric vector using the **Amazon Titan Embed Text v2** model via AWS Bedrock.

```
"text passage"  →  [0.023, -0.061, 0.045, ...]  (1024-dimensional vector)
```

Similar vectors represent semantically similar text, enabling search by meaning rather than keywords.

---

**4. Indexing (`indexer.py`)**
The original text and its vector are stored in OpenSearch with a `knn_vector` mapping, enabling K-nearest neighbor search.

```
{ "text": "passage...", "embedding": [...] }  →  OpenSearch (index: knowledge)
```

The index is automatically created on first run with the correct mapping.

---

**5. Orchestration (`run_ingestion.py`)**
Coordinates all the steps above in sequence for a given PDF file.

```bash
python app/ingestion/run_ingestion.py
```

---

## Query pipeline architecture

When a user asks a question via the API:

**1. Question embedding**
The question is converted into a vector using the same embedding model used during ingestion.

**2. KNN search**
The vector is compared against all indexed vectors in OpenSearch. The 5 most semantically similar passages are returned (`retrieval.py`).

**3. Answer generation**
The retrieved passages form the context sent alongside the question to **Claude 3 Haiku** on AWS Bedrock (`llm.py`). The model answers based exclusively on that context.

**4. Response**
The answer is returned as JSON from the `/query` endpoint.

---

## Technologies used

| Component | Purpose |
|---|---|
| FastAPI | REST API framework |
| pypdf | PDF reading and text extraction |
| AWS Bedrock (Titan Embed v2) | Vector embedding generation |
| AWS Bedrock (Claude 3 Haiku) | Natural language answer generation |
| OpenSearch | Vector database with KNN search support |
| Docker Compose | Local OpenSearch execution |
| python-dotenv | Environment variable management |

---

## Project structure

```
kaAI/
├── app/
│   ├── main.py                  # FastAPI endpoint (/query)
│   ├── ingestion/
│   │   ├── run_ingestion.py     # Ingestion pipeline orchestrator
│   │   ├── loader.py            # PDF reading
│   │   ├── chunker.py           # Text chunking
│   │   ├── embedder.py          # Embedding generation (Bedrock)
│   │   └── indexer.py           # OpenSearch indexing
│   └── services/
│       ├── embedding.py         # Embedding for real-time queries
│       ├── retrieval.py         # KNN search in OpenSearch
│       └── llm.py               # Answer generation (Bedrock / Claude)
├── docs/                        # PDFs to be ingested
├── docker-compose.yml           # Local OpenSearch
├── .env                         # Environment variables (do not commit)
└── requirements.txt
```

---

## Setup

### Prerequisites

- Python 3.10+
- Docker Desktop with WSL2 integration enabled (Settings > Resources > WSL Integration)
- AWS credentials with Bedrock access in region `sa-east-1`

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=sa-east-1
```

### 3. Start OpenSearch

```bash
docker compose up -d
```

Wait for the service to initialize and verify:

```bash
curl http://localhost:9200
```

### 4. Run the ingestion pipeline

Place PDFs in the `docs/` folder and run:

```bash
python app/ingestion/run_ingestion.py
```

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

---

## Testing

### Test ingestion

```bash
python app/ingestion/run_ingestion.py
# Expected output: Ingestion complete
```

### Test the API

```bash
curl -X POST "http://localhost:8000/query?q=What+is+the+vacation+policy?"
```

Expected response:

```json
{
  "answer": "According to the internal documents, ..."
}
```

### Check indexed documents in OpenSearch

```bash
curl http://localhost:9200/knowledge/_count
```

---

## Planned improvements

- Support for multiple document formats (DOCX, TXT, HTML)
- Automatic re-indexing when new files are detected in S3
- Feedback mechanism to rate answer quality
- Improved ranking with post-retrieval re-ranking
- Slack interface with buttons and interactive components
- API authentication
- AWS EC2 deployment with production configuration
