import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def run(df):
    st.header("📊 Monthly Customer Activity Dashboard")

    # --- Data Prep ---
    df["MRC"] = pd.to_numeric(df["MRC"], errors="coerce")
    df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")

    # --- Filters ---
    st.sidebar.header("🔍 Filters")
    min_date, max_date = df["Submission Date"].min(), df["Submission Date"].max()
    start_date, end_date = st.sidebar.date_input("Submission Date Range", [min_date, max_date])
    filtered_data = df[
        (df["Submission Date"] >= pd.Timestamp(start_date)) &
        (df["Submission Date"] <= pd.Timestamp(end_date))
    ]

    status_options = ["All"] + sorted(filtered_data["Status"].dropna().unique().tolist())
    selected_status = st.sidebar.selectbox("Status", status_options)
    if selected_status != "All":
        filtered_data = filtered_data[filtered_data["Status"] == selected_status]

    reason_options = ["All"] + sorted(filtered_data["Reason"].dropna().unique().tolist())
    selected_reason = st.sidebar.selectbox("Reason", reason_options)
    if selected_reason != "All":
        filtered_data = filtered_data[filtered_data["Reason"] == selected_reason]

    customer_search = st.sidebar.text_input("Search Customer Name")
    if customer_search:
        filtered_data = filtered_data[filtered_data["Customer Name"].str.contains(customer_search, case=False, na=False)]

    # --- Total Summary ---
    st.header("📌 Overall Totals")
    total_summary = filtered_data.groupby("Status").agg(Count=("Status", "count")).reset_index()
    total_mrc = filtered_data["MRC"].sum()
    st.dataframe(total_summary)
    st.metric("Total MRC", f"${total_mrc:,.2f}")

    # --- Churn Summary ---
    st.header("⚠️ Churn Summary by Reason")
    churn_df = filtered_data[filtered_data["Status"] == "Disconnect"]
    churn_summary = churn_df.groupby("Reason").agg(Count=("Reason", "count")).reset_index()
    churn_total_mrc = churn_df["MRC"].sum()
    st.dataframe(churn_summary)
    st.metric("Churn Total MRC", f"${churn_total_mrc:,.2f}")

    # --- Churn by Location ---
    st.header("📍 Churn by Location")
    loc_summary = churn_df.groupby("Location").agg(Count=("Location", "count")).sort_values(by="Count", ascending=False).reset_index()
    st.dataframe(loc_summary)

    # --- Visualizations ---
    st.header("📊 Visualizations")

    fig1, ax1 = plt.subplots()
    ax1.barh(churn_summary["Reason"], churn_summary["Count"])
    ax1.set_title("Churn Count by Reason")
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.bar(loc_summary["Location"], loc_summary["Count"])
    ax2.set_title("Churn Count by Location")
    ax2.tick_params(axis='x', rotation=90)
    st.pyplot(fig2)

    fig3, ax3 = plt.subplots()
    category_counts = filtered_data["Status"].value_counts()
    category_counts.plot(kind="pie", autopct='%1.1f%%', ax=ax3)
    ax3.set_ylabel("")
    ax3.set_title("Customer Status Breakdown")
    st.pyplot(fig3)

    # --- Trend Chart ---
    st.header("📈 Daily Activity Trend")
    daily_trend = filtered_data.groupby(["Submission Date", "Status"]).size().unstack(fill_value=0)
    st.line_chart(daily_trend)

    # --- Status Breakdown: New, Converted, Previous ---
    st.header("📊 Status Breakdown: New, Converted, Previous")
    filtered_statuses = filtered_data[filtered_data["Status"].isin(["NEW", "Convert", "Previous"])]
    status_counts = filtered_statuses["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    fig_status, ax_status = plt.subplots()
    ax_status.bar(status_counts["Status"], status_counts["Count"])
    ax_status.set_title("New vs Converted vs Previous Customers")
    st.pyplot(fig_status)

    if selected_status == "NEW":
        st.header("📍 New Customers by Location (Filtered)")
        new_by_location = filtered_data.groupby("Location").size().sort_values(ascending=False).reset_index(name="Count")

        fig_new, ax_new = plt.subplots()
        ax_new.bar(new_by_location["Location"], new_by_location["Count"])
        ax_new.set_title("New Customer Count by Location")
        ax_new.tick_params(axis='x', rotation=90)
        st.pyplot(fig_new)