
def run_construction_dashboard():
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    import re
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

    techs = df["Who filled this out?"].dropna().unique()
    projects = df["Project or labor?"].dropna().unique()
    trucks = df["What Truck?"].dropna().unique()

    selected_tech = st.selectbox("Filter by Technician", ["All"] + list(techs))
    selected_project = st.selectbox("Filter by Project/Labor", ["All"] + list(projects))
    selected_truck = st.selectbox("Filter by Truck", ["All"] + list(trucks))

    filtered_df = df.copy()
    if selected_tech != "All":
        filtered_df = filtered_df[filtered_df["Who filled this out?"] == selected_tech]
    if selected_project != "All":
        filtered_df = filtered_df[filtered_df["Project or labor?"] == selected_project]
    if selected_truck != "All":
        filtered_df = filtered_df[filtered_df["What Truck?"] == selected_truck]

    st.subheader("Filtered Data")
    st.dataframe(filtered_df)

    def extract_footage_by_activity(row):
        activity = str(row.get("What did you do.", "")).lower()
        source_col = None
        if "lashed fiber" in activity:
            source_col = "Fiber"
        elif "pulled fiber" in activity:
            source_col = "Fiber pull Info."
        elif "strand" in activity:
            source_col = "Stand info"

        if source_col and source_col in row:
            text = str(row.get(source_col, ""))
            match = re.search(r'(\d+[,.]?\d*)', text)
            if match:
                try:
                    return float(match.group(1).replace(",", ""))
                except:
                    return 0
        return 0

    def assign_footage(data):
        data = data.copy()
        data["Footage"] = data.apply(extract_footage_by_activity, axis=1)
        return data

    lash_df = assign_footage(filtered_df[filtered_df["What did you do."].str.contains("Lashed Fiber", na=False)])
    pull_df = assign_footage(filtered_df[filtered_df["What did you do."].str.contains("Pulled Fiber", na=False)])
    strand_df = assign_footage(filtered_df[filtered_df["What did you do."].str.contains("Strand", na=False)])

    lash_total = lash_df["Footage"].sum()
    pull_total = pull_df["Footage"].sum()
    strand_total = strand_df["Footage"].sum()

    st.subheader("Summary")
    st.write({
        "Fiber Lash Footage": lash_total,
        "Fiber Pull Footage": pull_total,
        "Strand Footage": strand_total
    })

    st.subheader("Footage Bar Charts per Technician")

    def plot_footage(data, label):
        tech_footage = data.groupby("Who filled this out?")["Footage"].sum()
        if not tech_footage.empty:
            st.write(f"### {label}")
            fig, ax = plt.subplots()
            tech_footage.plot(kind="bar", ax=ax)
            ax.set_ylabel("Footage")
            ax.set_xlabel("Technician")
            st.pyplot(fig)

    plot_footage(lash_df, "Fiber Lash Footage")
    plot_footage(pull_df, "Fiber Pull Footage")
    plot_footage(strand_df, "Strand Footage")

if __name__ == "__main__":
    run_construction_dashboard()
