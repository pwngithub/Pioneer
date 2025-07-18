
def run_construction_dashboard():
    import streamlit as st
    import pandas as pd
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

    st.subheader("🧾 Raw Data Columns")
    st.write("Below are the raw column names fetched from the Jotform Construction form:")
    st.json(list(df.columns))

    st.info("✅ Please copy the list above and paste it here so we can map them to the expected fields like 'Who filled this out?', 'Project or labor?', etc.")

if __name__ == "__main__":
    run_construction_dashboard()
