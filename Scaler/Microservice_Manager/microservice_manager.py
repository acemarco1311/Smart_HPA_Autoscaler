import argparse

'''
    Microservice Managers: retrieve resource information from the specified microservice.

    Input:
        microservice_name - String:
            the microservice name to track
        max_reps - Int:
            the maximum replicas defined by user for the microservice
        min_reps - Int:
            the minimum replicas defined by user for the microservice
        target_cpu_utilization- Int:
            the target CPU utilization to trigger resource exchange

    Output:
        microservice_name - String
        desired_reps - Int:
            needed scaled replicas.
        current_reps - Int
        current_cpu_utilization - Int:
            the average CPU utilization of current_reps
        target_cpu_utilization - Int
        max_reps - Int
        min_reps - Int

'''


def validate_argument(max_reps, min_reps, target_cpu_utilization):
    if (max_reps <= 0 or min_reps <= 0):
        raise ValueError("Invalid number of replicas.")
    if (max_reps < min_reps):
        raise ValueError("Invalid number of replicas.")
    if (target_cpu_utilization <= 0 or target_cpu_utilization > 100):
        raise ValueError("Invalid target CPU utilization.")

# entry point
if __name__ == "__main__":
    # only run this when the script is run directly

    # take user arguments from SLA
    parser = argparse.ArgumentParser()
    parser.add_argument("--microservice_name", type=str)
    parser.add_argument("--max_reps", type=int)
    parser.add_argument("--min_reps", type=int)
    parser.add_argument("--target_cpu_utilization", type=float)
    args = parser.parse_args()

    # validate arguments
    validate_argument(args.max_reps, args.min_reps, args.target_cpu_utilization)

    # assign for constants
    MICROSERVICE_NAME = args.microservice_name
    MAX_REPS = args.max_reps
    MIN_REPS = args.min_reps
    TARGET_CPU_UTILIZATION = args.target_cpu_utilization

    # test argument
    print(MICROSERVICE_NAME, MAX_REPS, MIN_REPS, TARGET_CPU_UTILIZATION)
