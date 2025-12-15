import streamlit as st
from utils import *
from LLM_OOP import *
from pages import data, single_demo, multiple_analysis, data_processing



def app():
    page_title = "Geophysics and its Engineering Friends"

    st.set_page_config(
        page_title=page_title, 
        page_icon=":earth_africa:", 
        layout="wide"
        )

    apply_custom_css()

    initialize_app_global_session_state()

    if st.session_state["password_correct"] == False:
        login_page(page_title)
        st.stop()

    data_page = st.Page(data.show, title="1. Data", icon="📈", url_path="data.py")
    data_processing_page = st.Page(data_processing.show, title="2. Processing", icon="🛠️", url_path="data_processing.py")
    demo_page = st.Page(single_demo.show, title="3. Single Line Analysis", icon="👷🏻‍♂️", url_path="single_demo.py")
    analysis_page = st.Page(multiple_analysis.show, title="4. Multiple Line Statistics", icon="📊", url_path="multiple_analysis.py")

    pages = st.navigation([data_page, data_processing_page, demo_page, analysis_page], position="sidebar")
    pages.run()

app()
