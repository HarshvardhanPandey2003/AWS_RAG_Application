# User/chat_interface.py
import streamlit as st
from User.chatbot import ChatBot

st.set_page_config(page_title="Chatbot Interface", layout="wide")
st.title("Chatbot Conversation Interface")

# Initialize chatbot instance in session state.
if "chatbot" not in st.session_state:
    st.session_state["chatbot"] = ChatBot()

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Create two columns: left for the chat, right for the memory history.
col_chat, col_history = st.columns([2, 1])

with col_chat:
    user_input = st.chat_input("Enter your message")
    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.spinner("Querying..."):
            response = st.session_state["chatbot"].get_response(user_input)
        st.session_state["chat_history"].append({"role": "assistant", "content": response})
    
    # Display conversation messages.
    for msg in st.session_state.get("chat_history", []):
        st.chat_message(msg["role"]).write(msg["content"])

with col_history:
    st.subheader("Chat History")
    memory_messages = st.session_state["chatbot"].get_memory()
    if memory_messages:
        for m in memory_messages:
            # Each memory message is typically an object with a `content` attribute.
            content = m.content if hasattr(m, "content") else str(m)
            st.write(content)
    else:
        st.info("No conversation history available yet.")