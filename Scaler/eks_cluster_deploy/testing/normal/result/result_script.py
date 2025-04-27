import json
import copy
import statistics

ms_names = [
        "cartservice",
        "checkoutservice",
        "currencyservice",
        "frontend",
        "paymentservice",
        "productcatalogservice",
        "redis-cart",
        "shippingservice"
]

# read resource data from Knowledge Base
all_resource_data = {}
for ms in ms_names:
    all_resource_data.update({ms: []})
for ms in ms_names:
    with open(f"one/kb/{ms}.txt", "r") as file:
        for line in file:
            data_obj = json.loads(line)
            all_resource_data[ms].append(data_obj)

# replace empty resource data (cannot get from kube-api-server)
# by previous resource data with updated test_time and max_reps
for i in range(len(ms_names)):
    for j in range(len(all_resource_data[ms_names[i]])):
        # if resource data only contain max_reps and test time
        if len(all_resource_data[ms_names[i]][j]) == 2:
            max_reps = all_resource_data[ms_names[i]][j]["max_reps"]
            test_time = all_resource_data[ms_names[i]][j]["test_time"]
            # get prev object
            prev_obj = copy.deepcopy(all_resource_data[ms_names[i]][j-1])
            prev_obj["max_reps"] = max_reps
            prev_obj["test_time"] = test_time
            # replace empty object by prev object
            all_resource_data[ms_names[i]][j] = prev_obj


# ensure same number of exchage round
exchange_round = []
for ms in ms_names:
    exchange_round.append(len(all_resource_data[ms]))
if len(set(exchange_round)) == 1:
    TOTAL_EXCHANGE_ROUND = exchange_round[0]
else:
    print("Nmuber of exchange round doesn't match among microservices.")

total_supply_cpu_each_rep = []
ms_supply_cpu_each_rep = {}
total_capacity_cpu_each_rep = []
ms_capacity_cpu_each_rep = {}
total_overutilization_cpu_each_rep = []
ms_overutilization_cpu_each_rep = {}
total_residual_cpu_each_rep = []
ms_residual_cpu_each_rep = {}
total_needed_cpu_each_rep = []
ms_needed_cpu_each_rep = {}
total_overutilization_time = 0
total_overprovision_time = 0
total_underprovision_time = 0

# init array for ms (per round)
for ms in ms_names:
    ms_supply_cpu_each_rep.update({ms: []})
    ms_capacity_cpu_each_rep.update({ms: []})
    ms_overutilization_cpu_each_rep.update({ms: []})
    ms_residual_cpu_each_rep.update({ms: []})
    ms_needed_cpu_each_rep.update({ms: []})

# check each round
prev_timestamp = float(all_resource_data[ms_names[0]][0]["test_time"])
for i in range(TOTAL_EXCHANGE_ROUND):
    total_supply_cpu_this_round = 0
    total_capacity_cpu_this_round = 0
    total_overutilization_cpu_this_round = 0
    total_residual_cpu_this_round = 0
    total_needed_cpu_this_round = 0
    has_overutilization = False # duration in which at least 1 microservice go beyond target utilization
    no_insufficient_cpu = True # duration in which no ms operates with insufficient cpu
    has_underprovision = False # duration in which at least 1 microservice operate with insufficient cpu
    # check each ms in the round
    for ms in ms_names:
        # extract data
        data = all_resource_data[ms][i]
        current_reps = data["current_reps"]
        cpu_request_per_rep = data["cpu_request_per_rep"]
        max_reps = data["max_reps"]
        cpu_utilization_per_rep = data["cpu_utilization_per_rep"]
        target_cpu_utilization = data["target_cpu_utilization"]
        desired_for_scale_reps = data["desired_for_scale_reps"]
        desired_reps = data["desired_reps"]

        # calculate metrics
        # use desired rep as current rep to eliminate
        # k8s scaling delay
        supply_cpu = desired_reps * cpu_request_per_rep
        capacity_cpu = max_reps * cpu_request_per_rep
        residual_cpu = capacity_cpu - supply_cpu
        needed_cpu = 0
        # ignore the scaling delay by k8s
        # current reps not updated but desired_rep updated
        # use desired_rep as current rep
        if desired_for_scale_reps > desired_reps:
            needed_cpu = (desired_for_scale_reps * cpu_request_per_rep) - supply_cpu
            has_underprovision = True
            no_insufficient_cpu = False # found at least 1 ms operates with insufficient cpu

        total_supply_cpu_this_round += supply_cpu
        total_capacity_cpu_this_round += capacity_cpu
        total_residual_cpu_this_round += residual_cpu
        total_needed_cpu_this_round += needed_cpu


        overutilization_cpu = 0
        if cpu_utilization_per_rep > target_cpu_utilization:
            overutilization_cpu = cpu_utilization_per_rep - target_cpu_utilization
            has_overutilization = True



        total_overutilization_cpu_this_round += overutilization_cpu



        # update array for each ms
        ms_supply_cpu_each_rep[ms].append(supply_cpu)
        ms_capacity_cpu_each_rep[ms].append(capacity_cpu)
        ms_overutilization_cpu_each_rep[ms].append(overutilization_cpu)
        ms_residual_cpu_each_rep[ms].append(residual_cpu)
        ms_needed_cpu_each_rep[ms].append(needed_cpu)
    # add overutilization time
    current_timestamp = float(all_resource_data[ms_names[0]][i]["test_time"])
    if i != 0 and has_overutilization:
        total_overutilization_time += (current_timestamp - prev_timestamp)
    if i != 0 and has_underprovision:
        total_underprovision_time += (current_timestamp - prev_timestamp)
    if i != 0 and no_insufficient_cpu:
        total_overprovision_time += (current_timestamp - prev_timestamp)
    # update previous_timestamp
    prev_timestamp = float(all_resource_data[ms_names[0]][i]["test_time"])

    # update total per round
    total_supply_cpu_each_rep.append(total_supply_cpu_this_round)
    total_capacity_cpu_each_rep.append(total_capacity_cpu_this_round)
    total_overutilization_cpu_each_rep.append(total_overutilization_cpu_this_round)
    total_residual_cpu_each_rep.append(total_residual_cpu_this_round)
    total_needed_cpu_each_rep.append(total_needed_cpu_this_round)


avg_supply_cpu_each_round = statistics.mean(total_supply_cpu_each_rep)
avg_capacity_cpu_each_round = statistics.mean(total_capacity_cpu_each_rep)
avg_overutilization_cpu_each_round = statistics.mean(total_overutilization_cpu_each_rep)
avg_residual_cpu_each_round = statistics.mean(total_residual_cpu_each_rep)
avg_needed_cpu_each_round = statistics.mean(total_needed_cpu_each_rep)
print("Average CPU supply for the system each round: ", avg_supply_cpu_each_round)
print("Average CPU capacity for the system each round: ", avg_capacity_cpu_each_round)
print("Average overutilized CPU (percentage) of the whole system each round: ", avg_overutilization_cpu_each_round)
print("Average overprovisioned CPU each rep: ", avg_residual_cpu_each_round)
print("Average underprovisioned CPU each rep: ", avg_needed_cpu_each_round)
print("Total overutilized time (in seconds): ", total_overutilization_time)
print("Total overprovisioned time where all microservices has sufficient CPU: ", total_overprovision_time)
print("Total underprovisioned time where at least 1 microservice has insufficient CPU: ", total_underprovision_time)

