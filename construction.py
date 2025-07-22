
def run_construction_dashboard():
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    import json
    import requests

    st.title("Construction Daily Workflow Dashboard")

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

    def extract_json_footage_from_column(df_partial, column, new_col):
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
        # merge back key metadata columns
        for col in df.columns:
            if col.lower() in ["town", "whofilled", "whattruck", "projector"]:
                df_out[col] = df.loc[df_out.index, col]
        return df_out

    lash_df = extract_json_footage_from_column(df[df["typeA45"].notna()], "typeA45", "LashFootage")
    pull_df = extract_json_footage_from_column(df[df["fiberPull"].notna()], "fiberPull", "PullFootage")
    strand_df = extract_json_footage_from_column(df[df["standInfo"].notna()], "standInfo", "StrandFootage")

    lash_total = lash_df["LashFootage"].sum()
    pull_total = pull_df["PullFootage"].sum()
    strand_total = strand_df["StrandFootage"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Fiber Lash Footage", f"{lash_total:,}")
    col2.metric("Fiber Pull Footage", f"{pull_total:,}")
    col3.metric("Strand Footage", f"{strand_total:,}")

    st.markdown("---")
    st.header("📍 Top Towns by Lash Footage")

    town_col = next((c for c in lash_df.columns if c.lower() == "town"), None)
    if town_col:
        town_summary = lash_df.groupby(town_col)["LashFootage"].sum().reset_index().sort_values(by="LashFootage", ascending=False).head(10)
        st.bar_chart(town_summary.set_index(town_col))
    else:
        st.warning("No 'Town' column found in data.")

    st.markdown("---")
    st.header("👷 Top Technicians")
    techs_lash = lash_df.groupby("whoFilled")["LashFootage"].sum()
    techs_pull = pull_df.groupby("whoFilled")["PullFootage"].sum()
    techs_strand = strand_df.groupby("whoFilled")["StrandFootage"].sum()

    col4, col5, col6 = st.columns(3)
    with col4:
        st.subheader("Lash")
        st.bar_chart(techs_lash)
    with col5:
        st.subheader("Pull")
        st.bar_chart(techs_pull)
    with col6:
        st.subheader("Strand")
        st.bar_chart(techs_strand)

    st.markdown("---")
    st.header("🚛 Most Used Trucks")
    truck_counts = df["whatTruck"].value_counts().head(10)
    st.bar_chart(truck_counts)

    st.markdown("---")
    st.header("🗓️ Work Summary by Day")
    daily_summary = df.groupby(df["Submission Date"].dt.date).size()
    st.line_chart(daily_summary)

    st.markdown("---")
    st.header("🌱 Projects Worked On")
    project_summary = df.groupby("projectOr").size().sort_values(ascending=False).head(10)
    st.bar_chart(project_summary)

    st.markdown("---")
    st.header("📋 Work Summary Table")
    st.dataframe(df[["Submission Date", "projectOr", "whoFilled", "whatTruck", "typeA45", "fiberPull", "standInfo"]])

if __name__ == "__main__":
    run_construction_dashboard()
