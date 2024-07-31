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


# Also if I have already 
# 1.) Created ec2 instance and installed all the dependencies like python 3.11.3 , Docker etc.
# 2.) Written the docker code , created a docker image and uploaded that docker image in the docker hub
# 3.) The docker image when I run it locally is working completely fine 
# What are the thing which I should do next 
# tell me the steps of how to run the code in productions 