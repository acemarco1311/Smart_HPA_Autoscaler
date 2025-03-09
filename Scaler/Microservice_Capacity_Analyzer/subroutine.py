# run kubectl command

# get services' cluster ip
# kubectl get service <service-name> -o=jsonpath='{.spec.clusterIP}'

# get the port
# kubectl get service <service-name> -o=jsonpath='{.spec.ports}'

#TODO: copy from Manager's subroutine for retry

import subprocess
import json
from tenacity import retry, stop_after_attempt, stop_after_delay
from tenacity import retry_if_result
from tenacity import wait_fixed
from tenacity import after
from tenacity import retry_if_exception_type

# callback function on each retry for execute_kubectl()
# notify the error message from last retry
def callback_each_retry(retry_state):
    if retry_state.outcome.failed:
        err = retry_state.outcome.exception()
        # error from server
        if isinstance(err, subprocess.CalledProcessError):
            print("Received error from kube-api-server")
            print(err.stdout.decode("utf-8"))
        # timeout error
        elif isinstance(err, subprocess.TimeoutExpired):
            print("Exceed timeout")
        # unexpected error
        else:
            print("Unexpected error occurred")
            print(err)
        print("Retrying...")


# callback function if all retries failed
# avoid raising exception and crash
# return None instead
def callback_all_retries(retry_state):
    print("All retries failed")
    # return None instead of crashing
    return None


'''
    Execute 'kubectl' commands

    Input:
        script - str:
            command to run

    Output:
        script_result_str - str
        None if failed
'''

#TODO: backoff exponential instead of fixed wait
# retry
@retry(
    # 3 attempts, total execution time = 6s
    stop=(stop_after_attempt(3) |
          stop_after_delay(6)),
    # wait 1 second between retries
    wait=wait_fixed(1),
    # if failed, show the type of error
    after=callback_each_retry,
    # if failed all retries, notify that it cannot be completed
    retry_error_callback=callback_all_retries
)
def execute_kubectl(script):
    script_result = subprocess.check_output(
        script.split(),
        stderr=subprocess.STDOUT,  # get error message in stdout
        timeout=2  # ensure enough timeout for some operations
    )  # Error from server or Timeout might get raised

    # convert output to from byte to string
    # empty string might become string "''"
    # avoid this
    script_result_str = script_result.decode("utf-8").strip().strip('"').strip("'")

    if len(script_result_str) == 0:
        raise ValueError("Received an empty result from kube-apiserver")
    return script_result_str


'''
    Get the clusterIP:port of the service
    with port name = "traffic" (differs from
    "health" port for liveness)

    Input:
        - microservice_name - str

    Output:
        - service_endpoint - str
        in form clusterIP:port

        - None if failed
'''


def get_service_endpoint(microservice_name):
    ip_script = (
            f"kubectl get service {microservice_name} "
            "-o=jsonpath='{.spec.clusterIP}'"
    )
    # retry-backoff with kubeapi-server
    ip_script_result = execute_kubectl(ip_script)

    ports_script = (
            f"kubectl get service {microservice_name} "
            "-o=jsonpath='{.spec.ports}'"
    )

    # retry-backoff with kubeapi-server
    ports_script_result = execute_kubectl(ports_script)

    # error occured in calling K8s API
    if (ip_script_result is None or
        ports_script_result is None):
        return None

    service_endpoint = None
    try:
        # convert string to List<Dict>
        # ports_script_result = valid string for List<Dict>
        available_ports = json.loads(ports_script_result)
        service_port = None
        for port in available_ports:
            if port["name"] == "traffic":
                service_port = port["port"]
        # convert port from int to string
        service_port_str = str(service_port)
        service_endpoint = ip_script_result + ":" + service_port_str
    except Exception as err:
        print("Unexpected error occurred in connecting to Service ", microservice_name)
        print(err)
    return service_endpoint


'''
    Get all the pods/servers endpoints that
    the specified Service is forwarding traffic to

    Input:
        microservice_name - str: name of K8s Service

    Output:
        List<String>: IP of all pod replicas
'''
def get_all_server_endpoints(microservice_name):
    script = f"kubectl get endpoints {microservice_name}"
    server_endpoints = subroutine.execute_kubectl(script)
    return server_endpoints
