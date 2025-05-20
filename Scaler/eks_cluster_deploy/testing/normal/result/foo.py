import json
import copy
import statistics
import pandas as pd
import matplotlib.pyplot as plt
import os

MS_NAMES = [
    "cartservice",
    "checkoutservice",
    "currencyservice",
    "frontend",
    "paymentservice",
    "productcatalogservice",
    "redis-cart",
    "shippingservice"
]

CAPACITY = 1650


def produce_graph(x_values,
                  y_values,
                  x_title,
                  y_title,
                  dest_path,
                  filename):

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_values, y_values)
    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    fig.savefig(f"{dest_path}/{filename}.png", dpi=150, format="png")
    plt.close(fig)
    return

def produce_system_graph(all_round_system_metrics,
                         overutilization_time,
                         overprovision_time,
                         underprovision_time,
                         dest_path):
    # [{round 1}, {round 2}]
    filenames = ["supply_cpu",
                 "capacity_cpu",
                 "overprovision_cpu",
                 "underprovision_cpu",
                 "overutilization_cpu",
                 "overutilization_percent"]
    y_labels = ["Supply CPU (mCPU)",
                "Capacity CPU (mCPU)",
                "Overprovision CPU (mCPU)",
                "Underprovision CPU (mCPU)",
                "Overutilization CPU (mCPU)",
                "Overutilization CPU (percent over target CPU utilization)"]
    metric_list = []
    metric_list.append([float(round["total_supply_cpu"]) for round in all_round_system_metrics])
    metric_list.append([float(round["total_capacity_cpu"]) for round in all_round_system_metrics])
    metric_list.append([float(round["total_residual_cpu"]) for round in all_round_system_metrics])
    metric_list.append([float(round["total_needed_cpu"]) for round in all_round_system_metrics])
    metric_list.append([float(round["total_overutilization_cpu"]) for round in all_round_system_metrics])
    metric_list.append([float(round["total_overutilization_percent"]) for round in all_round_system_metrics])
    test_time_list = [float(round["test_time"]) for round in all_round_system_metrics]
    
    # numerical evaluation metrics graphs
    for i in range(len(metric_list)):
        produce_graph(test_time_list,
                      metric_list[i],
                      "Test time (seconds)",
                      y_labels[i],
                      dest_path,
                      filenames[i])

    # produce time graph for the system
    produce_graph(test_time_list,
                  overutilization_time,
                  "Test time (seconds)",
                  "Overutilization time (seconds)",
                  dest_path,
                  "overutilization_time")
    produce_graph(test_time_list,
                  overprovision_time,
                  "Test time (seconds)",
                  "Overprovision time (seconds)",
                  dest_path,
                  "overprovision_time")
    produce_graph(test_time_list,
                  underprovision_time,
                  "Test time (seconds)",
                  "Underprovision time (seconds)",
                  dest_path,
                  "underprovision_time")


    pass

def produce_ms_graph(all_round_metrics,
                     dest_path):
    filenames = ["supply_cpu",
                 "capacity_cpu",
                 "overprovision_cpu",
                 "underprovision_cpu",
                 "overutilization_cpu",
                 "overutilization_percent"]
    y_labels = ["Supply CPU (mCPU)",
                "Capacity CPU (mCPU)",
                "Overprovision CPU (mCPU)",
                "Underprovision CPU (mCPU)",
                "Overutilization CPU (mCPU)",
                "Overutilization CPU (percent over target CPU utilization)"]
    # [{ms: round 1}, {ms: round 2}]
    # [{ms: [{round 1}, {round 2}]}]
    for ms in MS_NAMES:
        metric_list = []

        metric_list.append([float(round[ms]["supply_cpu"]) for round in all_round_metrics])
        metric_list.append([float(round[ms]["capacity_cpu"]) for round in all_round_metrics])
        metric_list.append([float(round[ms]["residual_cpu"]) for round in all_round_metrics])
        metric_list.append([float(round[ms]["needed_cpu"]) for round in all_round_metrics])
        metric_list.append([float(round[ms]["overutilization_cpu"]) for round in all_round_metrics])
        metric_list.append([float(round[ms]["overutilization_percent"]) for round in all_round_metrics])
        test_time_list = [float(round[ms]["test_time"]) for round in all_round_metrics]


        #metric_list.append([float(round["supply_cpu"]) for round in all_round_metrics[ms]])
        #metric_list.append([float(round["capacity_cpu"]) for round in all_round_metrics[ms]])
        #metric_list.append([float(round["residual_cpu"]) for round in all_round_metrics[ms]])
        #metric_list.append([float(round["needed_cpu"]) for round in all_round_metrics[ms]])
        #metric_list.append([float(round["overutilization_cpu"]) for round in all_round_metrics[ms]])
        #metric_list.append([float(round["overutilization_percent"]) for round in all_round_metrics[ms]])
        #test_time_list = [float(round["test_time"]) for round in all_round_metrics[ms]]

        for i in range(len(metric_list)):
            produce_graph(test_time_list,
                          metric_list[i],
                          "Test time (seconds)",
                          y_labels[i],
                          f"{dest_path}/{ms}",
                          filenames[i])
    return

