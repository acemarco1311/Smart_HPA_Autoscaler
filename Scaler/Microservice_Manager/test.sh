#!/usr/bin/env bash

# delete pod then check
# this get "''" from kube-api-server
# smart hpa manage '' -> empty string
./reset_cluster_state.sh
kubectl delete pod -l app=adservice
python3 subroutine.py

# delete deployment, restart deployment then check
# should get empty string from the server.
# similar to case 1
./reset_cluster_state.sh
kubectl delete deployment adservice
./reset_cluster_state.sh
python3 subroutine.py

