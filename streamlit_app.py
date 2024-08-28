import streamlit as st

from src.ui.components import display_chat

def main():
    user_input = display_chat()
    if user_input:
        st.write("im gay")

if __name__ == "__main__":
    main()