def produce_locust_graph(locust_log_path,
                         graph_dest):
    df = pd.read_csv(locust_log_path)
    # get aggregated data only
    df = df[df["Name"]== "Aggregated"].copy()
    # convert timestamp (Unix time) to experiment time:
    # 0 - 600s run time
    start_timestamp = df["Timestamp"].iloc[0]
    df["elapsed_seconds"] = df["Timestamp"] - start_timestamp

    # Extract total number of users during test time
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["elapsed_seconds"], df["User Count"])
    ax.set_xlabel("Time (seconds since load test starts)")
    ax.set_ylabel("Total number of concurrent users.")
    ax.set_xlim(right=600)
    fig.savefig(f"{graph_dest}/user_graph.png", dpi=150, format="png")
    plt.close(fig)

    # Extract total number of request per second
    # during test time 600s
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["elapsed_seconds"], df["Requests/s"])
    ax.set_xlabel("Time (seconds since load test starts)")
    ax.set_xlim(right=600)
    fig.savefig(f"{graph_dest}/request_graph.png", dpi=150, format="png")
    plt.close(fig)



# Load microservices' resource data history
# from Knowledge Base
# Input: string - path to knowledge base folder 
# which contains each microservice in txt storing json object

# Output: {ms: [{round 1 data}, {round 2 data}, ...]}

def load_kb(kb_path):
    # read resource data from KB
    all_resource_data = {}
    for ms in MS_NAMES:
        all_resource_data.update({ms: []})
    for ms in MS_NAMES:
        with open(f"{kb_path}/{ms}.txt", "r") as file:
            for line in file:
                data_obj = json.loads(line)
                all_resource_data[ms].append(data_obj)

    # replace empty resource data (cannot get from kube-api-server)
    # by previous resource data with updated test_time and max_reps
    for i in range(len(MS_NAMES)):
        for j in range(len(all_resource_data[MS_NAMES[i]])):
            # if resource data only contain max_reps and test time
            if len(all_resource_data[MS_NAMES[i]][j]) == 2:
                max_reps = all_resource_data[MS_NAMES[i]][j]["max_reps"]
                test_time = all_resource_data[MS_NAMES[i]][j]["test_time"]
                # get prev object
                prev_obj = copy.deepcopy(all_resource_data[MS_NAMES[i]][j-1])
                prev_obj["max_reps"] = max_reps
                prev_obj["test_time"] = test_time
                # replace empty object by prev object
                all_resource_data[MS_NAMES[i]][j] = prev_obj

    # only get the data < 750 seconds
    for ms in MS_NAMES:
        # list of data in each exchange round for this ms
        original_data = copy.deepcopy(all_resource_data[ms])
        # filter data with test time < 750
        filter_data = [data for data in original_data if data["test_time"] < 750]
        all_resource_data.update({ms: filter_data})

    # ensure same number of exchage round
    exchange_round = []
    for ms in MS_NAMES:
        exchange_round.append(len(all_resource_data[ms]))
    if len(set(exchange_round)) == 1:
        TOTAL_EXCHANGE_ROUND = exchange_round[0]
        return TOTAL_EXCHANGE_ROUND, all_resource_data
    else:
        print("Number of exchange round doesn't match among microservices.")
        return None


# Calculate evalutaion metrics from resource data.
def ms_metrics(current_reps,
               desired_reps,
               max_reps,
               desired_for_scale_reps,
               cpu_request_per_rep,
               cpu_utilization_per_rep,
               target_cpu_utilization,
               test_time):

    # use current reps, MM automatically
    # return desired_reps as current_reps
    # when ms is being scale to eliminate
    # k8s scaling delay
    supply_cpu = current_reps * cpu_request_per_rep
    capacity_cpu = max_reps * cpu_request_per_rep
    residual_cpu = capacity_cpu - supply_cpu
    needed_cpu =0
    if desired_for_scale_reps > current_reps:
        needed_cpu = (desired_for_scale_reps * cpu_request_per_rep) - supply_cpu

    # the cpu (mCPU) which this microservice
    # use beyond target cpu utilization
    overutilization_cpu = 0

    if cpu_utilization_per_rep > target_cpu_utilization:
        # overutilization percentage per rep, for example, 20%
        overutilization_cpu = cpu_utilization_per_rep - target_cpu_utilization
        # convert 20% -> 0.2
        overutilization_cpu /= 100
        # the total cpu beyond cpu threshold per rep
        overutilization_cpu *= cpu_request_per_rep
        # the total cpu beyond cpu threshold in all replicas for this ms
        overutilization_cpu *= current_reps
    
    # the percentage overutilization of this microservice (all reps, not per rep)
    # this for ms graph only, same method for system-wise
    overutilization_percent = overutilization_cpu / supply_cpu
    # convert from int -> %
    overutilization_percent *= 100
    return {
            "supply_cpu": supply_cpu,
            "capacity_cpu": capacity_cpu,
            "residual_cpu": residual_cpu,
            "needed_cpu": needed_cpu,
            "overutilization_cpu": overutilization_cpu,
            "overutilization_percent": overutilization_percent,
            "test_time": test_time
           }

