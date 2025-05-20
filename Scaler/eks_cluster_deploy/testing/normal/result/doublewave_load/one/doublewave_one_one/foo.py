import pandas as pd

df = pd.read_csv("doublewave_one_one_stats_history.csv")
print(df.columns)
print(df["Name"])
