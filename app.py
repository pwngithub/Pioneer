import streamlit as st
import jotform_client

st.set_page_config("JotForm Tally Dashboard", layout="wide")
st.title("📊 JotForm Tally Dashboard")

forms = jotform_client.get_forms()
form_dict = {title: fid for fid, title in forms}
form_choice = st.sidebar.selectbox("Select Form", list(form_dict.keys()))

if form_choice:
    df = jotform_client.get_submissions(form_dict[form_choice])

    st.sidebar.subheader("Filters")
    techs = df['Technician'].unique()
    work_types = df['Work Type'].unique()
    selected_techs = st.sidebar.multiselect("Technician", techs, default=list(techs))
    selected_work_types = st.sidebar.multiselect("Work Type", work_types, default=list(work_types))

    filtered = df[
        df['Technician'].isin(selected_techs) &
        df['Work Type'].isin(selected_work_types)
    ]

    st.subheader("Summary")
    st.metric("Total Jobs", len(filtered))
    st.metric("Total Duration", filtered['Duration'].sum())

    st.subheader("Details")
    st.dataframe(filtered)