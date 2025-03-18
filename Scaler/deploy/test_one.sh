#!/usr/bin/env bash

# delete deployment
kubectl delete deployment microservice-capacity-analyzer

sleep 20 
# restart
kubectl apply -f microservice-capacity-analyzer.yaml



# -f allow stream output
sleep 20
# get pod id of microservice capacity 
script=$(kubectl get pods -l app=microservice-capacity-analyzer)
# get pod id
result=$(echo -e "$script" | awk 'NR==2 {print $1}')


# reset output log
rm test.log
# set log stream to local file
kubectl logs -f "$result" >> test.log &


# run load test
cd ../Load_Script
# run locust load test, 2>&1 print error to terminal merge 2 streams into stdout
locust -f locustfile.py --host=http://localhost --headless -u 100 -r 2 --run-time=110 2>&1
