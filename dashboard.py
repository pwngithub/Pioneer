
def run_dashboard():
    import os
    import pandas as pd
    import streamlit as st
    import requests
    from datetime import datetime
    import plotly.express as px

    def load_from_jotform():
        api_key = "22179825a79dba61013e4fc3b9d30fa4"
        form_id = "240073839937062"
        url = f"https://api.jotform.com/form/{form_id}/submissions?apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        submissions = []
        for item in data["content"]:
            answers = item["answers"]
            submission_date = item["created_at"]
            record = {"Submission Date": submission_date}
            for ans in answers.values():
                record[ans["name"]] = ans["answer"]
            submissions.append(record)
        
        df = pd.DataFrame(submissions)
        return df

    st.set_page_config(page_title="Customer Activity Report", layout="wide")
    st.markdown("""<div style="text-align:center;"><img src='https://images.squarespace-cdn.com/content/v1/651eb4433b13e72c1034f375/369c5df0-5363-4827-b041-1add0367f447/PBB+long+logo.png?format=1500w' width="600"></div>""", unsafe_allow_html=True)

    st.markdown("<h1 style='color:#405C88;'>📊 Monthly Customer Performance Report</h1>", unsafe_allow_html=True)
    st.markdown("""
    This dashboard pulls the latest Talley form submissions via the Jotform API and presents key metrics and insights.
    """)

    df = load_from_jotform()

    df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")
    df = df.dropna(subset=["Submission Date"])
    df["Month"] = df["Submission Date"].dt.to_period("M").astype(str)

    total_customers = len(df)
    disconnects = df[df["Status"] == "Disconnect"]
    new_customers = df[df["Status"] == "NEW"]
    churn_mrc = pd.to_numeric(df["MRC"], errors="coerce").fillna(0).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Total Records", f"{total_customers}")
    col2.metric("📉 Churned Customers", f"{len(disconnects)}")
    col3.metric("💲 Total MRC", f"${churn_mrc:,.2f}")

    st.markdown("---")

    st.header("Churn Analysis by Reason")
    churn_summary = disconnects.groupby("Reason").agg(
        Count=("Reason", "count"),
        Total_MRC=("MRC", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum())
    ).reset_index()
    churn_summary = churn_summary.sort_values(by="Count", ascending=False)

    st.dataframe(churn_summary, use_container_width=True)

    fig_reason = px.bar(
        churn_summary,
        x="Count",
        y="Reason",
        orientation="h",
        title="Churn by Reason (Sorted)",
        color="Count", color_continuous_scale=["#7CB342", "#405C88"],
        height=500
    )
    st.plotly_chart(fig_reason, use_container_width=True)

    st.header("Churn by Location (Top 20)")
    loc_summary = disconnects.groupby("Location").size().reset_index(name="Count")
    loc_summary = loc_summary.sort_values(by="Count", ascending=False).head(20)

    fig_location = px.bar(
        loc_summary,
        x="Location",
        y="Count",
        title="Churn by Location (Top 20)",
        color="Count", color_continuous_scale=["#7CB342", "#405C88"]
    )
    st.plotly_chart(fig_location, use_container_width=True)

    st.header("New Customer Trends")
    new_by_category = new_customers.groupby("Category").size().reset_index(name="Count").sort_values(by="Count", ascending=False)
    new_by_location = new_customers.groupby("Location").size().reset_index(name="Count").sort_values(by="Count", ascending=False).head(20)

    col4, col5 = st.columns(2)

    with col4:
        fig_new_cat = px.bar(
            new_by_category,
            x="Category",
            y="Count",
            title="New Customers by Category",
            color="Count", color_continuous_scale=["#7CB342", "#405C88"]
        )
        st.plotly_chart(fig_new_cat, use_container_width=True)

    with col5:
        fig_new_loc = px.bar(
            new_by_location,
            x="Location",
            y="Count",
            title="New Customers by Location (Top 20)",
            color="Count", color_continuous_scale=["#7CB342", "#405C88"]
        )
        st.plotly_chart(fig_new_loc, use_container_width=True)

    st.markdown("---")
    st.caption("<span style='color:#405C88;'>Professional Dashboard generated with ❤️ for Board Review</span>", unsafe_allow_html=True)

if __name__ == "__main__":
    run_dashboard()
