import streamlit as st
import numpy as np
import pandas as pd

from src.ui.components import display_chat

def main():
    user_input = display_chat()
    if user_input:
        pass
    
    # Add a selectbox to the sidebar:
    add_selectbox = st.sidebar.selectbox(
        'How would you like to be contacted?',
        ('Email', 'Home phone', 'Mobile phone')
    )

    # Add a slider to the sidebar:
    add_slider = st.sidebar.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )
    
if __name__ == "__main__":
    main()