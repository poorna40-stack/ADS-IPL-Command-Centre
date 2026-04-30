"""
IPL Player Performance Prediction Model
Predicts expected runs and strike rate for a batter, and wickets and economy for a bowler.
"""

import pandas as pd
import numpy as np
import pickle
import os
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

MODEL_PATH = "data/player_perf_model.pkl"
ENCODER_PATH = "data/player_perf_encoders.pkl"

class PlayerPerformanceModel:
    """Predicts batter and bowler expected stats."""

    CAT_COLS_BAT = ["batter", "bowling_team", "venue"]
    CAT_COLS_BOWL = ["bowler", "batting_team", "venue"]

    def __init__(self):
        # Batting models
        self.model_runs = RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=10, random_state=42, n_jobs=-1)
        self.model_sr = RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=10, random_state=42, n_jobs=-1)
        self.bat_encoders: dict[str, LabelEncoder] = {}
        
        # Bowling models
        self.model_wickets = RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=10, random_state=42, n_jobs=-1)
        self.model_econ = RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=10, random_state=42, n_jobs=-1)
        self.bowl_encoders: dict[str, LabelEncoder] = {}
        
        self.trained = False

    def _prepare_batting_data(self, matches: pd.DataFrame, deliveries: pd.DataFrame) -> pd.DataFrame:
        batter_stats = deliveries.groupby(["match_id", "batter", "bowling_team"]).agg(
            runs=("runs_off_bat", "sum"),
            balls=("ball", "count")
        ).reset_index()

        batter_stats["strike_rate"] = np.where(
            batter_stats["balls"] > 0,
            (batter_stats["runs"] / batter_stats["balls"]) * 100,
            0
        )

        m_subset = matches[["id", "venue"]].rename(columns={"id": "match_id"})
        df = pd.merge(batter_stats, m_subset, on="match_id", how="inner")
        return df[df["balls"] >= 5].copy()
        
    def _prepare_bowling_data(self, matches: pd.DataFrame, deliveries: pd.DataFrame) -> pd.DataFrame:
        credited = ["caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket"]
        df_w = deliveries.copy()
        df_w["is_bowler_wicket"] = df_w["dismissal_kind"].isin(credited).astype(int)
        
        bowler_stats = df_w.groupby(["match_id", "bowler", "batting_team"]).agg(
            wickets=("is_bowler_wicket", "sum"),
            runs_conceded=("runs_off_bat", "sum"), # approximation, usually extras are included but keeping simple
            balls=("ball", "count")
        ).reset_index()
        
        bowler_stats["overs"] = bowler_stats["balls"] / 6.0
        bowler_stats["economy"] = np.where(
            bowler_stats["overs"] > 0,
            bowler_stats["runs_conceded"] / bowler_stats["overs"],
            0
        )
        
        m_subset = matches[["id", "venue"]].rename(columns={"id": "match_id"})
        df = pd.merge(bowler_stats, m_subset, on="match_id", how="inner")
        return df[df["balls"] >= 6].copy() # At least 1 over bowled

    def _encode(self, df: pd.DataFrame, cols: list, encoders_dict: dict, fit: bool = False) -> pd.DataFrame:
        out = df.copy()
        for col in cols:
            if col not in out.columns:
                continue
            enc_col = f"{col}_enc"
            if fit:
                le = LabelEncoder()
                out[enc_col] = le.fit_transform(out[col].astype(str))
                encoders_dict[col] = le
            else:
                le = encoders_dict[col]
                known = set(le.classes_)
                out[col] = out[col].apply(lambda x: x if x in known else le.classes_[0])
                out[enc_col] = le.transform(out[col].astype(str))
        return out

    def train(self, matches: pd.DataFrame, deliveries: pd.DataFrame):
        # Batting
        bat_df = self._prepare_batting_data(matches, deliveries)
        bat_df = self._encode(bat_df, self.CAT_COLS_BAT, self.bat_encoders, fit=True)
        X_bat = bat_df[[f"{c}_enc" for c in self.CAT_COLS_BAT]]
        self.model_runs.fit(X_bat, bat_df["runs"])
        self.model_sr.fit(X_bat, bat_df["strike_rate"])
        
        # Bowling
        bowl_df = self._prepare_bowling_data(matches, deliveries)
        bowl_df = self._encode(bowl_df, self.CAT_COLS_BOWL, self.bowl_encoders, fit=True)
        X_bowl = bowl_df[[f"{c}_enc" for c in self.CAT_COLS_BOWL]]
        self.model_wickets.fit(X_bowl, bowl_df["wickets"])
        self.model_econ.fit(X_bowl, bowl_df["economy"])
        
        self.trained = True

    def predict_batter(self, batter: str, bowling_team: str, venue: str) -> dict:
        if not self.trained: raise RuntimeError("Model not trained yet.")
        row = pd.DataFrame([{"batter": batter, "bowling_team": bowling_team, "venue": venue}])
        row = self._encode(row, self.CAT_COLS_BAT, self.bat_encoders, fit=False)
        X = row[[f"{c}_enc" for c in self.CAT_COLS_BAT]]
        
        return {
            "expected_runs": round(self.model_runs.predict(X)[0]),
            "expected_strike_rate": round(self.model_sr.predict(X)[0], 2)
        }
        
    def predict_bowler(self, bowler: str, batting_team: str, venue: str) -> dict:
        if not self.trained: raise RuntimeError("Model not trained yet.")
        row = pd.DataFrame([{"bowler": bowler, "batting_team": batting_team, "venue": venue}])
        row = self._encode(row, self.CAT_COLS_BOWL, self.bowl_encoders, fit=False)
        X = row[[f"{c}_enc" for c in self.CAT_COLS_BOWL]]
        
        return {
            "expected_wickets": round(self.model_wickets.predict(X)[0]),
            "expected_economy": round(self.model_econ.predict(X)[0], 2)
        }

    def save(self, model_path: str = MODEL_PATH, enc_path: str = ENCODER_PATH):
        with open(model_path, "wb") as f:
            pickle.dump({
                "runs": self.model_runs, "sr": self.model_sr,
                "wickets": self.model_wickets, "econ": self.model_econ
            }, f)
        with open(enc_path, "wb") as f:
            pickle.dump({"bat": self.bat_encoders, "bowl": self.bowl_encoders}, f)

    def load(self, model_path: str = MODEL_PATH, enc_path: str = ENCODER_PATH):
        with open(model_path, "rb") as f:
            models = pickle.load(f)
            self.model_runs, self.model_sr = models["runs"], models["sr"]
            if "wickets" in models:
                self.model_wickets, self.model_econ = models["wickets"], models["econ"]
        with open(enc_path, "rb") as f:
            encs = pickle.load(f)
            if "bat" in encs:
                self.bat_encoders, self.bowl_encoders = encs["bat"], encs["bowl"]
            else:
                self.bat_encoders = encs # backward compat
        self.trained = True

@st.cache_resource
def get_trained_player_model(matches: pd.DataFrame, deliveries: pd.DataFrame) -> PlayerPerformanceModel:
    m = PlayerPerformanceModel()
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        try:
            m.load()
            # If loaded model doesn't have bowling model trained, force retrain
            if not hasattr(m, 'model_wickets') or not hasattr(m.model_wickets, 'estimators_'):
                raise ValueError("Old model format")
            return m
        except Exception:
            pass
    m.train(matches, deliveries)
    try:
        m.save()
    except Exception:
        pass
    return m