'''
 Calculate evaluation metrics of a specific round
 Input:
 - all_resource_data -> {ms: [{round 1}, {round 2}, ...]}
 - round_index: index of {} for the round
 Output:
     {ms: {this round metric}}
     round metric:
         supply cpu
         capacity cpu
         residual cpu
         needed cpu
         overutilization cpu
         test time
 '''

def round_metrics(all_resource_data, round_index):
    this_round_metrics = {}
    # check each ms in the round
    for ms in MS_NAMES:
        data = all_resource_data[ms][round_index]
        # extract data
        current_reps = data["current_reps"]
        cpu_request_per_rep = data["cpu_request_per_rep"]
        max_reps = data["max_reps"]
        cpu_utilization_per_rep = data["cpu_utilization_per_rep"]
        target_cpu_utilization = data["target_cpu_utilization"]
        desired_for_scale_reps = data["desired_for_scale_reps"]
        desired_reps = data["desired_reps"]
        test_time = data["test_time"]

        resource_metrics = ms_metrics(current_reps,
                                      desired_reps,
                                      max_reps,
                                      desired_for_scale_reps,
                                      cpu_request_per_rep,
                                      cpu_utilization_per_rep,
                                      target_cpu_utilization,
                                      test_time)

        this_round_metrics.update({ms: resource_metrics})
    return this_round_metrics

'''
    Calculate the resource metric of the whole system
    (among all microservices
    in a specific round

    Input: {ms: {this round metric}}

    Output: 
        total supply cpu this round
        total capacity cpu this round
        total needed cpu this round
        total overutilization this round
'''
def system_round_metrics(this_round_metrics):
    total_supply_cpu = 0
    total_capacity_cpu = 0
    total_residual_cpu = 0
    total_needed_cpu = 0
    total_overutilization_cpu = 0

    for ms in MS_NAMES:
        total_supply_cpu += this_round_metrics[ms]["supply_cpu"]
        total_capacity_cpu += this_round_metrics[ms]["capacity_cpu"]
        total_residual_cpu += this_round_metrics[ms]["residual_cpu"]
        total_needed_cpu += this_round_metrics[ms]["needed_cpu"]
        total_overutilization_cpu += this_round_metrics[ms]["overutilization_cpu"]

    # use system wise overutilization percentage
    # not ms percentage because of potential uneven resource allocation
    total_overutilization_percent = total_overutilization_cpu / total_supply_cpu
    total_overutilization_percent *= 100

    return {
            "total_supply_cpu": total_supply_cpu,
            "total_capacity_cpu": total_capacity_cpu,
            "total_residual_cpu": total_residual_cpu,
            "total_needed_cpu": total_needed_cpu,
            "total_overutilization_cpu": total_overutilization_cpu,
            "total_overutilization_percent": total_overutilization_percent,
            # preserve test time
            "test_time": this_round_metrics[ms]["test_time"]
            }

def test_metrics(total_exchange_round, all_resource_data):
    # store metrics of all ms in each round
    all_round_metrics = []
    # store system metrics in each round
    all_round_system_metrics = []
    for round_index in range(total_exchange_round):
        # metrics of all ms in this round
        this_round_metrics = round_metrics(all_resource_data, round_index)
        # system metrics of this round
        this_round_system_metrics = system_round_metrics(this_round_metrics)

        all_round_metrics.append(this_round_metrics)
        all_round_system_metrics.append(this_round_system_metrics)

    return all_round_metrics, all_round_system_metrics

