import grpc
from data_format import ResourceData
from data_format import ARMDecision
import subroutine

# communicate to server of Adaptive Resource Manager
import adaptive_resource_manager_pb2
import adaptive_resource_manager_pb2_grpc

# communicate to servers of Microservice Managers
import microservice_manager_pb2
import microservice_manager_pb2_grpc


class CapacityAnalyzer:

    '''
    microservice_names - List<str>: 
        Name of Service/Deployment of MS Manager
    microservice_connections - List<Dict>:
        contains name, channel, stub
    arm_name  - str: Name of Service/Deployment of ARM
    arm_connection - Dict:
        conains name, channel, stub.
        
    '''
    
    
    '''
        Input:
            microservice_names - List<str>
            arm_name - str

        Connects to all other components (ms managers vs arm)
    '''
    def __init__(self, microservice_names):
        self.microservice_names = microservice_names
        # default
        self.arm_name = "adaptive-resource-manager"
        
        # concurrently connect to all microservice managers
        # connect to adaptive resource manager
        self._microservice_connections = []
        for microservice in mircoservice_names:
            connection = self.connect_to_server(microservice)
            self._microservice_connections.append()
            


'''
    Connect to gRPC server of a Microservice Manager or
    Adaptive Resource Manager
    
    Input:
        microservice_name - str:
            the name of microservice.
            or "ARM" if connecting to Adaptive
            Resource Manager

    Output:
        Dict<str, Obj>: 
            name - str:
                microservice_name or "ARM"
            channel - grpc.Channel:
                TCP connection
            - stub
        
        None if fails.
'''

def connect_to_server(microservice_name):
    service_endpoint = subroutine.get_service_endpoint(microservice_name)
    if service_endpoint is None:
        print("Cannot resolve endpoint to connect to Service to ", microservice_name)
        return None
    try:
        connection = None
        channel = grpc.insecure_channel(
            service_endpoint,
            options = [
                #TODO: fault tolerance
                # retry-backoff
                # health check
                # timeout
                # https://github.com/grpc/proposal/blob/master/A6-client-retries.md
            ]
        )
        if microservice_name == "adaptive-resource-manager":
            stub = adaptive_resource_manager_pb2_grpc.AdaptiveResourceManagerStub(channel)
        else:
            stub = microservice_manager_pb2_grpc.MicroserviceManagerStub(channel)
        # return Dict
        connection = {
                "name": microservice_name,
                "channel": channel, 
                "stub": stub
        }
    except Exception as err:
        print("Unexpected error occured while connecting to ", microservice_name)
        print(err)
    finally:
        return connection



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
