# chat_history_interface.py
import streamlit as st
from datetime import datetime

def display_chat_history():
    """
    Displays the chat history stored in st.session_state['chat_history'].
    """
    st.subheader("Chat History")
    chat_history = st.session_state.get("chat_history", [])

    if not chat_history:
        st.info("No chat history available.")
        return

    for msg in chat_history:
        # Use current time as default timestamp if not provided
        timestamp_str = msg.get("timestamp", datetime.utcnow().isoformat())
        message_time = datetime.fromisoformat(timestamp_str)

        if msg["role"] == "user":
            st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-timestamp">{message_time.strftime('%H:%M:%S')}</div>
                    <div><strong>You:</strong> {msg['message']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div class="message-timestamp">{message_time.strftime('%H:%M:%S')}</div>
                    <div><strong>Assistant:</strong> {msg['message']}</div>
                </div>
            """, unsafe_allow_html=True)