def aggregated_test_metrics(all_round_system_metrics):
    avg_system_supply_cpu_each_round = statistics.mean([item["total_supply_cpu"] for item in all_round_system_metrics])
    avg_system_capacity_cpu_each_round = statistics.mean([item["total_capacity_cpu"] for item in all_round_system_metrics])
    avg_system_residual_cpu_each_round = statistics.mean([item["total_residual_cpu"] for item in all_round_system_metrics])
    avg_system_needed_cpu_each_round = statistics.mean([item["total_needed_cpu"] for item in all_round_system_metrics])
    avg_system_overutilization_cpu_each_round = statistics.mean([item["total_overutilization_cpu"] for item in all_round_system_metrics])
    avg_system_overutilization_percent_each_round = statistics.mean([item["total_overutilization_percent"] for item in all_round_system_metrics])
    return {
            "supply_cpu": avg_system_supply_cpu_each_round,
            "capacity_cpu": avg_system_capacity_cpu_each_round,
            "residual_cpu": avg_system_residual_cpu_each_round,
            "needed_cpu": avg_system_needed_cpu_each_round,
            "overutilization_cpu": avg_system_overutilization_cpu_each_round,
            "overutilization_percent": avg_system_overutilization_percent_each_round
    }

def test_time_metrics(all_round_system_metrics):
    # first round placeholder
    overutilization_time = [0]
    overprovision_time = [0]
    underprovision_time = [0]

    total_overutilization_time = 0
    total_overprovision_time = 0
    total_underprovision_time = 0
    prev_timestamp = float(all_round_system_metrics[0]["test_time"])
    # start from second round
    for round in range(1, len(all_round_system_metrics)):
        current_timestamp = float(all_round_system_metrics[round]["test_time"])
        # has overutilization, add to time
        if all_round_system_metrics[round]["total_overutilization_cpu"] > 0:
            total_overutilization_time += current_timestamp - prev_timestamp
        overutilization_time.append(total_overutilization_time)
        # overprovisioned
        if all_round_system_metrics[round]["total_residual_cpu"] > 0:
            total_overprovision_time += current_timestamp - prev_timestamp
        # underprovisioned
        if all_round_system_metrics[round]["total_needed_cpu"] > 0:
            total_underprovision_time += current_timestamp - prev_timestamp
        overprovision_time.append(total_overprovision_time)
        underprovision_time.append(total_underprovision_time)
        # update prev timestamp
        prev_timestamp = float(all_round_system_metrics[round]["test_time"])
    return overutilization_time, overprovision_time, underprovision_time


# main function
if __name__=="__main__":
    experiment_path = input() # default_load/one

    # list all five experiment directories
    # no any other directories
    dir_list = [name for name in os.listdir(experiment_path)]
    experiment_dir_list = [dir for dir in dir_list if dir != "graph"]
    print(experiment_dir_list)

    experiment_metric_list = []
    for experiment in experiment_dir_list:

        os.makedirs(f"{experiment_path}/{experiment}/graph")
        os.makedirs(f"{experiment_path}/{experiment}/graph/locust")
        os.makedirs(f"{experiment_path}/{experiment}/graph/ms")
        for ms in MS_NAMES:
            os.makedirs(f"{experiment_path}/{experiment}/graph/ms/{ms}")
        os.makedirs(f"{experiment_path}/{experiment}/graph/system")


        experiment_graph_path = f"{experiment_path}/{experiment}/graph"
        # create locust user graph and request graph
        # default/one/one_one/one_one_stats_history.csv
        #TODO: produce locust graphs
        locust_graph_path = f"{experiment_graph_path}/locust"
        locust_log_path = f"{experiment_path}/{experiment}/{experiment}_stats_history.csv"
        print(locust_log_path)
        produce_locust_graph(locust_log_path,
                             locust_graph_path)

        # knowledge base path
        kb_path = f"{experiment_path}/{experiment}/kb"
        
        # load historical data
        total_exchange_round, all_resource_data = load_kb(kb_path)
        all_round_metrics, all_round_system_metrics = test_metrics(total_exchange_round, all_resource_data)

        # produce numerical evaluation metrics for each ms
        produce_ms_graph(all_round_metrics,
                         f"{experiment_graph_path}/ms")



        metrics = aggregated_test_metrics(all_round_system_metrics)

        # calculate time metrics for this test
        overutilization_time, overprovision_time, underprovision_time = test_time_metrics(all_round_system_metrics)
        # add time metrics to evaluation metrics
        metrics.update({"overutilization_time": overutilization_time[-1]})
        metrics.update({"overprovision_time": overprovision_time[-1]})
        metrics.update({"underprovision_time": underprovision_time[-1]})
        print(metrics)


        # save evaluation metrics for this test
        with open(f"{experiment_path}/{experiment}/aggregated_result.txt", "w") as file:
            json.dump(metrics, file)


        #experiment_metric_list.append(metrics)
        # produce evaluation metrics graphs for the system
        # both numerical and time graphs
        produce_system_graph(
                all_round_system_metrics,
                overutilization_time,
                overprovision_time,
                underprovision_time,
                f"{experiment_graph_path}/system"
        )
