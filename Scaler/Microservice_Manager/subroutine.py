import math
import statistics
import subprocess  # execute kubectl command
from tenacity import retry, stop_after_attempt, stop_after_delay
from tenacity import retry_if_result
from tenacity import wait_fixed
from tenacity import after

'''
    Validate user-defined arguments for microservice resource

    Input:
        max_reps - Int: number of max replicas
        min_reps - Int: number of min replicas
        target_cpu_utilization - Float: average cpu utilization for scaling

    Output:
        raise Error if max_reps/min_reps <= 0 or
        max_reps < min_reps or invalid CPU utilization
'''


def validate_argument(max_reps, min_reps, target_cpu_utilization):
    if (max_reps <= 0 or min_reps <= 0):
        raise ValueError("Invalid number of replicas.")
    if (max_reps < min_reps):
        raise ValueError("Invalid number of replicas.")
    if (target_cpu_utilization <= 0 or target_cpu_utilization > 100):
        raise ValueError("Invalid target CPU utilization.")


def callback_each_retry(retry_state):
    if retry_state.outcome.failed:
        err = retry_state.outcome.exception()
        # error from server
        if isinstance(err, subprocess.CalledProcessError):
            print("Received error from kube-api-server")
            print(err.stdout.decode("utf-8"))
        # timeout error
        elif isinstance(err, subprocess.TimeoutExpired):
            print("Exceed 1 second timeout")
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
    script_result = subprocess.check_output(script.split(),
                                            stderr=subprocess.STDOUT,
                                            timeout=1).decode("utf-8")
    # empty string from server might become string "''"
    # when decode from byte to str type
    script_result = script_result.strip().strip('"').strip("'")
    if len(script_result) == 0:
        raise ValueError("Received an empty result from kube-apiserver.")
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
    available_reps_script = f"kubectl get deployment \
                              {microservice_name} \
                              -o=jsonpath='{{.status.availableReplicas}}'"
    available_reps = execute_kubectl(available_reps_script)
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
'''


def get_cpu_usage(microservice_name, current_reps):
    print(f"Getting {microservice_name}'s CPU usage.")
    script = f"kubectl top pods -l app={microservice_name}"
    script_result = execute_kubectl(script)
    if script_result is None:
        return None
    # lines show replicas resource info
    # skip first line/header
    lines = script_result.splitlines()[1:]
    # --> ERROR when only 1 line

    # cross check if info from ALL reps has been collected
    if lines != current_reps:
        raise ValueError("")

    # cpu usage from each replica
    cpu_usage = []
    for rep_info in lines:
        # get cpu usage (0: name, 1: cpu, 2: memory)
        cpu = rep_info.split()[1]
        # remove milicore unit
        cpu = cpu[:-1]
        cpu_usage.append(int(cpu))

    avg_cpu_usage = math.ceil(statistics.mean(cpu_usage))
    return avg_cpu_usage


# entry point for testing
if __name__ == "__main__":
    print(get_available_reps("adservice"))
