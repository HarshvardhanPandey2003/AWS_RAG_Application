import boto3
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

# Get bucket name from environment variable; raise error if not set.
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
if not BUCKET_NAME:
    logger.error("S3_BUCKET_NAME environment variable is not set.")
    raise ValueError("S3_BUCKET_NAME environment variable is not set.")

# Initialize S3 client
s3_client = boto3.client("s3", region_name="us-east-1")

# Initialize Bedrock embeddings client.
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
bedrock_embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1", client=bedrock_client
)


def get_unique_id():
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def split_text(pages, chunk_size=1000, chunk_overlap=200):
    """
    Split the list of document pages into chunks using a recursive
    character text splitter.
    
    Args:
        pages (list): List of pages/documents.
        chunk_size (int): Maximum chunk size.
        chunk_overlap (int): Overlap size between chunks.
        
    Returns:
        list: Splitted document chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs = text_splitter.split_documents(pages)
    return docs


def create_vector_store(request_id, documents):
    """
    Create a FAISS vector store from the provided documents,
    save it locally using FAISS’s built-in mechanism, and upload
    the index files (.faiss and .pkl) to S3 under the
    'vector_indexes/' prefix.
    
    Args:
        request_id (str): Unique identifier for this processing request.
        documents (list): List of document chunks.
        
    Raises:
        Exception: If S3 upload fails.
    """
    # Use the request_id for naming files.
    file_name = f"{request_id}.bin"
    vectorstore_faiss = FAISS.from_documents(documents, bedrock_embeddings)

    with tempfile.TemporaryDirectory() as temp_dir:
        vectorstore_faiss.save_local(index_name=file_name, folder_path=temp_dir)
        
        # Build the file paths created by FAISS
        faiss_file_path = os.path.join(temp_dir, f"{file_name}.faiss")
        pkl_file_path = os.path.join(temp_dir, f"{file_name}.pkl")
        
        try:
            # Upload files under the dedicated prefix: vector_indexes/
            s3_key_faiss = f"vector_indexes/{file_name}.faiss"
            s3_key_pkl = f"vector_indexes/{file_name}.pkl"

            s3_client.upload_file(
                Filename=faiss_file_path, Bucket=BUCKET_NAME, Key=s3_key_faiss
            )
            logger.info(
                f"Uploaded {faiss_file_path} to s3://{BUCKET_NAME}/{s3_key_faiss}"
            )

            s3_client.upload_file(
                Filename=pkl_file_path, Bucket=BUCKET_NAME, Key=s3_key_pkl
            )
            logger.info(
                f"Uploaded {pkl_file_path} to s3://{BUCKET_NAME}/{s3_key_pkl}"
            )

        except Exception as e:
            error_msg = (
                f"Failed to upload files to S3: {str(e)}\n{traceback.format_exc()}"
            )
            logger.error(error_msg)
            raise


def process_pdf(upload_file, *args, **kwargs):
    """
    Process the uploaded PDF file:
      - Saves it to a temporary file.
      - Loads and splits the PDF into pages.
      - Further splits pages into text chunks.
    
    Args:
        upload_file (UploadedFile): The PDF file from Streamlit uploader.
        *args, **kwargs: Additional arguments passed (ignored).
        
    Returns:
        tuple: (request_id, splitted_docs)
    """
    request_id = get_unique_id()
    temp_pdf_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(upload_file.getvalue())
            temp_pdf_path = temp_pdf.name

        # Load and split the PDF pages.
        loader = PyPDFLoader(temp_pdf_path)
        pages = loader.load_and_split()

        # Further split the text into chunks.
        splitted_docs = split_text(pages, chunk_size=1000, chunk_overlap=200)
        return request_id, splitted_docs
    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        logger.error(error_msg)
        raise
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)
