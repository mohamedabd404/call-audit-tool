import streamlit as st
import pandas as pd

# ========== User Login ==========
allowed_users = ['aya', 'nour', 'zizi', 'danial', 'abdo', 'admins']
password = '12345resva'

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login to RES-VA Call Audit Tool")

    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    if st.button("Login"):
        if username_input.strip().lower() in allowed_users and password_input == password:
            st.session_state.authenticated = True
            st.success("✅ Login successful. Welcome!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.stop()

# ========== Main App ==========
st.set_page_config(page_title="ReadyMode Call Audit Tool", layout="wide")
st.title("📞 RES-VA Call Audit Automation")

uploaded_file = st.file_uploader("Upload your exported Call Log CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Clean column names and Disposition values
    df.columns = df.columns.str.strip()
    if 'Disposition' in df.columns:
        df['Disposition'] = df['Disposition'].astype(str).str.strip()

    # Fix Recording Length if misread as time
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

    df['Recording Length (Seconds)'] = pd.to_numeric(df['Recording Length (Seconds)'], errors='coerce')

    def format_duration(seconds):
        if pd.isnull(seconds):
            return ""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes}:{seconds:02d}"

    df['Recording Length (Formatted)'] = df['Recording Length (Seconds)'].apply(format_duration)

    # Original flagging logic
    df['Flag - Voicemail Over 15 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Voicemail' and row['Recording Length (Seconds)'] > 15 else '', axis=1)

    df['Flag - Dead Call Over 15 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Dead Call' and row['Recording Length (Seconds)'] > 15 else '', axis=1)

    df['Flag - Decision Maker - NYI Under 10 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Decision Maker - NYI' and row['Recording Length (Seconds)'] < 10 else '', axis=1)

    df['Flag - Wrong Number Under 10 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Wrong Number' and row['Recording Length (Seconds)'] < 10 else '', axis=1)

    df['Flag - Unknown Under 5 sec'] = df.apply(
        lambda row: 'Check' if row['Disposition'] == 'Unknown' and row['Recording Length (Seconds)'] < 5 else '', axis=1)

    # Agent summary
    agent_summary = df.groupby('Agent Name').agg({
        'Flag - Voicemail Over 15 sec': lambda x: (x == 'Check').sum(),
        'Flag - Dead Call Over 15 sec': lambda x: (x == 'Check').sum(),
        'Flag - Decision Maker - NYI Under 10 sec': lambda x: (x == 'Check').sum(),
        'Flag - Wrong Number Under 10 sec': lambda x: (x == 'Check').sum(),
        'Flag - Unknown Under 5 sec': lambda x: (x == 'Check').sum(),
    }).reset_index()

    # Overall Summary
    total_voicemail = df['Flag - Voicemail Over 15 sec'].value_counts().get('Check', 0)
    total_deadcall = df['Flag - Dead Call Over 15 sec'].value_counts().get('Check', 0)
    total_decision_maker_nyi = df['Flag - Decision Maker - NYI Under 10 sec'].value_counts().get('Check', 0)
    total_wrong_number_under = df['Flag - Wrong Number Under 10 sec'].value_counts().get('Check', 0)
    total_unknown_5sec = df['Flag - Unknown Under 5 sec'].value_counts().get('Check', 0)

    total_flagged = df[[
        'Flag - Voicemail Over 15 sec',
        'Flag - Dead Call Over 15 sec',
        'Flag - Decision Maker - NYI Under 10 sec',
        'Flag - Wrong Number Under 10 sec',
        'Flag - Unknown Under 5 sec'
    ]].apply(lambda x: 'Check' in x.values, axis=1).sum()

    st.write("### 🚀 Overall Summary")
    st.info(f"""
    - **Voicemail Calls Over 15 sec:** {total_voicemail}
    - **Dead Calls Over 15 sec:** {total_deadcall}
    - **Decision Maker - NYI Under 10 sec:** {total_decision_maker_nyi}
    - **Wrong Number Calls Under 10 sec:** {total_wrong_number_under}
    - **Unknown Calls Under 5 sec:** {total_unknown_5sec}
    - **Total Flagged Calls:** {total_flagged}
    """)

    st.write("### 👥 Agent Summary - Issues Overview")
    st.dataframe(agent_summary)

    flagged_calls = df[
        (df['Flag - Voicemail Over 15 sec'] == 'Check') |
        (df['Flag - Dead Call Over 15 sec'] == 'Check') |
        (df['Flag - Decision Maker - NYI Under 10 sec'] == 'Check') |
        (df['Flag - Wrong Number Under 10 sec'] == 'Check') |
        (df['Flag - Unknown Under 5 sec'] == 'Check')
    ]

    st.write("### 📋 Flagged Calls")
    st.dataframe(flagged_calls[['Agent Name', 'Phone Number', 'Disposition', 'Recording Length (Formatted)',
                                'Flag - Voicemail Over 15 sec',
                                'Flag - Dead Call Over 15 sec',
                                'Flag - Decision Maker - NYI Under 10 sec',
                                'Flag - Wrong Number Under 10 sec',
                                'Flag - Unknown Under 5 sec']])

    st.download_button("⬇️ Download Agent Summary", agent_summary.to_csv(index=False).encode('utf-8'), "agent_summary_flags.csv", "text/csv")
    st.download_button("⬇️ Download Flagged Calls", flagged_calls.to_csv(index=False).encode('utf-8'), "call_log_with_flags.csv", "text/csv")

else:
    st.info("Please upload your exported call log CSV file to start the audit.")

st.markdown(
    """
    <div style="
        position: fixed;
        bottom: 10px;
        width: 100%;
        text-align: center;
        font-size: 16px;
        color: white;
        background: linear-gradient(to right, #00c6ff, #0072ff);
        padding: 10px 0;
        border-radius: 8px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
        animation: fadeIn 2s ease-in-out;
    ">
        ✨ App developed by <strong>Mohamed Abdo</strong> ✨
    </div>

    <style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
    """,
    unsafe_allow_html=True
)




