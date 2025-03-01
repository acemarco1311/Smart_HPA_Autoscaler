import grpc
from data_format import ResourceData
from data_format import ARMDecision

# communicate to server of Adaptive Resource Manager
import adaptive_resource_manager_pb2
import adaptive_resource_manager_pb2_grpc

# communicate to servers of Microservice Managers
import microservice_manager_pb2
import microservice_manager_pb2_grpc


'''
    Trigger resource exchange if any microservice
    need to scale beyond its current limit.

    Input:
        microservices_data - List<ResourceData>

    Output:
        need_exchange - Boolean
'''


def need_resource_exchange(microservices_data):
    need_exchange = False
    i = 0
    while not need_exchange and i < len(microservices_data):
        # need to scale beyond max_reps
        if (microservices_data[i].desired_for_scale_reps >
                microservices_data[i].max_reps):
            need_exchange = True
        i += 1
    return need_exchange


'''
    Produce scaling instructions for microservices
    that are free to scale: scale up within limit,
    scale down, no scale.

    Input:
        microservices_data - List<ResourceData>
            free to scale microservices

    Output:
        scaling_instructions - List<ARMDecision>
'''


def free_to_scale(microservices_data):
    scaling_instructions = []
    for microservice in microservices_data:
        scaling_instructions.append(ARMDecision(
            microservice.microservice_name,
            microservice.scaling_action,
            microservice.desired_for_scale_reps,
            microservice.max_reps,
            microservice.cpu_request_per_rep
            ))
    return scaling_instructions

'''
    Send request to Adaptive Resource Manager to
    obtain scaling instructions in resource constrained
    environment.
    
    Input:
        microservices_data - List<ResourceData>

    Output:
        scaling_instructions - List<ARMDecision>
'''


def send_request_to_arm(microservices_data):
    with grpc.insecure_channel("localhost:5002") as channel:
        # obtain stub
        stub = adaptive_resource_manager_pb2_grpc.AdaptiveResourceManagerStub(channel)
        # create request ResourceDataList
        req = adaptive_resource_manager_pb2.ResourceDataList()
        for data in microservices_data:
            req.microservices_data.append(
                adaptive_resource_manager_pb2.ResourceData(
                    microservice_name=data.microservice_name,
                    current_reps=data.current_reps,
                    desired_reps=data.desired_reps,
                    cpu_usage_per_rep=data.cpu_usage_per_rep,
                    cpu_request_per_rep=data.cpu_request_per_rep,
                    cpu_utilization_per_rep=data.cpu_utilization_per_rep,
                    desired_for_scale_reps=data.desired_for_scale_reps,
                    scaling_action=data.scaling_action,
                    max_reps=data.max_reps,
                    min_reps=data.min_reps,
                    target_cpu_utilization=data.target_cpu_utilization
                )
            )

        # receive ARMDecisionList
        res = stub.ResourceExchange(req)

        # create a list of local ARMDecision named tuple
        scaling_instructions = []

        # iterate through grpc ARMDecisionList
        for decision in res.scaling_instructions:
            scaling_instructions.append(
                ARMDecision(
                    decision.microservice_name,
                    decision.allowed_scaling_action,
                    decision.feasible_reps,
                    decision.arm_max_reps,
                    decision.cpu_request_per_rep
                )
            )
        return scaling_instructions



'''
    Inspect microservices data to produce scaling actions.

    Input:
        microservices_data - List<ResourceData>
            resource data from all microservices

    Output:
        scaling_instructions - List<ARMDecision>
            scaling instruction for each microservice
'''


def inspect_microservices(microservices_data):
    # Resource Constraint environment
    if need_resource_exchange(microservices_data):
        scaling_instructions = send_request_to_arm(microservices_data)

    # no scaling over limit, all free to scale (ResourceRich)
    else:
        scaling_instructions = free_to_scale(microservices_data)

    return scaling_instructions


#TODO: update Knowledge Base
def update_knowledge_base():
    pass


# entry point
if __name__ == "__main__":
    pass
