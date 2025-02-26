import boto3
from boto3.dynamodb.conditions import Key
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

class ChatHistoryManager:
    def __init__(self):
        self.table_name = os.getenv('DYNAMODB_TABLE')
        if not self.table_name:
            raise ValueError("DYNAMODB_TABLE_NAME environment variable is not set")

        try:
            self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            self.table = self.dynamodb.Table(self.table_name)
            self.table.table_status
        except ClientError as e:
            raise Exception(f"Failed to initialize DynamoDB connection: {str(e)}")

    def _format_message_for_dynamodb(self, message: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Format a single message for DynamoDB storage"""
        return {
            "M": {
                "message": {"S": message.get('content', '')},
                "role": {"S": message.get('role', '')},
                "timestamp": {"S": message.get('timestamp', datetime.now().isoformat())}
            }
        }

    def _format_messages_for_dynamodb(self, messages: List[Dict[str, str]]) -> List[Dict[str, Dict[str, str]]]:
        """Format all messages for DynamoDB storage"""
        return [self._format_message_for_dynamodb(msg) for msg in messages]

    def _format_message_from_dynamodb(self, dynamo_message: Dict) -> Dict[str, str]:
        """Convert DynamoDB message format back to application format"""
        if 'M' in dynamo_message:
            msg_data = dynamo_message['M']
            return {
                'content': msg_data.get('message', {}).get('S', ''),
                'role': msg_data.get('role', {}).get('S', ''),
                'timestamp': msg_data.get('timestamp', {}).get('S', '')
            }
        return {}

    def save_chat_history(self, session_id: str, s3_key: str, messages: List[Dict[str, str]]) -> bool:
        """Save chat history to DynamoDB with the specified format"""
        try:
            if not isinstance(messages, list):
                raise ValueError("Messages must be a list")

            # Format messages for DynamoDB
            formatted_messages = self._format_messages_for_dynamodb(messages)
            
            # Create the DynamoDB item
            item = {
                'session_id': session_id,
                's3_key': s3_key,
                'messages': formatted_messages,
                'last_updated': datetime.now().isoformat(),
                'ttl': int((datetime.now().timestamp() + (30 * 24 * 60 * 60)))
            }
            
            # Save to DynamoDB
            self.table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving chat history: {str(e)}")
            return False

    def get_chat_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve and format chat history from DynamoDB"""
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            if 'Item' not in response:
                return None

            item = response['Item']
            
            # Convert messages back to application format
            if 'messages' in item:
                item['messages'] = [
                    self._format_message_from_dynamodb(msg)
                    for msg in item['messages']
                ]
            
            return item

        except Exception as e:
            print(f"Error retrieving chat history: {str(e)}")
            return None

    def list_sessions(self, limit: int = 10) -> List[Dict[str, str]]:
        """List available chat sessions"""
        try:
            response = self.table.scan(
                ProjectionExpression='session_id, last_updated',
                Limit=limit,
                FilterExpression=Key('ttl').gt(int(datetime.now().timestamp()))
            )
            
            sessions = response.get('Items', [])
            sessions.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
            return sessions

        except Exception as e:
            print(f"Error listing sessions: {str(e)}")
            return []