import os
import pickle
import tempfile
import boto3
from typing import List, Dict, Any
import faiss
import numpy as np
from langchain.embeddings import BedrockEmbeddings
from dotenv import load_dotenv

load_dotenv()

class EmbeddingsManager:
    def __init__(self):
        self.s3_client = boto3.client("s3", region_name="us-east-1")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
        self.embeddings_model = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v1",
            client=bedrock_client
        )
        
    def generate_and_store_embeddings(self, chunks: List[str], session_id: str) -> str:
        """
        Generate embeddings for text chunks and store them in S3 with FAISS index
        """
        try:
            # Generate embeddings
            embeddings = self.embeddings_model.embed_documents(chunks)
            
            # Create FAISS index
            dimension = len(embeddings[0])
            index = faiss.IndexFlatL2(dimension)
            index.add(np.array(embeddings, dtype=np.float32))
            
            # Package data
            data_package = {
                'embeddings': embeddings,
                'chunks': chunks,
                'faiss_index': index,
                'session_id': session_id
            }
            
            # Store in S3
            s3_key = self._store_in_s3(data_package, session_id)
            return s3_key
            
        except Exception as e:
            print(f"Error in generate_and_store_embeddings: {str(e)}")
            raise
    
    def _store_in_s3(self, data_package: Dict[str, Any], session_id: str) -> str:
        """Store the data package in S3 using session-specific folder"""
        filename = "document_embeddings.pkl"
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        
        with open(temp_path, "wb") as f:
            pickle.dump(data_package, f)
        
        s3_key = f"session_{session_id}/{filename}"
        self.s3_client.upload_file(temp_path, self.bucket_name, s3_key)
        os.remove(temp_path)
        return s3_key
    
    def load_embeddings(self, session_id: str) -> Dict[str, Any]:
        """Load embeddings and FAISS index from S3"""
        try:
            filename = "document_embeddings.pkl"
            s3_key = f"session_{session_id}/{filename}"
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            
            self.s3_client.download_file(self.bucket_name, s3_key, temp_path)
            
            with open(temp_path, "rb") as f:
                data = pickle.load(f)
            os.remove(temp_path)
            return data
            
        except Exception as e:
            print(f"Error loading embeddings: {str(e)}")
            raise