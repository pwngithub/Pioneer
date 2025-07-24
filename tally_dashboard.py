
import pandas as pd
import streamlit as st
import plotly.express as px
from utils import fetch_jotform_data, preprocess_data

def load_data():
    form_id = "240073839937062"  # Replace with the correct form ID for Tally
    raw_data = fetch_jotform_data(form_id)
    df = preprocess_data(raw_data)
    return df

def run(df):
    st.title("Tally Report")
    if df.empty:
        st.warning("No data available.")
        return
    st.dataframe(df)
    # Add basic KPI examples (can be replaced by more logic)
    st.metric("Total Records", len(df))
