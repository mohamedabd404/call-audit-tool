import streamlit as st
import pandas as pd

st.set_page_config(page_title="Audit Tool", layout="wide")
st.title("📞 Agent Summary - Issues Overview")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file is not None:
    # Load and clean data
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()  # Remove extra spaces from headers

    # Show columns to help identify issues
    st.write("Detected Columns:", df.columns.tolist())

    # Try to access critical columns with safe fallback
    required_columns = ['Agent Name', 'Recording Length', 'Disposition', 'Duration']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Missing column: {col}")
            st.stop()

    # Convert time fields safely
    df['Recording Length'] = pd.to_numeric(df['Recording Length'], errors='coerce')
    df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')

    # Define abuse logic
    df['Flag - Short Call'] = df['Recording Length'] < 10
    df['Flag - Voicemail'] = df['Disposition'].str.contains("voicemail", case=False, na=False)
    df['Flag - Dead Call'] = df['Disposition'].str.contains("dead call", case=False, na=False)
    df['Flag - Wrong Number'] = df['Disposition'].str.contains("wrong number", case=False, na=False)
    df['Flag - Unknown'] = df['Disposition'].str.lower().eq("unknown")

    # Group by agent and summarize flags
    summary = df.groupby('Agent Name').agg({
        'Flag - Short Call': 'sum',
        'Flag - Dead Call': 'sum',
        'Flag - Voicemail': 'sum',
        'Flag - Wrong Number': 'sum',
        'Flag - Unknown': 'sum',
        'Disposition': lambda x: (x.str.lower() == "not interested").sum(),
    }).reset_index()

    # Rename disposition column to Decision Maker - NYI
    summary.rename(columns={'Disposition': 'Decision Maker - NYI'}, inplace=True)

    # Optional: Add check if unknown calls exceed 50
    summary['Unknown Over 50 Calls'] = summary['Flag - Unknown'].apply(lambda x: '⚠️ Check' if x > 50 else '')

    st.dataframe(summary)

    # Optional: Download button
    csv = summary.to_csv(index=False)
    st.download_button("Download Summary CSV", csv, "summary.csv", "text/csv")

