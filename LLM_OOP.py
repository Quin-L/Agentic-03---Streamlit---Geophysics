from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from css import *
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
    Auto-generate a prompt whenever new data is uploaded.
    """
    prompt = """
            You are provided with raw geophysics data from field surveys. Perform a comprehensive initial data analysis.
            You need to be precise about your assessments.
            
            ## 1. DATA OVERVIEW (2-3 sentences maximum)
            Identify and describe:
            - Dataset type (seismic, gravity, magnetic, resistivity, GPR, etc.)
            - Total number of records/samples and key parameters measured

            ## 2. POTENTIAL ISSUES
            Systematically going through each dataset to identify issues.
            - **Duplicate records**: Count and percentage of duplicates if found
            - **Inconsistent data formats**: Note any mixed units, inconsistent date formats
            Provide a list of identified issues with exact geophysics line or data file references. (e.g., 162-2P1 DD') You have to go through each dataset systematically to identify issues.

            ---
            **Response Guidelines:**
            - Maximum 200 words total (strict limit)
            - Prioritize actionable insights over generic descriptions
            - Always include quantitative metrics: percentages, counts, ranges, statistical measures
            - Skip or minimize sections where no significant findings exist
            - Use bullet points for clarity and scannability
            - Be specific: instead of "some missing data", say "12.5% missing in elevation column"
            - Always provide exact data file or geophysics line when there is a findings
            """
    return prompt


def token_settings_and_controls():
    with st.expander("⚙️ Token Settings and controls", expanded=False):
        col1, col2, col3 = st.columns([8, 0.5, 2])
        with col1:
            max_output_token = st.slider("Max output tokens:", min_value=100, max_value=1000, value=500, step=100)
        with col3:
            adjust_button_font_size()
            if st.button("CLEAR"):
                st.session_state.chat_messages = []
                st.rerun()
    return max_output_token


def chatbot_section():
    """Simple chatbot section with text area input and response display"""

    st.header("Chatbot")
    max_output_token = token_settings_and_controls()
    user_prompt = st.text_area("Enter your prompt here:", value="", height=100)

    if user_prompt:
        stream = True
        response = get_llm_response(user_prompt, max_output_token, stream=stream)
        show_response(response, stream)


def chatbot_chat_interface(prompt, geophysics_data, initial_prompt):
    """
    ChatGPT-style chat interface with message bubbles and conversation history
    """

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

    # Check if this is an auto-prompt trigger
    is_auto_prompt = st.session_state.get('trigger_auto_prompt', False) and not prompt

    if is_auto_prompt:
        prompt = initial_prompt
        st.session_state.trigger_auto_prompt = False

    if prompt:
        history_context = "\n".join(f"{message['role'].upper()}:{message['content']}" for message in st.session_state.chat_messages[-5:])

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

        # Only display user message if NOT auto-prompt
        if not is_auto_prompt:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Get and display assistant response with streaming
        with st.chat_message("assistant"):
            response = get_llm_response(adjusted_prompt, max_output_token, stream=True)
            full_response = show_response(response, stream=True)

        # Only add to history if NOT auto-prompt
        # if not is_auto_prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
     

