import streamlit as st
from utils import fetch_jotform_data
import pandas as pd
import plotly.express as px

FORM_ID = "240207529846156"

def run():
    st.title("Construction Dashboard")

    api_key = st.secrets["JOTFORM_API_KEY"]
    data = fetch_jotform_data(FORM_ID, api_key)
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No data available.")
        return

    # Basic preprocessing
    df["date"] = pd.to_datetime(df.get("date", pd.NaT), errors="coerce")
    df["employee"] = df.get("employee", "")
    df["location"] = df.get("location", "")
    df["project"] = df.get("project", "")
    df["footage"] = pd.to_numeric(df.get("footage", 0), errors="coerce")
    df["closures"] = pd.to_numeric(df.get("closures", 0), errors="coerce")

    # Sidebar filters
    with st.sidebar:
        st.subheader("Filters")
        selected_employee = st.multiselect("Employee", df["employee"].dropna().unique(), default=list(df["employee"].dropna().unique()))
        selected_location = st.multiselect("Location", df["location"].dropna().unique(), default=list(df["location"].dropna().unique()))
        selected_project = st.multiselect("Project", df["project"].dropna().unique(), default=list(df["project"].dropna().unique()))
        start_date = st.date_input("Start Date", df["date"].min().date() if not df["date"].isna().all() else None)
        end_date = st.date_input("End Date", df["date"].max().date() if not df["date"].isna().all() else None)

    # Apply filters
    if start_date and end_date:
        mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
        df = df.loc[mask]
    df = df[df["employee"].isin(selected_employee)]
    df = df[df["location"].isin(selected_location)]
    df = df[df["project"].isin(selected_project)]

    st.markdown("### Summary")
    st.metric("Total Footage", f'{df["footage"].sum():,.0f}')
    st.metric("Total Closures", f'{df["closures"].sum():,.0f}')

    st.markdown("### Daily Production by Employee")
    daily_summary = df.groupby(["date", "employee"])[["footage", "closures"]].sum().reset_index()
    fig = px.bar(daily_summary, x="date", y="footage", color="employee", title="Footage by Day and Employee", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Raw Data")
    st.dataframe(df)

    # Export option
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "construction_filtered.csv", "text/csv")