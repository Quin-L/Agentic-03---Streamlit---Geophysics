import streamlit as st
import pandas as pd
from utils import *
from LLM_OOP import *
from css import *


def show():

    page_title = "👏 Geophysics and its Engineering Friends"

    # ===== Sidebar =====
    sidebar()

    # ===== Main Page =====
    st.title(page_title)
    # st.write("Welcome to the Geophysics Data Processing and Analysis App!")
    st.divider()

    col1, col2, col3 = st.columns([7,0.5,4])
    uploaded_files, geophysics_data = get_uploaded_data()
    prompt = st.chat_input("Ask me anything about the data and geophysics...")

    with col1:
        display_uploaded_data(uploaded_files, geophysics_data)

        # Check for file changes AFTER files are processed
        geophysics_data = st.session_state['all_geophysics']['geophysics_data']
        check_file_changes(geophysics_data)

        # st.write(list(geophysics_data.keys()))

    with col3:
        initial_prompt = auto_prompt()
        chatbot_chat_interface(prompt, geophysics_data, initial_prompt)


       













