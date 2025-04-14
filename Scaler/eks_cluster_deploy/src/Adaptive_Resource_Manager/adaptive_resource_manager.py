from collections import namedtuple
import math
from data_format import ResourceData
from data_format import UnderprovisionedData
from data_format import OverprovisionedData
from data_format import ARMDecision


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

    # list of ms that need to "scale up" over limit
    underprovisioned_ms = []
    # list of ms need to "scale down"
    overprovisioned_ms = []

    for microservice in microservice_data:
        # underprovisioned, need to scale up over user-defined limit
        if microservice.desired_for_scale_reps > microservice.max_reps:
            required_reps = microservice.desired_for_scale_reps - \
                            microservice.max_reps
            required_cpu = required_reps * microservice.cpu_request_per_rep
            underprovisioned_ms.append(UnderprovisionedData(
                    microservice.microservice_name,
                    microservice.desired_for_scale_reps,
                    int(required_reps),
                    int(required_cpu),
                    microservice.cpu_request_per_rep,
                    microservice.current_reps,
                    microservice.max_reps
                    ))

        # overprovisioned, need to scale down (auto accept)
        # and/or those who need to scale up within limit. (auto accept)
        # and/or "no scale" (auto accept)
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


def distribute_residual_cpu(underprovisioned_ms,
                            overprovisioned_ms):
    # calculate total residual cpu in the system
    total_residual_cpu = 0
    for microservice in overprovisioned_ms:
        total_residual_cpu += microservice.residual_cpu

    arm_underprovisioned_decision = []

    # sort underprovisioned microservice based on cpu need
    # prioritize those who need most
    underprovisioned_ms = sorted(underprovisioned_ms,
                                 key=lambda x: x.required_cpu,
                                 reverse=True)
    # distribute residual resources to underprovisioned ms
    for microservice in underprovisioned_ms:

        # how many reps for this microservice can be created
        # depend on the current residual cpu
        possible_reps = total_residual_cpu / microservice.cpu_request_per_rep

        # can provide full required resource
        if possible_reps >= microservice.required_reps:
            allowed_scaling_action = "scale up"

            # allow this microservice to scale to its desired_for_scale_reps
            # with new max rep replaced user-defined max_reps
            feasible_reps = microservice.desired_for_scale_reps
            arm_max_reps = microservice.desired_for_scale_reps

            arm_underprovisioned_decision.append(ARMDecision(
                microservice.microservice_name,
                allowed_scaling_action,
                feasible_reps,
                arm_max_reps,
                microservice.cpu_request_per_rep
            ))

            # update current residual cpu
            distributed_cpu = (microservice.required_reps *
                               microservice.cpu_request_per_rep)
            total_residual_cpu -= distributed_cpu

        # can partly provide more required resources (not full)
        elif possible_reps >= 1 and possible_reps < microservice.required_reps:
            allowed_scaling_action = "scale up"
            # scale as much as possible based on current residual
            feasible_reps = (math.floor(possible_reps) +
                             microservice.max_reps)
            # new max reps replace user-defined max_reps
            arm_max_reps = feasible_reps
            arm_underprovisioned_decision.append(ARMDecision(
                microservice.microservice_name,
                allowed_scaling_action,
                feasible_reps,
                arm_max_reps,
                microservice.cpu_request_per_rep
            ))

            # update total residual cpu
            distributed_cpu = (math.floor(possible_reps) *
                               microservice.cpu_request_per_rep)
            total_residual_cpu -= distributed_cpu

        # cannot provide any more replica for this microservice
        else:
            # although there is no cpu residual to scale over
            # current max_reps, but can scale = max_reps
            if microservice.current_reps < microservice.max_reps:
                allowed_scaling_action = "scale up"
                possible_reps = microservice.max_reps
                feasible_reps = arm_max_reps = possible_reps

            # using full allocated resource, need to scale more
            # but no residual cpu left

            #TODO: 
            # MM dies, current rep > max rep
            # current rep, max rep kept
            # trigger resource exchange every round
            # leak any residual resource
            else:
                allowed_scaling_action = "no scale"
                possible_reps = microservice.current_reps
                feasible_reps = arm_max_reps = possible_reps
            arm_underprovisioned_decision.append(ARMDecision(
                microservice.microservice_name,
                allowed_scaling_action,
                feasible_reps,
                arm_max_reps,
                microservice.cpu_request_per_rep
            ))
    return arm_underprovisioned_decision, total_residual_cpu


def back_distribute_residual_cpu(overprovisioned_ms, total_residual_cpu):
    arm_overprovisioned_decision = []

    # distribute cpu resource back based on residual cpu
    # prioritize less residual cpu
    overprovisioned_ms = sorted(overprovisioned_ms,
                                key=lambda x: x.residual_cpu,
                                reverse=False)

    for microservice in overprovisioned_ms:
        # how many reps can be created from
        # the current residual cpu for this microservice
        remaining_reps = math.floor(
            total_residual_cpu / microservice.cpu_request_per_rep
        )
        # number of reps after down scaling + back distribute
        possible_reps = microservice.desired_for_scale_reps + remaining_reps

        # arm_max_reps = new arm_max_reps for the microservice,
        # allowed by Adaptive Resource Manager

        # enough cpu to maintain current capacity
        if possible_reps >= microservice.max_reps:
            # current ms need to down scale,
            # don't need to distribute back more
            # than current capacity
            arm_max_reps = microservice.max_reps
        # cannot maintain current capacity,
        # give back whatever is left
        elif (remaining_reps >= 1 and
              possible_reps < microservice.max_reps):  #TODO: original Smart HPA mistake?
            arm_max_reps = possible_reps

        # nothing to give back,
        # all residual cpu has been taken,
        # the microservice only has enough cpu to function
        # and maintain target cpu utilization
        else:
            arm_max_reps = microservice.desired_for_scale_reps

        # update total residual cpu
        distributed_cpu = ((arm_max_reps - microservice.desired_for_scale_reps) *
                           microservice.cpu_request_per_rep)
        total_residual_cpu -= distributed_cpu
        arm_overprovisioned_decision.append(ARMDecision(
            microservice.microservice_name,
            # free to scale: "scale down", "no scale"
            # or "scale up" within limit
            microservice.scaling_action,  # auto accept
            microservice.desired_for_scale_reps,  # auto accept
            arm_max_reps,  # how much has been given back to this ms
            microservice.cpu_request_per_rep
        ))
    return arm_overprovisioned_decision
