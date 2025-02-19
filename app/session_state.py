# session_state.py
import streamlit as st
from datetime import datetime
from typing import Dict, Any
from llm import get_llm, create_conversational_chain, create_vectorstore
from embeddings import load_embeddings_from_s3

class SessionManager:
    @staticmethod
    def initialize_session_state():
        """Initialize all required session state variables."""
        initial_states = {
            'initialized': False,
            'chat_history': [],
            'texts': None,
            'vectorstore': None,
            'conversation_chain': None,
            'session_id': None,
            'chat_sessions': [],
            'selected_session': None,
            'pdf_processed': False  # New flag to track PDF processing
        }
        
        for key, value in initial_states.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def load_session(session_data: Dict[str, Any]) -> bool:
        """Load a chat session into the session state."""
        try:
            session_id = session_data['session_id']
            st.session_state.selected_session = session_id
            st.session_state.session_id = session_id
            
            # Load chat history
            st.session_state.chat_history = session_data.get('chat_history', [])
            
            # Load embeddings (and chunks) directly using session_id
            embeddings_data = load_embeddings_from_s3(session_id)
            if embeddings_data:
                chunks = embeddings_data.get('chunks')
                embeddings = embeddings_data.get('embeddings')
                if not chunks or not embeddings:
                    st.error("The loaded session is missing the required text chunks or embeddings.")
                    return False
                st.session_state.vectorstore = create_vectorstore(chunks, embeddings)
                llm = get_llm()
                st.session_state.conversation_chain = create_conversational_chain(llm)
                st.session_state.initialized = True
                st.session_state.pdf_processed = True  # Mark PDF as processed
                return True
            
            return False
        except Exception as e:
            st.error(f"Error loading session: {str(e)}")
            return False
    
    @staticmethod
    def clear_session() -> None:
        """Clear all session-related state variables."""
        session_vars = [
            'initialized',
            'chat_history',
            'texts',
            'vectorstore',
            'conversation_chain',
            'session_id',
            'selected_session',
            'pdf_processed'
        ]
        
        for var in session_vars:
            if var in st.session_state:
                st.session_state[var] = None if var != 'chat_history' else []
        
        st.session_state.initialized = False
        st.session_state.pdf_processed = False

    @staticmethod
    def update_chat_history(role: str, message: str) -> None:
        """Update the chat history in the session state."""
        new_message = {
            "role": role,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        st.session_state.chat_history.append(new_message)

# Create a singleton instance
session_manager = SessionManager()