import os
import streamlit as st
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# Import session and chat history management code
from session_state import SessionManager
from chat_history import (
    create_chat_session,
    update_chat_history,
    fetch_chat_history,
    fetch_recent_sessions
)
from chat_history_interface import display_chat_history
from utils import extract_text_from_pdf, split_text
from embeddings import get_unique_id, generate_embeddings, store_embeddings
from llm import get_llm, create_conversational_chain, create_vectorstore, get_relevant_context

# Initialize session state and environment variables
SessionManager.initialize_session_state()
load_dotenv()

# Set up page configuration
st.set_page_config(page_title="PDF Chat Assistant", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
        .stTextInput > div > div > input {
            caret-color: #00BFFF;
        }
        .stButton > button {
            width: 100%;
            border-radius: 20px;
            height: 3em;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .user-message {
            background-color: #d8f3dc;
        }
        .assistant-message {
            background-color: #f8d7da;
        }
        .message-timestamp {
            font-size: 0.8em;
            color: #666;
            margin-bottom: 0.3em;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------
# Title and Description
# -----------------------
st.title("📚 PDF Chat Assistant")
st.markdown("Upload a PDF and start chatting about its contents!")

# -----------------------
# DynamoDB Table Setup
# -----------------------
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(DYNAMODB_TABLE)

# -----------------------
# Sidebar: Document Upload & Chat History
# -----------------------
with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    # Process PDF when uploaded
    if uploaded_file and not st.session_state.pdf_processed:
        with st.spinner("Processing PDF..."):
            try:
                # Extract and process text from the PDF
                text = extract_text_from_pdf(uploaded_file)
                chunks = split_text(text)
                
                # Generate embeddings and create a new session ID
                embeddings = generate_embeddings(chunks)
                session_id = get_unique_id()
                st.session_state.session_id = session_id
                
                # Store embeddings (with chunks) and create vectorstore
                s3_key = store_embeddings(chunks, embeddings, session_id)
                st.session_state.vectorstore = create_vectorstore(chunks, embeddings)
                llm = get_llm()
                st.session_state.conversation_chain = create_conversational_chain(llm)
                
                # Create chat session in DynamoDB
                create_chat_session(
                    session_id=session_id,
                    embeddings_key=s3_key,
                    file_name=uploaded_file.name
                )
                
                st.session_state.pdf_processed = True
                st.success("PDF processed successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
                SessionManager.clear_session()

    st.markdown("---")
    
    # -----------------------
    # Sidebar: Chat History Section
    # -----------------------
    st.header("Chat History")
    if st.button("Refresh History"):
        with st.spinner("Fetching chat sessions..."):
            sessions = fetch_recent_sessions()  # Fetch sessions from the past 7 days (default)
            st.session_state.chat_sessions = sessions
            st.success("Chat sessions refreshed!")

    # If chat sessions have been loaded, display them in a selectbox
    if st.session_state.get("chat_sessions"):
        # Build a mapping for display purposes (showing first 8 characters of session_id and file name)
        session_options = {
            f"{session['session_id'][:8]} - {session.get('file_name', 'No file')}": session 
            for session in st.session_state.chat_sessions
        }
        selected_session_key = st.selectbox("Select a session", list(session_options.keys()))
        if st.button("Load Selected Session"):
            session_data = session_options[selected_session_key]
            if SessionManager.load_session(session_data):
                st.success("Session loaded successfully!")
            else:
                st.error("Failed to load session")

# -----------------------
# Main Chat Interface
# -----------------------
st.header("💬 Chat Interface")

# Show current session info if available
if st.session_state.session_id:
    st.caption(f"Current Session: {st.session_state.session_id[:8]}...")

# Display chat history for the current session
display_chat_history()

# Chat input section – only available when PDF is processed and the vectorstore is ready
if st.session_state.pdf_processed and st.session_state.vectorstore is not None:
    user_input = st.text_input("Type your message here...", key="user_input")
    
    if st.button("Send") and user_input:
        try:
            # Update local chat history and save to DynamoDB
            SessionManager.update_chat_history("user", user_input)
            update_chat_history(st.session_state.session_id, "user", user_input)
            
            # Retrieve relevant context and generate an assistant response
            context = get_relevant_context(user_input, st.session_state.vectorstore)
            with st.spinner("Thinking..."):
                response = st.session_state.conversation_chain.run(
                    input=user_input,
                    context=context
                )
            
            # Update the chat history with the assistant's response
            SessionManager.update_chat_history("assistant", response)
            update_chat_history(st.session_state.session_id, "assistant", response)
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")
else:
    if not st.session_state.pdf_processed:
        st.info("Please upload a PDF to start chatting!")

# -----------------------
# End Chat Option
# -----------------------
if st.session_state.session_id and st.button("End Chat"):
    try:
        # Save final chat history to DynamoDB
        table.update_item(
            Key={"session_id": st.session_state.session_id},
            UpdateExpression="SET chat_history = :chat_history",
            ExpressionAttributeValues={":chat_history": st.session_state.chat_history}
        )
        st.success("Chat history saved successfully!")
        SessionManager.clear_session()
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")
