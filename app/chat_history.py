# chat_history.py
import os
import boto3
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(DYNAMODB_TABLE)

def create_chat_session(session_id, file_name, embeddings_key=None):
    """
    Create a new chat session entry in DynamoDB.
    The embeddings_key parameter is optional.
    """
    session_item = {
        "session_id": session_id,
        "file_name": file_name,
        "embeddings_key": embeddings_key,
        "chat_history": [],
        "created_at": datetime.utcnow().isoformat()
    }
    table.put_item(Item=session_item)

def update_chat_history(session_id: str, role: str, message: str) -> None:
    """Appends a new message to the chat history."""
    new_message = {
        "role": role,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    table.update_item(
        Key={"session_id": session_id},
        UpdateExpression="SET chat_history = list_append(if_not_exists(chat_history, :empty), :msg)",
        ExpressionAttributeValues={
            ":msg": [new_message],
            ":empty": []
        }
    )

def fetch_chat_history(session_id: str) -> List[Dict]:
    """Fetches chat history for a given session."""
    response = table.get_item(Key={"session_id": session_id})
    item = response.get("Item")
    if item and "chat_history" in item:
        return item["chat_history"]
    return []

def fetch_recent_sessions(days: int = 7) -> List[Dict]:
    """
    Fetches recent chat sessions within the specified number of days.
    Returns a list of sessions with their basic info.
    """
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    response = table.scan(
        FilterExpression="created_at >= :cutoff",
        ExpressionAttributeValues={":cutoff": cutoff_date}
    )
    
    return response.get("Items", [])