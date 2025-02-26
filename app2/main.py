import streamlit as st
import uuid
from utils import read_pdf, split_text
from embeddings import EmbeddingsManager
from chat_interface import ChatInterface
from chat_history import ChatHistoryManager
from datetime import datetime
import time
from typing import Optional

def initialize_session() -> None:
    """Initialize session state variables with error handling"""
    try:
        if "initialization_complete" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.embeddings_manager = EmbeddingsManager()
            st.session_state.chat_interface = None
            st.session_state.chat_history_manager = ChatHistoryManager()
            st.session_state.current_s3_key = None
            st.session_state.messages = []
            st.session_state.error_message = None
            st.session_state.initialization_complete = True
    except Exception as e:
        st.error(f"Failed to initialize session: {str(e)}")
        st.session_state.error_message = "Session initialization failed"

def load_chat_session(session_id: str) -> bool:
    """Load a previous chat session with validation and error handling"""
    try:
        if not session_id:
            raise ValueError("Invalid session ID")

        history = st.session_state.chat_history_manager.get_chat_history(session_id)
        if not history:
            st.warning("Chat history not found")
            return False

        # Validate required fields
        required_fields = {'messages', 's3_key'}
        if not all(field in history for field in required_fields):
            raise ValueError("Invalid chat history format")

        # Load embeddings with error handling
        embeddings_data = st.session_state.embeddings_manager.load_embeddings(session_id)
        if not embeddings_data:
            raise ValueError("Failed to load embeddings")

        # Update session state
        st.session_state.messages = history.get('messages', [])
        st.session_state.chat_interface = ChatInterface(embeddings_data)
        st.session_state.session_id = session_id
        st.session_state.current_s3_key = history.get('s3_key')
        return True

    except Exception as e:
        st.error(f"Error loading chat session: {str(e)}")
        return False

def handle_file_upload(uploaded_file) -> Optional[str]:
    """Handle PDF file upload with validation and error handling"""
    try:
        if not uploaded_file:
            return None

        # Validate file size (e.g., 10MB limit)
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("File size exceeds 10MB limit")
            return None

        # Process PDF
        pdf_text = read_pdf(uploaded_file)
        if not pdf_text:
            st.error("Failed to extract text from PDF")
            return None

        chunks = split_text(pdf_text)
        if not chunks:
            st.error("Failed to process PDF content")
            return None

        # Generate and store embeddings
        s3_key = st.session_state.embeddings_manager.generate_and_store_embeddings(
            chunks, st.session_state.session_id
        )
        return s3_key

    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

def main():
    try:
        st.set_page_config(page_title="PDF Chat Assistant", layout="wide")
        st.title("AI-Powered PDF Chat Assistant")
        
        initialize_session()
        
        # Show any pending error messages
        if st.session_state.get('error_message'):
            st.error(st.session_state.error_message)
            st.session_state.error_message = None
        
        # Sidebar
        with st.sidebar:
            st.header("Upload PDF Document")
            uploaded_pdf = st.file_uploader("Select a PDF file", type=["pdf"])
            
            if uploaded_pdf:
                with st.spinner("Processing PDF..."):
                    s3_key = handle_file_upload(uploaded_pdf)
                    if s3_key:
                        st.session_state.current_s3_key = s3_key
                        embeddings_data = st.session_state.embeddings_manager.load_embeddings(
                            st.session_state.session_id
                        )
                        st.session_state.chat_interface = ChatInterface(embeddings_data)
                        st.session_state.messages = []
                        st.success("PDF processed successfully!")
            
            # Chat History Section
            st.header("Chat History")
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🔄 Refresh"):
                    time.sleep(0.1)  # Prevent button spam
                    st.experimental_rerun()
            
            # Display available sessions with error handling
            sessions = st.session_state.chat_history_manager.list_sessions()
            if sessions:
                for session in sessions:
                    try:
                        session_id = session['session_id']
                        last_updated = datetime.fromisoformat(session['last_updated'])
                        last_updated_str = last_updated.strftime("%Y-%m-%d %H:%M")
                        
                        if st.button(
                            f"Session: {session_id[:8]}... ({last_updated_str})",
                            key=session_id,
                            help="Click to load this chat session"
                        ):
                            with st.spinner("Loading session..."):
                                if load_chat_session(session_id):
                                    st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error displaying session: {str(e)}")
            else:
                st.info("No previous chat sessions found")
        
        # Main chat area
        if st.session_state.chat_interface:
            st.header("Chat with Your PDF")
            
            # Display chat history
            for message in st.session_state.messages:
                try:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                except Exception as e:
                    st.error(f"Error displaying message: {str(e)}")
            
            # Chat input
            if prompt := st.chat_input(
                "Ask a question about your PDF",
                key="chat_input",
                max_chars=1000
            ):
                try:
                    # Add user message
                    new_message = {
                        "role": "user",
                        "content": prompt,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.messages.append(new_message)
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    # Generate response
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = st.session_state.chat_interface.generate_response(prompt)
                            st.markdown(response)
                            
                            # Add assistant message
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response,
                                "timestamp": datetime.now().isoformat()
                            })
                    
                    # Save chat history
                    if st.session_state.current_s3_key:
                        success = st.session_state.chat_history_manager.save_chat_history(
                            st.session_state.session_id,
                            st.session_state.current_s3_key,
                            st.session_state.messages
                        )
                        if not success:
                            st.warning("Failed to save chat history")
                
                except Exception as e:
                    st.error(f"Error processing message: {str(e)}")
        
        else:
            st.info("Please upload a PDF to start chatting.")

    except Exception as e:
        st.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()

    #