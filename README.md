# kaAI — Knowledge Agent AI

> Versao em ingles: [README-en.md](README-en.md)

---

## O que e isso?

O kaAI e um assistente interno baseado em RAG (Retrieval-Augmented Generation) que responde perguntas em linguagem natural sobre documentos internos da empresa.

O usuario faz uma pergunta, o sistema busca os trechos mais relevantes nos documentos indexados e um modelo de IA gera uma resposta contextualizada — sem que o usuario precise abrir arquivos ou ler documentacoes extensas.

---

## Como funciona (visao geral)

```
Pergunta do usuario
       |
       v
  Gerar embedding da pergunta
       |
       v
  Busca KNN no OpenSearch  <──────────────────────┐
       |                                           |
       v                                    Pipeline de Ingestao
  Recuperar trechos relevantes              (roda separadamente)
       |
       v
  Enviar pergunta + trechos para o LLM
       |
       v
  Resposta gerada pelo modelo
```

1. O usuario envia uma pergunta via API
2. A pergunta e transformada em vetor (embedding)
3. O sistema busca os K trechos mais similares no OpenSearch usando busca vetorial (KNN)
4. Os trechos recuperados + a pergunta original sao enviados ao modelo Claude no Bedrock
5. O modelo gera uma resposta baseada exclusivamente no contexto recuperado

---

## Arquitetura do pipeline de ingestao

Antes de responder perguntas, os documentos precisam ser processados e indexados. Esse pipeline roda uma unica vez por documento (ou quando o conteudo e atualizado).

### Etapas

**1. Carregamento (`loader.py`)**
Le o arquivo PDF da pasta `docs/` e extrai o texto bruto de todas as paginas usando `pypdf`.

```
docs/arquivo.pdf  →  texto puro (string)
```

---

**2. Chunking (`chunker.py`)**
Divide o texto em blocos menores com sobreposicao para preservar contexto entre trechos.

```
Texto completo  →  ["trecho 1...", "trecho 2...", ...]
```

- Tamanho padrao do chunk: **500 caracteres**
- Sobreposicao entre chunks: **50 caracteres**

A sobreposicao garante que frases importantes que caem na fronteira entre dois chunks nao sejam perdidas.

---

**3. Embedding (`embedder.py`)**
Cada chunk e convertido em um vetor numerico de alta dimensionalidade usando o modelo **Amazon Titan Embed Text v2** via AWS Bedrock.

```
"trecho de texto"  →  [0.023, -0.061, 0.045, ...]  (vetor de 1024 dimensoes)
```

Vetores semelhantes representam textos semanticamente proximos, o que permite busca por significado em vez de palavras-chave.

---

**4. Indexacao (`indexer.py`)**
O texto original e seu vetor sao armazenados no OpenSearch com mapeamento `knn_vector`, que habilita a busca por vizinhos mais proximos (KNN).

```
{ "text": "trecho...", "embedding": [...] }  →  OpenSearch (indice: knowledge)
```

O indice e criado automaticamente na primeira execucao com o mapeamento correto.

---

**5. Orquestracao (`run_ingestion.py`)**
Coordena todas as etapas acima em sequencia para um arquivo PDF informado.

```bash
python app/ingestion/run_ingestion.py
```

---

## Arquitetura do pipeline de consulta (query)

Quando o usuario faz uma pergunta via API:

**1. Embedding da pergunta**
A pergunta e convertida em vetor usando o mesmo modelo de embedding da ingestao.

**2. Busca KNN**
O vetor e comparado contra todos os vetores indexados no OpenSearch. Os 5 trechos mais proximos semanticamente sao retornados (`retrieval.py`).

**3. Geracao de resposta**
Os trechos recuperados formam o contexto que e enviado junto com a pergunta ao modelo **Claude 3 Haiku** no AWS Bedrock (`llm.py`). O modelo responde baseado exclusivamente nesse contexto.

**4. Retorno**
A resposta e devolvida via JSON pelo endpoint `/query`.

---

## Tecnologias utilizadas

| Componente | Para que serve |
|---|---|
| FastAPI | Framework da API REST |
| pypdf | Leitura e extracao de texto de PDFs |
| AWS Bedrock (Titan Embed v2) | Geracao de embeddings vetoriais |
| AWS Bedrock (Claude 3 Haiku) | Geracao de respostas em linguagem natural |
| OpenSearch | Banco de dados vetorial com suporte a busca KNN |
| Docker Compose | Execucao local do OpenSearch |
| python-dotenv | Gerenciamento de variaveis de ambiente |

---

## Estrutura do projeto

```
kaAI/
├── app/
│   ├── main.py                  # Endpoint FastAPI (/query)
│   ├── ingestion/
│   │   ├── run_ingestion.py     # Orquestrador do pipeline de ingestao
│   │   ├── loader.py            # Leitura de PDFs
│   │   ├── chunker.py           # Divisao do texto em chunks
│   │   ├── embedder.py          # Geracao de embeddings (Bedrock)
│   │   └── indexer.py           # Indexacao no OpenSearch
│   └── services/
│       ├── embedding.py         # Embedding para queries em tempo real
│       ├── retrieval.py         # Busca KNN no OpenSearch
│       └── llm.py               # Geracao de respostas (Bedrock / Claude)
├── docs/                        # PDFs a serem ingeridos
├── docker-compose.yml           # OpenSearch local
├── .env                         # Variaveis de ambiente (nao versionar)
└── requirements.txt
```

---

## Configuracao

### Pre-requisitos

- Python 3.10+
- Docker Desktop com integracao WSL2 ativada (Settings > Resources > WSL Integration)
- Credenciais AWS com acesso ao Bedrock na regiao `sa-east-1`

### 1. Instalar as dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar as variaveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
AWS_ACCESS_KEY_ID=sua_chave
AWS_SECRET_ACCESS_KEY=sua_chave_secreta
AWS_REGION=sa-east-1
```

### 3. Subir o OpenSearch

```bash
docker compose up -d
```

Aguarde o servico inicializar e verifique:

```bash
curl http://localhost:9200
```

### 4. Executar o pipeline de ingestao

Coloque os PDFs na pasta `docs/` e execute:

```bash
python app/ingestion/run_ingestion.py
```

### 5. Iniciar a API

```bash
uvicorn app.main:app --reload
```

---

## Testando

### Testar a ingestao

```bash
python app/ingestion/run_ingestion.py
# Saida esperada: Ingestion complete
```

### Testar a API

```bash
curl -X POST "http://localhost:8000/query?q=Qual+e+a+politica+de+ferias?"
```

Resposta esperada:

```json
{
  "answer": "De acordo com os documentos internos, ..."
}
```

### Verificar documentos indexados no OpenSearch

```bash
curl http://localhost:9200/knowledge/_count
```

---

## Melhorias previstas

- Suporte a multiplos formatos de documento (DOCX, TXT, HTML)
- Reindexacao automatica ao detectar novos arquivos em S3
- Mecanismo de feedback para avaliar a qualidade das respostas
- Melhoria no ranqueamento com re-ranking pos-recuperacao
- Interface via Slack com botoes e componentes interativos
- Autenticacao na API
- Deploy em AWS EC2 com configuracao de producao