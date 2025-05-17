import streamlit as st
import pandas as pd

st.set_page_config(page_title="ReadyMode Call Audit Tool", layout="wide")

st.title("📞 RES-VA Call Audit Automation")

uploaded_file = st.file_uploader("Upload your exported Call Log CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Ensure 'Recording Length (Seconds)' is numeric (force errors to NaN)
    df['Recording Length (Seconds)'] = pd.to_numeric(df['Recording Length (Seconds)'], errors='coerce')

    # Add flags based on your rules
    df['Flag - Voicemail/Dead Call Over 15 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] in ['Voicemail', 'Dead Call'] and row['Recording Length (Seconds)'] > 15 else '', axis=1)

    df['Flag - Not Interested Under 10 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Not Interested' and row['Recording Length (Seconds)'] < 10 else '', axis=1)

    df['Flag - Wrong Number Over 10 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Wrong Number' and row['Recording Length (Seconds)'] > 10 else '', axis=1)

    df['Flag - Unknown'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Unknown' else '', axis=1)

    # Agent summary counts
    agent_summary = df.groupby('Agent Name').agg({
        'Flag - Voicemail/Dead Call Over 15 sec': lambda x: (x == 'Check').sum(),
        'Flag - Not Interested Under 10 sec': lambda x: (x == 'Check').sum(),
        'Flag - Wrong Number Over 10 sec': lambda x: (x == 'Check').sum(),
        'Flag - Unknown': lambda x: (x == 'Check').sum(),
        'Disposition': lambda x: (x == 'Unknown').sum(),
    }).reset_index()

    agent_summary.rename(columns={
        'Disposition': 'Unknown Calls'
    }, inplace=True)

    agent_summary['Unknown Over 50 Calls'] = agent_summary.apply(
        lambda row: '⚠️ Check' if row['Unknown Calls'] > 50 else '', axis=1)

    st.write("### 👥 Agent Summary - Issues Overview")
    st.dataframe(agent_summary)

    flagged_calls = df[
        (df['Flag - Voicemail/Dead Call Over 15 sec'] == 'Check') |
        (df['Flag - Not Interested Under 10 sec'] == 'Check') |
        (df['Flag - Wrong Number Over 10 sec'] == 'Check') |
        (df['Flag - Unknown'] == 'Check')
    ]

    st.write("### 📋 Flagged Calls (With Phone Numbers)")
    st.dataframe(flagged_calls[['Agent Name', 'Phone Number', 'Disposition', 'Recording Length (Seconds)',
                                'Flag - Voicemail/Dead Call Over 15 sec',
                                'Flag - Not Interested Under 10 sec',
                                'Flag - Wrong Number Over 10 sec',
                                'Flag - Unknown']])

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


# Add developer credit at the bottom
st.markdown(
    """
    <hr style="border: 1px solid #f0f0f0">
    <div style='text-align: center; color: grey; font-size: small;'>
        📱 App Developed by <b>Mohamed Abdo</b> - All rights reserved.
    </div>
    """, unsafe_allow_html=True
)

