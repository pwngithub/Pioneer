from utils import fetch_jotform_data

def load_data():
    form_id = "240073839937062"  # Replace if needed
    return fetch_jotform_data(form_id)

def run(df):
    import streamlit as st
    import pandas as pd
    import plotly.express as px

    st.header("Tally Report")
    st.dataframe(df)

    if df.empty:
        st.warning("No data available.")
        return

    # Example KPI
    st.metric("Total Records", len(df))

    # Optional chart
    if "date" in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        count_by_day = df.groupby(df['date'].dt.date).size().reset_index(name='count')
        fig = px.bar(count_by_day, x='date', y='count', title='Submissions by Date')
        st.plotly_chart(fig)