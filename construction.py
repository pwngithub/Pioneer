
def run_construction_dashboard():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import json
    import requests

    st.title("Construction Dashboard")

    def load_from_jotform():
        api_key = "22179825a79dba61013e4fc3b9d30fa4"
        form_id = "230173417525047"
        url = f"https://api.jotform.com/form/{form_id}/submissions?apiKey={api_key}&limit=1000"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        submissions = []
        for item in data["content"]:
            answers = item.get("answers", {})
            submission_date = item.get("created_at", None)
            record = {"Submission Date": submission_date}
            for ans in answers.values():
                name = ans.get("name")
                answer = ans.get("answer")
                if name and answer is not None:
                    record[name] = answer
            submissions.append(record)
        
        df = pd.DataFrame(submissions)
        return df

    df = load_from_jotform()
    df.columns = df.columns.str.strip()
    df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")
    df = df.dropna(subset=["Submission Date"])

    min_date = df["Submission Date"].min().date()
    max_date = df["Submission Date"].max().date()

    start_date, end_date = st.date_input(
        "📅 Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    df = df[(df["Submission Date"].dt.date >= start_date) & (df["Submission Date"].dt.date <= end_date)]

    selected_projects = st.multiselect(
        "Filter by Project(s)",
        options=df["projectOr"].dropna().unique(),
        default=df["projectOr"].dropna().unique()
    )
    selected_techs = st.multiselect(
        "Filter by Technician(s)",
        options=df["whoFilled"].dropna().unique(),
        default=df["whoFilled"].dropna().unique()
    )

    df = df[df["projectOr"].isin(selected_projects) & df["whoFilled"].isin(selected_techs)]

    def extract_json_footage(df_partial, column, new_col):
        df_out = df_partial.copy()
        df_out[new_col] = 0
        for idx, val in df_out[column].dropna().items():
            try:
                items = json.loads(val)
                for item in items:
                    footage_str = item.get("Footage", "0").replace(",", "").strip()
                    if footage_str.isdigit():
                        df_out.at[idx, new_col] += int(footage_str)
            except:
                continue
        return df_out

    lash_df = extract_json_footage(df[df["typeA45"].notna()], "typeA45", "LashFootage")
    pull_df = extract_json_footage(df[df["fiberPull"].notna()], "fiberPull", "PullFootage")
    strand_df = extract_json_footage(df[df["standInfo"].notna()], "standInfo", "StrandFootage")

    lash_total = lash_df["LashFootage"].sum()
    pull_total = pull_df["PullFootage"].sum()
    strand_total = strand_df["StrandFootage"].sum()
    total_projects = df["projectOr"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lash Footage", f"{lash_total:,}")
    col2.metric("Pull Footage", f"{pull_total:,}")
    col3.metric("Strand Footage", f"{strand_total:,}")
    col4.metric("Projects", f"{total_projects}")

    st.markdown("---")
    st.header("👷 Technician Breakdown")
    tech_lash = lash_df.groupby("whoFilled")["LashFootage"].sum().reset_index()
    tech_pull = pull_df.groupby("whoFilled")["PullFootage"].sum().reset_index()
    tech_strand = strand_df.groupby("whoFilled")["StrandFootage"].sum().reset_index()

    fig_lash = px.bar(tech_lash, x="LashFootage", y="whoFilled", orientation="h", title="Lash by Technician")
    fig_pull = px.bar(tech_pull, x="PullFootage", y="whoFilled", orientation="h", title="Pull by Technician")
    fig_strand = px.bar(tech_strand, x="StrandFootage", y="whoFilled", orientation="h", title="Strand by Technician")

    st.plotly_chart(fig_lash, use_container_width=True)
    st.plotly_chart(fig_pull, use_container_width=True)
    st.plotly_chart(fig_strand, use_container_width=True)

    st.markdown("---")
    st.header("🗓️ Average Work Hours per Truck per Week")

    df["Week"] = df["Submission Date"].dt.to_period("W").apply(lambda r: r.start_time.date())
    df["workHours"] = pd.to_numeric(df["workHours"], errors="coerce").fillna(0)
    truck_week_avg = df.groupby(["whatTruck", "Week"])["workHours"].mean().reset_index()

    fig_truck_week = px.bar(
        truck_week_avg,
        x="workHours",
        y="whatTruck",
        color="Week",
        barmode="group",
        orientation="h",
        title="Average Work Hours per Truck per Week"
    )
    st.plotly_chart(fig_truck_week, use_container_width=True)

    st.markdown("---")
    st.header("🚛 Most Used Trucks")
    truck_counts = df["whatTruck"].value_counts().reset_index()
    truck_counts.columns = ["Truck", "Count"]
    fig_trucks = px.bar(truck_counts.head(10), x="Count", y="Truck", orientation="h")
    st.plotly_chart(fig_trucks, use_container_width=True)

    st.markdown("---")
    st.header("🌱 Top Projects by Count")
    project_counts = df["projectOr"].value_counts().reset_index()
    project_counts.columns = ["Project", "Count"]
    fig_projects = px.bar(project_counts.head(10), x="Count", y="Project", orientation="h")
    st.plotly_chart(fig_projects, use_container_width=True)

    st.markdown("---")
    st.header("📋 Detailed Work Table")
    st.dataframe(df[["Submission Date", "projectOr", "whoFilled", "whatTruck", "workHours", "typeA45", "fiberPull", "standInfo"]])

if __name__ == "__main__":
    run_construction_dashboard()
