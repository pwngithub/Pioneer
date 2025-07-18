
import streamlit as st

page = st.sidebar.selectbox("📊 Select Report", ["Home", "Talley"])

if page == "Home":
    st.title("🏠 Welcome to Pioneer Dashboard")
    st.markdown("""
    Use the sidebar to select a specific report.
    """)

elif page == "Talley":
    import dashboard
    dashboard.run_dashboard()
