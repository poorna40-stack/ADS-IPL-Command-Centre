import pandas as pd

df = pd.read_csv("data/archive/IPL.csv", nrows=1000)

print(df.columns)
print(df[["match_won_by", "win_outcome"]].head())
