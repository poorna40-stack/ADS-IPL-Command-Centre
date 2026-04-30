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


st.title("🏆 Team Analytics")
st.subheader("Team Performance Overview")

win_df = team_win_percentage(filt_m)
st.plotly_chart(plot_win_percentage(win_df), use_container_width=True)

col1, col2 = st.columns([1.2, 1])
with col1:
    toss_df = toss_impact(filt_m)
    st.subheader("Toss Impact")
    st.plotly_chart(plot_toss_impact(toss_df), use_container_width=True)
with col2:
    st.subheader("Full Team Table")
    st.dataframe(win_df[["team", "played", "won", "win_pct"]], use_container_width=True, hide_index=True)
