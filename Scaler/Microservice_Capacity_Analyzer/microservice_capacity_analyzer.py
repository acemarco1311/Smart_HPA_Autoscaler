from concurrent import futures
from multiprocessing import Process, Lock
import time

import grpc

# health check
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from data_format import ResourceData
from data_format import ARMDecision
import subroutine

from tenacity import retry, stop_after_attempt, stop_after_delay
from tenacity import wait_fixed, wait_exponential
from tenacity import after
from tenacity import retry_if_exception
from tenacity import retry_if_result

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

        # connect to ARM
        self._arm_connection = self._connect_to_arm()

        # connect to adaptive resource manager
        self._microservice_connections = []
        for microservice in microservice_names:
            connection = self._connect_to_server(microservice)
            self.add_microservice_connection(connection)
        return

    # microservice manager connections getter
    # output List<Dict<str, Object>>
    def get_microservice_connections(self):
        return self._microservice_connections


    '''
        Remove a connection to a microservice manager based
        on microservice_name

        Input:
            microservice_name - str

        Output:
            True - success
            False if incorrect microservice_name
    '''
    def remove_microservice_connection(self, microservice_name):
        index = 0
        target_index = -1
        for i in range(len(self._microservice_connections)):
            connection = self._microservice_connections[i]
            if connection["name"] == microservice_name:
                target_index = i
                break
            else:
                index += 1

        if target_index == -1:
            return False
        else:
            # close channel
            self._microservice_connections[target_index]["channel"].close()
            #TODO: mutex
            self._microservice_connections.pop(target_index)
            return True


    '''
        Add a new microservice manager connection

        Input:
            connection - Dict<str, Object>
    '''

    #TODO: mutex
    def add_microservice_connection(self, connection):
        self._microservice_connections.append(connection)



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

    '''
    def _connect_to_server(self, microservice_name):
        # connect to MS manager from microservice name
        ms_manager_name = microservice_name + "-manager"

        service_endpoint = subroutine.get_service_endpoint(ms_manager_name)
        if service_endpoint is None:
            print("Cannot resolve endpoint to connect to Service to ", microservice_name)
            raise ValueError("Incorrect microservice name.")

        # NO ERROR HERE: LOCAL OPERATION
        # create connection with server
        connection = None
        channel = grpc.insecure_channel(
            service_endpoint,
            options=[]
        )
        stub = microservice_manager_pb2_grpc.MicroserviceManagerStub(channel)
        # return Dict
        connection = {
                "name": microservice_name,  # still use ms name
                "channel": channel,
                "stub": stub
        }
        return connection


    # similar to connect_to_server()
    # but connect to arm instead
    def _connect_to_arm(self):
        service_endpoint = subroutine.get_service_endpoint(self.arm_name)
        if service_endpoint is None:
            print("Cannot resolve endpoint to connect to Service to ", self.arm_name)
            raise ValueError("Incorrect server name for Adaptive Resource Manager.")

        # NO ERROR: Lazy connection establishment
        # create channel object
        channel = grpc.insecure_channel(
            service_endpoint,
            options=[]
        )
        stub = adaptive_resource_manager_pb2_grpc.AdaptiveResourceManagerStub(channel)
        # return Dict
        connection = {
                "name": self.arm_name,  # still use ms name
                "channel": channel,
                "stub": stub
        }
        return connection

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
        Send a health check to a Microservice Manager server.

        Input:
            microservice_name - str

        Output:
            True - if server active
            False - if server not available
            None - if cannot find microservice in the connection pool
    '''
    def health_check(self, microservice_name):
        connection = self._get_connection(microservice_name)
        if connection is None:
            print("No connected server named ", microservice_name)
            return None
        health_stub = health_pb2_grpc.HealthStub(connection["channel"])
        health_req = health_pb2.HealthCheckRequest(service="")
        try:
            health_res = health_stub.Check(health_req)
            if (health_res.status == health_pb2.HealthCheckResponse.SERVING):
                health = True
            else:
                health = False
        except Exception as err:
            print("Error occured while health check ", microservice_name)
            health = None
        finally:
            return health


    def reset_connection(self, microservice_list):
        for microservice_name in microservice_list:
            print("Reset connection with: ", microservice_name)
            self.remove_microservice_connection(microservice_name)
            Process(target=self._connect_to_server, args=(microservice_name,)).start()

    '''
        Get ResourceData from all connected Microservice Manager

        Input:
            None

        Output:
            List<ResourceData> resource_data
            List<str> failed_call
    '''

    def obtain_all_resource_data(self):
        resource_data = []
        failed_call = []
        #TODO: do concurrently with threading
        for connection in self._microservice_connections:
            data = self._obtain_resource_data(connection)
            if data is None:
                failed_call.append(connection["name"])
            else:
                resource_data.append(data)

        #TODO: Use thread to callback, the healthy pod
        # go ahead with the resource exchange round
        # reset the connection with the service
        # see if it switches to healthy pods
        if len(failed_call) != 0:
            # remove the channel from connection pool
            for ms in failed_call:
                self.remove_microservice_connection(ms)
        # continue with healthy pod only
        return (resource_data, failed_call)


    '''
        Fault tolerance when interacting with Servers

        Retry-backoff (exponential) on:
            UNAVAILABLE (restarting hopefully)
            or DEADLINE_EXCEEDED (network partition hopefully)
    '''

    # Retry when unavailable (restarting hopefully)
    # or timeout (network error hopefully)
    @staticmethod
    def should_retry(err):
        if isinstance(err, grpc.RpcError):
            unavailable = (err.code() == grpc.StatusCode.UNAVAILABLE)
            deadline_exceeded = (err.code() == grpc.StatusCode.DEADLINE_EXCEEDED)
            return unavailable or deadline_exceeded
        return False


    # return None as callback
    @staticmethod
    def error_callback(retry_state):
        print("All retries failed.")
        return None

    '''
        Send request to extract the metrics (resource data)
        from a Microservice Manager and perform scaling

        Input:
            microservice_name - str

        Output:
            resource_data - ResourceData

            None if failed

    '''
    @retry(
        # maximum attemp & total execution time
        stop=(stop_after_attempt(3) |
              stop_after_delay(20)),
        # exponential wait between retries
        wait=wait_exponential(multiplier=1,
                              min=2,
                              max=4),
        # error notification callback: unavailable or deadline exceed
        after=lambda retry_state: print(retry_state.outcome.exception()),
        # retry condition
        # retry when server unavailable (restarting hopefully)
        # or deadline exceeded (network partition hopefully)
        retry=retry_if_exception(should_retry),
        # return None if failed
        retry_error_callback=error_callback
    )
    def _obtain_resource_data(self, connection):
        stub = connection["stub"]

        # create request
        request = microservice_manager_pb2.ResourceDataRequest()

        try:
            # set timeout on request
            # retry on UNAVAILABLE or DEADLINE_EXCEEDEDED
            response = stub.ExtractResourceData(request,
                                                timeout=10)

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
        except Exception as e:
            if isinstance(e, grpc.RpcError):
                unavailable = (e.code() == grpc.StatusCode.UNAVAILABLE)
                deadline_exceeded = (e.code() == grpc.StatusCode.DEADLINE_EXCEEDED)
                do_retry = unavailable or deadline_exceeded
                # re-raise for retry
                if do_retry:
                    raise e
                # re-raise error for retry
                else:
                    print("Cannot extract resource from ", connection["name"])
                    print(e)
                    return None
            else:
                print("Cannot extract resource from ", connection["name"])
                print(e)
                return None

    '''
        Send scaling instruction to Microservice Manager

        Input:
            ARMDecision

        Output:
            scaling_status - str

            retry on UNAVAILABLE or DEADLINE_EXCEEDED
            None if failed.
    '''

    @retry(
        # maximum attemp & total execution time
        stop=(stop_after_attempt(3) |
              stop_after_delay(20)),
        # exponential wait between retries
        wait=wait_exponential(multiplier=1,
                              min=2,
                              max=4),
        # error notification callback
        after=lambda retry_state: print(retry_state.outcome.exception()),
        # retry condition
        # retry when server unavailable (restarting hopefully)
        # or deadline exceeded (network partition hopefully)
        retry=retry_if_exception(should_retry),
        # return None if failed
        retry_error_callback=error_callback
    )
    def _send_scaling_instruction(self, arm_decision):
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

        try:
            response = stub.ExecuteScaling(request, timeout=10)
            return response.status
        except Exception as e:
            if isinstance(e, grpc.RpcError):
                unavailable = (e.code() == grpc.StatusCode.UNAVAILABLE)
                deadline_exceeded = (e.code() == grpc.StatusCode.DEADLINE_EXCEEDED)
                do_retry = unavailable or deadline_exceeded
                # re-raise for retry
                if do_retry:
                    raise e
                # re-raise error for retry
                else:
                    print("Cannot send scaling instruction to ", connection["name"])
                    return None
            else:
                print("Cannot send scaling instruction to ", connection["name"])
                return None


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
        failed_call = []
        for decision in arm_decisions:
            status = self._send_scaling_instruction(decision)
            if status is None:
                failed_call.append(decision.microservice_name)
            else:
                status_list.append({
                    "microservice_name": decision.microservice_name,
                    "status": status
                })

        # TODO: callback for fault tolerance
        # health pod continue
        if len(failed_call) != 0:
            # remove connection for reconnect later
            for ms in failed_call:
                self.remove_microservice_connection(ms)
        return (status_list, failed_call)

    '''
        Send request to Adaptive Resource Manager to
        obtain scaling instructions in resource constrained
        environment.

        Input:
            microservices_data - List<ResourceData>

        Output:
            scaling_instructions - List<ARMDecision>
    '''

    @retry(
        # maximum attemp & total execution time
        stop=(stop_after_attempt(3) |
              stop_after_delay(20)),
        # exponential wait between retries
        wait=wait_exponential(multiplier=1,
                              min=2,
                              max=4),
        # error notification callback
        after=lambda retry_state: print(retry_state.outcome.exception()),
        # retry condition
        # retry when server unavailable (restarting hopefully)
        # or deadline exceeded (network partition hopefully)
        retry=retry_if_exception(should_retry),
        # return None if failed
        retry_error_callback=error_callback
    )
    def _send_request_to_arm(self, microservices_data):
        # obtain stub
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

        try:
            # receive ARMDecisionList
            res = stub.ResourceExchange(req, timeout=10)
        except Exception as e:
            if not CapacityAnalyzer.should_retry(e):
                print("Failed to send request to ARM")
                print(e)
                return None
            # raise for retry
            else:
                raise(e)

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


    ########################################################
    ### MICROSEVICE CAPACITY ANALYZER INTERNAL OPERATION ###
    ########################################################

    # Local operations on received data only
    # No fault tolerance

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
        Inspect microservices data to produce scaling actions.

        Input:
            microservices_data - List<ResourceData>
                resource data from all microservices

        Output:
            scaling_instructions - List<ARMDecision>
                scaling instruction for each microservice

            None if cannot call to Adaptive Resource Manager
            in Resource-constraint environment
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


