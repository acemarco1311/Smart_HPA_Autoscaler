import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("doublewave_one_one_stats_history.csv")
# get aggregated data only
df = df[df["Name"] == "Aggregated"].copy()

# convert timestamp (Unix time) to experiment time: 0 - 600s
start_timestamp = df["Timestamp"].iloc[0]
df["elapsed_seconds"] = df["Timestamp"] - start_timestamp

# Extract total number of user during test time 600s
plt.plot(df["elapsed_seconds"], df["User Count"])
plt.savefig("user_graph.png")
# Extract total number of request per second during test time 600s
plt.plot(df["elapsed_seconds"], df["Requests/s"])
plt.savefig("request_graph.png")
