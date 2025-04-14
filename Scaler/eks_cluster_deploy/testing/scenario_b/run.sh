#!/usr/bin/env bash


# deploy MCA
kubectl apply -f manifest/microservice-capacity-analyzer.yaml

# ensure the deployment has been ready
kubectl wait --for=condition=Available deployment/microservice-capacity-analyzer --timeout=120s


# get pod id of microservice capacity 
script=$(kubectl get pods -l app=microservice-capacity-analyzer)
# get pod id
result=$(echo -e "$script" | awk 'NR==2 {print $1}')

path="result/$1.log"
kubectl logs -f "$result" >> "$path" &

# run load test
locust_path="result/$1"
target_ip=$2
locust -f locustfile.py --host=http://"$target_ip" --headless -u 200 -r 1 --run-time=600 2>&1 --csv="$locust_path" --csv-full-history



