import streamlit as st

from Admin.processing import process_pdf, create_vector_store
from User.chatbot import ChatBot

st.set_page_config(page_title="Chatbot & Admin Interface", layout="wide")

# Sidebar for navigation.
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select Mode:", options=["Upload PDF", "Ask Question"])

if app_mode == "Upload PDF":
    st.title("Admin Interface: PDF Processing & FAISS Index Creation")
    st.write("Upload a PDF document to process and update the FAISS index.")
    
    # Directly use the Streamlit file uploader output.
    uploaded_pdf = st.file_uploader("Upload a PDF document", type=["pdf"])
    if uploaded_pdf is not None:
        st.success("PDF uploaded successfully!")
        st.info("Processing the PDF, please wait...")
        try:
            # process_pdf now expects the uploaded file (a file-like object)
            request_id, splitted_docs = process_pdf(uploaded_pdf)
            st.write(f"Request ID: {request_id}")
            st.write(f"Total chunks extracted: {len(splitted_docs)}")
            
            st.info("Creating the vector store (please wait)...")
            create_vector_store(request_id, splitted_docs)
            
            st.success("FAISS vector index created and uploaded to S3!")
        except Exception as e:
            st.error(f"Error during processing: {e}")
    else:
        st.info("Please upload a PDF file to begin processing.")

elif app_mode == "Ask Question":
    st.title("Chatbot Conversation Interface")
    st.write("Ask questions based on the processed PDF documents.")
    
    # Create two columns: one for chat, one for history.
    col_chat, col_history = st.columns([2, 1])
    
    with col_chat:
        # Initialize chatbot instance in session state.
        if "chatbot" not in st.session_state:
            st.session_state["chatbot"] = ChatBot()
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        
        user_message = st.chat_input("Enter your message")
        if user_message:
            st.session_state["chat_history"].append({
                "role": "user", "content": user_message
            })
            with st.spinner("Querying..."):
                answer = st.session_state["chatbot"].get_response(user_message)
            st.session_state["chat_history"].append({
                "role": "assistant", "content": answer
            })
        
        for msg in st.session_state.get("chat_history", []):
            st.chat_message(msg["role"]).write(msg["content"])
    
    with col_history:
        st.subheader("Chat History")
        if "chatbot" in st.session_state:
            memory_messages = st.session_state["chatbot"].get_memory()
            if memory_messages:
                for m in memory_messages:
                    content = m.content if hasattr(m, "content") else str(m)
                    st.write(content)
            else:
                st.info("No conversation history available yet.")
        else:
            st.info("Chatbot not initialized yet.")