
def run_dashboard():
    import pandas as pd
    import streamlit as st
    import requests

    def load_from_jotform():
        api_key = "22179825a79dba61013e4fc3b9d30fa4"
        form_id = "240073839937062"
        url = f"https://api.jotform.com/form/{form_id}/submissions?apiKey={api_key}"
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

    st.set_page_config(page_title="Customer Activity Report", layout="wide")
    st.markdown("""<div style="text-align:center;"><img src='https://images.squarespace-cdn.com/content/v1/651eb4433b13e72c1034f375/369c5df0-5363-4827-b041-1add0367f447/PBB+long+logo.png?format=1500w' width="600"></div>""", unsafe_allow_html=True)

    st.markdown("<h1 style='color:#405C88;'>📊 Monthly Customer Performance Report</h1>", unsafe_allow_html=True)
    st.markdown("""
    This dashboard pulls the latest Talley form submissions via the Jotform API and displays the available column names.
    """)

    df = load_from_jotform()

    st.subheader("🧾 Raw Data Columns")
    st.write("Below are the raw column names fetched from the Jotform API:")
    st.json(list(df.columns))

    st.info("✅ Please copy the list above and paste it here so I can help you map them to friendly names like 'Status', 'Category', etc.")

    st.markdown("---")
    st.caption("<span style='color:#405C88;'>Professional Dashboard generated with ❤️ for Board Review</span>", unsafe_allow_html=True)

if __name__ == "__main__":
    run_dashboard()
