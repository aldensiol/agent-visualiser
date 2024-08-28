import streamlit as st

def display_chat():
    st.title("RAG Chatbot")
    user_input = st.text_input("Ask a question:")
    return user_input