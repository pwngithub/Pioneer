
import streamlit as st

st.set_page_config(page_title="Pioneer Dashboard", layout="wide")

st.sidebar.title("📊 Reports")
report = st.sidebar.selectbox(
    "Select a Report",
    ["Home", "Tally", "Construction", "Work Orders", "Installs", "Financial / Customer Insights"]
)

if report == "Home":
    st.markdown(
        "<div style='text-align:center;'><img src='https://images.squarespace-cdn.com/content/v1/651eb4433b13e72c1034f375/369c5df0-5363-4827-b041-1add0367f447/PBB+long+logo.png?format=1500w' width='500'></div>",
        unsafe_allow_html=True
    )
    st.title("Welcome to Pioneer Dashboard")
    st.write("Use the sidebar to open a report.")

elif report == "Tally":
    try:
        import tally_dashboard as tally_dashboard
        # Expect tally_dashboard.run(df) signature; since live fetch was in old app, show a friendly note
        st.info("Tally report module found. If this errors, we may need the original data loader.")
        # If you have a data loader here, call it and pass df to tally_dashboard.run(df)
    except Exception as e:
        st.error(f"Could not load Tally report: {e}")

elif report == "Construction":
    try:
        import construction as construction
        construction.run_construction_dashboard()
    except Exception as e:
        st.error(f"Could not load Construction report: {e}")

elif report == "Work Orders":
    try:
        import workorders as workorders
        workorders.run_workorders_dashboard()
    except Exception as e:
        st.error(f"Could not load Work Orders report: {e}")

elif report == "Installs":
    try:
        import install as install
        install.run_installs_dashboard()
    except Exception as e:
        st.error(f"Could not load Installs report: {e}")

elif report == "Financial / Customer Insights":
    try:
        import financial_dashboard as fd
        fd.run_financial_dashboard()
    except Exception as e:
        st.error(f"Could not load Financial dashboard: {e}")
