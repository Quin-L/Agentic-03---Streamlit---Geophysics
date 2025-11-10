import streamlit as st
from LLM_OOP import *
import pandas as pd

# =========== Login Page ===========
def login_page(page_title):
    col1, col2, col3 = st.columns([0.9, 1.1, 0.9])
    with col2:
        if not st.session_state['password_correct']:
            adjust_title_font_size(32, "#D52020")
            st.title(page_title)
            st.write("")
            st.write("")
            st.text_input(
                label="Password",
                label_visibility="hidden",
                type="password",
                key="password_input",
                on_change=check_password,
                width=580,
                placeholder="Enter your password to access the app"
                )

            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.divider()
            # st.write("quin.li@eicactiv.com")
            st.stop()


def check_password():
        """Check user input and store login status"""

        PASSWORD = "1"

        if st.session_state["password_input"] == PASSWORD:
            st.session_state['password_correct'] = True
            del st.session_state["password_input"]
        else:
            st.error("😕 Incorrect password. Try again.")

# =========== Sidebar Components ===========
def sidebar():
    # sidebar_info()
    # sidebar_warning()
    # sidebar_error()
    # sidebar_success("Data processed successfully!")

    st.sidebar.title("Data Upload and Settings")
    upload_geophysics_file()

def sidebar_info():
    st.sidebar.info(
        """
        **Note:** This application is designed for geophysics data processing and analysis.
        Please ensure that the uploaded data files are in the correct format (CSV).
        For any issues or suggestions, feel free to contact the developer.
        """
    )

def sidebar_warning():
    st.sidebar.warning(
        """
        **Warning:** Make sure to upload only CSV files.
        Uploading unsupported file types may lead to errors in data processing.
        """
    )

def sidebar_error():
    st.sidebar.error(
        """
        **Error:** An unexpected error occurred.
        Please check the uploaded files and try again.
        If the problem persists, contact support for assistance.
        """
    )

def sidebar_success(message):
    st.sidebar.success(
        f"""
        **Success:** {message}
        """
    )

def upload_geophysics_file():
    uploaded = st.sidebar.file_uploader(
        label="Geophysics data",
        type=["csv"],
        accept_multiple_files=True,
        width=180,
        key="geophysics_uploader"
    )

    if uploaded:
        existing_names = {f.name for f in st.session_state.get('uploaded_files', [])}
        new_files = [f for f in uploaded if f.name not in existing_names]


        if new_files:
            # Append only new files
            current_files = st.session_state.get('uploaded_files', [])
            st.session_state['uploaded_files'] = current_files + new_files

    elif 'uploaded_files' not in st.session_state:
        st.session_state['uploaded_files'] = []

# =========== Data page utils ===========
def get_uploaded_data():
    uploaded_files = st.session_state.get('uploaded_files', [])
    if 'all_geophysics' not in st.session_state:
        st.session_state['all_geophysics'] = {'geophysics_data': {}}

    all_geophysics = st.session_state['all_geophysics']
    geophysics_data = all_geophysics['geophysics_data']

    return uploaded_files, geophysics_data

def display_uploaded_data(uploaded_files, geophysics_data):
    # uploaded_files, geophysics_data = get_uploaded_data()

    if len(uploaded_files) == 0:
        st.warning("No data uploaded yet. Please upload CSV files in the sidebar.")

    elif len(uploaded_files) > 0:
        st.header(f"🗃️ Uploaded Files ({len(uploaded_files)} in total):")
        number_of_columns = st.slider("Number of columns to display", min_value=1, max_value=8, value=3, step=1)
        cols = st.columns(number_of_columns)

        for idx, uploaded_file in enumerate(uploaded_files):
            col_idx = idx % number_of_columns
            with cols[col_idx]:

                uploaded_filename = uploaded_file.name.rstrip(".csv")

                if uploaded_filename not in geophysics_data.keys():
                    try:
                        geophysics_data[uploaded_filename] = pd.read_csv(uploaded_file)
                    except Exception as e:
                        st.error(f"Error loading {uploaded_file.name}: {e}")
                        continue

                st.write(f"{idx+1}, {uploaded_file.name}")
                if uploaded_filename in geophysics_data.keys():
                    st.dataframe(geophysics_data[uploaded_filename].head(20))

def check_file_changes(geophysics_data):
    current_files = list(geophysics_data.keys())

    # Initialize on first run
    if 'previous_files' not in st.session_state:
        st.session_state['previous_files'] = []

    # Check if this is initial upload (previous was empty, now has files)
    was_empty = len(st.session_state['previous_files']) == 0
    has_files_now = len(current_files) > 0
    is_initial_upload = was_empty and has_files_now

    # Check if files changed
    files_changed = current_files != st.session_state['previous_files'] and len(current_files) > 0

    # Trigger auto-prompt on initial upload OR when files change
    if is_initial_upload or files_changed:
        st.session_state.trigger_auto_prompt = True
        st.session_state.previous_files = current_files.copy()
    else:
        st.session_state.trigger_auto_prompt = False







