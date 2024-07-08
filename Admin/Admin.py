import boto3
import streamlit as st
import os
import uuid
import logging
import traceback
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Creating an S3 Cliet
s3_client = boto3.client('s3')
BUCKET_NAME = "pdfembeddings"

from langchain_community.embeddings import BedrockEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community import document_loaders
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_client)

def get_unique_id():
    return str(uuid.uuid4())

# Splitting the Pages into Text Chunks 
def split_text(pages, chunk_size , chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    docs = text_splitter.split_documents(pages)
    return docs

# Creating a Vector Store
def create_vector_store(request_id, documents):
    vectorstore_faiss = FAISS.from_documents(documents, bedrock_embeddings)
    file_name = f"{request_id}.bin"
    folder_path = tempfile.gettempdir()  # Get the system's temporary directory
    vectorstore_faiss.save_local(index_name=file_name, folder_path=folder_path)
    
    s3_client.upload_file(Filename=folder_path+"/"+file_name+".faiss",Bucket=BUCKET_NAME,Key="my_faiss.faiss")
    s3_client.upload_file(Filename=folder_path+"/"+file_name+".pkl",Bucket=BUCKET_NAME,Key="my_faiss.pkl")

def main():
    st.write("This is admin state Chat with Pdf")
    upload_file = st.file_uploader("Upload file", type=["pdf"])
    if upload_file is not None:
        try:
            request_id = get_unique_id()
            st.write(f"Request Id : {request_id}")
            saved_file_name = f"{request_id}.pdf"
            with open(saved_file_name, "wb") as w:
                w.write(upload_file.getvalue())

            loader = PyPDFLoader(saved_file_name)
            pages = loader.load_and_split()

            st.write(f"Total Pages : {len(pages)}")

            # Split text
            splitted_docs = split_text(pages, 1000, 200)
            st.write(f"Splitted Docs length: {len(splitted_docs)}")

            # Create vector store
            st.write("Creating the Vector Store")
            create_vector_store(request_id, splitted_docs)

            st.write("Hurray!! PDF processed successfully")

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            st.error(f"Error!! Please check logs. Error details: {error_msg}")




if __name__ == "__main__":
    main()