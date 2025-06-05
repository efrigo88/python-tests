"""Script to list AWS Bedrock models that support on-demand inference."""

import os

import boto3
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    "bedrock",
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

response = client.list_foundation_models()

# print(response)

for model in response["modelSummaries"]:
    if "ON_DEMAND" in model.get("inferenceTypesSupported", []):
        print(model["modelId"])
