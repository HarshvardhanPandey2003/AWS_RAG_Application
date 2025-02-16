import os
import tempfile
import logging
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import BedrockEmbeddings
from langchain_google_genai import GoogleGenerativeAI

import boto3

# Import conversation memory helper (optional module)
from User.memory import get_conversation_memory

load_dotenv()  # Load configuration from .env

# Configuration from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
FAISS_INDEX_NAME = "my_faiss"
TEMP_FOLDER = tempfile.gettempdir()

# Create a boto3 s3 client
s3_client = boto3.client("s3", region_name="us-east-1")

# Initialize Bedrock embeddings using boto3 client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
bedrock_embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1", client=bedrock_client
)

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_index_files():
    """
    Download required FAISS index files from S3.
    """
    try:
        # Files to download for the FAISS index.
        files = {
            "faiss_index": f"{FAISS_INDEX_NAME}.faiss",
            "pkl_index": f"{FAISS_INDEX_NAME}.pkl"
        }
        for key, filename in files.items():
            local_path = os.path.join(TEMP_FOLDER, filename)
            s3_client.download_file(
                Bucket=BUCKET_NAME, Key=filename, Filename=local_path
            )
            logger.info(f"Downloaded {filename} to {local_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading index files: {e}")
        raise e


def get_llm():
    """
    Initialize and return the Gemini LLM.
    """
    llm = GoogleGenerativeAI(
        model="gemini-1.5-pro-latest", google_api_key=GEMINI_API_KEY
    )
    return llm


class ChatBot:
    """
    A conversational retrieval-augmented chatbot that:
      - Downloads and loads a FAISS vector index from S3/local storage.
      - Uses a Conversational Retrieval Chain with conversation memory.
      - Generates answers based on the retrieved context.
    """

    def __init__(self):
        # Download index files from S3.
        download_index_files()

        # Load the FAISS index from local storage.
        try:
            self.index = FAISS.load_local(
                index_name=FAISS_INDEX_NAME,
                folder_path=TEMP_FOLDER,
                embeddings=bedrock_embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("FAISS index loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            raise e

        # Create a prompt template for the retrieval chain.
        prompt_template = """
        Context: {context}
        
        Question: {question}
        
        Provide a concise, factual answer based on the context.
        If there isn't enough information, state that explicitly.
        """
        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        # Obtain conversation memory using our helper.
        memory = get_conversation_memory()

        # Create the Conversational Retrieval Chain with memory.
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=get_llm(),
            retriever=self.index.as_retriever(search_kwargs={"k": 5}),
            memory=memory,
            chain_type="stuff",  # Using "stuff" strategy for combining documents.
            chain_type_kwargs={"prompt": prompt},
        )

    def get_response(self, query: str) -> str:
        """
        Processes a user query using the conversational retrieval chain
        and returns the generated answer.
        """
        try:
            result = self.chain({"question": query})
            answer = result.get("answer", "I was unable to generate a response.")
            logger.info("Answer generated successfully.")
            return answer
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return "An error occurred while generating a response."

    def get_memory(self):
        """
        Return the conversation memory messages.
        """
        # Depending on the memory type, messages may be stored in different attributes.
        # ConversationBufferMemory, for example, stores messages in the "buffer" attribute.
        if hasattr(self.chain.memory, "buffer"):
            return self.chain.memory.buffer
        return []
    