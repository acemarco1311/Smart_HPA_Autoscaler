import grpc  # for gRPC server
from concurrent import futures  # for request handling
from data_format import ResourceData
from data_format import ARMDecision
import argparse
from microservice_manager import MicroserviceManager


import microservice_manager_pb2  # for message definitions
# for stub (client) or implementation class (server)
import microservice_manager_pb2_grpc


# implementation for remote gRPC services
class MicroserviceManagerImpl(
        microservice_manager_pb2_grpc.MicroserviceManagerServicer):
    # constructor, pass microservice manager object
    # to execute
    def __init__(self, microservice_manager):
        # Microservice Manager object to execute tasks
        self._microservice_manager = microservice_manager

    # implementation
    def ExtractResourceData(self, request, context):
        data = self._microservice_manager.Extract()
        # response
        res = microservice_manager_pb2.ResourceData(
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
        return res

    def ExecuteScaling(self, request, context):
        arm_decision = ARMDecision(
                microservice_name = request.microservice_name,
                allowed_scaling_action = request.allowed_scaling_action,
                feasible_reps = request.feasible_reps,
                arm_max_reps = request.arm_max_reps,
                cpu_request_per_rep = request.cpu_request_per_rep
        )
        result = self._microservice_manager.Execute(arm_decision)
        res = microservice_manager_pb2.ScalingStatus(
                status = result
        )
        return res

    def GetMaxReps(self, request, context):
        # type int ensured
        current_max_reps = self._microservice_manager.get_max_reps()
        res = microservice_manager_pb2.MaxRepResponse(max_reps=current_max_reps)
        return res

vvcv# entry point
if __name__ == "__main__":
    # get client inputs
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostname", type=str)
    parser.add_argument("--port", type=str)
    parser.add_argument("--microservice_name", type=str)
    parser.add_argument("--min_reps", type=int)
    parser.add_argument("--max_reps", type=int)
    parser.add_argument("--target_cpu_utilization", type=int)
    args = parser.parse_args()

    # create a Microservice Manager
    ms = MicroserviceManager(args.microservice_name,
                             args.min_reps,
                             args.max_reps,
                             args.target_cpu_utilization)

    # configure server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    implementation = MicroserviceManagerImpl(ms)
    # register implementation class to server
    microservice_manager_pb2_grpc.add_MicroserviceManagerServicer_to_server(
            implementation,
            server
    )
    # configure server
    server.add_insecure_port("[::]:" + args.port)
    server.start()
    print("Microservice Manager for " + args.microservice_name + " started on port " + args.port)
    server.wait_for_termination()


