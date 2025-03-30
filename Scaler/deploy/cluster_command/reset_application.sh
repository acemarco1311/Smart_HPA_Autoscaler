#!/usr/bin/env bash
./delete_application.sh
cd "/mnt/c/Users/acema/Project/Smart_HPA/src/Smart_HPA_Autoscaler/Scaler/deploy/manifest/Reduced_Application/"
kubectl apply -f .
