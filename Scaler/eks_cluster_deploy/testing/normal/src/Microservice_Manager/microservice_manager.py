import time
import math
import os
import json
import threading
from subroutine import validate_argument
from subroutine import get_available_reps
from subroutine import get_cpu_usage
from subroutine import get_desired_reps
from subroutine import get_cpu_request
from subroutine import scale
from subroutine import update_leader_label
from data_format import ResourceData
from data_format import ARMDecision





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
        microservice_name - str
        min_reps - Int
        max_reps - Int
        target_cpu_utilization - Int
        current_arm_max_reps - Int/None
        current_arm_max_reps_lock - threading.Lock
    '''



    '''
        Microservice Manager constructor

        Input: 
            microservice_name - str
            min_reps - Int
            max_reps - Int
            target_cpu_utilization - Int

    '''
    # constructor
    def __init__(self, microservice_name, min_reps, max_reps,
                 target_cpu_utilization):

        # validate type and value
        validate_argument(max_reps,
                          min_reps,
                          target_cpu_utilization,
                          )

        self.microservice_name = microservice_name
        self.min_reps = min_reps  # user-defined
        self.max_reps = max_reps  # user-defined
        self.target_cpu_utilization = target_cpu_utilization  # user-defined
        self._current_arm_max_reps = None
        self.path = f"/microservice_manager/state/{microservice_name}.txt"

    '''
        Get current arm max reps.
        Input: None

        Output:
            current_arm_max_reps - Int
            None if haven't exchange resource
    '''
    def get_current_arm_max_reps(self):
        return self._current_arm_max_reps


    def promote_to_leader(self):
        pod_ip = os.environ.get("POD")
        result = update_leader_label(pod_ip)
        return result



    '''
        Set current arm_max_reps

        Input:
            new_arm_max_reps - Int

        Output: None
    '''
    def _set_current_arm_max_reps(self, new_arm_max_reps):
        # check input
        try:
            if (new_arm_max_reps >= self.min_reps):
                self._current_arm_max_reps = new_arm_max_reps
        except Exception as err:
            print("Error occurred in setting arm max_reps")
            print(err)

    def get_max_reps(self):
        # no resource exchange for this ms before
        if self._current_arm_max_reps is None:
            return self.max_reps
        else:
            return self._current_arm_max_reps

    '''
        Microservice Manager functionality
    '''

    '''
        Extract the resource metrics of the
        microservice.

        Input:

        Output:
            current_reps - Int:
                available reps, running and pass
                probe at least some specified time.
            desired_reps - Int
                reps that deployment will maintain,
                specified in deployment config
            cpu_usage_per_rep - Int
            cpu_request_per_rep - Int

            OR:

            None if there is error in calling kube API
    '''
    def _Monitor(self):
        print("Start collecting metrics")
        current_reps = get_available_reps(self.microservice_name)
        desired_reps = get_desired_reps(self.microservice_name)
        if current_reps is None:
            return None

        # microservice being scaled
        if current_reps != desired_reps:
            # use desired reps stored by ms deployment
            # to eliminate K8s scaling delay
            current_reps = desired_reps

        cpu_usage_per_rep = get_cpu_usage(self.microservice_name, current_reps)
        cpu_request_per_rep = get_cpu_request(self.microservice_name)
        print("Complete collecting metrics")

        result = (current_reps,
                  desired_reps,
                  cpu_usage_per_rep,
                  cpu_request_per_rep)
        valid_result = True
        for i in result:
            if i is None:
                valid_result = False
                break
        if valid_result:
            return result
        return None


    '''
        Analyze the resource metrics to make scaling
        decisions.

        Input:
            current_reps - Int
            desired_reps - Int
            cpu_usage_per_rep - Int
            cpu_request_per_rep - Int

        Output:
            cpu_utilization_per_rep - Int
            desired_for_scale_reps - Int
            scaling_action- str
    '''
    def _Analyze(self, current_reps,
                 desired_reps,
                 cpu_usage_per_rep,
                 cpu_request_per_rep):

        print("Start analyzing metrics")
        cpu_utilization_per_rep = (cpu_usage_per_rep / cpu_request_per_rep) * 100
        # the new desired_reps to scale
        # in order to maintain the required cpu utilization
        desired_for_scale_reps = math.ceil(
                current_reps *
                (cpu_utilization_per_rep / self.target_cpu_utilization)
                )
        scaling_action = ""
        if (desired_reps != desired_for_scale_reps) and \
           (desired_for_scale_reps > current_reps) and  \
           (desired_for_scale_reps >= self.min_reps):

            scaling_action = "scale up"
        elif (desired_reps != desired_for_scale_reps) and \
             (desired_for_scale_reps < current_reps) and \
             (desired_reps >= self.min_reps):
            scaling_action = "scale down"
        else:
            scaling_action = "no scale"
        print("Complete analyzing metrics")
        return (
                int(cpu_utilization_per_rep),
                int(desired_for_scale_reps),
                scaling_action
                )

    '''
        Extract the resource metrics and scaling
        action from the microservice.

        Input: None

        Output:
            resource_data - ResourceData
            
            or

            None if there is any error
    '''

    def Extract(self):
        monitor_data = self._Monitor()
        # some pod are not available yet
        if monitor_data is None:
            return None

        analyze_data = self._Analyze(monitor_data[0],
                                     monitor_data[1],
                                     monitor_data[2],
                                     monitor_data[3])
        resource_data = ResourceData(
                microservice_name=self.microservice_name,
                current_reps=monitor_data[0],
                desired_reps=monitor_data[1],
                cpu_usage_per_rep=monitor_data[2],
                cpu_request_per_rep=monitor_data[3],
                cpu_utilization_per_rep=analyze_data[0],
                desired_for_scale_reps=analyze_data[1],
                scaling_action=analyze_data[2],
                max_reps=self.get_max_reps(),
                min_reps=self.min_reps,
                target_cpu_utilization=self.target_cpu_utilization
        )
        return resource_data

    def Execute(self, arm_decision):
        if arm_decision.microservice_name != self.microservice_name:
            raise TypeError("Wrong destination for scaling instruction.")

        # scale microservice
        scaling_result = scale(self.microservice_name,
                               arm_decision.feasible_reps,
                               self.min_reps)

        # change max_R to update_max_R by ARM if success
        if scaling_result is not None:
            print("Scaled to " + str(arm_decision.feasible_reps) + "/" + str(arm_decision.arm_max_reps))
            self._set_current_arm_max_reps(arm_decision.arm_max_reps)
        return scaling_result

    def sync_max_reps(self):
        return

