#!/usr/bin/env bash


cd "/mnt/c/Users/acema/Project/Smart_HPA/src/Smart_HPA_Autoscaler/Scaler/deploy/manifest/"
# create service account to run kubectl command within cluster
kubectl apply -f god-manifests.yaml
# create persistent volume for shared state storage
kubectl apply -f nfs.yaml
kubectl apply -f adaptive-resource-manager.yaml

cd Microservice_Manager
kubectl apply -f .
