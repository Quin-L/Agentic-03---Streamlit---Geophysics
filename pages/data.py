import streamlit as st
import pandas as pd
from utils import *
from LLM_OOP import *


def show():

    page_title = "👏 Geophysics and its Engineering Friends"

    # ===== Sidebar =====
    sidebar()

    # ===== Main Page =====
    st.title(page_title)
    st.write("Welcome to the Geophysics Data Processing and Analysis App!")
    st.divider()

    col1, col2, col3 = st.columns([7,0.5,3])
    prompt = st.chat_input("Ask me anything...")

    with col1:
        uploaded_files, geophysics_data = get_uploaded_data()
        display_uploaded_data(uploaded_files, geophysics_data)

        st.write(list(geophysics_data.keys()))
        # st.write(geophysics_data)

    with col3:
        initial_prompt = auto_prompt()
        
        chatbot_chat_interface(prompt, geophysics_data)



def chatbot_chat_interface(prompt, geophysics_data):
    """ChatGPT-style chat interface with message bubbles and conversation history"""

    st.header("💬 AI Assistant")
    st.subheader("!!! Note, chat history is preserved, agent short term memory up to 5 messages.")
    max_output_token = token_settings_and_controls()


    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display all existing chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt:
        history_context = "\n".join(f"{message['role'].upper()}:{message['content']}" for message in
    st.session_state.chat_messages[-5:])

        adjusted_prompt = f"""

        You are an expert specialized in geotechnical engineering and geophysics.
        You are also an expert in data processing and analysis using Python programming language.
        Your task is to assist the user with their queries related to these fields.

        geophysics_data: {geophysics_data}

        User query: {prompt}

        You have access to conversation history for context.

        conversation history:{history_context}


        When user ask for anything that is not related to geotechnical engineering, geophysics, data processing, or Python programming,
        politely inform them that you can only assist with topics related to these fields.
        """

        # Display and process new user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant response with streaming
        with st.chat_message("assistant"):
            response = get_llm_response(adjusted_prompt, max_output_token, stream=True)
            full_response = show_response(response, stream=True)

        # Add both messages to history after streaming completes
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
            















