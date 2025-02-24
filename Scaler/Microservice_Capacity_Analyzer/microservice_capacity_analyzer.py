from data_format import ResourceData
from data_format import ARMDecision


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


def inspect_microservices(microservices_data):
    if need_resource_exchange(microservices_data):
        #TODO: send request to ARM server
        print("")

    # no scaling over limit, all free to scale
    else:
        # capacity give instruction for scaling
        return free_to_scale(microservices_data)


#TODO: update Knowledge Base
def update_knowledge_base():
    pass


# entry point
if __name__ == "__main__":
    arm_saved_decision = []
    arm_decision = []
    print("")
