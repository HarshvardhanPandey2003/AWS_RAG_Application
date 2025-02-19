import os
import pickle
import uuid
import tempfile
import boto3
from langchain.embeddings import BedrockEmbeddings

# Initialize S3 client using boto3
s3_client = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Initialize Bedrock client and embeddings wrapper
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_client)

def get_unique_id():
    """Generates a unique session ID."""
    return str(uuid.uuid4())

def generate_embeddings(text_chunks):
    """Generate embeddings for text chunks using Bedrock."""
    embeddings = bedrock_embeddings.embed_documents(text_chunks)
    return embeddings
def store_embeddings(chunks, embeddings, session_id):
    """
    Store embeddings (and chunks) in S3 using the session_id as part of the key.
    """
    filename = f"{session_id}.pkl"
    file_path = os.path.join(tempfile.gettempdir(), filename)
    
    # Package the data including both embeddings and chunks
    data_package = {
        'embeddings': embeddings,
        'chunks': chunks,
        'session_id': session_id
    }
    
    with open(file_path, "wb") as f:
        pickle.dump(data_package, f)
    
    s3_key = f"embeddings/{filename}"
    s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
    os.remove(file_path)  # Clean up temp file
    return s3_key

def load_embeddings_from_s3(session_id):
    """
    Load embeddings from S3 using the session_id.
    Returns the loaded dictionary containing embeddings, chunks, and metadata.
    """
    try:
        s3_key = f"embeddings/{session_id}.pkl"
        file_path = os.path.join(tempfile.gettempdir(), f"{session_id}.pkl")
        s3_client.download_file(BUCKET_NAME, s3_key, file_path)
        
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        os.remove(file_path)  # Clean up temp file
        return data
    except Exception as e:
        print(f"Error loading embeddings: {str(e)}")
        return None
