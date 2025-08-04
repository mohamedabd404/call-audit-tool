import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# Helper function to safely read CSV files
def safe_read_csv(uploaded_file):
    """Safely read CSV file with multiple encoding attempts"""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding)
            return df
        except Exception as e:
            continue
    
    # If all encodings fail, try without specifying encoding
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        raise Exception(f"Failed to read CSV file with any encoding: {str(e)}")

# Page configuration
st.set_page_config(
    page_title="RES-VA Call Audit Tool",
    page_icon="vos_logo.png",  # Custom VOS logo
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional dark theme
st.markdown("""
<style>
    /* Base styling */
    .main {
        background-color: #1E1E2F;
        color: #E0E0E0;
    }
    
    .stApp {
        background-color: #1E1E2F;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1E1E2F;
    }
    
    .css-1lcbmhc {
        background-color: #1E1E2F;
    }
    
    /* Headers */
    .main-header {
        background: linear-gradient(90deg, #4C84FF 0%, #2A2A40 100%);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .section-header {
        background: linear-gradient(90deg, #2B2D42 0%, #1E1E2F 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #4C84FF;
        color: #FFFFFF;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    /* Metric cards with specific colors */
    .metric-card-voicemail {
        background: linear-gradient(135deg, #FF6B6B 0%, #E85555 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: #FFFFFF;
        text-align: center;
        box-shadow: 0 4px 12px rgba(255,107,107,0.3);
        font-size: 0.95rem;
    }
    
    .metric-card-dead {
        background: linear-gradient(135deg, #FFA94D 0%, #E8943D 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: #FFFFFF;
        text-align: center;
        box-shadow: 0 4px 12px rgba(255,169,77,0.3);
        font-size: 0.95rem;
    }
    
    .metric-card-decision {
        background: linear-gradient(135deg, #F9C74F 0%, #E6B43F 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: #FFFFFF;
        text-align: center;
        box-shadow: 0 4px 12px rgba(249,199,79,0.3);
        font-size: 0.95rem;
    }
    
    .metric-card-total {
        background: linear-gradient(135deg, #4C84FF 0%, #3B6BD6 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: #FFFFFF;
        text-align: center;
        box-shadow: 0 4px 12px rgba(76,132,255,0.3);
        font-size: 0.95rem;
    }
    
    /* Table styling */
    .stDataFrame {
        background-color: #2B2D42;
        color: #E0E0E0;
    }
    
    .stDataFrame th {
        background-color: #1E1E2F;
        color: #FFFFFF;
    }
    
    .stDataFrame td {
        background-color: #2B2D42;
        color: #E0E0E0;
    }
    
    .stDataFrame tr:nth-child(even) td {
        background-color: #252537;
    }
    
    .stDataFrame tr:hover td {
        background-color: #2C2C3A;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4C84FF 0%, #3B6BD6 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #3B6BD6 0%, #2A5BC6 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76,132,255,0.4);
    }
    
    .download-btn {
        background: linear-gradient(135deg, #4C84FF 0%, #3B6BD6 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .download-btn:hover {
        background: linear-gradient(135deg, #3B6BD6 0%, #2A5BC6 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76,132,255,0.4);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1.2rem;
        color: #8A8D9A;
        font-size: 0.9rem;
        font-weight: 400;
        border-top: 1px solid #2B2D42;
        margin-top: 2rem;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, rgba(30, 30, 47, 0.95) 0%, rgba(30, 30, 47, 0.98) 100%);
        z-index: 1000;
        box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(8px);
    }
    
    .footer-link {
        color: #4C84FF;
        text-decoration: none !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .footer-link:hover {
        color: #6BA4FF;
        text-decoration: none !important;
    }
    
    .footer-link:visited {
        text-decoration: none !important;
    }
    
    .footer-link:active {
        text-decoration: none !important;
    }
    
    /* Typography */
    body {
        font-family: 'Inter', 'Poppins', sans-serif;
        color: #E0E0E0;
    }
    
    /* Chart styling */
    .plotly_chart {
        background-color: transparent;
    }
    
    /* Overall Summary Header */
    .overall-summary-header {
        background: linear-gradient(90deg, #dc2626 0%, #1f2937 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #dc2626;
        color: #FFFFFF;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    /* Aya's Idea component */
    .aya-idea {
        background: linear-gradient(135deg, #4C84FF 0%, #3B6BD6 100%);
        padding: 0.7rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #FFFFFF;
        text-align: center;
        box-shadow: 0 4px 12px rgba(76,132,255,0.3);
        font-size: 0.9rem;
        font-weight: 600;
        animation: bounce 2s infinite;
        float: right;
        width: 160px;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
</style>
""", unsafe_allow_html=True)

# User credentials
USERS = {
    "Abdo": "12345resva",
    "Ahmed Hanafy": "12345resva", 
    "destroyer of the galaxy": "12345resva",
    "el dlo3a": "12345resva",
    "Nour": "12345resva",
    "Danial": "12345resva",
    "Zizi": "12345resva",
    "Yehia": "12345resva"
}

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def logout():
    st.session_state.authenticated = False
    st.rerun()

# Login page
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">RES-VA Call Audit Tool</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="
            background-color: #2B2D42;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        ">
            <h2 style="color: #FFFFFF; margin-bottom: 1.5rem;">Login Required</h2>
            <p style="color: #E0E0E0; margin-bottom: 2rem;">Please enter your credentials to access the audit tool.</p>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")
        
        if st.button("Login", key="login_button"):
            if username in USERS and USERS[username] == password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
    
    st.markdown('<div class="footer">Developed by Mohamed Abdo © 2025</div>', unsafe_allow_html=True)
    st.stop()

# Main application
st.markdown('<div class="main-header">RES-VA Call Audit Tool</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("Logout"):
        logout()
    
    st.markdown("---")
    st.markdown("### Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
    
    st.markdown("---")
    st.markdown("### Filters")
    
    # Agent filter
    if 'agent_options' not in st.session_state:
        st.session_state.agent_options = ['All users']
    
    # Initialize selected_agent in session state if not exists
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = 'All users'
    
    # Update agent options immediately when data is available
    if uploaded_file is not None:
        # Check if we need to reload data
        file_key = uploaded_file.name + str(uploaded_file.size)
        
        if 'current_file_key' not in st.session_state or st.session_state.current_file_key != file_key:
            # Load data immediately for agent options
            try:
                temp_df = safe_read_csv(uploaded_file)
                if 'Agent Name' in temp_df.columns:
                    agent_values = temp_df['Agent Name'].astype(str).fillna('Unknown').unique()
                    agent_names = ['All users'] + sorted([str(x) for x in agent_values if str(x) != 'nan'])
                    st.session_state.agent_options = agent_names
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
                st.session_state.agent_options = ['All users']
        elif 'original_df' in st.session_state and st.session_state.original_df is not None and 'Agent Name' in st.session_state.original_df.columns:
            # Use cached data
            agent_values = st.session_state.original_df['Agent Name'].astype(str).fillna('Unknown').unique()
            agent_names = ['All users'] + sorted([str(x) for x in agent_values if str(x) != 'nan'])
            st.session_state.agent_options = agent_names
    
    selected_agent = st.selectbox("Select Agent", st.session_state.agent_options, key="agent_selectbox")
    
    # Debug: Show available agents
    if uploaded_file is not None and len(st.session_state.agent_options) > 1:
        agent_count = len(st.session_state.agent_options) - 1  # Subtract 1 for 'All users'
        st.caption(f"Available agents: {agent_count} agents loaded")
    
    # Update session state when selection changes
    if selected_agent != st.session_state.selected_agent:
        st.session_state.selected_agent = selected_agent
    
    # Campaign filter
    if 'campaign_options' not in st.session_state:
        st.session_state.campaign_options = ['All campaigns']
    
    # Initialize selected_campaign in session state if not exists
    if 'selected_campaign' not in st.session_state:
        st.session_state.selected_campaign = 'All campaigns'
    
    # Update campaign options immediately when data is available
    if uploaded_file is not None:
        # Check if we need to reload data
        file_key = uploaded_file.name + str(uploaded_file.size)
        
        if 'current_file_key' not in st.session_state or st.session_state.current_file_key != file_key:
            # Load data immediately for campaign options
            try:
                temp_df = safe_read_csv(uploaded_file)
                if 'Current campaign' in temp_df.columns:
                    campaign_values = temp_df['Current campaign'].astype(str).fillna('Unknown').unique()
                    campaign_names = ['All campaigns'] + sorted([str(x) for x in campaign_values if str(x) != 'nan'])
                    st.session_state.campaign_options = campaign_names
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
                st.session_state.campaign_options = ['All campaigns']
        elif 'original_df' in st.session_state and st.session_state.original_df is not None and 'Current campaign' in st.session_state.original_df.columns:
            # Use cached data
            campaign_values = st.session_state.original_df['Current campaign'].astype(str).fillna('Unknown').unique()
            campaign_names = ['All campaigns'] + sorted([str(x) for x in campaign_values if str(x) != 'nan'])
            st.session_state.campaign_options = campaign_names
    
    selected_campaign = st.selectbox("Select Campaign", st.session_state.campaign_options, key="campaign_selectbox")
    
    # Update session state when selection changes
    if selected_campaign != st.session_state.selected_campaign:
        st.session_state.selected_campaign = selected_campaign
    
    # Download button
    if st.button("Download Agent Audit"):
        if uploaded_file is not None:
            st.info("Download functionality would be implemented here")
        else:
            st.warning("Please upload a CSV file first")

# Main content
if uploaded_file is not None:
    # Check if we need to reload data
    file_key = uploaded_file.name + str(uploaded_file.size)
    
    if 'current_file_key' not in st.session_state or st.session_state.current_file_key != file_key:
        # Load and process data
        try:
            df = safe_read_csv(uploaded_file)
            st.session_state.df = df
            st.session_state.original_df = df.copy()
            st.session_state.current_file_key = file_key
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")
            st.stop()
    else:
        # Use cached data
        df = st.session_state.df.copy()
        original_df = st.session_state.original_df.copy()
    
    # Store original data for agent options
    original_df = df.copy()
    
    # Standardize column names
    df.columns = df.columns.str.strip()
    original_df.columns = original_df.columns.str.strip()
    
    # Standardize disposition values
    df['Disposition'] = df['Disposition'].str.strip()
    original_df['Disposition'] = original_df['Disposition'].str.strip()
    
    # Parse recording length
    df['Recording Length (Seconds)'] = pd.to_numeric(df['Recording Length (Seconds)'], errors='coerce')
    original_df['Recording Length (Seconds)'] = pd.to_numeric(original_df['Recording Length (Seconds)'], errors='coerce')
    
    # Flagging logic
    df['Flag - Voicemail Over 15 sec'] = ((df['Disposition'] == 'Voicemail') & (df['Recording Length (Seconds)'] > 15)).map({True: 'Check', False: ''})
    df['Flag - Dead Call Over 15 sec'] = ((df['Disposition'] == 'Dead Call') & (df['Recording Length (Seconds)'] > 15)).map({True: 'Check', False: ''})
    df['Flag - Decision Maker - NYI Under 10 sec'] = ((df['Disposition'] == 'Decision Maker - NYI') & (df['Recording Length (Seconds)'] < 10)).map({True: 'Check', False: ''})
    df['Flag - Wrong Number Under 10 sec'] = ((df['Disposition'] == 'Wrong Number') & (df['Recording Length (Seconds)'] < 10)).map({True: 'Check', False: ''})
    df['Flag - Unknown Under 5 sec'] = ((df['Disposition'] == 'Unknown') & (df['Recording Length (Seconds)'] < 5)).map({True: 'Check', False: ''})
    
    # New flag for potential release/tech issue
    df['Flag - Potential Release/Tech Issue'] = ((df['Disposition'] == 'Dead Call') | (df['Disposition'] == 'Unknown')).map({True: 'Check', False: ''})
    
    # Also add flag columns to original_df for Agent Summary
    original_df['Flag - Voicemail Over 15 sec'] = ((original_df['Disposition'] == 'Voicemail') & (original_df['Recording Length (Seconds)'] > 15)).map({True: 'Check', False: ''})
    original_df['Flag - Dead Call Over 15 sec'] = ((original_df['Disposition'] == 'Dead Call') & (original_df['Recording Length (Seconds)'] > 15)).map({True: 'Check', False: ''})
    original_df['Flag - Decision Maker - NYI Under 10 sec'] = ((original_df['Disposition'] == 'Decision Maker - NYI') & (original_df['Recording Length (Seconds)'] < 10)).map({True: 'Check', False: ''})
    original_df['Flag - Wrong Number Under 10 sec'] = ((original_df['Disposition'] == 'Wrong Number') & (original_df['Recording Length (Seconds)'] < 10)).map({True: 'Check', False: ''})
    original_df['Flag - Unknown Under 5 sec'] = ((original_df['Disposition'] == 'Unknown') & (original_df['Recording Length (Seconds)'] < 5)).map({True: 'Check', False: ''})
    original_df['Flag - Potential Release/Tech Issue'] = ((original_df['Disposition'] == 'Dead Call') | (original_df['Disposition'] == 'Unknown')).map({True: 'Check', False: ''})
    
    # Add call duration label
    df['Call Duration Label'] = pd.cut(df['Recording Length (Seconds)'], 
                                      bins=[0, 30, 60, float('inf')], 
                                      labels=['Very Short', 'Short', 'OK'])
    original_df['Call Duration Label'] = pd.cut(original_df['Recording Length (Seconds)'], 
                                               bins=[0, 30, 60, float('inf')], 
                                               labels=['Very Short', 'Short', 'OK'])
    
    # Format recording length
    def format_duration(seconds):
        if pd.isna(seconds):
            return "0:00"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    df['Recording Length (Formatted)'] = df['Recording Length (Seconds)'].apply(format_duration)
    original_df['Recording Length (Formatted)'] = original_df['Recording Length (Seconds)'].apply(format_duration)
    
    # Create filtered dataframe for flagged calls only
    filtered_df = df.copy()
    
    # Apply filters only to the filtered dataframe for flagged calls
    if st.session_state.selected_agent and st.session_state.selected_agent != 'All users':
        filtered_df = filtered_df[filtered_df['Agent Name'] == st.session_state.selected_agent]
    
    if st.session_state.selected_campaign and st.session_state.selected_campaign != 'All campaigns':
        filtered_df = filtered_df[filtered_df['Current campaign'] == st.session_state.selected_campaign]
    
    # Overall Summary
    st.markdown('<div class="overall-summary-header">Overall Summary</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        voicemail_count = len(df[df['Flag - Voicemail Over 15 sec'] == 'Check'])
        st.markdown(f'''
        <div class="metric-card-voicemail">
            <div style="font-size: 1.5rem; font-weight: bold;">{voicemail_count}</div>
            <div>Voicemail Over 15s</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        dead_count = len(df[df['Flag - Dead Call Over 15 sec'] == 'Check'])
        st.markdown(f'''
        <div class="metric-card-dead">
            <div style="font-size: 1.5rem; font-weight: bold;">{dead_count}</div>
            <div>Dead Calls Over 15s</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        decision_count = len(df[df['Flag - Decision Maker - NYI Under 10 sec'] == 'Check'])
        st.markdown(f'''
        <div class="metric-card-decision">
            <div style="font-size: 1.5rem; font-weight: bold;">{decision_count}</div>
            <div>Decision Maker Under 10s</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        total_flagged = len(df[df[['Flag - Voicemail Over 15 sec', 'Flag - Dead Call Over 15 sec', 
                                  'Flag - Decision Maker - NYI Under 10 sec', 'Flag - Wrong Number Under 10 sec', 
                                  'Flag - Unknown Under 5 sec']].eq('Check').any(axis=1)])
        st.markdown(f'''
        <div class="metric-card-total">
            <div style="font-size: 1.5rem; font-weight: bold;">{total_flagged}</div>
            <div>Total Flagged</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Agent Summary - Issues Overview
    st.markdown('<div class="section-header">Agent Summary - Issues Overview</div>', unsafe_allow_html=True)
    
    if 'Agent Name' in original_df.columns:
        # Always show summary for all agents (use original_df)
        agent_summary = original_df.groupby('Agent Name').agg({
            'Flag - Voicemail Over 15 sec': lambda x: (x == 'Check').sum(),
            'Flag - Dead Call Over 15 sec': lambda x: (x == 'Check').sum(),
            'Flag - Unknown Under 5 sec': lambda x: (x == 'Check').sum(),
        }).reset_index()
        
        # Calculate Decision Maker - NYI and Wrong Number totals per agent (for internal calculation only)
        decision_maker_nyi_counts = original_df.groupby('Agent Name')['Disposition'].apply(
            lambda x: (x == 'Decision Maker - NYI').sum()
        )
        wrong_number_counts = original_df.groupby('Agent Name')['Disposition'].apply(
            lambda x: (x == 'Wrong Number').sum()
        )
        dead_call_counts = original_df.groupby('Agent Name')['Disposition'].apply(
            lambda x: (x == 'Dead Call').sum()
        )
        unknown_counts = original_df.groupby('Agent Name')['Disposition'].apply(
            lambda x: (x == 'Unknown').sum()
        )
        
        # Calculate potential release/tech issue flag
        agent_summary['Potential Release/Tech Issue'] = agent_summary.apply(
            lambda row: 'Yes' if (decision_maker_nyi_counts.get(row['Agent Name'], 0) + wrong_number_counts.get(row['Agent Name'], 0)) < (dead_call_counts.get(row['Agent Name'], 0) + unknown_counts.get(row['Agent Name'], 0)) else 'No', axis=1
        )
        
        st.dataframe(agent_summary, use_container_width=True)
    

    
    # Flagged Calls
    st.markdown('<div class="section-header">Flagged Calls</div>', unsafe_allow_html=True)
    
    # Get flagged calls from filtered data
    flagged_calls = filtered_df[filtered_df[['Flag - Voicemail Over 15 sec', 'Flag - Dead Call Over 15 sec', 
                           'Flag - Decision Maker - NYI Under 10 sec', 'Flag - Wrong Number Under 10 sec', 
                           'Flag - Unknown Under 5 sec']].eq('Check').any(axis=1)]
    
    if not flagged_calls.empty:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Display flagged calls table with specific columns
            display_columns = ['Agent Name', 'Disposition', 'Recording Length (Formatted)', 'Phone Number']
            available_columns = [col for col in display_columns if col in flagged_calls.columns]
            
            if available_columns:
                st.dataframe(flagged_calls[available_columns], use_container_width=True)
        
        with col2:
            # Pie chart - Show only specific dispositions for filtered data
            # Filter to only show the 4 specific dispositions
            specific_dispositions = ['Decision Maker - NYI', 'Dead Call', 'Wrong Number', 'Unknown']
            pie_chart_df = filtered_df[filtered_df['Disposition'].isin(specific_dispositions)]
            disposition_counts = pie_chart_df['Disposition'].value_counts()
            
            color_map = {
                'Decision Maker - NYI': '#4C84FF',  
                'Unknown': '#ca1b1b',              
                'Wrong Number': '#F9C74F',          
                'Dead Call': '#FF6B6B'             
            }
            
            # Add counts to disposition names for the legend
            # Reorder to ensure Dead Call and Unknown are adjacent
            disposition_counts_with_counts = {}
            
            # Define the order we want: Dead Call and Unknown should be adjacent
            desired_order = ['Decision Maker - NYI', 'Wrong Number', 'Dead Call', 'Unknown']
            
            # Add items in the desired order
            for disposition in desired_order:
                if disposition in disposition_counts:
                    disposition_counts_with_counts[f"{disposition} ({disposition_counts[disposition]})"] = disposition_counts[disposition]
            
            # Add any remaining dispositions that weren't in our desired order
            for disposition, count in disposition_counts.items():
                if disposition not in desired_order:
                    disposition_counts_with_counts[f"{disposition} ({count})"] = count
            
            fig_pie = px.pie(
                values=list(disposition_counts_with_counts.values()),
                names=list(disposition_counts_with_counts.keys()),
                title="Total Calls by Disposition",
                color_discrete_map=color_map
            )
            # Force the exact order we want
            fig_pie.update_traces(
                marker_colors=[color_map.get(name.split(' (')[0], '#000000') for name in disposition_counts_with_counts.keys()]
            )
            fig_pie.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E0E0E0')
            )
            st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart_1")
        
        # Disposition Summary
        
        # Calculate totals for the 4 specific dispositions from filtered data
        specific_dispositions = ['Decision Maker - NYI', 'Dead Call', 'Wrong Number', 'Unknown']
        disposition_totals = {}
        
        for disposition in specific_dispositions:
            disposition_totals[disposition] = len(filtered_df[filtered_df['Disposition'] == disposition])
        
        # Create summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'''
            <div class="metric-card-total">
                <div style="font-size: 1.5rem; font-weight: bold;">{disposition_totals.get('Decision Maker - NYI', 0)}</div>
                <div>Decision Maker - NYI</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="metric-card-dead">
                <div style="font-size: 1.5rem; font-weight: bold;">{disposition_totals.get('Dead Call', 0)}</div>
                <div>Dead Call</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'''
            <div class="metric-card-decision">
                <div style="font-size: 1.5rem; font-weight: bold;">{disposition_totals.get('Wrong Number', 0)}</div>
                <div>Wrong Number</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'''
            <div class="metric-card-voicemail">
                <div style="font-size: 1.5rem; font-weight: bold;">{disposition_totals.get('Unknown', 0)}</div>
                <div>Unknown</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Aya's Idea component
        st.markdown('''
        <div class="aya-idea">
            💡 Aya's Idea ↑
        </div>
        ''', unsafe_allow_html=True)
    
    # Export Data
    st.markdown('<div class="section-header">Export Data</div>', unsafe_allow_html=True)
    
    if st.button("Download Flagged Calls CSV"):
        if not flagged_calls.empty:
            csv = flagged_calls.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="flagged_calls.csv",
                mime="text/csv"
            )
        else:
            st.warning("No flagged calls to export")

else:
    st.info("Please upload a CSV file to begin analysis.")

# Campaign Summary - Collapsible Section (at the end)
if uploaded_file is not None and 'Current campaign' in original_df.columns:
    st.markdown("---")
    
    # Collapsible section
    with st.expander("📊 Campaign Summary - Disposition Distribution", expanded=False):
        st.markdown('<div class="section-header">Campaign Summary - Disposition Distribution</div>', unsafe_allow_html=True)
        
        # Filter to only show the 5 specific dispositions for selected campaign (including Voicemail)
        specific_dispositions = ['Decision Maker - NYI', 'Dead Call', 'Wrong Number', 'Unknown', 'Voicemail']
        campaign_disposition_df = filtered_df[filtered_df['Disposition'].isin(specific_dispositions)]
        disposition_counts = campaign_disposition_df['Disposition'].value_counts()
        
        color_map = {
            'Decision Maker - NYI': '#4C84FF',
            'Unknown': '#ca1b1b',
            'Wrong Number': '#F9C74F',
            'Dead Call': '#FF6B6B',
            'Voicemail': '#9B59B6'
        }
        
        # Add counts to disposition names for the legend
        # Reorder to ensure Dead Call and Unknown are adjacent
        disposition_counts_with_counts = {}
        
        # Define the order we want: Dead Call and Unknown should be adjacent
        desired_order = ['Decision Maker - NYI', 'Wrong Number', 'Dead Call', 'Unknown', 'Voicemail']
        
        # Add items in the desired order
        for disposition in desired_order:
            if disposition in disposition_counts:
                disposition_counts_with_counts[f"{disposition} ({disposition_counts[disposition]})"] = disposition_counts[disposition]
        
        # Add any remaining dispositions that weren't in our desired order
        for disposition, count in disposition_counts.items():
            if disposition not in desired_order:
                disposition_counts_with_counts[f"{disposition} ({count})"] = count
        
        fig_campaign_disposition_pie = px.pie(
            values=list(disposition_counts_with_counts.values()),
            names=list(disposition_counts_with_counts.keys()),
            title="Total Calls by Disposition (Campaign Filtered)",
            color_discrete_map=color_map
        )
        # Force the exact order we want
        fig_campaign_disposition_pie.update_traces(
            marker_colors=[color_map.get(name.split(' (')[0], '#000000') for name in disposition_counts_with_counts.keys()]
        )
        fig_campaign_disposition_pie.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0')
        )
        st.plotly_chart(fig_campaign_disposition_pie, use_container_width=True, key="pie_chart_2")
        
        # Campaign Reachability Analysis
        st.markdown('<div class="section-header">Campaign Reachability Analysis</div>', unsafe_allow_html=True)
        
        # Calculate the metrics
        dead_calls = disposition_counts.get('Dead Call', 0)
        unknown_calls = disposition_counts.get('Unknown', 0)
        voicemail_calls = disposition_counts.get('Voicemail', 0)
        decision_maker = disposition_counts.get('Decision Maker - NYI', 0)
        wrong_number = disposition_counts.get('Wrong Number', 0)
        
        # Calculate totals
        low_reachability_total = dead_calls + unknown_calls + voicemail_calls
        good_reachability_total = decision_maker + wrong_number
        
        # Determine reachability status
        if low_reachability_total > good_reachability_total:
            status = "⚠️ LOW REACHABILITY"
            status_color = "#FF6B6B"
            message = f"""This campaign shows low reachability.<br><br>
Low Engagement ({low_reachability_total:,} calls):<br>
• Dead Calls: {dead_calls:,}<br>
• Unknown: {unknown_calls:,}<br>
• Voicemails: {voicemail_calls:,}<br><br>
Good Engagement ({good_reachability_total:,} calls):<br>
• Decision Makers: {decision_maker:,}<br>
• Wrong Numbers: {wrong_number:,}<br><br>
Low engagement exceeds good engagement — action may be needed to improve contact rates."""
        else:
            status = "✅ GOOD REACHABILITY"
            status_color = "#4C84FF"
            message = f"""This campaign shows good reachability.<br><br>
Good Engagement ({good_reachability_total:,} calls):<br>
• Decision Makers: {decision_maker:,}<br>
• Wrong Numbers: {wrong_number:,}<br><br>
Low Engagement ({low_reachability_total:,} calls):<br>
• Dead Calls: {dead_calls:,}<br>
• Unknown: {unknown_calls:,}<br>
• Voicemails: {voicemail_calls:,}<br><br>
Good engagement exceeds low engagement — campaign is performing well."""
        
        # Display the analysis
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, {status_color}20 0%, {status_color}10 100%);
            border: 2px solid {status_color};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: #E0E0E0;
        ">
            <div style="
                font-size: 1.5rem;
                font-weight: bold;
                color: {status_color};
                margin-bottom: 1rem;
                text-align: center;
            ">
                {status}
            </div>
            <div style="
                font-size: 1rem;
                line-height: 1.6;
                text-align: left;
            ">
                {message}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Credits Footer
    st.markdown('''
    <div class="footer">
        Developed by <a href="https://t.me/Mohmed_abdo" target="_blank" class="footer-link">Mohamed Abdo</a> © 2025
    </div>
    ''', unsafe_allow_html=True)