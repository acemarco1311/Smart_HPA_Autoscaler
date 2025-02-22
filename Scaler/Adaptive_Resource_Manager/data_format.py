from collections import namedtuple

ResourceData = namedtuple("ResourceData", [
    "microservice_name",
    "current_reps",
    "desired_reps",  # num reps to be maintained before scaling decision
    "cpu_usage_per_rep",
    "cpu_request_per_rep",
    "cpu_utilization_per_rep",
    "desired_for_scale_reps"  # num reps needs to be scaled
])

UnderprovisionedData = namedtuple("UnderprovisionedData", [
    "microservice_name",
    "desired_for_scale_reps"
    "required_reps",  # new data
    "required_cpu",  # new data
    "cpu_request_per_rep",
    "current_reps",
    "max_reps"  # current max reps restrictions (user/ARM)
])

OverprovisionedData = namedtuple("OverprovisionedData", [
    "microservice_name",
    "residual_cpu",  # new data
    "scaling_action",
    "desired_for_scale_reps",
    "current_reps",
    "cpu_request_per_rep",
    "max_reps"  # current max reps restrictions (user/ARM)
])

# scaling instruction for each microservice
ARMDecision = namedtuple("ARMDecision", [
    "microservice_name",

    "allowed_scaling_action",  # scaling action allowed by ARM

    # number of reps that ARM allows this ms to scale up to
    "feasible_reps",

    "arm_max_reps",  # microservice max rep restrictions,
                     # replace user-defined max_reps
                     # kept track by ARM

    "cpu_request_per_rep"
])
