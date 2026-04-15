# kaAI — Knowledge Agent AI

> Portuguese version: [README.md](README.md)

---

## What is this?

kaAI is an internal RAG (Retrieval-Augmented Generation) assistant that answers natural language questions about company documents.

The user asks a question, the system retrieves the most relevant passages from indexed documents, and an AI model generates a contextualized answer — without the user needing to open files or read lengthy documentation.

---

## Stack

| Component | Technology |
|---|---|
| API | FastAPI (Python) |
| LLM | Claude 3 Haiku (AWS Bedrock) |
| Embeddings | Amazon Titan Embed Text v2 (AWS Bedrock) |
| Vector database | Amazon OpenSearch (KNN) |
| Document storage | Amazon S3 |
| Messaging integration | Slack Events API |
| Containerization | Docker / Docker Compose |

---

## How it works (overview)

```
User question (API or Slack)
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
  Send question + passages to LLM (Claude 3 Haiku)
       |
       v
  AI-generated answer
```

1. The user sends a question via REST API or Slack
2. The question is converted into a vector (embedding)
3. The system finds the K most semantically similar passages in OpenSearch using KNN search
4. The retrieved passages + original question are sent to Claude on AWS Bedrock
5. The model generates a response based exclusively on the retrieved context

---

## Ingestion pipeline architecture

Before answering questions, documents must be processed and indexed. This pipeline runs once per document (or whenever content is updated).

### Steps

**1. Loading (`loader.py`)**
Supports two sources:
- Local: reads PDF files from the `docs/` folder
- S3: automatically lists and downloads all PDFs from an S3 bucket

```
docs/file.pdf              →  plain text
s3://bucket/docs/file.pdf  →  plain text
```

---

**2. Chunking (`chunker.py`)**
Splits the text into smaller overlapping blocks to preserve context across boundaries.

```
Full text  →  ["chunk 1...", "chunk 2...", ...]
```

- Default chunk size: **500 characters**
- Overlap between chunks: **50 characters**

---

**3. Embedding (`embedder.py`)**
Each chunk is converted into a high-dimensional numeric vector using the **Amazon Titan Embed Text v2** model via AWS Bedrock.

```
"text passage"  →  [0.023, -0.061, 0.045, ...]  (1024-dimensional vector)
```

---

**4. Indexing (`indexer.py`)**
The original text and its vector are stored in OpenSearch with a `knn_vector` mapping.

```
{ "text": "passage...", "embedding": [...] }  →  OpenSearch (index: knowledge)
```

---

**5. Orchestration (`run_ingestion.py`)**
Coordinates all steps above. Behavior is controlled by environment variables:

```bash
# Local ingestion
python app/ingestion/run_ingestion.py docs/my-file.pdf

# S3 ingestion (all PDFs in the bucket)
INGEST_SOURCE=s3 python app/ingestion/run_ingestion.py
```

---

## Query pipeline architecture

**1. Question embedding** — same function used during ingestion
**2. KNN search** — 5 most semantically similar passages from OpenSearch
**3. Answer generation** — Claude 3 Haiku receives question + context and responds
**4. Response** — JSON via `/query` or a message back in Slack

---

## Slack integration

kaAI answers questions directly in Slack. When the app is mentioned or receives a direct message, the system processes the question through the full RAG pipeline and returns the answer in the channel.

Endpoint configured at `/slack/events`.

---

## Environment variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM credential |
| `AWS_SECRET_ACCESS_KEY` | IAM credential |
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |
| `OPENSEARCH_HOST` | OpenSearch host (`localhost` or AWS domain) |
| `OPENSEARCH_PORT` | Port (default: `9200`) |
| `OPENSEARCH_USE_SSL` | `true` for AWS OpenSearch, `false` for local |
| `S3_BUCKET` | S3 bucket name containing the documents |
| `S3_PREFIX` | Prefix/folder inside the bucket (e.g. `docs/`) |
| `INGEST_SOURCE` | `local` or `s3` |
| `SLACK_SIGNING_SECRET` | Slack App signing secret |

---

## Running locally

### Prerequisites
- Docker and Docker Compose
- AWS credentials with Bedrock and S3 access

### Start everything locally (API + local OpenSearch)

```bash
cp .env.example .env
# fill in .env with your AWS credentials

docker compose up -d
```

The API will be available at `http://localhost:8000`.

### Local ingestion

```bash
# place a PDF in docs/ and run:
python app/ingestion/run_ingestion.py docs/my-file.pdf
```

---

## Deploying on EC2 (AWS)

```bash
# 1. On the EC2 instance (with Docker installed):
git clone https://github.com/your-user/kaAI.git
cd kaAI

# 2. Create .env with production values
cp .env.example .env
# Edit .env: OPENSEARCH_HOST=your-domain.region.es.amazonaws.com
#            OPENSEARCH_USE_SSL=true

# 3. Start only the API (OpenSearch is already on AWS)
docker compose up -d api

# 4. Run document ingestion from S3
INGEST_SOURCE=s3 docker compose run --rm api python app/ingestion/run_ingestion.py
```

> In production, the EC2 instance should have an IAM Role with the following policies:
> `AmazonBedrockFullAccess`, `AmazonS3ReadOnlyAccess`, `AmazonOpenSearchServiceFullAccess`
> In that case, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` can be omitted from `.env`.

---

## Project structure

```
kaAI/
├── app/
│   ├── main.py               # FastAPI — main routes
│   ├── ingestion/
│   │   ├── loader.py         # Loads PDFs (local or S3)
│   │   ├── chunker.py        # Splits text into chunks
│   │   ├── embedder.py       # Generates embeddings via Bedrock
│   │   ├── indexer.py        # Indexes into OpenSearch
│   │   └── run_ingestion.py  # Pipeline orchestrator
│   ├── services/
│   │   ├── embedding.py      # Embedder re-export
│   │   ├── retrieval.py      # KNN search in OpenSearch
│   │   └── llm.py            # Claude call via Bedrock
│   └── slack/
│       └── handler.py        # Slack event receiver
├── docs/                     # PDFs for local ingestion (not committed)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---


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
