from data_format import ResourceData
from data_format import ARMDecision


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
        #TODO: send request to ARM server
        pass

    # no scaling over limit, all free to scale (ResourceRich)
    else:
        # capacity give instruction for scaling
        return free_to_scale(microservices_data)


#TODO: update Knowledge Base
def update_knowledge_base():
    pass


# entry point
if __name__ == "__main__":
    pass