def test_one(sleep_time, microservice_name, delete_interval):
    time.sleep(sleep_time)
    script = f"kubectl get pods -l app={microservice_name}"
    pod_id_list = []
    result = subroutine.execute_kubectl(script)
    for line in result.splitlines()[1:]:
        # pod id in first column
        pod_id = line.split()[0]
        pod_id_list.append(str(pod_id))
    # delete replicas in the deployment
    for pod_id in pod_id_list:
        script = f"kubectl delete pod {pod_id}"
        print(subroutine.execute_kubectl(script))
        time.sleep(delete_interval)


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
    #while True:
    #    resource_data = client.obtain_all_resource_data()
    #    print("Extracted metrics from " + str(len(resource_data)) + "/11 microservices")

    #    scaling_instructions = client.inspect_microservices(resource_data)
    #    if scaling_instructions is None:
    #        continue
    #    else:
    #        total_arm_resources = 0
    #        for microservice in scaling_instructions:
    #            total_arm_resources += (microservice.arm_max_reps *
    #                                   microservice.cpu_request_per_rep)
    #        print("Total Resources: ", total_arm_resources)
    #        scaling_status = client.distribute_all_instructions(scaling_instructions)
    #        print("Scaled " + str(len(scaling_status)) + "/11 microservices")
    #    print("----------------------")
    #    time.sleep(3)

    ### Test 1: Delete microservice pods
    test_one_total_time = 100
    test_one_start_time = time.time()

    print("TEST 1 STARTED.")
    # delete pods in parallel with Smart HPA
    # delete pod of adservice, checkoutservice
    #p1 = Process(target=test_one, args=(15, "adservice", 4,))
    #p2 = Process(target=test_one, args=(20, "checkoutservice", 4,))
    #p1.start()
    #p2.start()

    # run Smart HPA for the test
    while (time.time() - test_one_start_time) < test_one_total_time:
        print("--------------------")
        resource_data, extract_failed_calls = client.obtain_all_resource_data()
        print("Extracted metrics from " + str(len(resource_data)) + "/11 microservices")
        scaling_instructions = client.inspect_microservices(resource_data)
        if scaling_instructions is None:
            print("Couldn't get scaling instruction, skip resource exchange round")
            continue
        else:
            total_arm_resources = 0
            for microservice in scaling_instructions:
                total_arm_resources += (microservice.arm_max_reps *
                                        microservice.cpu_request_per_rep)
            print("Total Resources: ", total_arm_resources)
            scaling_status, distribute_failed_calls = client.distribute_all_instructions(scaling_instructions)
            print("Scaled " + str(len(scaling_status)) + "/11 microservices")
        print("Reset failed calls: ")
        print(extract_failed_calls)
        print(distribute_failed_calls)
        for microservice in microservice_names:
            if client._get_connection(microservice) is None:
                print("Reset connection with ", microservice)
                client._connect_to_server(microservice)
        print("--------------------")


    
    ### Test 2: Delete the whole microservice deployments

    ### Test 3: Delete each microservice manager pod

    ### Test 4: Delete the whole microservice manager deployment
