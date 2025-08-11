
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def run_financial_dashboard():
    st.image("https://images.squarespace-cdn.com/content/v1/651eb4433b13e72c1034f375/369c5df0-5363-4827-b041-1add0367f447/PBB+long+logo.png?format=1500w", width=300)
    st.title("📊 Financial / Customer Insights Dashboard")

    # File handling
    saved_folder = "saved_financial"
    os.makedirs(saved_folder, exist_ok=True)

    mode = st.radio("Select Mode", ["Upload New File", "Load Existing File"])

    if mode == "Upload New File":
        uploaded_file = st.file_uploader("Upload Revenue CSV", type=["csv"])
        custom_filename = st.text_input("Enter a name to save this file as (without extension):")
        if uploaded_file and custom_filename:
            save_path = os.path.join(saved_folder, custom_filename + ".csv")
            with open(save_path, "wb") as f:
                f.write(uploaded_file.read())
            st.success(f"File saved as: {save_path}")
            df = pd.read_csv(save_path)
        elif uploaded_file and not custom_filename:
            st.warning("Please enter a file name to save.")
            return
        else:
            return
    else:
        saved_files = [f for f in os.listdir(saved_folder) if f.endswith(".csv")]
        if not saved_files:
            st.warning("No saved financial files found. Please upload one.")
            return
        selected_file = st.selectbox("Select a saved financial file", saved_files)
        df = pd.read_csv(os.path.join(saved_folder, selected_file))

        # Delete option
        st.markdown("### 🗑 Delete a Saved File")
        file_to_delete = st.selectbox("Select a file to delete", saved_files, key="delete_financial_file")
        if st.button("Delete Selected Financial File"):
            os.remove(os.path.join(saved_folder, file_to_delete))
            st.success(f"{file_to_delete} has been deleted.")
            st.experimental_rerun()

    st.subheader("Raw Data")
    st.dataframe(df)

    # Basic KPIs
    try:
        total_revenue = df["Total Amount"].sum()
        total_subs = df["Sub Count End"].sum()
        total_lost = df["Sub Count Start"].sum() - total_subs
        arpu = total_revenue / total_subs if total_subs else 0
        churn_rate = (total_lost / df["Sub Count Start"].sum()) * 100 if df["Sub Count Start"].sum() else 0
        penetration_avg = df["Penetration %"].mean() if "Penetration %" in df.columns else None

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Revenue", f"${total_revenue:,.2f}")
        col2.metric("ARPU", f"${arpu:,.2f}")
        col3.metric("Churn Rate", f"{churn_rate:.2f}%")
        if penetration_avg is not None:
            col4.metric("Avg Penetration %", f"{penetration_avg:.2f}%")
    except Exception as e:
        st.error(f"Error calculating KPIs: {e}")

    # Charts
    if "Total Amount" in df.columns and "Product Name" in df.columns:
        st.subheader("Revenue by Product")
        rev_by_product = df.groupby("Product Name")["Total Amount"].sum().sort_values()
        fig, ax = plt.subplots()
        rev_by_product.plot(kind="barh", ax=ax)
        ax.set_xlabel("Revenue ($)")
        st.pyplot(fig)

    if "Sub Count End" in df.columns and "Product Name" in df.columns:
        st.subheader("Subscribers by Product")
        subs_by_product = df.groupby("Product Name")["Sub Count End"].sum().sort_values()
        fig, ax = plt.subplots()
        subs_by_product.plot(kind="barh", ax=ax, color="orange")
        ax.set_xlabel("Subscribers")
        st.pyplot(fig)

    if "Penetration %" in df.columns and "Product Name" in df.columns:
        st.subheader("Penetration % by Product")
        pen_by_product = df.groupby("Product Name")["Penetration %"].mean().sort_values()
        fig, ax = plt.subplots()
        pen_by_product.plot(kind="barh", ax=ax, color="green")
        ax.set_xlabel("Penetration %")
        st.pyplot(fig)

    # Executive Summary
    st.subheader("Executive Summary")
    summary = f"""
    For the selected period, Pioneer Broadband generated **${total_revenue:,.2f}** in total revenue with an ARPU of **${arpu:,.2f}**.
    The churn rate for this period was **{churn_rate:.2f}%**, with an average penetration of **{penetration_avg:.2f}%** across products.
    Revenue was primarily driven by {rev_by_product.idxmax()} (${rev_by_product.max():,.2f}).
    """
    st.markdown(summary)
