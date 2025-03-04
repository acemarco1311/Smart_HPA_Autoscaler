#!/usr/bin/env bash

# rebuild image
docker build -t acemarco/adaptive-resource-manager:latest .  # specify build context (local dir)

# get the image id of the old version with tag = none
dangling_id=$(docker images acemarco/adaptive-resource-manager -f dangling=true | awk '{print $3}' | sed -n '2p')

# delete old version
docker rmi -f "$dangling_id"

# push to registry
docker push acemarco/adaptive-resource-manager
