#!/usr/bin/env bash
kubectl apply -f "/mnt/c/Users/acema/Project/Smart_HPA/src/Smart_HPA_Autoscaler/Application/release/kubernetes-manifests.yaml" 
sleep 5
kubectl delete deployment loadgenerator
