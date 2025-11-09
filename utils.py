import streamlit as st
from LLM_OOP import *
import pandas as pd

def apply_custom_css(
    # ======= Main Content Styling =======
    # Title (h1) styling
    title_font_size=26,
    title_color="#D52020",
    title_font_family="'Arial', sans-serif",
    title_font_weight="bold",

    # Header (h2) styling
    header_font_size=18,
    header_color="#D52020",
    header_font_family="'Arial', sans-serif",
    header_font_weight="600",

    # Subheader (h3) styling
    subheader_font_size=14,
    subheader_color="#D52020",
    subheader_font_family="'Arial', sans-serif",
    subheader_font_weight="bold",

    # Regular text (p) styling
    text_font_size=13,  
    text_color="#000000",
    text_font_family="'Arial', sans-serif",
    text_font_weight="normal",

    # ======= Sidebar Styling =======
    # Sidebar title (h1)
    sidebar_title_font_size=16,
    sidebar_title_color="#D52020",
    sidebar_title_font_family="'Arial', sans-serif",
    sidebar_title_font_weight="bold",

    # Sidebar header (h2)
    sidebar_header_font_size=14,
    sidebar_header_color="#000000",
    sidebar_header_font_family="'Arial', sans-serif",
    sidebar_header_font_weight="600",

    # Sidebar subheader (h3)
    sidebar_subheader_font_size=14,
    sidebar_subheader_color="#000000",
    sidebar_subheader_font_family="'Arial', sans-serif",
    sidebar_subheader_font_weight="normal",

    # Sidebar normal text (p)
    sidebar_write_font_size=11,
    sidebar_write_color="#000000",
    sidebar_write_font_family="'Arial', sans-serif",
    sidebar_write_font_weight="normal",

    # ------ Sidebar - File Uploader Styling ------
    # Drag and drop text ("Drag and drop files here")
    file_uploader_drag_font_size=12,
    file_uploader_drag_color="#000000",
    file_uploader_drag_font_family="'Arial', sans-serif",
    file_uploader_drag_font_weight="normal",

    # Limit text ("Limit 200MB per file • CSV")
    file_uploader_limit_font_size=10,
    file_uploader_limit_color="#666666",
    file_uploader_limit_font_family="'Arial', sans-serif",
    file_uploader_limit_font_weight="normal",

    # Browse files button
    file_uploader_button_font_size=10,
    file_uploader_button_color="#000000",
    file_uploader_button_font_family="'Arial', sans-serif",
    file_uploader_button_font_weight="normal",

    # Sidebar background
    sidebar_bg_color="#F9FBFF"
):
    """
    Apply custom CSS styling to Streamlit app with customizable parameters.

    Parameters example:
    -----------

    Font Families - Examples:
        - "'Arial', sans-serif"
        - "'Helvetica', sans-serif"
        - "'Verdana', sans-serif"
        - "'Georgia', serif"
        - "'Times New Roman', serif"
        - "'Courier New', monospace"
        - "'Trebuchet MS', sans-serif"
        - "'Comic Sans MS', cursive"
        - "system-ui, -apple-system, sans-serif"
    
    Font Weights:
        - Text: "normal", "bold", or numbers 100-900
        - Examples: 300 (light), 400 (normal), 600 (semi-bold), 700 (bold), 900 (black)

    """
    
    st.markdown(
        f"""
        <style>
        /* Main content titles */
        h1 {{
            font-size: {title_font_size}px !important;
            color: {title_color} !important;
            font-family: {title_font_family} !important;
            font-weight: {title_font_weight} !important;
        }}

        /* Main content headers */
        h2 {{
            font-size: {header_font_size}px !important;
            color: {header_color} !important;
            font-family: {header_font_family} !important;
            font-weight: {header_font_weight} !important;
        }}

        /* Main content subheaders */
        h3 {{
            font-size: {subheader_font_size}px !important;
            color: {subheader_color} !important;
            font-family: {subheader_font_family} !important;
            font-weight: {subheader_font_weight} !important;
        }}

        /* Main content regular text */
        p {{
            font-size: {text_font_size}px !important;
            color: {text_color} !important;
            font-family: {text_font_family} !important;
            font-weight: {text_font_weight} !important;
            line-height: 1.6 !important;
        }}

        /* Sidebar background - Updated for modern Streamlit */
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color} !important;
        }}

        section[data-testid="stSidebar"] > div:first-child {{
            background-color: {sidebar_bg_color} !important;
        }}

        /* Sidebar title (h1) */
        section[data-testid="stSidebar"] h1 {{
            font-size: {sidebar_title_font_size}px !important;
            color: {sidebar_title_color} !important;
            font-family: {sidebar_title_font_family} !important;
            font-weight: {sidebar_title_font_weight} !important;
        }}

        /* Sidebar header (h2) */
        section[data-testid="stSidebar"] h2 {{
            font-size: {sidebar_header_font_size}px !important;
            color: {sidebar_header_color} !important;
            font-family: {sidebar_header_font_family} !important;
            font-weight: {sidebar_header_font_weight} !important;
        }}

        /* Sidebar subheader (h3) */
        section[data-testid="stSidebar"] h3 {{
            font-size: {sidebar_subheader_font_size}px !important;
            color: {sidebar_subheader_color} !important;
            font-family: {sidebar_subheader_font_family} !important;
            font-weight: {sidebar_subheader_font_weight} !important;
        }}

        /* Sidebar normal text (p) */
        section[data-testid="stSidebar"] p {{
            font-size: {sidebar_write_font_size}px !important;
            color: {sidebar_write_color} !important;
            font-family: {sidebar_write_font_family} !important;
            font-weight: {sidebar_write_font_weight} !important;
            line-height: 1.5 !important;
        }}

        /* Sidebar markdown text */
        section[data-testid="stSidebar"] .stMarkdown {{
            font-size: {sidebar_write_font_size}px !important;
            color: {sidebar_write_color} !important;
            font-family: {sidebar_write_font_family} !important;
            font-weight: {sidebar_write_font_weight} !important;
        }}

        /* Sidebar lists (ordered and unordered) */
        section[data-testid="stSidebar"] ol,
        section[data-testid="stSidebar"] ul {{
            font-size: {sidebar_write_font_size}px !important;
            color: {sidebar_write_color} !important;
            font-family: {sidebar_write_font_family} !important;
            font-weight: {sidebar_write_font_weight} !important;
        }}

        /* Sidebar list items */
        section[data-testid="stSidebar"] li {{
            font-size: {sidebar_write_font_size}px !important;
            color: {sidebar_write_color} !important;
            font-family: {sidebar_write_font_family} !important;
            font-weight: {sidebar_write_font_weight} !important;
            line-height: 1.5 !important;
        }}

        /* ======= Sidebar File Uploader Specific Styling ======= */

        /* Drag and drop text */
        section[data-testid="stSidebar"] .st-emotion-cache-ycmcfb.e16n7gab3 {{
            font-size: {file_uploader_drag_font_size}px !important;
            color: {file_uploader_drag_color} !important;
            font-family: {file_uploader_drag_font_family} !important;
            font-weight: {file_uploader_drag_font_weight} !important;
        }}

        /* Limit text ("Limit 200MB per file • CSV") */
        section[data-testid="stSidebar"] .st-emotion-cache-1sct1q3.e16n7gab4 {{
            font-size: {file_uploader_limit_font_size}px !important;
            color: {file_uploader_limit_color} !important;
            font-family: {file_uploader_limit_font_family} !important;
            font-weight: {file_uploader_limit_font_weight} !important;
        }}

        /* Browse files button - using data-testid (more stable) */
        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {{
            font-size: {file_uploader_button_font_size}px !important;
            color: {file_uploader_button_color} !important;
            font-family: {file_uploader_button_font_family} !important;
            font-weight: {file_uploader_button_font_weight} !important;
        }}

        /* Browse files button - using Emotion classes (fallback) */
        section[data-testid="stSidebar"] button.st-emotion-cache-18b91qn.etdmgzm2 {{
            font-size: {file_uploader_button_font_size}px !important;
            color: {file_uploader_button_color} !important;
            font-family: {file_uploader_button_font_family} !important;
            font-weight: {file_uploader_button_font_weight} !important;
        }}

        /* Hide file list that appears after file uploader widget */
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] ul {{
            display: none !important;
        }}

        /* Hide pagination text "Showing page X of Y" */
        section[data-testid="stSidebar"] small {{
            display: none !important;
        }}

        /* Hide pagination arrow buttons (< and >) */
        section[data-testid="stSidebar"] button[data-testid="stBaseButton-minimal"] {{
            display: none !important;
        }}

        /* Chat message alignment - ChatGPT style */
        /* Target user messages - align to right */
        div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
            justify-content: flex-end !important;
            flex-direction: row-reverse !important;
            margin-left: auto !important;
            margin-right: 0 !important;
        }}

        /* Target the message content within user messages */
        div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) > div {{
            text-align: right !important;
            margin-left: auto !important;
        }}

        /* Target assistant messages - align to left */
        div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
            justify-content: flex-start !important;
            flex-direction: row !important;
            margin-left: 0 !important;
            margin-right: auto !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def adjust_title_font_size(size_px = 30, color = "#D52020"):
    """Adjust the font size of all h1 titles in the app."""
    st.markdown(
        f"""<style>
        h1 {{
            font-size: {size_px}px !important;
            color: {color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def adjust_text_font_size(size_px = 14, color = "#FF0000"):
    """Adjust the font size of all p texts in the app."""
    st.markdown(
        f"""<style>
        p {{
            font-size: {size_px}px !important;
            color: {color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def adjust_button_font_size(size_px=8, height_px=50, color="#E91111", font_weight="bold"):
    """Adjust the font size, height, and styling of buttons in the app."""
    st.markdown(
        f"""<style>
        /* Target the button's parent container - align vertically */
        div[data-testid="stButton"] {{
            vertical-align: middle !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        /* Target buttons by data-testid attribute - most specific */
        button[data-testid*="stBaseButton"] {{
            height: {height_px}px !important;
            min-height: {height_px}px !important;
            # padding: 0.5rem 1rem !important;
            vertical-align: middle !important;
        }}

        /* Target the p tag inside buttons */
        button[data-testid*="stBaseButton"] p {{
            font-size: {size_px}px !important;
            color: {color} !important;
            font-weight: {font_weight} !important;
            margin: 0 !important;
            vertical-align: middle !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# =========== Login Page ===========
def login_page(page_title):
    col1, col2, col3 = st.columns([1, 3, 1])
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

def token_settings_and_controls():
    with st.expander("⚙️ Token Settings and controls", expanded=True):
        col1, col2, col3 = st.columns([8, 0.5, 2])
        with col1:
            max_output_token = st.slider("Max output tokens:", min_value=100, max_value=1000, value=500, step=100)
        with col3:
            adjust_button_font_size()
            if st.button("CLEAR"):
                st.session_state.chat_messages = []
                st.rerun()
    return max_output_token








