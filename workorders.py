
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

def run_workorders_dashboard():
    st.set_page_config(page_title="Tech Workflow Summary", layout="wide")

    st.markdown("<div style='text-align:center;'><img src='https://images.squarespace-cdn.com/content/v1/651eb4433b13e72c1034f375/369c5df0-5363-4827-b041-1add0367f447/PBB+long+logo.png?format=1500w' width='600'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#405C88;'>🛠️ Technician Work Order Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("This report summarizes technician activity, job counts, durations, and status variety using daily and overall metrics from uploaded work order data.")

    uploaded_file = st.file_uploader("Upload Technician Workflow CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df["Date When"] = pd.to_datetime(df["Date When"], errors="coerce")
        df = df.dropna(subset=["Date When"])
        df["Day"] = df["Date When"].dt.date

        min_day = df["Day"].min()
        max_day = df["Day"].max()
        start_date, end_date = st.date_input("📅 Filter by Date Range", [min_day, max_day], min_value=min_day, max_value=max_day)

        work_types = sorted(df["Work Type"].dropna().unique())
        technicians = sorted(df["Techinician"].dropna().unique())

        selected_types = st.multiselect("Filter by Work Type", work_types, default=work_types)
        selected_techs = st.multiselect("Filter by Technician", technicians, default=technicians)

        mask = (
            (df["Work Type"].isin(selected_types)) &
            (df["Techinician"].isin(selected_techs)) &
            (df["Day"] >= start_date) & (df["Day"] <= end_date)
        )
        filtered_df = df[mask]

        # KPI Metrics
        st.markdown("### 📌 Key Performance Indicators")
        col1, col2, col3 = st.columns(3)
        col1.metric("🔧 Total Jobs Completed", filtered_df["WO#"].nunique())
        col2.metric("🕒 Average Duration", f"{pd.to_numeric(filtered_df['Duration'].str.extract(r'(\d+\.?\d*)')[0], errors='coerce').mean():.2f} hrs")
        col3.metric("📋 Unique Tech Statuses", filtered_df["Tech Status"].nunique())

        st.markdown("---")

        # Daily Summary
        st.subheader("📅 Daily Summary by Work Type")
        df_daily = filtered_df.groupby(["Techinician", "Day", "Work Type"]).agg(
            Jobs_Completed=("WO#", "nunique"),
            Total_Entries=("WO#", "count"),
            Unique_Statuses=("Tech Status", pd.Series.nunique),
            Average_Duration=("Duration", lambda x: pd.to_numeric(x.str.extract(r'(\d+\.?\d*)')[0], errors="coerce").mean())
        ).reset_index()
        st.dataframe(df_daily, use_container_width=True)

        # Overall Summary
        st.subheader("📈 Overall Average Summary by Work Type")
        df_overall = filtered_df.groupby(["Techinician", "Work Type"]).agg(
            Total_Jobs=("WO#", "nunique"),
            Total_Entries=("WO#", "count"),
            Unique_Statuses=("Tech Status", pd.Series.nunique),
            Average_Duration=("Duration", lambda x: pd.to_numeric(x.str.extract(r'(\d+\.?\d*)')[0], errors="coerce").mean())
        ).reset_index()
        st.dataframe(df_overall, use_container_width=True)

        # Charts
        st.markdown("### 📊 Visualizations")

        fig_jobs = px.bar(
            df_overall,
            x="Work Type",
            y="Total_Jobs",
            color="Techinician",
            title="Total Jobs by Work Type",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_jobs, use_container_width=True)

        fig_duration = px.bar(
            df_overall,
            x="Work Type",
            y="Average_Duration",
            color="Techinician",
            title="Average Duration by Work Type",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_duration, use_container_width=True)

        # Company Average
        st.subheader("🏢 Company-Wide Averages")
        df_company_avg = filtered_df.groupby("Work Type").agg(
            Total_Jobs=("WO#", "nunique"),
            Average_Duration=("Duration", lambda x: pd.to_numeric(x.str.extract(r'(\d+\.?\d*)')[0], errors="coerce").mean())
        ).reset_index()

        fig_company = px.bar(
            df_company_avg,
            x="Work Type",
            y="Average_Duration",
            title="Company Average Duration by Work Type",
            color="Work Type",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_company, use_container_width=True)

        # Export
        st.subheader("📤 Export Filtered Data")
        csv = df_overall.to_csv(index=False).encode("utf-8")
        st.download_button("Download Overall Summary as CSV", data=csv, file_name="filtered_overall_summary.csv", mime="text/csv")
