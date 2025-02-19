# llm.py
import os
from typing import List
import boto3
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.vectorstores import FAISS
import pickle
import tempfile
import streamlit as st
from langchain.embeddings import BedrockEmbeddings
import numpy as np

# Global configurations
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API")
folder_path = tempfile.gettempdir()

# Initialize AWS clients
s3_client = boto3.client("s3", region_name="us-east-1")
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
bedrock_embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1", 
    client=bedrock_client
)

@st.cache_resource(show_spinner=False)
def get_llm():
    """
    Initialize the Gemini LLM with streaming enabled.
    """
    llm = GoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        google_api_key=GEMINI_API_KEY,
        streaming=True
    )
    return llm

def load_embeddings_from_s3(s3_key: str):
    """
    Downloads and loads the embeddings file from S3.
    Returns both embeddings and the FAISS index if it exists.
    """
    try:
        local_path = os.path.join(folder_path, os.path.basename(s3_key))
        s3_client.download_file(BUCKET_NAME, s3_key, local_path)
        
        with open(local_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading embeddings: {str(e)}")
        return None

def create_conversational_chain(llm):
    """
    Creates a conversation chain with the LLM and a custom prompt template.
    """
    template = """You are a helpful AI assistant that helps users understand their documents.
    
    Previous conversation:
    {chat_history}
    
    Context from the document:
    {context}
    
    Human: {input}
    Assistant: Let me help you with that."""

    prompt = PromptTemplate(
        input_variables=["chat_history", "context", "input"],
        template=template
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="input",
        return_messages=True
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )
    
    return chain

def create_vectorstore(texts: List[str], precomputed_embeddings=None) -> FAISS:
    """
    Creates a new FAISS vectorstore from the given texts.
    
    If precomputed_embeddings is provided (a list of vectors corresponding
    to the texts), the function builds the index using them.
    Otherwise, it computes embeddings using the bedrock_embeddings object.
    """
    try:
        if precomputed_embeddings is None:
            # Standard behavior: compute embeddings from texts
            return FAISS.from_texts(texts, bedrock_embeddings)
        else:
            # Use precomputed embeddings to build the FAISS index manually.
            from langchain.docstore.document import Document
            import faiss
            import numpy as np

            # Create Document objects from texts
            docs = [Document(page_content=text) for text in texts]
            # Assume each embedding vector has the same dimension
            d = len(precomputed_embeddings[0])
            # Create a FAISS index for L2 distance
            index = faiss.IndexFlatL2(d)
            # Convert embeddings to a numpy array of type float32 and add to index
            index.add(np.array(precomputed_embeddings).astype("float32"))
            
            # Build a docstore dictionary mapping string IDs to documents
            docstore = {str(i): doc for i, doc in enumerate(docs)}
            # Create mapping from index positions to docstore IDs
            index_to_docstore_id = {i: str(i) for i in range(len(docs))}
            
            # Create and return the FAISS vectorstore instance with the new parameter
            vectorstore = FAISS(
                embedding_function=bedrock_embeddings,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )
            return vectorstore
    except Exception as e:
        st.error(f"Error creating vectorstore: {str(e)}")
        return None



def get_relevant_context(query: str, vectorstore: FAISS, k: int = 3) -> str:
    """
    Retrieves the most relevant context from the vectorstore based on the query.
    """
    try:
        if vectorstore is None:
            return ""
            
        similar_docs = vectorstore.similarity_search(query, k=k)
        context = "\n".join([doc.page_content for doc in similar_docs])
        return context
    except Exception as e:
        st.error(f"Error getting context: {str(e)}")
        return ""