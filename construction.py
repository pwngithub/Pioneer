
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
    st.header("🗓️ 2-Week Average Lash, Pull, Strand per Truck (by Month)")

    df["Month"] = df["Submission Date"].dt.to_period("M").astype(str)
    lash_df["Month"] = lash_df["Submission Date"].dt.to_period("M").astype(str)
    pull_df["Month"] = pull_df["Submission Date"].dt.to_period("M").astype(str)
    strand_df["Month"] = strand_df["Submission Date"].dt.to_period("M").astype(str)

    lash_group = lash_df.groupby(["whatTruck", "Month"])["LashFootage"].sum().reset_index()
    pull_group = pull_df.groupby(["whatTruck", "Month"])["PullFootage"].sum().reset_index()
    strand_group = strand_df.groupby(["whatTruck", "Month"])["StrandFootage"].sum().reset_index()

    merged = pd.merge(lash_group, pull_group, on=["whatTruck", "Month"], how="outer")
    merged = pd.merge(merged, strand_group, on=["whatTruck", "Month"], how="outer")
    merged = merged.fillna(0)

    # compute 2-week averages
    merged["Lash2Week"] = merged["LashFootage"] / 2
    merged["Pull2Week"] = merged["PullFootage"] / 2
    merged["Strand2Week"] = merged["StrandFootage"] / 2

    melted = pd.melt(
        merged,
        id_vars=["whatTruck", "Month"],
        value_vars=["Lash2Week", "Pull2Week", "Strand2Week"],
        var_name="Type",
        value_name="2WeekAvgFootage"
    )

    fig_2week = px.bar(
        melted,
        x="2WeekAvgFootage",
        y="whatTruck",
        color="Type",
        barmode="group",
        orientation="h",
        facet_col="Month",
        title="2-Week Average Lash, Pull, Strand per Truck by Month"
    )
    st.plotly_chart(fig_2week, use_container_width=True)

    st.markdown("---")
    st.header("📋 Detailed Work Table")
    st.dataframe(df[["Submission Date", "projectOr", "whoFilled", "whatTruck", "workHours", "typeA45", "fiberPull", "standInfo"]])

if __name__ == "__main__":
    run_construction_dashboard()
