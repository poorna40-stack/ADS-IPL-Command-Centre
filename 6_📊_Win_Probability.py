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


from src.win_probability import get_trained_wp_model, create_match_state, extract_key_events

st.title("📊 Ball-by-Ball Win Probability")
with st.spinner("Training win probability model..."):
    wp_model = get_trained_wp_model(merged)

if wp_model.auc:
    st.success(f"Model AUC: **{wp_model.auc}**")

wp_season = st.selectbox("Select Season", seasons, index=len(seasons)-1)
season_matches = matches[matches["season"] == wp_season].sort_values("date", ascending=False)
season_matches["label"] = season_matches["team1"] + " vs " + season_matches["team2"]

if not season_matches.empty:
    selected_label = st.selectbox("Select Match", season_matches["label"].tolist())
    chosen_row = season_matches[season_matches["label"] == selected_label].iloc[0]
    
    if st.button("🔍 Analyse Match", type="primary"):
        with st.spinner("Computing probabilities..."):
            match_state = create_match_state(merged, chosen_row["id"])
            if not match_state.empty:
                wp_result = wp_model.predict_match(match_state)
                events = extract_key_events(match_state)
                fig_wp = plot_win_probability(wp_result["ball_number"].tolist(), wp_result["win_probability"].tolist(), events=events, team=chosen_row["team2"])
                st.plotly_chart(fig_wp, use_container_width=True)
