import math
from subroutine import validate_argument
from subroutine import get_available_reps
from subroutine import get_cpu_usage
from subroutine import get_desired_reps
from subroutine import get_cpu_request
import argparse
from collections import namedtuple


'''
    Microservice Managers:
        retrieve resource information from the specified microservice

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


def Monitor(microservice_name):
    current_reps = get_available_reps(microservice_name)
    cpu_usage_per_rep = get_cpu_usage(microservice_name, current_reps)
    desired_reps = get_desired_reps(microservice_name)
    cpu_request_per_rep = get_cpu_request(microservice_name)
    return desired_reps, current_reps, cpu_usage_per_rep, cpu_request_per_rep


def Analyze(desired_reps,
            current_reps,
            cpu_usage_per_rep,
            cpu_request_per_rep,
            target_cpu_utilization,
            min_reps,
            max_reps):
    cpu_utilization_per_rep = (cpu_usage_per_rep / cpu_request_per_rep) * 100
    # the new desired_reps to scale
    # in order to maintain the required cpu utilization
    desired_for_scale_reps = math.ceil(
            current_reps *
            (cpu_utilization_per_rep / target_cpu_utilization)
            )
    scaling_action = ""
    if (desired_reps != desired_for_scale_reps) and \
       (desired_for_scale_reps > current_reps) and  \
       (desired_for_scale_reps >= min_reps):

        scaling_action = "scale up"
    elif (desired_reps != desired_for_scale_reps) and \
         (desired_for_scale_reps < current_reps) and \
         (desired_reps >= min_reps):
        scaling_action = "scale down"
    else:
        scaling_action = "no scale"
    return cpu_utilization_per_rep, desired_for_scale_reps, scaling_action


def test_func():
    # declare ResourceData object
    ResourceData = namedtuple("ResourceData", [
        "microservice_name",
        "current_reps",
        "desired_reps",  # num reps before scaling decision
        "cpu_usage_per_rep",
        "cpu_request_per_rep",
        "cpu_utilization_per_rep",
        "desired_for_scale_reps"  # num reps needs to be scaled
        ])
    data = ResourceData("test", 0, 0, 0, 0, 0, 230)
    # after return, data can be used directly as ResourceData
    return data


# entry point
if __name__ == "__main__":
    # only run this when the script is run directly

    data = test_func()
    print(type(data.desired_reps))

    # take user arguments from SLA
    # parse user input into specified type to avoid TypeError
    #parser = argparse.ArgumentParser()
    #parser.add_argument("--microservice_name", type=str)
    #parser.add_argument("--max_reps", type=int)
    #parser.add_argument("--min_reps", type=int)
    #parser.add_argument("--target_cpu_utilization", type=float)
    #args = parser.parse_args()

    ## validate arguments
    #validate_argument(args.max_reps,
    #                  args.min_reps,
    #                  args.target_cpu_utilization)

    ## assign for constants
    #MICROSERVICE_NAME = args.microservice_name
    #MAX_REPS = args.max_reps
    #MIN_REPS = args.min_reps
    #TARGET_CPU_UTILIZATION = args.target_cpu_utilization

    ## test argument
    #print(MICROSERVICE_NAME, MAX_REPS, MIN_REPS, TARGET_CPU_UTILIZATION)
    #print(type(MICROSERVICE_NAME))
    #print(type(MAX_REPS))
    #print(type(MIN_REPS))
    #print(type(TARGET_CPU_UTILIZATION))
