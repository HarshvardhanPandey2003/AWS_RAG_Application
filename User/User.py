# # User.py

# import boto3
# import streamlit as st
# import os
# import tempfile
# from langchain_community.embeddings import BedrockEmbeddings
# from langchain_community.llms.bedrock import Bedrock  # Corrected import
# from langchain.prompts import PromptTemplate
# from langchain.chains import RetrievalQA
# from langchain_community.vectorstores import FAISS

# # S3 client
# s3_client = boto3.client("s3")
# BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "pdfembeddings")

# # Bedrock client and embeddings
# bedrock_client = boto3.client(service_name="bedrock-runtime")
# bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_client)


import boto3
import streamlit as st
import os
import tempfile
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.llms.bedrock import Bedrock  # Corrected import
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS

# S3 client
s3_client = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Bedrock client and embeddings
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_client)

# Temporary directory for storing files
folder_path = tempfile.gettempdir()

@st.cache_resource
def get_llm():
    llm = Bedrock(model_id="meta.llama3-8b-instruct-v1:0", client=bedrock_client)
    return llm

@st.cache_data
def load_index():
    try:
        with st.spinner("Loading index..."):
            s3_client.download_file(Bucket=BUCKET_NAME, Key="my_faiss.faiss", Filename=os.path.join(folder_path, "my_faiss.faiss"))
            s3_client.download_file(Bucket=BUCKET_NAME, Key="my_faiss.pkl", Filename=os.path.join(folder_path, "my_faiss.pkl"))
    except Exception as e:
        st.error(f"Error loading index: {e}")
        raise

def get_response(llm, vectorstore, question):
    prompt_template = """
    Context: {context}

    Question: {question}

    Provide a concise, factual answer to the question based on the given context. 
    If the information is not available in the context, simply state that you don't have enough information to answer.
    Do not invent information or engage in role-play.
    """

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    answer = qa.invoke({"query": question})
    return answer['result']

def main():
    st.header("This is Client Site for Chat with PDF demo using Bedrock, RAG etc")

    load_index()

    if "faiss_index" not in st.session_state:
        try:
            with st.spinner("Creating index..."):
                st.session_state.faiss_index = FAISS.load_local(
                    index_name="my_faiss",
                    folder_path=folder_path,
                    embeddings=bedrock_embeddings,
                    allow_dangerous_deserialization=True
                )
            st.write("INDEX IS READY")
        except Exception as e:
            st.error(f"Error creating index: {e}")
            return

    question = st.text_input("Please ask your question")
    if st.button("Ask Question"):
        with st.spinner("Querying..."):
            llm = get_llm()
            try:
                answer = get_response(llm, st.session_state.faiss_index, question)
                st.write(answer)
                st.success("Done")
            except Exception as e:
                st.error(f"Error getting response: {e}")

if __name__ == "__main__":
    main()