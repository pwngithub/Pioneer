
def run(df):
    import streamlit as st
    import pandas as pd
    from datetime import datetime

    st.title("Tally Dashboard")

    # Map column names
    df.rename(columns={"date": "Submission Date"}, inplace=True)
    df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")
    df["mrc"] = pd.to_numeric(df["mrc"], errors="coerce").fillna(0)

    min_date = df["Submission Date"].min()
    max_date = df["Submission Date"].max()

    if pd.isna(min_date) or pd.isna(max_date):
        min_date = max_date = datetime.today()

    min_date = min_date.date()
    max_date = max_date.date()

    start_date, end_date = st.date_input(
        "📅 Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)

    df = df[(df["Submission Date"] >= start_ts) & (df["Submission Date"] <= end_ts)]

    total_customers = df.shape[0]
    total_mrc = df["mrc"].sum()
    new_customers = df[df["status"].str.lower() == "connect"].shape[0]
    churn_customers = df[df["status"].str.lower() == "disconnect"].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", total_customers)
    col2.metric("Total MRC", f"${total_mrc:,.2f}")
    col3.metric("New Customers", new_customers)
    col4.metric("Churn Customers", churn_customers)

    st.markdown("---")
    st.header("📈 New Customer Trends Over Time")
    df_trend = df[df["status"].str.lower() == "connect"]
    trend = df_trend.groupby(df_trend["Submission Date"].dt.to_period("M")).size().reset_index(name="New Customers")
    trend["Submission Date"] = trend["Submission Date"].dt.to_timestamp()
    fig_trend = px.line(trend, x="Submission Date", y="New Customers", markers=True, title="New Customers by Month")
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")
    st.header("🏠 Churn by Location")
    churn_by_loc = df[df["status"].str.lower() == "disconnect"].groupby("location").size().reset_index(name="Churn")
    fig_churn_loc = px.bar(churn_by_loc, x="Churn", y="location", orientation="h", title="Churn by Location")
    st.plotly_chart(fig_churn_loc, use_container_width=True)

    st.markdown("---")
    st.header("📊 Status and Category Breakdown")
    status_count = df["status"].value_counts().reset_index()
    status_count.columns = ["Status", "Count"]
    fig_status = px.pie(status_count, values="Count", names="Status", title="Status Breakdown")
    st.plotly_chart(fig_status, use_container_width=True)

    category_count = df["category"].value_counts().reset_index()
    category_count.columns = ["Category", "Count"]
    fig_category = px.pie(category_count, values="Count", names="Category", title="Category Breakdown")
    st.plotly_chart(fig_category, use_container_width=True)

    st.markdown("---")
    st.header("📋 Detailed Data")
    st.dataframe(df)
