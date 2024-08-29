import streamlit as st

def display_chat():
    st.title("LangGraph-based Agentic Chatbot")
    user_input = st.text_input("Ask a question:", key="user_input")
    return user_input