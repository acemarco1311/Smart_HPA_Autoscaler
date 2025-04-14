#!/bin/bash
# update kubectl context to connect to cluster
# requirements: create cluster access point.
# turn on docker desktop
aws eks update-kubeconfig --region ap-southeast-2 --name smart-hpa

# scale down addon deployments
kubectl scale deployment coredns -n kube-system --replicas=1
kubectl scale deployment metrics-server -n kube-system --replicas=1
kubectl scale deployment efs-csi-controller -n kube-system --replicas=1

# deploy efs
# requirements: update manifest/efs.yaml file system id
./deploy_efs.sh

kubectl apply -f ../manifest/god-manifests.yaml

# create cluster role binding for Managers
# to run kubectl command
kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts

