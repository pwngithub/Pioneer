
def run_construction_dashboard():
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    import json
    import requests

    st.title("Construction Daily Workflow Dashboard — With Date Filter")

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

    mask = (df["Submission Date"].dt.date >= start_date) & (df["Submission Date"].dt.date <= end_date)
    df = df.loc[mask]

    def extract_total_footage_from_json_column(col):
        total = 0
        for val in col.dropna():
            try:
                items = json.loads(val)
                for item in items:
                    footage_str = item.get("Footage", "0").replace(",", "").strip()
                    if footage_str.isdigit():
                        total += int(footage_str)
            except:
                continue
        return total

    lash_total = 0  # still no confirmed source for lash
    pull_total = extract_total_footage_from_json_column(df["fiberPull"])
    strand_total = extract_total_footage_from_json_column(df["standInfo"])

    st.subheader("Summary")
    st.write({
        "Fiber Lash Footage": lash_total,
        "Fiber Pull Footage": pull_total,
        "Strand Footage": strand_total
    })

if __name__ == "__main__":
    run_construction_dashboard()
