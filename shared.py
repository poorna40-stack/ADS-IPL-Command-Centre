import streamlit as st
import os
import sys

# Add root to path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import load_all_data
from src.preprocessing import get_clean_data

# ── Colors & Branding ──────────────────────────────────────────────────────────
GOLD = "#FFD700"
TEAL = "#00D4AA"
RED  = "#FF4B4B"
NAVY = "#050505"
CARD = "#121212"

def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
        background-color: {NAVY};
        color: #E8EAF6;
    }}
    .stApp {{ background-color: {NAVY}; }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #111111 0%, #000000 100%);
        border-right: 1px solid rgba(255,215,0,0.15);
    }}
    
    /* Metric cards */
    [data-testid="metric-container"] {{
        background: {CARD};
        border: 1px solid rgba(255,215,0,0.12);
        border-radius: 12px;
        padding: 16px 20px;
    }}
    
    /* Headers */
    h1 {{ font-family: 'Space Grotesk', sans-serif; color: {GOLD} !important; }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-track {{ background: {NAVY}; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255,215,0,0.3); border-radius: 4px; }}

    /* Top Header overrides (Deploy button and 3 dots) */
    .stAppDeployButton, [data-testid="stAppDeployButton"] {{ display: none !important; visibility: hidden !important; }}
    #MainMenu, [data-testid="stHeaderActionElements"], [data-testid="stToolbar"] {{ display: none !important; visibility: hidden !important; }}

    /* Change sidebar toggle arrow to hamburger (☰) for both Open and Close states */
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg {{
        display: none !important;
    }}
    
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {{
        position: relative !important;
        opacity: 1 !important;
        visibility: visible !important;
    }}

    [data-testid="stSidebarCollapsedControl"]::before,
    [data-testid="stSidebarCollapseButton"]::before,
    [data-testid="collapsedControl"]::before {{
        content: "☰" !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        line-height: 1 !important;
        display: block !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: none !important;
    }}
    [data-testid="stSidebarNavItems"] li:first-child a span {{
        display: none !important;
    }}
    [data-testid="stSidebarNavItems"] li:first-child a::after {{
        content: "🏠 HOME";
        font-size: 14px;
        margin-left: 0.5rem;
    }}
    /* Fallback for older Streamlit versions */
    [data-testid="stSidebarNav"] li:first-child a span {{
        display: none !important;
    }}
    [data-testid="stSidebarNav"] li:first-child a::after {{
        content: "🏠 HOME";
        font-size: 14px;
        margin-left: 0.5rem;
    }}
    </style>
    """, unsafe_allow_html=True)

def load_data():
    if "matches" not in st.session_state:
        try:
            m_raw, d_raw = load_all_data()
            m, d, mrg = get_clean_data(m_raw, d_raw)
            
            st.session_state["matches"] = m
            st.session_state["deliveries"] = d
            st.session_state["merged"] = mrg
            st.session_state["seasons"] = sorted(m["season"].unique().tolist())
            st.session_state["all_teams"] = sorted(list(set(m["team1"].unique()) | set(m["team2"].unique())))
            
            batter_seasons = mrg.groupby("batter")["season"].nunique()
            st.session_state["valid_batters"] = batter_seasons[batter_seasons >= 5].index.tolist()
            
            bowler_seasons = mrg.groupby("bowler")["season"].nunique()
            st.session_state["valid_bowlers"] = bowler_seasons[bowler_seasons >= 5].index.tolist()
            return True
        except Exception as e:
            return False
    return True

def require_data():
    if "matches" not in st.session_state:
        st.warning("Please load data from the Home page first.")
        st.stop()
