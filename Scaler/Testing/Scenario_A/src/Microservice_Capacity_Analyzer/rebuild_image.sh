#!/usr/bin/env bash

# delete deployment on cluster
kubectl delete deployment microservice-capacity-analyzer

# wait for termination
kubectl wait --for=delete deployment/"microservice-capacity-analyzer" --timeout=60s

# rebuild image
docker build -t acemarco/microservice-capacity-analyzer:A .  # specify build context

# get the image id of the old version
dangling_id=$(docker images acemarco/microservice-capacity-analyzer -f dangling=true | awk '{print $3}' | sed -n '2p')


# delete old version
docker rmi -f "$dangling_id"

# push to registry
docker push acemarco/microservice-capacity-analyzer:A


