# Admin/admin_interface.py
import streamlit as st
import traceback
import logging

from Admin.processing import process_pdf, create_vector_store

# Set up logger for the interface.
logger = logging.getLogger(__name__)


def main():
    st.title("Admin Interface - PDF Processing & Vector Store Creation")
    
    upload_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if upload_file:
        try:
            st.info("Processing the uploaded PDF file...")
            request_id, splitted_docs = process_pdf(upload_file)
            
            # Save the request ID in the session state
            st.session_state.request_id = request_id
            st.success("Request ID saved in session state!")
            
            st.write(f"Request ID: {request_id}")
            st.write(f"Total chunks extracted: {len(splitted_docs)}")
            
            st.info("Creating the vector store (please wait)...")
            create_vector_store(request_id, splitted_docs)
            
            st.success("Hurray!! PDF processed; vector store created successfully.")
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            st.error("Error!! Please check logs for details.\n" + error_msg)

if __name__ == "__main__":
    main()
