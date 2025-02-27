import grpc
import helloworld_pb2 # for message definitions
import helloworld_pb2_grpc # for stub
from concurrent import futures


# remote procedure implementation
# GreetServicer class which implements the service methods
# CanBeAnything extends GreetServicer to put the custom behavior

class CanBeAnything(helloworld_pb2_grpc.GreetServicer):

    def __init__(self, foo):
        self.foo = foo

    # request: HelloRequest
    # self: convention because this is just implementation file?
    #TODO: context: grpc.server Context object
    def SayHello(self, request, context):
        # create a HelloResponse message
        # which is defined in helloworld_pb2
        return helloworld_pb2.HelloResponse(message=f"Hi {request.name} and {self.foo}")


if __name__ == "__main__":
    port = "5001"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # register custom gRPC implementation (CanBeAnything object)
    # to gRPC server
    helloworld_pb2_grpc.add_GreetServicer_to_server(CanBeAnything("hehe"), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started.")
    server.wait_for_termination()
