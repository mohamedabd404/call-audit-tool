import streamlit as st
import pandas as pd
import hashlib
import io
from datetime import datetime

# Set page config
st.set_page_config(page_title="QA Flag Summary", layout="wide")

# -- Simple login system --
users = {
    "teamleader1": hashlib.sha256("12345resva".encode()).hexdigest(),
    "supervisor1": hashlib.sha256("98765resva".encode()).hexdigest()
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        if username in users and users[username] == hashed_pw:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
else:
    st.sidebar.title("Navigation")
    st.sidebar.write(f"**Logged in as:** {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    st.title("QA Flag Summary")

    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        required_columns = ["Agent Name", "Disposition", "Recording Link", "Recording Length"]
        if not all(col in df.columns for col in required_columns):
            st.error("The uploaded file is missing one or more required columns.")
        else:
            def flag_call(length):
                try:
                    length = int(length)
                    if length < 20:
                        return "Very Short - Check"
                    elif length < 60:
                        return "Short - Check"
                    else:
                        return "OK"
                except:
                    return "Check - Invalid"

            df["Flag"] = df["Recording Length"].apply(flag_call)

            # Filters
            agent_filter = st.sidebar.selectbox("Select Agent", options=["All"] + sorted(df["Agent Name"].unique().tolist()))
            disposition_filter = st.sidebar.multiselect("Filter by Disposition", df["Disposition"].unique())

            filtered_df = df.copy()
            if agent_filter != "All":
                filtered_df = filtered_df[filtered_df["Agent Name"] == agent_filter]
            if disposition_filter:
                filtered_df = filtered_df[filtered_df["Disposition"].isin(disposition_filter)]

            flagged_calls = filtered_df[filtered_df["Flag"].str.contains("Check")]

            # Summary
            total_calls = len(filtered_df)
            total_flagged = len(flagged_calls)
            flag_percentage = (total_flagged / total_calls * 100) if total_calls > 0 else 0

            st.subheader("Summary")
            st.metric("Total Calls", total_calls)
            st.metric("Flagged Calls", total_flagged)
            st.metric("Flag %", f"{flag_percentage:.2f}%")

            if total_flagged > 0:
                st.subheader("Flagged Calls")
                styled_df = flagged_calls.style.applymap(
                    lambda val: "background-color: yellow" if "Check" in str(val) else ""
                , subset=["Flag"])
                st.dataframe(styled_df, use_container_width=True)

            st.subheader("All Data with Flags")
            st.dataframe(filtered_df, use_container_width=True)

            # Export flagged calls
            st.download_button(
                label="Download Flagged Calls CSV",
                data=flagged_calls.to_csv(index=False).encode("utf-8"),
                file_name="flagged_calls.csv",
                mime="text/csv"
            )

            st.download_button(
                label="Download All Data CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="all_calls_with_flags.csv",
                mime="text/csv"
            )




