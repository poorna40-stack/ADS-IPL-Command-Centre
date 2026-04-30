import pandas as pd
df = pd.DataFrame(columns=["bowler", "dismissal_kind", "runs_off_bat"])
credited = ["caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket"]
wicket_df = df[df["dismissal_kind"].isin(credited)]
print("Wicket columns:", wicket_df.columns)
wickets = wicket_df.groupby("bowler").size().reset_index(name="wickets")
print("Wickets columns:", wickets.columns)
balls = df.groupby("bowler").size().reset_index(name="balls")
print("Balls columns:", balls.columns)
runs_given = df.groupby("bowler")["runs_off_bat"].sum().reset_index()
print("Runs given columns:", runs_given.columns)
grp = wickets.merge(balls, on="bowler").merge(runs_given, on="bowler")
print("Grp columns:", grp.columns)
