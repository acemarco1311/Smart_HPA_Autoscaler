from collections import namedtuple


# resource extraction from MS Manager
ResourceData = namedtuple("ResourceData", [
    "microservice_name",
    "current_reps",
    "desired_reps",  # num reps to be maintained before scaling decision
    "cpu_usage_per_rep",
    "cpu_request_per_rep",
    "cpu_utilization_per_rep",
    "desired_for_scale_reps"  # num reps needs to be scaled
    "scaling_action",  # needed scaling action
    "max_reps",
    "min_reps",
    "target_cpu_utilization"
])
