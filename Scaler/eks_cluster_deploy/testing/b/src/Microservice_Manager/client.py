import grpc
import microservice_manager_pb2
import microservice_manager_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc


with grpc.insecure_channel("localhost:5001") as channel:
    stub = microservice_manager_pb2_grpc.MicroserviceManagerStub(channel)
    health_stub = health_pb2_grpc.HealthStub(channel)
    request = health_pb2.HealthCheckRequest(service="")
    response = health_stub.Check(request)
    print(response)
    print(type(response))

