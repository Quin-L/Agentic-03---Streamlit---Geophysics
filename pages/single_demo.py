import streamlit as st


def show():
    next_step = """
    ### 1. Data has been presented in data page, then next step is to prepare the data and clean the data. 
    ### 2. After data preparation, we can do single analysis on selected data file.
    ### 3. Finally, we can do multiple analysis on multiple data files.
    ### 4. Note that we are following the jupyter notebook workflow here.

    ### For data page, maybe we can use edit dataframe instead of just showing dataframe?

    ### give geospatial filtering options for data files that have location info?
"""
    st.write(next_step)

