import boto3
import json
from dotenv import load_dotenv
import os

load_dotenv()


ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("AWS_REGION")

client = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

MODEL_ID = "amazon.titan-embed-text-v2:0"

def generate_embedding(text: str):
    body = {
        "inputText": text
    }

    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    return result["embedding"]