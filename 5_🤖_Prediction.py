import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shared import require_data, CARD, GOLD, TEAL, RED, NAVY

require_data()

matches = st.session_state["matches"]
all_teams = st.session_state["all_teams"]
venues_list = ["None"] + sorted(matches["venue"].dropna().unique().tolist())

with st.sidebar:
    st.markdown("### Match Prediction")
    st.info("Predicts match outcomes purely based on historical head-to-head records and selected conditions.")

st.title("🤖 Historical Match Prediction")
st.markdown("<p style='color:rgba(232,234,246,0.5);'>Evaluate winning probabilities based purely on past history (Head-to-Head) from the dataset.</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    pred_team1 = st.selectbox("Team 1", all_teams)
with col2:
    pred_team2 = st.selectbox("Team 2", [t for t in all_teams if t != pred_team1])
with col3:
    pred_toss_winner = st.selectbox("Toss Winner", ["None", pred_team1, pred_team2])

col4, col5 = st.columns(2)
with col4:
    pred_toss_decision = st.selectbox("Toss Decision", ["None", "bat", "field"])
with col5:
    pred_venue = st.selectbox("Venue", venues_list)

if st.button("🎯 Predict Winner", type="primary"):
    # Base Head-to-Head mask
    h2h_mask = ((matches["team1"] == pred_team1) & (matches["team2"] == pred_team2)) | \
               ((matches["team1"] == pred_team2) & (matches["team2"] == pred_team1))
    
    base_subset = matches[h2h_mask & (matches["winner"] != "No Result")]
    
    # Filtered mask
    mask = h2h_mask.copy()
    filters_applied = []
    
    if pred_toss_winner != "None":
        mask = mask & (matches["toss_winner"] == pred_toss_winner)
        filters_applied.append(f"Toss Winner: {pred_toss_winner}")
    if pred_toss_decision != "None":
        mask = mask & (matches["toss_decision"] == pred_toss_decision)
        filters_applied.append(f"Toss Decision: {pred_toss_decision}")
    if pred_venue != "None":
        mask = mask & (matches["venue"] == pred_venue)
        filters_applied.append(f"Venue: {pred_venue}")
        
    subset = matches[mask & (matches["winner"] != "No Result")]
    
    fallback = False
    if len(subset) == 0:
        if len(filters_applied) > 0:
            st.warning(f"No historical matches found matching the exact combination ({', '.join(filters_applied)}). Falling back to overall Head-to-Head.")
        subset = base_subset
        fallback = True
        
    if len(subset) == 0:
        st.error(f"No historical matches found between {pred_team1} and {pred_team2}!")
    else:
        win_counts = subset["winner"].value_counts()
        t1_wins = win_counts.get(pred_team1, 0)
        t2_wins = win_counts.get(pred_team2, 0)
        total = t1_wins + t2_wins
        
        if total == 0:
            st.error(f"No conclusive match results found between {pred_team1} and {pred_team2}!")
        else:
            t1_prob = round((t1_wins / total) * 100, 1)
            t2_prob = round((t2_wins / total) * 100, 1)
            
            winner = pred_team1 if t1_prob > t2_prob else (pred_team2 if t2_prob > t1_prob else "Tie")
            
            st.markdown(f"### Historical Win Probability")
            if not fallback and len(filters_applied) > 0:
                st.caption(f"Based on **{total} matches** matching your specific filters.")
            else:
                st.caption(f"Based on **{total} overall Head-to-Head matches**.")
                
            fig_bar = go.Figure(go.Bar(
                x=[t1_prob, t2_prob], 
                y=[pred_team1, pred_team2], 
                orientation="h", 
                text=[f"{t1_prob}% ({t1_wins} wins)", f"{t2_prob}% ({t2_wins} wins)"],
                textposition="inside",
                marker=dict(color=[GOLD if winner == pred_team1 else "#1a3a5c", GOLD if winner == pred_team2 else "#1a3a5c"])
            ))
            fig_bar.update_layout(
                paper_bgcolor=NAVY, 
                plot_bgcolor=CARD, 
                font=dict(color="#E8EAF6"),
                height=180,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.0)"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
