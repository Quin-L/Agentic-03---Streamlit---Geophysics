import streamlit as st
import pandas as pd
from utils import *
from LLM_OOP import *
from css import *
import datetime

now = datetime.datetime.now()



def show():

    page_title = "👏 Geophysics and its Engineering Friends"

    # ===== Sidebar =====
    sidebar()

    # ===== Main Page =====
    st.title(page_title)
    st.write("Welcome to the Geophysics Data Processing and Analysis App!")
    st.divider()
    # sticky_chat_input()

    # ====== Initial State Management ======
    initialize_data_page_session_state()

    prompt = st.chat_input("Ask me anything ...")

    col1, col2, col3 = st.columns([7,0.5,4])
    uploaded_files, geophysics_data = get_uploaded_data()
    check_file_changes(uploaded_files)


    with col1:
        display_uploaded_data(uploaded_files, geophysics_data)

    with col3:
        initial_prompt = auto_prompt()
        chatbot_chat_interface(prompt, geophysics_data, initial_prompt)


       













