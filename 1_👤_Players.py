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


st.title("👤 Player Analytics")

st.subheader("Batting Leaderboard")
bat_df = top_batsmen(filt_d, n=20,
                     season=None if selected_season == "All Seasons" else selected_season,
                     team=None if selected_team == "All Teams" else selected_team)
st.plotly_chart(plot_top_batsmen(bat_df, n=15), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Top Batsmen — Stats**")
    st.dataframe(
        bat_df[["batter", "total_runs", "strike_rate", "fours", "sixes", "innings"]].head(10),
        use_container_width=True, hide_index=True,
    )
with col2:
    st.markdown("**Top Bowlers — Stats**")
    bowl_df = top_bowlers(filt_d, n=10,
                          season=None if selected_season == "All Seasons" else selected_season,
                          team=None if selected_team == "All Teams" else selected_team)
    st.dataframe(
        bowl_df[["bowler", "wickets", "economy", "overs"]].head(10),
        use_container_width=True, hide_index=True,
    )

st.markdown("<hr style='margin:1rem 0;'/>", unsafe_allow_html=True)
st.subheader("Bowling Leaderboard")
st.plotly_chart(plot_top_bowlers(bowl_df, n=10), use_container_width=True)

