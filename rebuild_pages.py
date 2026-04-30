import os

pages_dir = "pages"
os.makedirs(pages_dir, exist_ok=True)

# Common header for all pages
header = """import streamlit as st
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

"""

# 1. PLAYERS
with open(f"{pages_dir}/1_👤_Players.py", "w", encoding="utf-8") as f:
    f.write(header + """
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

""")

# 2. TEAMS
with open(f"{pages_dir}/2_🏆_Teams.py", "w", encoding="utf-8") as f:
    f.write(header + """
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
""")

# 3. VENUES
with open(f"{pages_dir}/3_🏟️_Venues.py", "w", encoding="utf-8") as f:
    f.write(header + """
st.title("🏟️ Venue Intelligence")
st.subheader("Venue Scoring Analysis")
v_stats = venue_stats(filt_m, merged)
if not v_stats.empty:
    st.plotly_chart(plot_venue_stats(v_stats), use_container_width=True)
else:
    st.info("No venue data for current filters.")

st.subheader("Team Wins per Venue (Heatmap)")
hm_pivot = team_venue_wins(filt_m)
if not hm_pivot.empty and hm_pivot.shape[1] >= 2:
    st.plotly_chart(plot_venue_heatmap(hm_pivot), use_container_width=True)
""")

# 4. TRENDS
with open(f"{pages_dir}/4_📈_Trends.py", "w", encoding="utf-8") as f:
    f.write(header + """
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
""")

# 5. PREDICTION
with open(f"{pages_dir}/5_🤖_Prediction.py", "w", encoding="utf-8") as f:
    f.write(header + """
from src.model import get_trained_match_model

st.title("🤖 ML Match Prediction")
with st.spinner("Loading prediction model..."):
    match_model = get_trained_match_model(matches)

acc = match_model.accuracy
if acc:
    st.success(f"Model accuracy on holdout set: **{acc}%**")

col1, col2, col3 = st.columns(3)
with col1:
    pred_team1 = st.selectbox("Team 1", all_teams)
with col2:
    pred_team2 = st.selectbox("Team 2", [t for t in all_teams if t != pred_team1])
with col3:
    pred_toss_winner = st.selectbox("Toss Winner", [pred_team1, pred_team2])

col4, col5 = st.columns(2)
with col4:
    pred_toss_decision = st.selectbox("Toss Decision", ["bat", "field"])
with col5:
    venues_list = sorted(matches["venue"].dropna().unique().tolist())
    pred_venue = st.selectbox("Venue", venues_list)

if st.button("🎯 Predict Winner", type="primary"):
    result = match_model.predict(pred_team1, pred_team2, pred_toss_winner, pred_toss_decision, pred_venue)
    winner = max(result, key=result.get)
    st.markdown(f"### Predicted Winner: **{winner}** ({result[winner]}%)")
    fig_bar = go.Figure(go.Bar(x=[result[pred_team1], result[pred_team2]], y=[pred_team1, pred_team2], orientation="h", text=[f"{result[pred_team1]}%", f"{result[pred_team2]}%"]))
    fig_bar.update_layout(paper_bgcolor=NAVY, plot_bgcolor=CARD, font=dict(color="#E8EAF6"))
    st.plotly_chart(fig_bar, use_container_width=True)
""")

# 6. WIN PROBABILITY
with open(f"{pages_dir}/6_📊_Win_Probability.py", "w", encoding="utf-8") as f:
    f.write(header + """
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
""")

print("Successfully generated all pages!")
