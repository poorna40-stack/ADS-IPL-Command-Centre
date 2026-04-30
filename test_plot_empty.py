import pandas as pd
from src.visualization import plot_top_batsmen
df = pd.DataFrame(columns=['batter', 'total_runs', 'balls_faced', 'fours', 'sixes', 'innings', 'strike_rate', 'avg_per_innings'])
try:
    fig = plot_top_batsmen(df, n=15)
    print("plot_top_batsmen successful on empty DF")
except Exception as e:
    print("plot_top_batsmen ERROR:", type(e), e)
