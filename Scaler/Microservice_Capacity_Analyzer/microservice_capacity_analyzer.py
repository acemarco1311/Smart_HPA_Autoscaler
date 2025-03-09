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
        containes name, channel, stub.
    '''

    '''
        Input:
            microservice_names - List<str>
            arm_name - str

        Connects to all other components (ms managers vs arm)
    '''

    def __init__(self, microservice_names, arm_name):
        self.microservice_names = microservice_names
        # default
        self.arm_name = arm_name

        #TODO: handle errors
        # connect to ARM
        self._arm_connection = self._connect_to_arm()

        #TODO: handle timeout/errors
        # use threads for optimization
        # concurrently connect to all microservice managers
        # connect to adaptive resource manager
        self._microservice_connections = []
        for microservice in microservice_names:
            connection = self._connect_to_server(microservice)
            self._microservice_connections.append(connection)
        return

    # microservice manager connections getter
    # output List<Dict<str, Object>>
    def get_microservice_connections(self):
        return self._microservice_connections

    # ARM connection getter
    # output: Dict
    def get_arm_connection(self):
        return self._arm_connection


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

    def _connect_to_server(self, microservice_name):
        # connect to MS manager from microservice name
        ms_manager_name = microservice_name + "-manager"

        service_endpoint = subroutine.get_service_endpoint(ms_manager_name)
        if service_endpoint is None:
            print("Cannot resolve endpoint to connect to Service to ", microservice_name)
            return None

        # create connection with server
        connection = None
        try:
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
            stub = microservice_manager_pb2_grpc.MicroserviceManagerStub(channel)
            # return Dict
            connection = {
                    "name": microservice_name,  # still use ms name
                    "channel": channel,
                    "stub": stub
            }
        except Exception as err:
            print("Unexpected error occured while connecting to Manager of ", microservice_name)
            print(err)
        finally:
            return connection

    # similar to connect_to_server()
    # but connect to arm instead
    def _connect_to_arm(self):
        service_endpoint = subroutine.get_service_endpoint(self.arm_name)
        if service_endpoint is None:
            print("Cannot resolve endpoint to connect to Service to ", self.arm_name)
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
            stub = microservice_manager_pb2_grpc.MicroserviceManagerStub(channel)
            # return Dict
            connection = {
                    "name": self.arm_name,  # still use ms name
                    "channel": channel,
                    "stub": stub
            }
        except Exception as err:
            print("Unexpected error occured while connecting to Adaptive Resource Manager")
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

    def _need_resource_exchange(self, microservices_data):
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

    def _free_to_scale(self, microservices_data):
        # TODO: no need to send decision if
        # scaling = "no scale"
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
        Get the connection (name, channel, stub) in the
        connection pool

        Input:
            microservice_name - str:

        Output:
            connection - Dict<str, Obj>

            None if not exists.
    '''

    def _get_connection(self, microservice_name):
        connection = None
        i = 0
        while connection is None and i < len(self._microservice_connections):
            if microservice_name == self._microservice_connections[i]["name"]:
                connection = self._microservice_connections[i]
            i += 1
        return connection

    '''
        Get ResourceData from all connected Microservice Manager

        Input:
            None

        Output:
            List<ResourceData>
    '''

    #TODO: fault tolerance, some manager disconnected
    def obtain_all_resource_data(self):
        resource_data = []
        for connection in self._microservice_connections:
            resource_data.append(self._obtain_resource_data(connection))
        return resource_data

    '''
        Send request to extract the metrics (resource data)
        from a Microservice Manager and perform scaling

        Input:
            microservice_name - str

        Output:
            resource_data - ResourceData

    '''

    def _obtain_resource_data(self, connection):
        #TODO: fault tolerance: not exist (None)
        stub = connection["stub"]

        # create request
        request = microservice_manager_pb2.ResourceDataRequest()

        #TODO: network fault tolerance
        # get response
        response = stub.ExtractResourceData(request)

        # convert gRPC ResourceData into named tuple ResourceData
        return ResourceData(
            response.microservice_name,
            response.current_reps,
            response.desired_reps,
            response.cpu_usage_per_rep,
            response.cpu_request_per_rep,
            response.cpu_utilization_per_rep,
            response.desired_for_scale_reps,
            response.scaling_action,
            response.max_reps,
            response.min_reps,
            response.target_cpu_utilization
        )

    '''
        Send scaling instruction to Microservice Manager

        Input:
            ARMDecision

        Output:
            scaling_status - str
    '''

    def _send_scaling_instruction(self, arm_decision):
        #TODO: fault tolerance, not exist None
        microservice_name = arm_decision.microservice_name
        connection = self._get_connection(microservice_name)
        stub = connection["stub"]

        # create request
        request = microservice_manager_pb2.ARMDecision(
            microservice_name=arm_decision.microservice_name,
            allowed_scaling_action=arm_decision.allowed_scaling_action,
            feasible_reps=arm_decision.feasible_reps,
            arm_max_reps=arm_decision.arm_max_reps,
            cpu_request_per_rep=arm_decision.cpu_request_per_rep
        )


        #TODO: connection fault tolerance
        # send request
        response = stub.ExecuteScaling(request)
        return response.status

    '''
        Distribute all scaling instructions to all
        Microservice Managers

        Input:
            scaling_instructions - List<ARMDecision>


        Output:
            status_list - List<Dict>:
                Dict contains: microservice names (str),
                scaling status (str)
    '''
    def distribute_all_instructions(self, arm_decisions):
        status_list = []
        for decision in arm_decisions:
            status_list.append({
                "microservice_name": decision.microservice_name,
                "status": self._send_scaling_instruction(decision)
            })
        return status_list

    '''
        Send request to Adaptive Resource Manager to
        obtain scaling instructions in resource constrained
        environment.

        Input:
            microservices_data - List<ResourceData>

        Output:
            scaling_instructions - List<ARMDecision>
    '''


    def _send_request_to_arm(self, microservices_data):
        # obtain stub
        #TODO: fault tolerance, None - doesn't exist
        connection = self._arm_connection
        stub = connection["stub"]
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

    def inspect_microservices(self, microservices_data):
        # Resource Constraint environment
        if self._need_resource_exchange(microservices_data):
            scaling_instructions = self._send_request_to_arm(microservices_data)

        # no scaling over limit, all free to scale (ResourceRich)
        else:
            scaling_instructions = self._free_to_scale(microservices_data)
        return scaling_instructions

    #TODO: update Knowledge Base
    def update_knowledge_base(self):
        pass

    #TODO: close a connection
    def close_microservice_connection(microservice_manager):
        pass

    #TODO: close arm connection
    def close_arm_connection():
        pass

    #TODO: close all microservice manager connection
    def close_all_microservice_connections():
        pass

    def total_allocated_resource():
        pass


# entry point
if __name__ == "__main__":
    microservice_names = [
        "adservice",
        "cartservice",
        "checkoutservice",
        "frontend",
        "paymentservice",
        "productcatalogservice",
        "recommendationservice",
        "shippingservice",
        "redis-cart",
        "emailservice",
        "currencyservice",
    ]
    arm_name = "adaptive-resource-manager"
    # create capacity analyzer
    # connect to all
    client = CapacityAnalyzer(microservice_names, arm_name)
    while True:
        resource_data = client.obtain_all_resource_data()
        scaling_instructions = client.inspect_microservices(resource_data)
        scaling_status = client.distribute_all_instructions(scaling_instructions)
