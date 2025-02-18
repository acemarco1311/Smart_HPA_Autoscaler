#!/usr/bin/env bash


# delete pod then check (in main ground)
echo "TEST 1"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete pod -l app=adservice
python3 subroutine.py # get available reps of adservice
# -> this return a string '' -> converted to empty string
echo "---------------------------------"


# delete pod (in background) then check
echo "TEST 2"
./reset_cluster_state.sh > /dev/null
kubectl delete pod -l app=adservice &
python3 subroutine.py
echo "---------------------------------"
# -> no difference to test 1

# delete deployment then check
echo "TEST 3"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete deployment adservice
python3 subroutine.py 
echo "---------------------------------"
# -> server returns error NotFound

# delete deployment (in background) then check 
echo "TEST 4"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete deployment adservice &
python3 subroutine.py
echo "---------------------------------"
# -> server returns error NotFound


# delete deployment, then restart deployment, then check
echo "TEST 5"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete deployment adservice
echo "Restart adservice deployment"
./reset_cluster_state.sh > /dev/null
python3 subroutine.py
echo "---------------------------------"
# -> return a string '' -> converted to empty string

# delete deployment, then restart deployment in background, then check
echo "TEST 6"
./reset_cluster_state.sh > /dev/null  # hide output
kubectl delete deployment adservice
echo "Restart adservice deployment"
./reset_cluster_state.sh > /dev/null &
python3 subroutine.py
echo "---------------------------------"
# -> Error NotFound: the kube-api needs time to start the deployment.

# what if delete service?
