import os
import boto3
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
if not DYNAMODB_TABLE:
    raise ValueError("DYNAMODB_TABLE environment variable is not set.")

print(f"Using DynamoDB table: {DYNAMODB_TABLE}")
print(f"AWS Region: us-east-1")

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(DYNAMODB_TABLE)


# Verify AWS credentials and table access
try:
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print(f"AWS Identity: {identity}")
    
    table_desc = dynamodb.meta.client.describe_table(TableName=DYNAMODB_TABLE)
    print(f"Table exists and is accessible")
except Exception as e:
    print(f"Error with AWS setup: {e}")
    raise

def save_chat_to_dynamodb(session_id, messages):
    """
    Saves a chat session with messages to DynamoDB.
    """
    try:
        # Prepare the item to save
        item = {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "embedding_key": "direct_vectorstore",
            "chat_history": messages
        }
        
        print(f"Attempting to save item: {json.dumps(item, indent=2)}")  # Debug print
        # Save the item to DynamoDB
        table.put_item(Item=item)
        return True
    except Exception as e:
        print(f"Error saving to DynamoDB: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def fetch_chat_from_dynamodb(session_id):
    """
    Fetches a chat session from DynamoDB.
    """
    try:
        # Fetch the item from DynamoDB
        response = table.get_item(Key={"session_id": session_id})
        item = response.get("Item")
        if item:
            return item.get("chat_history", [])
        else:
            print("Session not found in DynamoDB.")
            return []
    except Exception as e:
        print(f"Error fetching from DynamoDB: {str(e)}")
        return []
def main():
    # Verify AWS identity
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print(f"AWS Identity: {json.dumps(identity, indent=2)}")
    
    # Check table structure
    # Add this right after initializing the table
def verify_table_structure():
    try:
        response = dynamodb.meta.client.describe_table(TableName=DYNAMODB_TABLE)
        print("\nTable Structure:")
        print(f"Table Name: {response['Table']['TableName']}")
        print(f"Primary Key: {response['Table']['KeySchema']}")
        print(f"Status: {response['Table']['TableStatus']}")
        return response
    except Exception as e:
        print(f"Error describing table: {e}")
        return None

# Add this to your main() before any operations
verify_table_structure()
    
    # Check permissions
def check_permissions():
    try:
        # Test put_item permission
        test_item = {
            "session_id": "test-permission",
            "test_data": "test"
        }
        table.put_item(Item=test_item)
        print("Put item permission: ✓")
        
        # Test get_item permission
        table.get_item(Key={"session_id": "test-permission"})
        print("Get item permission: ✓")
        
        # Test scan permission
        table.scan(Limit=1)
        print("Scan permission: ✓")
        
        # Clean up test item
        table.delete_item(Key={"session_id": "test-permission"})
        print("Delete item permission: ✓")
        
    except Exception as e:
        print(f"Permission check failed: {e}")

# Add this to your main() at the start
    check_permissions()
    
    # Your existing test code
    test_messages = [
        {"role": "user", "message": "Hello!"},
        {"role": "assistant", "message": "Hello, how can I help you?"}
    ]
    
    session_id = str(uuid.uuid4())
    print(f"\nGenerated session ID: {session_id}")
    
    if save_chat_to_dynamodb(session_id, test_messages):
        print("Chat saved successfully.")
    else:
        print("Failed to save chat.")
        return
    
    # Add delay for consistency
    import time
    time.sleep(2)
    
    fetched_messages = fetch_chat_from_dynamodb(session_id)
    print("\nFetched Chat History:")
    for msg in fetched_messages:
        print(f"{msg['role'].capitalize()}: {msg['message']}")
    
    print("\nScanning entire table...")
    def list_all_items():
        try:
            response = table.scan()
            items = response.get('Items', [])
            print(f"\nTotal items in table: {len(items)}")
            for item in items:
                print(f"\nItem: {json.dumps(item, indent=2)}")
            return items
        except Exception as e:
            print(f"Error scanning table: {e}")
            return []

    # Add this to your main() function after the fetch_chat operation:
    print("\nScanning entire table...")
    list_all_items()

if __name__ == "__main__":
        main()