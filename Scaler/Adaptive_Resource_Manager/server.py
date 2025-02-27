from adaptive_resource_manager import classify_ms
from adaptive_resource_manager import distribute_residual_cpu
from adaptive_resource_manager import back_distribute_residual_cpu

import adaptive_resource_manager_pb2
import adaptive_resource_manager_pb2_grpc

from data_format import ResourceData
from data_format import ARMDecision


class ARMImpl(adaptive_resource_manager_pb2_grpc.AdaptiveResourceManagerServicer):
    def ResourceExchange(self, request, context):
        # convert request to ResourceData
        microservices_data = []
        # loop through ResourceData in ResourceDataList
        for data in request.microservices_data:
            microservices_data.append(
                ResourceData(
                    data.microservice_data,
                    data.current_reps,
                    data.desired_reps,
                    data.cpu_usage_per_rep,
                    data.cpu_request_per_rep,
                    data.cpu_utilization_per_rep,
                    data.desired_for_scale_reps,
                    data.scaling_action,
                    data.max_reps,
                    data.min_reps,
                    data.target_cpu_utilization
                )
            )

        # classify microservice data
        underprovisioned_ms, overprovisioned_ms = classify_ms(microservices_data)
        # distribute residual cpu
        arm_underprovisioned_decision, total_residual_cpu = distribute_residual_cpu(underprovisioned_ms, overprovisioned_ms)
        # pay back final residual cpu
        arm_overprovisioned_decision = back_distribute_residual_cpu(overprovisioned_ms, total_residual_cpu)

        final_decision = arm_underprovisioned_decision + arm_overprovisioned_decision

        # build response message
        res = adaptive_resource_manager_pb2.ARMDecisionList()
        for decision in final_decision:
            res.scaling_instructions.append(
                adaptive_resource_manager_pb2.ARMDecision(
                    microservice_name = decision.microservice_name,
                    allowed_scaling_action = decision.allowed_scaling_action,
                    feasible_reps = decision.feasible_reps,
                    arm_max_reps = decision.arm_max_reps,
                    cpu_request_per_rep = decision.cpu_request_per_rep
                )
            )
        return res
