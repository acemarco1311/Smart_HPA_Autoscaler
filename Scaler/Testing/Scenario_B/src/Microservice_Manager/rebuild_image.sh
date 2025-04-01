#!/usr/bin/env bash

# rebuild image
docker build -t acemarco/microservice-manager-base:B .  # specify build context (local dir)

# get the image id of the old version with tag = none
dangling_id=$(docker images acemarco/microservice-manager-base -f dangling=true | awk '{print $3}' | sed -n '2p')

# delete old version
docker rmi -f "$dangling_id"

# push to registry
docker push acemarco/microservice-manager-base:B
