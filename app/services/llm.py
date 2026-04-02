import os
import boto3
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("AWS_REGION")

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=REGION,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

model_id = "anthropic.claude-3-haiku-20240307-v1:0"
def generate_answer(question, context):

    prompt = f"""
You are a helpful assistant. Consider the the following context as true and use it to answer the question at the end. If you don't know the answer, say you don't know.

Context:
{context}

Question:
{question}
"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 300,
        "temperature": 0.3
    }

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]