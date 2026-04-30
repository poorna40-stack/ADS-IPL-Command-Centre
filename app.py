"""
app.py — Home / Landing Page
IPL Advanced Analytics Dashboard (2008–2025)

Streamlit multi-page app entry point.
Sub-pages live in pages/
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from shared import (
    require_data, load_data, inject_css,
    GOLD, TEAL, RED, NAVY, CARD,
)
from src.analysis import (
    season_scoring_trends,
)



# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IPL Analytics · 2008–2025",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Sidebar nav ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] > div:first-child > div:first-child > div:first-child {
            display: flex;
            flex-direction: column;
        }
        [data-testid="stSidebarNav"] {
            order: 2;
        }
        div[data-testid="stSidebarUserContent"] {
            order: 1;
        }
    </style>
    <div style='text-align:center;padding:0.2rem 0 .6rem;'>
        <div style='font-size:2.4rem;'>🏏</div>
        <div style='font-family:Space Grotesk,sans-serif;font-size:1.15rem;
                     font-weight:700;color:#FFD700;letter-spacing:-.01em;'>
            IPL Analytics
        </div>
        <div style='font-size:.68rem;color:rgba(232,234,246,.35);
                     letter-spacing:.1em;margin-top:.2rem;'>2008 – 2025</div>
    </div>
    <hr style='border-color:rgba(255,215,0,.12);margin:.5rem 0;'/>
    """, unsafe_allow_html=True)


# ── Hero banner ────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:2rem 0 1.2rem;'>
    <div style='font-size:.75rem;color:rgba(232,234,246,.3);letter-spacing:.18em;
                 text-transform:uppercase;margin-bottom:.6rem;'>
        Sports Intelligence Platform
    </div>
    <h1 style='margin:0;font-size:2.8rem;font-family:Space Grotesk,sans-serif;
                color:#FFD700;letter-spacing:-.03em;line-height:1.1;'>
        IPL Advanced Analytics
    </h1>
    <p style='color:rgba(232,234,246,.42);margin:.7rem 0 0;font-size:.98rem;
               max-width:560px;'>
        18 seasons of ball-by-ball intelligence. ML-powered win prediction.
        Deep player, team and venue insights.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
ok = load_data()
if not ok:
    st.error("⚠️  Data files not found in `data/`.")
    st.code(
        "# Generate synthetic demo data:\n"
        "python generate_sample_data.py\n\n"
        "# Or download real data from Kaggle and place in data/:\n"
        "# matches.csv + deliveries.csv",
        language="bash",
    )
    st.stop()

matches   = st.session_state["matches"]
deliveries = st.session_state["deliveries"]
merged    = st.session_state["merged"]
seasons   = st.session_state["seasons"]
all_teams = st.session_state["all_teams"]

# ── Global KPIs ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Seasons",    matches["season"].nunique())
c2.metric("Matches",    f"{len(matches):,}")
c3.metric("Deliveries", f"{len(deliveries):,}")
c4.metric("Teams",      len(all_teams))
c5.metric("Venues",     matches["venue"].nunique())
c6.metric("Players",    deliveries["batter"].nunique())

st.markdown("<hr style='margin:1.2rem 0;border-color:rgba(255,215,0,.1);'/>",
            unsafe_allow_html=True)

trend_df = season_scoring_trends(merged)

# ── Scoring evolution ──────────────────────────────────────────────────────────
st.subheader("📈 18-Season Scoring Evolution")

fig_spark = go.Figure()
scores = trend_df["avg_first_innings_score"].round(1)
# colour by direction: green if rising, red if falling
deltas = scores.diff().fillna(0)
colors_bar = [TEAL if d >= 0 else RED for d in deltas]

fig_spark.add_trace(go.Bar(
    x=trend_df["season"], y=scores,
    marker_color=colors_bar, opacity=0.6,
    hovertemplate="Season %{x}<br>Avg: %{y:.1f}<extra></extra>",
    showlegend=False,
))
fig_spark.add_trace(go.Scatter(
    x=trend_df["season"], y=scores,
    mode="lines+markers",
    line=dict(color=GOLD, width=2.5),
    marker=dict(size=6, color=GOLD),
    hovertemplate="Season %{x}<br>Avg: %{y:.1f}<extra></extra>",
    name="Avg 1st innings",
))
fig_spark.update_layout(
    paper_bgcolor=NAVY, plot_bgcolor=CARD, height=280,
    font=dict(color="#E8EAF6"), margin=dict(l=50, r=20, t=10, b=40),
    xaxis_title="Season", yaxis_title="Avg 1st Innings Score",
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
    showlegend=False,
)
st.plotly_chart(fig_spark, use_container_width=True)

st.markdown("<hr style='margin:1rem 0;border-color:rgba(255,215,0,.08);'/>",
            unsafe_allow_html=True)

# ── Feature grid ──────────────────────────────────────────────────────────────
st.subheader("🚀 Explore the Dashboard")
st.caption("Use the sidebar to navigate between pages.")

features = [
    ("👤", "Player Analytics",    "Batting & bowling leaderboards, career arcs, "
                                   "phase-wise strike rate, player comparison, Best XI generator",    GOLD),
    ("🏆", "Team Analytics",      "Win percentages, head-to-head scoreboard, "
                                   "toss strategy analysis, season-by-season form heatmap",           TEAL),
    ("🏟️", "Venue Intelligence",  "Ground scoring profiles, team-venue win heatmap, "
                                   "advantage scoring, batting vs bowling venues",                    "#38BDF8"),
    ("📈", "Match Trends",        "Over-by-over run rates, boundary frequency charts, "
                                   "powerplay vs death analysis, scoring evolution",                  "#FB923C"),
    ("🤖", "ML Prediction",       "Random Forest pre-match winner prediction using "
                                   "team composition, toss decision and venue history",               "#A78BFA"),
    ("📊", "Win Probability",     "GradientBoosting ball-by-ball win probability, "
                                   "momentum swing chart, live match simulator, commentary",          RED),
]

row1 = st.columns(3)
row2 = st.columns(3)
for i, (icon, title, desc, color) in enumerate(features):
    col = row1[i] if i < 3 else row2[i - 3]
    with col:
        st.markdown(f"""
        <div style='background:{CARD};border:1px solid {color}18;
                    border-top:2px solid {color};border-radius:12px;
                    padding:1.2rem;min-height:120px;margin-bottom:.5rem;'>
            <div style='font-size:1.4rem;margin-bottom:.5rem;'>{icon}</div>
            <div style='font-family:Space Grotesk;font-size:.9rem;
                         font-weight:600;color:{color};margin-bottom:.35rem;'>{title}</div>
            <div style='font-size:.73rem;color:rgba(232,234,246,.45);
                         line-height:1.5;'>{desc}</div>
        </div>""", unsafe_allow_html=True)



# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:2.5rem 0 1rem;
             color:rgba(232,234,246,.15);font-size:.7rem;letter-spacing:.05em;'>
    IPL Advanced Analytics Dashboard &nbsp;·&nbsp;
    Streamlit + Plotly + Scikit-learn &nbsp;·&nbsp;
    Data: 2008–2025
</div>
""", unsafe_allow_html=True)
