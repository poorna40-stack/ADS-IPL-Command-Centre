import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shared import require_data, CARD, GOLD, TEAL, RED, NAVY
from src.analysis import *
from src.visualization import *

require_data()

matches = st.session_state["matches"]
deliveries = st.session_state["deliveries"]
merged = st.session_state["merged"]
seasons = st.session_state["seasons"]
all_teams = st.session_state["all_teams"]

with st.sidebar:
    st.markdown("### Filters")
    selected_season = st.selectbox("Season", ["All Seasons"] + seasons)
    selected_team = st.selectbox("Team", ["All Teams"] + all_teams)

def filter_deliveries():
    df = merged.copy()
    if selected_season != "All Seasons":
        df = df[df["season"] == selected_season]
    if selected_team != "All Teams":
        df = df[(df["batting_team"] == selected_team) | (df["bowling_team"] == selected_team)]
    return df

def filter_matches():
    df = matches.copy()
    if selected_season != "All Seasons":
        df = df[df["season"] == selected_season]
    if selected_team != "All Teams":
        df = df[(df["team1"] == selected_team) | (df["team2"] == selected_team)]
    return df

filt_d = filter_deliveries()
filt_m = filter_matches()


st.title("📈 Match Trends")
st.subheader("Season Scoring Trends")
filt_mrg = merged.copy()
if selected_season != "All Seasons":
    filt_mrg = filt_mrg[filt_mrg["season"] == selected_season]
if selected_team != "All Teams":
    filt_mrg = filt_mrg[(filt_mrg["batting_team"] == selected_team) | (filt_mrg["bowling_team"] == selected_team)]

trend_df = season_scoring_trends(filt_mrg)
st.plotly_chart(plot_season_scoring(trend_df), use_container_width=True)

st.subheader("Over-by-Over Average Scoring")
over_df = filt_d.groupby("over")["total_runs"].mean().reset_index().rename(columns={"total_runs": "avg_runs"})
fig_over = go.Figure(go.Bar(x=over_df["over"] + 1, y=over_df["avg_runs"].round(2), marker=dict(color=over_df["avg_runs"], colorscale=[[0, "#1a3a5c"], [0.5, TEAL], [1, GOLD]])))
fig_over.update_layout(paper_bgcolor=NAVY, plot_bgcolor=CARD, font=dict(color="#E8EAF6"))
st.plotly_chart(fig_over, use_container_width=True)
