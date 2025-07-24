
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_jotform_data

def run():
    st.title("Splicing Dashboard")

    # Fetch data from JotForm API
    form_id = "251683946561164"
    data = fetch_jotform_data(form_id)

    if data.empty:
        st.warning("No data available from JotForm API.")
        return

    # Convert date column
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    # Filters
    with st.sidebar:
        st.subheader("Filters")
        start_date = st.date_input("Start Date", value=data["Date"].min())
        end_date = st.date_input("End Date", value=data["Date"].max())
        technicians = st.multiselect("Technician", data["Technician Name"].dropna().unique(), default=data["Technician Name"].dropna().unique())
        other_employees = st.multiselect("Other Employee", data["Other Employee"].dropna().unique(), default=data["Other Employee"].dropna().unique())
        closure_types = st.multiselect("Closure Type", data["Closure Type"].dropna().unique(), default=data["Closure Type"].dropna().unique())
        splice_types = st.multiselect("Splice Type", data["Splice Type"].dropna().unique(), default=data["Splice Type"].dropna().unique())
        projects = st.multiselect("Project", data["Project"].dropna().unique(), default=data["Project"].dropna().unique())

    # Apply filters
    mask = (
        (data["Date"].dt.date >= start_date) &
        (data["Date"].dt.date <= end_date) &
        (data["Technician Name"].isin(technicians)) &
        (data["Other Employee"].isin(other_employees)) &
        (data["Closure Type"].isin(closure_types)) &
        (data["Splice Type"].isin(splice_types)) &
        (data["Project"].isin(projects))
    )
    filtered_data = data[mask]

    # KPI metrics
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Splice Events", len(filtered_data))
    col2.metric("Total FATs", filtered_data["Closure Type"].str.contains("FAT", case=False, na=False).sum())
    col3.metric("Total SCs", filtered_data["Closure Type"].str.contains("SC", case=False, na=False).sum())
    col4.metric("Total Splice Count", pd.to_numeric(filtered_data["Splice Count"], errors="coerce").fillna(0).sum())

    # Charts
    st.subheader("Closure Type by Splice Type")
    ct_st = filtered_data.groupby(["Closure Type", "Splice Type"]).agg(Splice_Count=("Splice Count", "sum")).reset_index()
    fig1 = px.bar(ct_st, x="Closure Type", y="Splice_Count", color="Splice Type", barmode="group", title="Closure Type by Splice Type")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Splice Count by Technician by Day")
    filtered_data["Day"] = filtered_data["Date"].dt.date
    tech_day = filtered_data.groupby(["Day", "Technician Name"]).agg(Splice_Count=("Splice Count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum())).reset_index()
    fig2 = px.bar(tech_day, x="Day", y="Splice_Count", color="Technician Name", barmode="group", title="Technician Daily Splice Count")
    st.plotly_chart(fig2, use_container_width=True)

    # Export
    st.subheader("Export Filtered Data")
    st.download_button("Download CSV", filtered_data.to_csv(index=False), "splicing_filtered.csv", "text/csv")

