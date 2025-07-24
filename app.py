
import streamlit as st
import tally_dashboard
import construction
import splicing

st.set_page_config(layout="wide", page_title="Pioneer Dashboard")
st.title("📊 Pioneer Broadband Dashboard")

report = st.sidebar.selectbox("Select Report", ["Tally", "Construction", "Splicing"])

if report == "Tally":
    df = tally_dashboard.load_data()
    tally_dashboard.run(df)
elif report == "Construction":
    construction.run()
elif report == "Splicing":
    splicing.run()
