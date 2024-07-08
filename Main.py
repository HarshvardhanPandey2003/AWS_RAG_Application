import streamlit as st
import sys
import os

# Add the Admin and User directories to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'Admin'))
sys.path.append(os.path.join(current_dir, 'User'))

# Now you can import your modules
import User
import Admin

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload PDF", "Ask Questions"])

    if page == "Upload PDF":
        Admin.main()
    elif page == "Ask Questions":
        User.main()

if __name__ == "__main__":
    main()