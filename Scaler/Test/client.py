import grpc
import helloworld_pb2 # for message definitions
import helloworld_pb2_grpc # for stub
import microservice_manager_pb2
import microservice_manager_pb2_grpc

from collections import namedtuple


# resource extraction from MS Manager
ResourceData = namedtuple("ResourceData", [
    "microservice_name",
    "current_reps",
    "desired_reps",  # num reps to be maintained before scaling decision
    "cpu_usage_per_rep",
    "cpu_request_per_rep",
    "cpu_utilization_per_rep",
    "desired_for_scale_reps"  # num reps needs to be scaled
    "scaling_action",  # needed scaling action
    "max_reps",
    "min_reps",
    "target_cpu_utilization"
])



# scaling instruction for each microservice
ARMDecision = namedtuple("ARMDecision", [
    "microservice_name",

    "allowed_scaling_action",  # scaling action allowed by ARM

    # number of reps that ARM allows this ms to scale up to
    "feasible_reps",

    "arm_max_reps",  # microservice max rep restrictions,
                     # replace user-defined max_reps
                     # kept track by ARM

    "cpu_request_per_rep"
])
# send request to server to provoke
# remote procedure
def run():
    with grpc.insecure_channel("localhost:5001") as channel:
        # get the stub from generated code
        # pass the channel to connect to the server
        # stub name = <ServiceName.Stub
        # service name = Greet
        stub = helloworld_pb2_grpc.GreetStub(channel)

        # create a message request
        request = helloworld_pb2.HelloRequest(name="Toan")

        # provoke remote procedure through stub
        # wait for a response
        response = stub.SayHello(request)

        # response is HelloResponse object
        print(response.message)


def run_test():
    with grpc.insecure_channel("localhost:5001") as channel:
        stub = microservice_manager_pb2_grpc.MicroserviceManagerStub(channel)
        # metric request
        resource_request = microservice_manager_pb2.ResourceDataRequest()
        response = stub.ExtractResourceData(resource_request)
        print(type(response))
        print(response)
        scaling_request = microservice_manager_pb2.ARMDecision(
                microservice_name = "adservice",
                allowed_scaling_action = "scale up",
                feasible_reps = 1,
                arm_max_reps = 3,
                cpu_request_per_rep = 100,
        )
        response = stub.ExecuteScaling(scaling_request)
        print(type(response))
        print(response)
        max_rep_request = microservice_manager_pb2.MaxRepRequest()
        response = stub.GetMaxReps(max_rep_request)
        print(type(response))
        print(response)

if __name__ == "__main__":
    run_test()
