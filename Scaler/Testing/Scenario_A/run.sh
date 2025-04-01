#!/usr/bin/env bash


# deploy microservice managers
cd manifest/Microservice_Manager
kubectl apply -f .

sleep 20 # wait for all ms manager run

cd ..
# deploy MCA
kubectl apply -f microservice-capacity-analyzer.yaml

# ensure the deployment has been ready
kubectl wait --for=condition=Available deployment/microservice-capacity-analyzer --timeout=120s

# get pod id of microservice capacity 
script=$(kubectl get pods -l app=microservice-capacity-analyzer)
# get pod id
result=$(echo -e "$script" | awk 'NR==2 {print $1}')

cd ../
path="result/$1.log"
kubectl logs -f "$result" >> "$path" &

# run load test
locust_path="result/$1"
locust -f locustfile.py --host=http://localhost --headless -u 150 -r 0.7 --run-time=600 2>&1 --csv="$locust_path" --csv-full-history



