#!/usr/bin/env bash


# delete pod then check (in main ground)
echo "Reset the cluster state to start test 1"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete pod -l app=adservice
python3 subroutine.py # get available reps of adservice
# -> this return a string '' -> converted to empty string


# delete pod (in background) then check
echo "Reset the cluster state to start test 2"
./reset_cluster_state.sh > /dev/null
kubectl delete pod -l app=adservice &
python3 subroutine.py
# -> no difference to test 1

# delete deployment then check
echo "Reset the cluster state to start test 3"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete deployment adservice
python3 subroutine.py 
# -> server returns error NotFound

# delete deployment (in background) then check 
echo "Reset the cluster state to start test 4"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete deployment adservice &
python3 subroutine.py
# -> server returns error NotFound


# delete deployment, then restart deployment, then check
echo "Reset the cluster state to start test 5"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete deployment adservice
echo "Restart adservice deployment"
./reset_cluster_state.sh > /dev/null
python3 subroutine.py
# -> return a string '' -> converted to empty string

# delete deployment, then restart deployment in background, then check
echo "Reset the cluster state to start test 6"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete deployment adservice
echo "Restart adservice deployment"
./reset_cluster_state.sh > /dev/null &
python3 subroutine.py
# -> Error NotFound: the kube-api needs time to start the deployment.
