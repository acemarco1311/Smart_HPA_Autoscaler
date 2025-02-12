import subprocess

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
    available_reps_script = f"kubectl get deployment \
                            {microservice_name} \
                            -o=jsonpath='{{.status.availableReplicas}}'"

    # execute command with timeout
    try:
        available_reps = subprocess.check_output(available_reps_script.split(),
                                                 stderr=subprocess.STDOUT,
                                                 timeout=1).decode("utf-8")
        # handle None value
        if (available_reps is None):
            raise ValueError
        # strip leading/trailing values from kube-api-server
        available_reps = available_reps.strip().strip('\'').strip('\"')
        print(type(available_reps))
        print(available_reps)
        if (len(available_reps) == 0):
            sum = 0
            # raise error
        # convert string to int if not empty
        available_reps = int(available_reps)
    except subprocess.TimeoutExpired as err:
        print("Timeout")
        # retry again
    except subprocess.CalledProcessError as err:
        print("Error from kube-api-server.")
        # stdout include stderr by subprocess
        err_msg = err.stdout.decode("utf-8")  # convert byte to string
        print(err_msg)
    except ValueError:
        print("Received invalid response from server:")
        print(available_reps)
    else:
        return available_reps


# entry point for testing
if __name__ == "__main__":
    get_available_reps("adservice")
