import subprocess  # execute kubectl command
from tenacity import retry, stop_after_attempt, stop_after_delay
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


# show error on each failed retry
def callback_each_retry(retry_state):
    if retry_state.outcome.failed:
        err = retry_state.outcome.exception()
        # either not numerical or empty string
        # exception raised when converting str -> int
        if isinstance(err, ValueError):
            print("Error response is not a numerical string")
            print(retry_state.outcome.exception())
        # error from server
        elif isinstance(err, subprocess.CalledProcessError):
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


# retry on exeception raised
@retry(
    # 3 attempts, total execution time = 6s
    stop=(stop_after_attempt(3) |
          stop_after_delay(6)),
    # wait 1 second between retries
    wait=wait_fixed(1),
    after=callback_each_retry,
    retry_error_callback=callback_all_retries
    )
def get_available_reps(microservice_name):
    available_reps_script = f"kubectl get deployment \
                            {microservice_name} \
                            -o=jsonpath='{{.status.availableReplicas}}'"

    available_reps = subprocess.check_output(available_reps_script.split(),
                                             stderr=subprocess.STDOUT,
                                             timeout=1).decode("utf-8")
    available_reps = available_reps.strip()\
                                   .strip('\'')\
                                   .strip('\"')
    return int(available_reps)


# entry point for testing
if __name__ == "__main__":
    print(get_available_reps("adservice"))
