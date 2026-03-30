# Knowledge Agent

> Versao em ingles: [README-en.md](README-en.md)

---

## O que e isso?

Este projeto e um assistente interno que responde perguntas em linguagem natural direto pelo Slack.

Ele pesquisa nos documentos internos da empresa para encontrar o conteudo mais relevante e usa um modelo de inteligencia artificial para gerar uma resposta clara e contextualizada, sem que o usuario precise buscar arquivos manualmente ou ler documentacoes longas.

---

## Como funciona

1. O usuario envia uma pergunta no Slack
2. O sistema busca nos documentos internos os trechos mais relevantes
3. O modelo de IA le esses trechos e gera uma resposta
4. A resposta e devolvida para o usuario no proprio Slack

---

## Tecnologias utilizadas

| Componente | Para que serve |
|---|---|
| Slack API | Interface onde o usuario faz perguntas e recebe respostas |
| AWS S3 | Armazenamento dos documentos internos |
| AWS OpenSearch | Banco de dados vetorial, permite busca semantica nos documentos |
| AWS Bedrock | Modelo de IA responsavel por gerar as respostas |
| AWS EC2 | Servidor onde a aplicacao fica hospedada |

---

## Estrutura do projeto

```
/app
  /api          - Pontos de entrada (rotas e endpoints)
  /services     - Logica de negocio
  /retrieval    - Busca nos documentos
  /embedding    - Vetorizacao dos textos
  /llm          - Comunicacao com o modelo de IA
/ingestion      - Pipeline de importacao e processamento de documentos
/models         - Estruturas de dados
/utils          - Utilitarios compartilhados
```

---

## Configuracao em Python

> Os passos abaixo sao especificos para a implementacao em Python.

### 1. Instalar as dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar as variaveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variaveis:

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
OPENSEARCH_ENDPOINT=
S3_BUCKET_NAME=
BEDROCK_MODEL_ID=
```

### 3. Iniciar a API

```bash
uvicorn app.main:app --reload
```

### 4. Executar o pipeline de ingestao de documentos

Esta etapa processa e indexa os documentos que o assistente usara para responder as perguntas.

```bash
python ingestion/run_ingestion.py
```

---

## Melhorias previstas

- Mecanismo de feedback para avaliar a qualidade das respostas
- Melhoria no ranqueamento dos documentos na busca
- Interface mais rica no Slack com botoes e componentes interativos