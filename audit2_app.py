import streamlit as st
import pandas as pd

st.set_page_config(page_title="ReadyMode Call Audit Tool", layout="wide")

st.title("📞 RES-VA Call Audit Automation")
st.caption("App developed by Mohamed Abdo")

uploaded_file = st.file_uploader("Upload your exported Call Log CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Clean column names and Disposition values
    df.columns = df.columns.str.strip()
    if 'Disposition' in df.columns:
        df['Disposition'] = df['Disposition'].astype(str).str.strip()

    # Fix 'Recording Length (Seconds)' if misread as time format
    if df['Recording Length (Seconds)'].dtype == 'object':
        try:
            df['Recording Length (Seconds)'] = pd.to_datetime(
                df['Recording Length (Seconds)'], format='%I:%M:%S %p', errors='coerce'
            )
            df['Recording Length (Seconds)'] = (
                df['Recording Length (Seconds)'].dt.hour * 3600 +
                df['Recording Length (Seconds)'].dt.minute * 60 +
                df['Recording Length (Seconds)'].dt.second
            )
        except:
            pass

    # Ensure numeric type
    df['Recording Length (Seconds)'] = pd.to_numeric(df['Recording Length (Seconds)'], errors='coerce')

    # Convert to MM:SS format
    def format_duration(seconds):
        if pd.isnull(seconds):
            return ""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes}:{seconds:02d}"

    df['Recording Length (Formatted)'] = df['Recording Length (Seconds)'].apply(format_duration)

    # Add flag columns
    df['Flag - Voicemail Over 15 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Voicemail' and row['Recording Length (Seconds)'] > 15 else '', axis=1)

    df['Flag - Dead Call Over 15 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Dead Call' and row['Recording Length (Seconds)'] > 15 else '', axis=1)

    df['Flag - Decision Maker - NYI Under 10 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Decision Maker - NYI' and row['Recording Length (Seconds)'] < 10 else '', axis=1)

    df['Flag - Wrong Number Under 10 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Wrong Number' and row['Recording Length (Seconds)'] < 10 else '', axis=1)

    df['Flag - Unknown'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Unknown' else '', axis=1)

    # New: Unknown Under 5 sec per agent if count > 20
    df['Temp - Unknown Under 5'] = df.apply(
        lambda row: 1 if row['Disposition'] == 'Unknown' and row['Recording Length (Seconds)'] < 5 else 0,
        axis=1
    )
    unknown_under_5_counts = df.groupby('Agent Name')['Temp - Unknown Under 5'].sum()
    agents_over_20 = unknown_under_5_counts[unknown_under_5_counts > 20].index

    df['Flag - Unknown Under 5 sec'] = df.apply(
        lambda row: 'Check' if (
            row['Disposition'] == 'Unknown' and 
            row['Recording Length (Seconds)'] < 5 and 
            row['Agent Name'] in agents_over_20
        ) else '',
        axis=1
    )

    df.drop(columns=['Temp - Unknown Under 5'], inplace=True)

    # Agent summary
    agent_summary = df.groupby('Agent Name').agg({
        'Flag - Voicemail Over 15 sec': lambda x: (x == 'Check').sum(),
        'Flag - Dead Call Over 15 sec': lambda x: (x == 'Check').sum(),
        'Flag - Decision Maker - NYI Under 10 sec': lambda x: (x == 'Check').sum(),
        'Flag - Wrong Number Under 10 sec': lambda x: (x == 'Check').sum(),
        'Flag - Unknown': lambda x: (x == 'Check').sum(),
        'Flag - Unknown Under 5 sec': lambda x: (x == 'Check').sum(),
        'Disposition': lambda x: (x == 'Unknown').sum(),
    }).reset_index()

    agent_summary.rename(columns={'Disposition': 'Unknown Calls'}, inplace=True)

    agent_summary['Unknown Over 50 Calls'] = agent_summary.apply(
        lambda row: '⚠️ Check' if row['Unknown Calls'] > 50 else '', axis=1)

    # Overall summary
    total_voicemail = df['Flag - Voicemail Over 15 sec'].value_counts().get('Check', 0)
    total_deadcall = df['Flag - Dead Call Over 15 sec'].value_counts().get('Check', 0)
    total_decision_maker_nyi = df['Flag - Decision Maker - NYI Under 10 sec'].value_counts().get('Check', 0)
    total_wrong_number_under = df['Flag - Wrong Number Under 10 sec'].value_counts().get('Check', 0)
    total_unknown = df['Flag - Unknown'].value_counts().get('Check', 0)
    total_unknown_under_5 = df['Flag - Unknown Under 5 sec'].value_counts().get('Check', 0)

    total_flagged = df[[
        'Flag - Voicemail Over 15 sec',
        'Flag - Dead Call Over 15 sec',
        'Flag - Decision Maker - NYI Under 10 sec',
        'Flag - Wrong Number Under 10 sec',
        'Flag - Unknown',
        'Flag - Unknown Under 5 sec'
    ]].apply(lambda x: 'Check' in x.values, axis=1).sum()

    # Display summaries
    st.write("### 🚀 Overall Summary")
    st.info(f"""
    - **Voicemail Calls Over 15 sec:** {total_voicemail}
    - **Dead Calls Over 15 sec:** {total_deadcall}
    - **Decision Maker - NYI Under 10 sec:** {total_decision_maker_nyi}
    - **Wrong Number Calls Under 10 sec:** {total_wrong_number_under}
    - **Unknown Calls:** {total_unknown}
    - **Unknown Under 5 sec (Agents > 20):** {total_unknown_under_5}
    - **Total Flagged Calls:** {total_flagged}
    """)

    st.write("### 👥 Agent Summary - Issues Overview")
    st.dataframe(agent_summary)

    # Filter flagged calls
    flagged_calls = df[
        (df['Flag - Voicemail Over 15 sec'] == 'Check') |
        (df['Flag - Dead Call Over 15 sec'] == 'Check') |
        (df['Flag - Decision Maker - NYI Under 10 sec'] == 'Check') |
        (df['Flag - Wrong Number Under 10 sec'] == 'Check') |
        (df['Flag - Unknown'] == 'Check') |
        (df['Flag - Unknown Under 5 sec'] == 'Check')
    ]

    st.write("### 📋 Flagged Calls (With Phone Numbers)")
    st.dataframe(flagged_calls[[
        'Agent Name', 'Phone Number', 'Disposition', 'Recording Length (Formatted)',
        'Flag - Voicemail Over 15 sec',
        'Flag - Dead Call Over 15 sec',
        'Flag - Decision Maker - NYI Under 10 sec',
        'Flag - Wrong Number Under 10 sec',
        'Flag - Unknown',
        'Flag - Unknown Under 5 sec'
    ]])

    # Downloads
    st.download_button(
        "⬇️ Download Agent Summary",
        agent_summary.to_csv(index=False).encode('utf-8'),
        "agent_summary_flags.csv",
        "text/csv"
    )

    st.download_button(
        "⬇️ Download Flagged Calls",
        flagged_calls.to_csv(index=False).encode('utf-8'),
        "call_log_with_flags.csv",
        "text/csv"
    )

else:
    st.info("Please upload your exported call log CSV file to start the audit.")

