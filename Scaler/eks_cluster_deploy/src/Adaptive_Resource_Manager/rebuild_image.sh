#!/usr/bin/env bash
# login into Amazon ECR
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 843300524918.dkr.ecr.ap-southeast-2.amazonaws.com

# rebuild image
docker build -t 843300524918.dkr.ecr.ap-southeast-2.amazonaws.com/smart-hpa/adaptive-resource-manager:latest .

# get the image id of the old version with tag = none
dangling_id=$(docker images 843300524918.dkr.ecr.ap-southeast-2.amazonaws.com/smart-hpa/adaptive-resource-manager -f dangling=true | awk '{print $3}' | sed -n '2p')

# delete old version
docker rmi -f "$dangling_id"

# push to registry
docker push 843300524918.dkr.ecr.ap-southeast-2.amazonaws.com/smart-hpa/adaptive-resource-manager
