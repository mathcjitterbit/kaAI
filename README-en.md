# Knowledge Agent

## What is this?

This project is an internal assistant that answers questions in natural language via Slack.

It searches through internal documents to find relevant content and uses an AI model to generate a clear, contextualized response, without the user needing to manually search for files or read long documentation.

---

## How it works

1. The user sends a question in Slack
2. The system searches the document base for the most relevant content
3. The AI model reads that content and generates a response
4. The response is delivered back in Slack

---

## Technology used

| Component | Purpose |
|---|---|
| Slack API | Interface where the user sends questions and receives answers |
| AWS S3 | Storage for internal documents |
| AWS OpenSearch | Vector database, enables semantic search across documents |
| AWS Bedrock | AI model used to generate responses |
| AWS EC2 | Server where the application runs |

---

## Project structure

```
/app
  /api          - Entry points (routes and endpoints)
  /services     - Business logic
  /retrieval    - Document search
  /embedding    - Text vectorization
  /llm          - Communication with the AI model
/ingestion      - Pipeline for importing and processing documents
/models         - Data structures
/utils          - Shared utilities
```

---

## Python setup

> The steps below are specific to the Python implementation.

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root with the following variables:

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
OPENSEARCH_ENDPOINT=
S3_BUCKET_NAME=
BEDROCK_MODEL_ID=
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

### 4. Run the document ingestion pipeline

This step processes and indexes the documents that the assistant will use to answer questions.

```bash
python ingestion/run_ingestion.py
```

---

## Planned improvements

- Feedback mechanism to rate answer quality
- Improved document ranking in search results
- Richer Slack interface with buttons and interactive components
