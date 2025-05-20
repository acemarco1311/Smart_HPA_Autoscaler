import pandas as pd
import matplotlib.pyplot as plt
import os


# list all result dirs
dir_list = [name for name in os.listdir() if os.path.isdir(name)]
print(dir_list)

for dir in dir_list:
    df = pd.read_csv(f"{dir}/{dir}_stats_history.csv")
    if os.path.isdir(f"{dir}/graph"):
        continue
    os.makedirs(f"{dir}/graph")

    # get aggregated data only
    df = df[df["Name"] == "Aggregated"].copy()

    # convert timestamp (Unix time) to experiment time: 0 - 600s
    start_timestamp = df["Timestamp"].iloc[0]
    df["elapsed_seconds"] = df["Timestamp"] - start_timestamp

    # Extract total number of user during test time 600s
    plt.figure(figsize=(10, 5))
    plt.plot(df["elapsed_seconds"], df["User Count"])
    plt.xlabel("Time (seconds since load test starts)")
    plt.ylabel("Total number of concurrent user")
    plt.title("Concurrent user during normal load test.")
    plt.xlim(right=600)
    plt.savefig(f"{dir}/graph/user_graph.png")



    # Extract total number of request per second during test time 600s
    plt.figure(figsize=(10, 5))
    plt.plot(df["elapsed_seconds"], df["Requests/s"])
    plt.xlabel("Time (seconds since load test starts)")
    plt.ylabel("Total number of concurrent user")
    plt.title("Total number of request per second during normal load test.")
    plt.xlim(right=600)
    plt.savefig(f"{dir}/graph/request_graph.png")
