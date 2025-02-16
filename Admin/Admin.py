import boto3
import streamlit as st
import os
import uuid
import logging
import traceback
import tempfile
from langchain_community.embeddings import BedrockEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bucket name from environment variable
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Check if the bucket name is set
if not BUCKET_NAME:
    logger.error("S3_BUCKET_NAME environment variable is not set.")
    raise ValueError("S3_BUCKET_NAME environment variable is not set.")

# Creating an S3 Client
s3_client = boto3.client('s3', region_name="us-east-1")

bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_client)


def get_unique_id():
    return str(uuid.uuid4())

def split_text(pages, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    docs = text_splitter.split_documents(pages)
    return docs

def create_vector_store(request_id, documents):
    vectorstore_faiss = FAISS.from_documents(documents, bedrock_embeddings)
    file_name = f"{request_id}.bin"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        vectorstore_faiss.save_local(index_name=file_name, folder_path=temp_dir)
        
        faiss_file_path = os.path.join(temp_dir, f"{file_name}.faiss")
        pkl_file_path = os.path.join(temp_dir, f"{file_name}.pkl")

        try:
            s3_client.upload_file(Filename=faiss_file_path, Bucket=BUCKET_NAME, Key="my_faiss.faiss")
            logger.info(f"Uploaded {faiss_file_path} to s3://{BUCKET_NAME}/my_faiss.faiss")
            s3_client.upload_file(Filename=pkl_file_path, Bucket=BUCKET_NAME, Key="my_faiss.pkl")
            logger.info(f"Uploaded {pkl_file_path} to s3://{BUCKET_NAME}/my_faiss.pkl")

        except Exception as e:
            error_msg = f"Failed to upload files to S3: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise

def main():
    st.write("This is admin state Chat with Pdf")
    upload_file = st.file_uploader("Upload file", type=["pdf"])
    if upload_file is not None:
        try:
            request_id = get_unique_id()
            st.write(f"Request Id : {request_id}")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                temp_pdf.write(upload_file.getvalue())
                temp_pdf_path = temp_pdf.name

            loader = PyPDFLoader(temp_pdf_path)
            pages = loader.load_and_split()

            st.write(f"Total Pages : {len(pages)}")

            splitted_docs = split_text(pages, 1000, 200)
            st.write(f"Splitted Docs length: {len(splitted_docs)}")

            st.write("Creating the Vector Store")
            create_vector_store(request_id, splitted_docs)

            st.write("Hurray!! PDF processed successfully")

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            st.error(f"Error!! Please check logs. Error details: {error_msg}")
        finally:
            if 'temp_pdf_path' in locals():
                os.unlink(temp_pdf_path)

if __name__ == "__main__":
    main()
