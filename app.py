import streamlit as st
import tally_dashboard
import construction
import splicing

st.set_page_config(layout="wide")
st.sidebar.image("https://pioneerbroadband.net/img/logo.svg", use_column_width=True)

report = st.sidebar.selectbox(
    "📊 Select Report",
    ["Home", "Tally", "Construction", "Work Orders", "Splicing"]
)

if report == "Home":
    st.title("🏠 Welcome to Pioneer Dashboard")
    st.markdown("Use the sidebar to select a specific report.")

elif report == "Tally":
    df = tally_dashboard.load_data()
    tally_dashboard.run(df)

elif report == "Construction":
    construction.run_construction_dashboard()

elif report == "Splicing":
    splicing.run()