from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import os

# load_dotenv('/Users/qinli/secrets/.env')
load_dotenv()
# load_dotenv("C:\\Users\\qli\\OneDrive - CPB Contractors Pty LTD\\01 Digitisation Project\\Agentic 01\\.env")
client = OpenAI()

# @st.cache_data
def get_llm_response(prompt, max_output_token, stream=False):
    with st.spinner("Generating response..."):
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[{
                "role" : "user",
                "content" : prompt
            }],
            max_output_tokens=max_output_token,
            # background=True,
            stream = stream,
        )
        return response
    
def show_response(response, stream):
    """
    Display the response from the LLM in Streamlit.
    Can handle both streaming and non-streaming responses.
    Response is based on OpenAI's streaming response format.
    Args:
        response (str): The response object from the LLM (OpenAI).
        stream (bool): Whether the response is streamed or not (OpenAI).
    """
    if stream:
        full_response = ""
        response_placeholder = st.empty()
        for chunk in response:
            if hasattr(chunk, 'delta') and chunk.delta:
                full_response += chunk.delta
                response_placeholder.markdown(full_response)

    elif not stream:
        full_response = response.output_text
        st.write(full_response)
    
    return full_response


def auto_prompt():
    """
    This function generates an automatic prompt for the chatbot based on the uploaded data.
    """
    prompt = f"""
    Check the uploaded geophysics data files in the data page.
    Give a brief overview of the data files.
    Give a summary of the data files.
    Identify any potential issues or anomalies in the data.
    Suggest possible data processing steps to clean and prepare the data for analysis.
    """
    return prompt


def chatbot_section():
    """Simple chatbot section with text area input and response display"""

    st.header("Chatbot")
    max_output_token = st.slider("Select max_output_token:", min_value=100, max_value=1000, value=500, step=100)
    user_prompt = st.text_area("Enter your prompt here:", value="", height=100)

    if user_prompt:
        stream = True
        response = get_llm_response(user_prompt, max_output_token, stream=stream)
        show_response(response, stream)




