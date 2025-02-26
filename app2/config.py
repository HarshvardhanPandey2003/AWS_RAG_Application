
#config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS credentials (not used in the MVP but kept for later use)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# LLM (Gemini) API key
GEMINI_API = os.getenv("GEMINI_API")

# For MVP, we are not using DynamoDB; however, the variable is still available.
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "ChatSessions")
#