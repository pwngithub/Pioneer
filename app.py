
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Tech Workflow Summary", layout="wide")

st.title("📊 Tech Daily and Overall Summary by Work Type")

uploaded_file = st.file_uploader("Upload Technician Workflow CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["Date When"] = pd.to_datetime(df["Date When"], errors="coerce")
    df = df.dropna(subset=["Date When"])
    df["Day"] = df["Date When"].dt.date

    df_daily = df.groupby(["Techinician", "Day", "Work Type"]).agg(
        Jobs_Completed=("WO#", "nunique"),
        Total_Entries=("WO#", "count"),
        Unique_Statuses=("Tech Status", pd.Series.nunique),
        Average_Duration=("Duration", lambda x: pd.to_numeric(x.str.extract(r"(\d+\.?\d*)")[0], errors="coerce").mean())
    ).reset_index()

    df_overall = df.groupby(["Techinician", "Work Type"]).agg(
        Total_Jobs=("WO#", "nunique"),
        Total_Entries=("WO#", "count"),
        Unique_Statuses=("Tech Status", pd.Series.nunique),
        Average_Duration=("Duration", lambda x: pd.to_numeric(x.str.extract(r"(\d+\.?\d*)")[0], errors="coerce").mean())
    ).reset_index()

    df_company_avg = df.groupby("Work Type").agg(
        Total_Jobs=("WO#", "nunique"),
        Average_Duration=("Duration", lambda x: pd.to_numeric(x.str.extract(r"(\d+\.?\d*)")[0], errors="coerce").mean())
    ).reset_index()

    work_types = sorted(df["Work Type"].dropna().unique())
    technicians = sorted(df["Techinician"].dropna().unique())

    selected_types = st.multiselect("Filter by Work Type", work_types, default=work_types)
    selected_techs = st.multiselect("Filter by Technician", technicians, default=technicians)

    st.subheader("📅 Daily Summary by Work Type")
    filtered_daily = df_daily[
        (df_daily["Work Type"].isin(selected_types)) & (df_daily["Techinician"].isin(selected_techs))
    ]
    st.dataframe(filtered_daily, use_container_width=True)

    st.subheader("📈 Overall Average Summary by Work Type")
    filtered_overall = df_overall[
        (df_overall["Work Type"].isin(selected_types)) & (df_overall["Techinician"].isin(selected_techs))
    ]
    st.dataframe(filtered_overall, use_container_width=True)

    st.subheader("📊 Charts")

    chart1 = alt.Chart(filtered_overall).mark_bar().encode(
        x="Work Type:N",
        y="Total_Jobs:Q",
        color="Techinician:N",
        tooltip=["Techinician", "Work Type", "Total_Jobs"]
    ).properties(title="Total Jobs by Work Type")

    chart2 = alt.Chart(filtered_overall).mark_bar().encode(
        x="Work Type:N",
        y="Average_Duration:Q",
        color="Techinician:N",
        tooltip=["Techinician", "Work Type", "Average_Duration"]
    ).properties(title="Average Duration by Work Type")

    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(chart2, use_container_width=True)

    st.subheader("🏢 Company Average Chart by Work Type")

    filtered_company_avg = df_company_avg[df_company_avg["Work Type"].isin(selected_types)]

    chart3 = alt.Chart(filtered_company_avg).mark_bar().encode(
        x="Work Type:N",
        y="Average_Duration:Q",
        tooltip=["Work Type", "Average_Duration"]
    ).properties(title="Company Average Duration by Work Type")

    st.altair_chart(chart3, use_container_width=True)

    st.subheader("📤 Export Filtered Data")
    csv = filtered_overall.to_csv(index=False).encode("utf-8")
    st.download_button("Download Overall Summary as CSV", data=csv, file_name="filtered_overall_summary.csv", mime="text/csv")
