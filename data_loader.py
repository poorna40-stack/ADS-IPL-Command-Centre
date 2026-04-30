"""
IPL Data Loader Module
Handles loading and initial validation of IPL datasets from the archive monolith file.
"""

import pandas as pd
import streamlit as st


@st.cache_data
def load_all_data(filepath: str = "data/dataset/IPL.csv"):
    """Load monolith dataset from archive and split into matches and deliveries."""
    df = pd.read_csv(filepath, low_memory=False)

    # ── DELIVERIES ─────────────────────────────────────────────────────────────
    deliveries = df[[
        "match_id", "innings", "batting_team", "bowling_team", "over", "ball",
        "batter", "bowler", "non_striker", "runs_batter", "runs_extras", "runs_total",
        "player_out", "wicket_kind", "fielders"
    ]].copy()

    deliveries = deliveries.rename(columns={
        "runs_batter": "runs_off_bat",
        "runs_extras": "extras",
        "runs_total": "total_runs",
        "player_out": "player_dismissed",
        "wicket_kind": "dismissal_kind",
        "fielders": "fielder"
    })

    # Ensure missing values are filled
    deliveries["player_dismissed"] = deliveries["player_dismissed"].fillna("")
    deliveries["dismissal_kind"] = deliveries["dismissal_kind"].fillna("")
    deliveries["fielder"] = deliveries["fielder"].fillna("")
    
    numeric_cols = ["runs_off_bat", "extras", "total_runs"]
    for col in numeric_cols:
        deliveries[col] = pd.to_numeric(deliveries[col], errors="coerce").fillna(0)

    # ── MATCHES ────────────────────────────────────────────────────────────────
    matches = df.groupby("match_id").first().reset_index()

    matches = matches.rename(columns={
        "match_id": "id",
        "match_won_by": "winner",
    })

    matches["team1"] = matches["batting_team"]
    matches["team2"] = matches["bowling_team"]

    # result extraction
    if "win_outcome" in matches.columns:
        matches["result"] = matches["win_outcome"].astype(str).str.extract(r'([a-zA-Z]+)')[0].fillna("Unknown")
        matches["result_margin"] = matches["win_outcome"].astype(str).str.extract(r'(\d+)')[0].fillna(0).astype(float)
    else:
        matches["result"] = "No Result"
        matches["result_margin"] = 0

    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")
    if "season" in matches.columns:
        matches["season"] = matches["season"].astype(str)

    fills = {
        "result": "No Result", "result_margin": 0,
        "player_of_match": "Unknown", "venue": "Unknown Venue",
        "city": "Unknown", "winner": "No Result", "toss_decision": "Unknown",
    }
    for col, val in fills.items():
        if col in matches.columns:
            matches[col] = matches[col].fillna(val)

    return matches, deliveries
