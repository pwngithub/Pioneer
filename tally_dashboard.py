
import streamlit as st
import pandas as pd
from utils import fetch_jotform_data, preprocess_data

FORM_ID = "240073839937062"  # Replace with actual tally form ID

def load_data():
    data = fetch_jotform_data(FORM_ID, 'ba9013143bfda3a448297144c0527f7e')
    df = preprocess_data(data)
    return df

def run(df):
    st.title("Tally Dashboard")
    st.dataframe(df)
