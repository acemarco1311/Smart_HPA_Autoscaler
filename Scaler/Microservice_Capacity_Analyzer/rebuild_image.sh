#!/usr/bin/env bash

# rebuild image
docker build -t acemarco/microservice-capacity-analyzer:latest .  # specify build context

# get the image id of the old version
dangling_id=$(docker images acemarco/microservice-capacity-analyzer -f dangling=true | awk '{print $3}' | sed -n '2p')

# delete old version
docker rmi -f "$dangling_id"

# push to registry
docker push acemarco/microservice-capacity-analyzer
