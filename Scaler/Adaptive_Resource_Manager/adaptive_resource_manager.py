from collections import namedtuple


'''
    Classifying microservices into underprovisioned and
    overprovisioned microservices to prepare for resource
    exchange.

    Input:
        microservice_data - List<ResourceData>:
            contain resource data of all microservices whose scaling
            action is either "scale up" (underprovisioned) or
            "scale down" (overprovisioned)

    ResourceData:
        microservice_name - str
        current_reps - int
        desired_reps - int
        cpu_usage_per_rep - int
        cpu_request_per_rep - int
        cpu_utilization_per_rep - int
        desired_for_scale_reps - int
        scaling_action - str
        max_reps - Int
        min_reps - Int
        target_cpu_utilization - Int

    Output:
        underprovisioned_ms - List<UnderprovisionedData>
        overprovisioned_ms - List<OverprovisionedData>

'''


def classify_ms(microservice_data):
    # required data format for adaptive resource manager
    UnderprovisionedData = namedtuple("UnderprovisionedData", [
        "microservice_name",
        "required_reps",  # new data
        "required_cpu",  # new data
        "cpu_request_per_rep",
        "current_reps",
        "max_reps",
    ])
    OverprovisionedData = namedtuple("OverprovisionedData", [
        "microservice_name",
        "residual_cpu",  # new data
        "scaling_action",
        "desired_for_scale_reps",
        "current_reps",
        "cpu_request_per_rep",
        "max_reps"
    ])
    underprovisioned_ms = []
    overprovisioned_ms = []
    # all "no scale" ms has been removed from microservice_data
    for microservice in microservice_data:
        # underprovisioned, need to scale up over user-defined limit
        if microservice.desired_for_scale_reps > microservice.max_reps:
            required_reps = microservice.desired_for_scale_reps - \
                            microservice.max_reps
            required_cpu = required_reps * microservice.cpu_request_per_rep
            underprovisioned_ms.append(UnderprovisionedData(
                    microservice.microservice_name,
                    int(required_reps),
                    int(required_cpu),
                    microservice.cpu_request_per_rep,
                    microservice.current_reps,
                    microservice.max_reps
                    ))
        # overprovisioned
        else:
            residual_reps = microservice.max_reps - \
                            microservice.desired_for_scale_reps
            residual_cpu = residual_reps * microservice.cpu_request_per_rep
            overprovisioned_ms.append(OverprovisionedData(
                microservice.microservice_name,
                int(residual_cpu),
                microservice.scaling_action,
                microservice.desired_for_scale_reps,
                microservice.current_reps,
                microservice.cpu_request_per_rep,
                microservice.max_reps
                ))
    return underprovisioned_ms, overprovisioned_ms

# entry point
if __name__ == "__main__":
    print("")
