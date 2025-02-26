# llm.py
import streamlit as st
from config import GEMINI_API

@st.cache_resource(show_spinner=False)
def get_llm():
    """
    Initializes the LLM using the GoogleGenerativeAI model.
    For the MVP, we use streaming mode.
    """
    from langchain_google_genai import GoogleGenerativeAI
 # Update with your actual module path
    llm = GoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        google_api_key=GEMINI_API,
        streaming=True
    )
    return llm
