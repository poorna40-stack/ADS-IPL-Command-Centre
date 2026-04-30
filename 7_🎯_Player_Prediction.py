import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shared import require_data, CARD, GOLD, TEAL, RED, NAVY
from src.player_model import get_trained_player_model

require_data()

matches = st.session_state["matches"]
deliveries = st.session_state["deliveries"]
merged = st.session_state["merged"]
seasons = st.session_state["seasons"]
all_teams = st.session_state["all_teams"]

with st.sidebar:
    st.markdown("### Player Prediction")
    st.info("Uses Random Forest models to predict expected performance based on historical data.")

st.title("🎯 Player Performance Prediction")
st.markdown("<p style='color:rgba(232,234,246,0.5);'>Predict how a batter or bowler is expected to perform against a specific team at a specific venue.</p>", unsafe_allow_html=True)

with st.spinner("Training/Loading player performance models..."):
    model = get_trained_player_model(matches, deliveries)

venues_list = ["None"] + sorted(matches["venue"].dropna().unique().tolist())
batters = sorted(st.session_state.get("valid_batters", deliveries["batter"].dropna().unique().tolist()))
bowlers = sorted(st.session_state.get("valid_bowlers", deliveries["bowler"].dropna().unique().tolist()))

tab1, tab2 = st.tabs(["🏏 Batter Prediction", "⚾ Bowler Prediction"])

with tab1:
    st.subheader("Predict Batting Performance")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_batter = st.selectbox("Batter", batters, key="pred_batter")
    with col2:
        opp_team = st.selectbox("Bowling Team (Opposition)", all_teams, key="pred_bat_opp")
    with col3:
        venue = st.selectbox("Venue", venues_list, key="pred_bat_ven")
        
    if st.button("Predict Batting Performance", type="primary"):
        res = model.predict_batter(selected_batter, opp_team, venue)
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {CARD}, #181818);
                    border: 1px solid rgba(255,215,0,0.3); border-radius: 16px;
                    padding: 2rem; text-align: center; margin-top: 1rem;'>
            <div style='font-size: 0.75rem; color: rgba(232,234,246,0.4);
                         letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.5rem;'>
                EXPECTED PERFORMANCE FOR {selected_batter.upper()}
            </div>
            <div style='font-family: Space Grotesk; font-size: 2.5rem;
                         font-weight: 700; color: {GOLD}; line-height: 1.2;'>
                {res['expected_runs']} Runs
            </div>
            <div style='font-size: 1.1rem; color: rgba(232,234,246,0.6); margin-top: 0.5rem;'>
                Expected Strike Rate: <strong style='color:{TEAL};'>{res['expected_strike_rate']}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.subheader("Predict Bowling Performance")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_bowler = st.selectbox("Bowler", bowlers, key="pred_bowler")
    with col2:
        opp_team_bowl = st.selectbox("Batting Team (Opposition)", all_teams, key="pred_bowl_opp")
    with col3:
        venue_bowl = st.selectbox("Venue", venues_list, key="pred_bowl_ven")
        
    if st.button("Predict Bowling Performance", type="primary"):
        res = model.predict_bowler(selected_bowler, opp_team_bowl, venue_bowl)
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {CARD}, #181818);
                    border: 1px solid rgba(0,212,170,0.3); border-radius: 16px;
                    padding: 2rem; text-align: center; margin-top: 1rem;'>
            <div style='font-size: 0.75rem; color: rgba(232,234,246,0.4);
                         letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.5rem;'>
                EXPECTED PERFORMANCE FOR {selected_bowler.upper()}
            </div>
            <div style='font-family: Space Grotesk; font-size: 2.5rem;
                         font-weight: 700; color: {TEAL}; line-height: 1.2;'>
                {res['expected_wickets']} Wickets
            </div>
            <div style='font-size: 1.1rem; color: rgba(232,234,246,0.6); margin-top: 0.5rem;'>
                Expected Economy: <strong style='color:{RED};'>{res['expected_economy']}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
