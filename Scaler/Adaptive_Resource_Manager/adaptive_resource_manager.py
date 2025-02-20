from collections import namedtuple


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
    # all no scale ms has been removed from microservice_data
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
            residual





# entry point
if __name__ == "__main__":
    print("")
