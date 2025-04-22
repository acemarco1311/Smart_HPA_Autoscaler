import json
import copy


#ms_names = ["cartservice",
#            "checkoutservice",
#            "currencyservice",
#            "frontend",
#            "paymentservice",
#            "productcatalogservice",
#            "redis-cart",
#            "shippingservice"]

ms_names = ["cartservice",
            "checkoutservice"]



all_resource_data = {}
for ms in ms_names:
    all_resource_data.update({ms: []})
for ms in ms_names:
    with open(f"kb/{ms}.txt", "r") as file:
        for line in file:
            data_obj = json.loads(line)
            all_resource_data[ms].append(data_obj)

# replace empty obj to previous object but update test time
for i in range(len(ms_names)):
    for j in range(len(all_resource_data[ms_names[i]])):
        # if empty, use the previous obj
        if not all_resource_data[ms_names[i]][j]:
            # copy the previous object
            sub_obj = copy.deepcopy(all_resource_data[ms_names[i]][j-1])
            # update timestamp for previous object
            # from timestamp of another microservice
            # on the same line
            for t in range(len(ms_names)):
                if t == i:
                    continue
                elif all_resource_data[ms_names[t]][j]:
                    sub_obj["test_time"] = all_resource_data[ms_names[t]][j]["test_time"]
                    break
            # replace empty object to new object
            all_resource_data[ms_names[i]][j] = sub_obj

total_supply_cpu_each_rep = []
ms_supply_cpu_each_rep = {}











