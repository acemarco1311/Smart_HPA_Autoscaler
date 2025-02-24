import math
import statistics
import subprocess  # execute kubectl command
from tenacity import retry, stop_after_attempt, stop_after_delay
from tenacity import retry_if_result
from tenacity import wait_fixed
from tenacity import after
from tenacity import retry_if_exception_type

'''
    Validate user-defined arguments for microservice resource

    Input:
        max_reps - Int: number of max replicas
        min_reps - Int: number of min replicas
        target_cpu_utilization - Float: average cpu utilization for scaling
        current_arm_max_reps - Int: max_reps defined by ARM.

    Output:
        raise Error if max_reps/min_reps <= 0 or
        max_reps < min_reps or invalid CPU utilization
'''


def validate_argument(max_reps, min_reps, target_cpu_utilization, current_arm_max_reps):
    if (max_reps <= 0 or min_reps <= 0):
        raise ValueError("Invalid number of replicas.")
    if (max_reps < min_reps):
        raise ValueError("Invalid number of replicas.")
    if (target_cpu_utilization <= 0 or target_cpu_utilization > 100):
        raise ValueError("Invalid target CPU utilization.")
    if (current_arm_max_reps is not None):
        if current_arm_max_reps < min_reps:
            raise ValueError("Invalid ARM max_reps.")


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
    Execute `kubectl` command to interact with
    kube-api-server

    Input:
        script - str: kubectl command to run

    Output:
        result - str: response from kube-api-server
        None if: empty response or error from kube-api-server
'''


# retry
@retry(
    # 3 attempts, total execution time = 6s
    stop=(stop_after_attempt(3) |
          stop_after_delay(6)),
    # wait 1 second between retries
    wait=wait_fixed(1),
    # show error of retry
    after=callback_each_retry,
    # cannot complete notification
    retry_error_callback=callback_all_retries
)
def execute_kubectl(script):
    # capture stderr in stdout if error occurs
    # convert result to string
    # timeout = 2, > 1 for commands
    # such as kubectl delete
    script_result = subprocess.check_output(script.split(),
                                            stderr=subprocess.STDOUT,
                                            timeout=2).decode("utf-8")
    # empty string from server might become string "''"
    # when decode from byte to str type
    script_result = script_result.strip().strip('"').strip("'")
    if len(script_result) == 0:
        raise ValueError("Received an empty result from kube-apiserver.")
    return script_result


#TODO: is there any chance the number of reps = 0.
# the microservice being shutdown by Smart HPA
# > but we don't allow reps < min_reps
# so no problem here.
# further failure scenarios for handling
def scale(microservice_name, reps, min_reps):
    if reps < min_reps:
        raise ValueError("reps to scale < minimum reps")
    script = f"kubectl scale deployment {microservice_name} --replicas={reps}"
    script_result = execute_kubectl(script)
    return script_result


'''
    Get the number of available replicas in the deployment of
    the specified microservice. Use available replicas as
    current replicas.
    Because current replicas (status.replicas) will also count
    ready replicas (even those being init). Available replicas
    only count those who is running and pass readiness (accept traffic).


    Input:
        microservice_name - str: name of the microservice

    Output:
        available_replicas - Int: number of available replicas
        which passed the readiness probe and has been "Ready" >=
        `minReadySeconds` in deployment spec.

'''


def get_available_reps(microservice_name):
    print(f"Getting {microservice_name}'s number of available replicas.")
    script = (
            f"kubectl get deployment {microservice_name} "
            "-o=jsonpath='{.status.availableReplicas}'"
            )
    available_reps = execute_kubectl(script)
    if available_reps is None:
        return None
    return int(available_reps)


'''
    Get CPU usage from all replicas of this microservice using
    Metric servers.

    Input:
        microservice_name - str

    Output:
        cpu_usage - int: the average cpu usage by each replica (in milicores)
        None if kube-api-server error
'''


@retry(
    stop=(stop_after_attempt(3) |
          stop_after_delay(6)),
    wait=wait_fixed(1),
    after=callback_each_retry,  # show error
    retry_error_callback=callback_all_retries,
    retry=retry_if_exception_type(ValueError)

)
def get_cpu_usage(microservice_name, current_reps):
    print(f"Getting {microservice_name}'s CPU usage.")
    script = f"kubectl top pods -l app={microservice_name}"
    script_result = execute_kubectl(script)
    if script_result is None:
        return None
    # lines show replicas resource info
    # skip first line/header
    lines = script_result.splitlines()[1:]

    # the number of lines for cpu usage must match the
    # number of available reps, avoid some replicas
    # get deleted between two steps leading to incorrect
    # average cpu usage
    if len(lines) != current_reps or len(lines) == 0:
        raise ValueError("The number of replicas doesn't match.")

    # cpu usage from each replica
    cpu_usage = []
    for rep_info in lines:
        # get cpu usage (0: name, 1: cpu, 2: memory)
        cpu = rep_info.split()[1]
        # remove milicore unit
        cpu = cpu[:-1]
        cpu_usage.append(int(cpu))  # might raise ValueError

    avg_cpu_usage = math.ceil(statistics.mean(cpu_usage))
    return avg_cpu_usage


'''
    Get the number of desired replicas of the specified
    microservice.

    desired_replicas is the number of replicas that the
    deployment must maintain (similar to min_reps?). This
    is specified as `replicas` spec in deployment config
    (default 1)

    Input:
        microservice_name - str

    Output:
        desired_reps - int
        None if server error

'''


def get_desired_reps(microservice_name):
    print(f"Getting {microservice_name}'s desired replicas")
    script = (
            f"kubectl get deployment {microservice_name} "
            "-o=jsonpath='{.spec.replicas}'"
            )
    result = execute_kubectl(script)
    if result is None:
        return None
    return int(result)


'''
    Get the CPU request for each container/pod/replica
    CPU request is CPU resource that the cluster ensure
    for the pod (min CPU)

    Input:
        microservice_name - str

    Ouput:
        cpu_request - int (in milicores)
'''


def get_cpu_request(microservice_name):
    print(f"Getting {microservice_name}'s CPU request.")

    script = (
            f"kubectl get deployment {microservice_name} "
            "-o=jsonpath="
            "'{.spec.template.spec.containers[0].resources.requests.cpu}'"
            )
    result = execute_kubectl(script)
    if result is None:
        return None
    # remove unit, change to int
    cpu_request = int(result[:-1])
    return cpu_request


# entry point for testing
if __name__ == "__main__":
    microservice_name = "adservice"
    #available_reps = get_available_reps(microservice_name)
    #print(available_reps)
    #get_rep_names = f"kubectl get pods -l app={microservice_name}"
    #rep_names = execute_kubectl(get_rep_names)
    #rep_name = rep_names.splitlines()[1].split()[0]
    #print(execute_kubectl(f"kubectl delete pod {rep_name}"))
    #cpu_usage = get_cpu_usage(microservice_name, available_reps)
    #print(cpu_usage)
    #cpu_request = get_cpu_request(microservice_name)
    #print(cpu_request)
    #desired_reps = get_desired_reps(microservice_name)
    #print(desired_reps)
    #print("-----------------------")
    scale_pod = scale(microservice_name, 3, 1)
    print(scale_pod)
