from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from css import *

load_dotenv()
client = OpenAI()

def get_analysis_instructions():
    """
    Get system instructions for comprehensive data analysis.
    Used in system_content for LLM, not displayed to user.
    """
    instructions = """
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
    return instructions

def auto_prompt():
    """
    Get user-friendly prompt text for auto-triggered analysis.
    Displayed to user when files are uploaded.
    """
    auto_prompt = """
        1. Analyze the uploaded geophysics data and identify any issues or anomalies.
        2. Check for data inconsistency across different files, especially focusing on the column names, some data may not have the same column names, and this would be problematic and would require user intervention to fix them.
            - Get understanding  of what is the most likely column names for common geophysics data
            - The length of column should be the same across all files, if not, flag this as a potential issue.
            - This should be done based on what column headings appears the most across all uploaded files.
            - Identify and missing or inconsistent column names across different files as compared to the most common column names, and suggest me which file has the issue.
        3. Check into details of each column, and suggest the range of the data, and these information should be used to compared against typical expected ranges across the majority of geophysics data.
            - For example, if depth / elevation values are expected to be between 0-100m, but one file has depth values ranging from 0-1000m, flag this as a potential issue.
            - For example, if easting and northing values are expected to be within a certain coordinate system range, but one file has values outside this range, flag this as a potential issue.
            - For example, if velocity values are expected to be within typical geophysics survey ranges, but one file has values that are significantly higher or lower, flag this as a potential issue.
        4. Easting and northing values, and elevation values should also be checked for consistency.
        5. Summarize your findings and suggest next steps for data cleaning or validation.
    """

    return auto_prompt


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


def chatbot_chat_interface(prompt, geophysics_data, initial_prompt):
    """
    ChatGPT-style chat interface with message bubbles and conversation history
    """

    st.header("💬 AI Assistant")
    st.subheader("!!! Note, chat history is preserved, agent short term memory up to 5 messages.")
    max_output_token = token_settings_and_controls()

    # Display all existing chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Check if this is an auto-prompt trigger
    trigger_flag = st.session_state.get('trigger_auto_prompt', False)
    is_auto_prompt = trigger_flag and not prompt

    if is_auto_prompt:
        prompt = initial_prompt

    if prompt:
        adjusted_prompt = f"""
        User query: {prompt}
        """

        # Use analysis instructions if auto-prompt, otherwise use general instructions
        if is_auto_prompt:
            analysis_instructions = get_analysis_instructions()
        else:
            analysis_instructions = ""

        # Build data summary for the system message
        data_summary = ""
        if geophysics_data.keys():
            data_summary = "AVAILABLE GEOPHYSICS DATA:\n"
            for key in geophysics_data.keys():
                df = geophysics_data[key]
                data_summary += f"\n- Dataset: {key}\n"
                data_summary += f"  Rows: {len(df)}, Columns: {len(df.columns)}\n"
                data_summary += f"  Column names: {', '.join(df.columns.tolist())}\n"
                data_summary += f"  Data types: {df.dtypes.to_dict()}\n"
        else:
            data_summary = "No datasets currently loaded."

        system_content = f"""
        You are an expert specialized in geotechnical engineering, geophysics, data processing, and Python programming.
        Your primary task is to assist the user by analyzing geophysics data and answering technical questions within these fields.

        {data_summary}

        For questions within your expertise (geotechnical engineering, geophysics, data processing, Python):
        - Provide thorough, detailed answers
        - Analyze data when requested
        - Help with technical problems and explanations

        If a user asks about topics completely unrelated to your fields of expertise (sports, politics, entertainment, etc.),
        politely explain that you specialize in geotechnical engineering, geophysics, data processing, and Python programming.

        {analysis_instructions}
        """

        history_message = []
        for message in st.session_state.chat_messages[-5:]:
            history_message.append({"role": message["role"], "content": message["content"]})

        # Only display user message if NOT auto-prompt
        if not is_auto_prompt:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Get and display assistant response with streaming
        with st.chat_message("assistant"):
            response = get_llm_response(adjusted_prompt, history_message, system_content, max_output_token, stream=True)
            full_response = show_response(response, stream=True)

        # Add to history (skip user message for auto-prompt to keep it silent)
        if not is_auto_prompt:
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.chat_messages.append({"role": "assistant", "content": full_response})

        # Clear auto-prompt flag after processing completes
        if is_auto_prompt:
            st.session_state.trigger_auto_prompt = False

        st.rerun()


def get_llm_response(prompt, history_message, system_content, max_output_token, stream=False):
    with st.spinner("Generating response..."):
        messages = [{"role": "system",  "content": system_content}]
        messages.extend(history_message)
        messages.append({"role": "user", "content": prompt})

        response = client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            max_output_tokens=max_output_token,
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
