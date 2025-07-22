
def run_construction_dashboard():
    import streamlit as st
    import pandas as pd
    import requests

    st.title("Construction Dashboard — Inspecting typeA45 Contents")

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

    st.subheader("🧾 Non-empty `typeA45` values in selected date range")
    typeA45_nonempty = df[df["typeA45"].notna()][["Submission Date", "typeA45"]]
    st.dataframe(typeA45_nonempty, use_container_width=True)

    st.info("📩 Please copy a few example `typeA45` values above and paste them here so I can refine the parsing logic.")

if __name__ == "__main__":
    run_construction_dashboard()
