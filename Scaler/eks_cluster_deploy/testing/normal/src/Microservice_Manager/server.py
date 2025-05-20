import grpc  # for gRPC server
from concurrent import futures  # for request handling
from data_format import ResourceData
from data_format import ARMDecision
import argparse
from microservice_manager import MicroserviceManager
import time

# for grpc health check
# generated from a provided health check .proto
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

# for leader election - passive replication
import threading
import uuid
from kubernetes import client, config
from kubernetes.leaderelection import leaderelection
from kubernetes.leaderelection.resourcelock.configmaplock import ConfigMapLock
from kubernetes.leaderelection import electionconfig

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
    
    def get_microservice_manager(self):
        return self._microservice_manager

    # implementation
    def ExtractResourceData(self, request, context):
        # data can be None if error when calling kube-api-server
        data = self._microservice_manager.Extract()

        # if receive a None in extracting metrics
        # send error
        if data is None:
            context.abort(grpc.StatusCode.INTERNAL,
                          "Error in extracting resource data")

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
        # return Error if faults occured in interacting with kube-api
        if result is None:
            # this return an error and terminate the channel
            context.abort(grpc.StatusCode.INTERNAL,
                          "Error in execute scaling for microservice.")
        res = microservice_manager_pb2.ScalingStatus(
                status = result
        )
        return res

    def GetMaxReps(self, request, context):
        # type int ensured
        current_max_reps = self._microservice_manager.get_max_reps()
        res = microservice_manager_pb2.MaxRepResponse(max_reps=current_max_reps)
        return res


'''
    Configure health service in server for liveness probe
    via Check(), Watch() 

    Input: 
        server - gRPC server

'''
def _configure_health_server(server: grpc.Server):
    # create a health servicer
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
    )
    # add health servicer to Server
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)



# entry point
if __name__ == "__main__":

    # geta client inputs
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

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    implementation = MicroserviceManagerImpl(ms)

    def start_server():
        print("I'm the leader.")
        print("Updating label to receive traffic...")
        while ms.promote_to_leader() is None:
             print("Failed to update label, retrying...")
        print("Updated pod label, starting server...")
        # register implementation class to server
        microservice_manager_pb2_grpc.add_MicroserviceManagerServicer_to_server(
                implementation,
                server
        )
        # configure server
        server.add_insecure_port("[::]:" + args.port)
        _configure_health_server(server)
        server.start()
        print("Microservice Manager for " + args.microservice_name + " started on port " + args.port)
        server.wait_for_termination()


    # load this pod config
    config.load_incluster_config()
    candidate_id = uuid.uuid4()
    # use each configmaplock for each microservice manager
    lock_name = f"{args.microservice_name}-leader-lock"
    lock_namespace = "default"
    config = electionconfig.Config(
                ConfigMapLock(lock_name, lock_namespace, candidate_id),
                lease_duration=17,
                renew_deadline=15,
                retry_period=5,
                onstarted_leading=start_server,
                onstopped_leading=None
            )
    leaderelection.LeaderElection(config).run()






