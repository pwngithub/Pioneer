
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

    # Helper to extract footage totals from JSON column
    def extract_footage(df, column):
        df = df.copy()
        df["Footage"] = 0
        for idx, val in df[column].dropna().items():
            try:
                items = json.loads(val)
                for item in items:
                    footage_str = item.get("Footage", "0").replace(",", "").strip()
                    if footage_str.isdigit():
                        df.at[idx, "Footage"] += int(footage_str)
            except:
                continue
        return df

    # Filter rows by activity type
    lash_df = df[df["whatDid"].str.contains("Lashed Fiber", case=False, na=False)]
    pull_df = df[df["whatDid"].str.contains("Pulled Fiber", case=False, na=False)]
    strand_df = df[df["whatDid"].str.contains("Strand", case=False, na=False)]

    lash_df = extract_footage(lash_df, "fiber")
    pull_df = extract_footage(pull_df, "fiberPull")
    strand_df = extract_footage(strand_df, "standInfo")

    lash_total = lash_df["Footage"].sum()
    pull_total = pull_df["Footage"].sum()
    strand_total = strand_df["Footage"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Fiber Lash Footage", f"{lash_total:,}")
    col2.metric("Fiber Pull Footage", f"{pull_total:,}")
    col3.metric("Strand Footage", f"{strand_total:,}")

    st.markdown("---")
    st.header("Footage by Technician")

    def plot_tech_chart(df, title):
        tech_footage = df.groupby("whoFilled")["Footage"].sum()
        if not tech_footage.empty:
            fig, ax = plt.subplots()
            tech_footage.plot(kind="bar", ax=ax)
            ax.set_ylabel("Footage")
            ax.set_xlabel("Technician")
            ax.set_title(title)
            st.pyplot(fig)

    plot_tech_chart(lash_df, "Fiber Lash Footage per Technician")
    plot_tech_chart(pull_df, "Fiber Pull Footage per Technician")
    plot_tech_chart(strand_df, "Strand Footage per Technician")

    st.markdown("---")
    st.header("Work Summary")

    summary_rows = []
    for (date, project), group in df.groupby([df["Submission Date"].dt.date, "projectOr"]):
        text = f"📅 **{date}** — 📁 **{project if pd.notna(project) else 'N/A'}**"
        st.markdown(text)
        for _, row in group.iterrows():
            employees = [row.get(col) for col in ["employee", "employee17", "employee19", "employee20", "employee21", "employee22"]]
            employees = [e for e in employees if pd.notna(e)]
            employees_str = ", ".join(employees) if employees else "Unknown"
            truck = row.get("whatTruck", "Unknown Truck")
            activity = row.get("whatDid", "Unknown Activity")
            fiber = row.get("fiber", "Unknown Fiber")
            st.markdown(f"- {employees_str} used {truck} to perform **{activity}** on **{fiber}**")

if __name__ == "__main__":
    run_construction_dashboard()
