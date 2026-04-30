import pandas as pd

def test_loader():
    df = pd.read_csv("data/archive/IPL.csv", low_memory=False, nrows=5000)
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
    
    matches = df.groupby("match_id").first().reset_index()
    matches = matches.rename(columns={
        "match_id": "id",
        "match_won_by": "winner",
    })
    matches["team1"] = matches["batting_team"]
    matches["team2"] = matches["bowling_team"]
    
    # print columns
    print("Deliveries shape:", deliveries.shape)
    print("Matches shape:", matches.shape)
    print("Matches sample team1:", matches["team1"].head(2).tolist())
    print("Matches winner:", matches["winner"].head(2).tolist())
    
test_loader()
