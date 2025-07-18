
import streamlit as st

# Sidebar Navigation
page = st.sidebar.selectbox("📊 Select Report", ["Home", "Talley"])

if page == "Home":
    st.title("🏠 Welcome to Pioneer Dashboard")
    st.markdown("""
    Use the sidebar to select a specific report.
    """)

elif page == "Talley":
    # Run the Talley dashboard
    exec(open("dashboard.py").read())
