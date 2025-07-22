
import streamlit as st

report = st.sidebar.selectbox("Select Report", ["Tally", "Construction", "Work Orders"])

if report == "Tally":
    import dashboard
    dashboard.run_dashboard()
elif report == "Construction":
    import construction
    construction.run_construction_dashboard()
elif report == "Work Orders":
    import workorders
    workorders.run_workorders_dashboard()
