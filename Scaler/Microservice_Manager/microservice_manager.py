import math
import argparse
from subroutine import validate_argument
from subroutine import get_available_reps
from subroutine import get_cpu_usage
from subroutine import get_desired_reps
from subroutine import get_cpu_request
from data_format import ResourceData





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

class MicroserviceManager:

    '''
        Microservice Manager class definition
    '''
    # constructor
    def __init__(self, microservice_name, min_reps, max_reps,
                 target_cpu_utilization, current_arm_max_reps):

        # validate type and value
        validate_argument(max_reps,
                          min_reps,
                          target_cpu_utilization,
                          current_arm_max_reps)

        self.microservice_name = microservice_name
        self.min_reps = min_reps  # user-defined
        self.max_reps = max_reps  # user-defined
        self.target_cpu_utilization = target_cpu_utilization  # user-defined
        # ARM defined, replace user-defined max_reps
        self._current_arm_max_reps = current_arm_max_reps

    def get_current_arm_max_reps(self):
        return self._current_arm_max_reps

    def _set_current_arm_max_reps(self, new_arm_max_reps):
        # check input
        try:
            if (new_arm_max_reps >= self.min_reps):
                self._current_arm_max_reps = new_arm_max_reps
        except Exception as err:
            print("Error occurred in setting arm max_reps")
            print(err)

    def get_max_reps(self):
        if self._current_arm_max_reps is not None:
            return self.max_reps
        else:
            return self._current_arm_max_reps


    '''
        Microservice Manager functionality
    '''
    def _Monitor(microservice_name):
        current_reps = get_available_reps(microservice_name)
        cpu_usage_per_rep = get_cpu_usage(microservice_name, current_reps)
        desired_reps = get_desired_reps(microservice_name)
        cpu_request_per_rep = get_cpu_request(microservice_name)

        return (current_reps,
                desired_reps,
                cpu_usage_per_rep,
                cpu_request_per_rep)

    def _Analyze(desired_reps,
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

    def Extract(self):
        monitor_data = self._Monitor()
        analyze_data = self._Analyze()
        return ResourceData(
                self.microservice_name,
                monitor_data[0],
                monitor_data[1],
                monitor_data[2],
                monitor_data[3],
                analyze_data[0],
                analyze_data[1],
                analyze_data[2],
                self.get_max_reps(),
                self.min_reps,
                self.target_cpu_utilization
                )


# entry point
if __name__ == "__main__":
    # only run this when the script is run directly

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
