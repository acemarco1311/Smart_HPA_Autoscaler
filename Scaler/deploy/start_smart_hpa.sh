#!/usr/bin/env bash

cd "/mnt/c/Users/acema/Project/Smart_HPA/src/Smart_HPA_Autoscaler/Scaler/deploy/Microservice_Manager"
kubectl apply -f .

cd ..
kubectl apply -f adaptive-resource-manager.yaml

#sleep 45
#
#kubectl apply -f microservice-capacity-analyzer.yaml
