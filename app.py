
import streamlit as st
import tally_dashboard
import construction
import splicing

st.set_page_config(layout="wide", page_title="Pioneer Dashboard")

st.title("Pioneer Broadband Dashboard")

menu = ["Home", "Tally", "Construction", "Splicing"]
choice = st.sidebar.selectbox("Select Report", menu)

if choice == "Home":
    st.markdown("### Welcome to the Pioneer Broadband Dashboard")
elif choice == "Tally":
    df = tally_dashboard.load_data()
    tally_dashboard.run(df)
elif choice == "Construction":
    construction.run()
elif choice == "Splicing":
    splicing.run()
