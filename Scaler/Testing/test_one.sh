#!/usr/bin/env bash


# restart capacity analyzer
kubectl delete deployment microservice-capacity-analyzer
# ensure the deployment has been deleted
kubectl wait --for=delete deployment/microservice-capacity-analyzer --timeout=30s
# deploy
kubectl apply -f ../deploy/microservice-capacity-analyzer.yaml
# ensure the deployment has been ready
kubectl wait --for=condition=Available deployment/microservice-capacity-analyzer --timeout=120s



# get pod id of microservice capacity 
script=$(kubectl get pods -l app=microservice-capacity-analyzer)
# get pod id
result=$(echo -e "$script" | awk 'NR==2 {print $1}')


# reset output log
rm test_one.log
# set log stream to local file
# -f allow stream output
kubectl logs -f "$result" >> test_one.log &


# run load test
# run locust load test, 2>&1 print error to terminal merge 2 streams into stdout
locust -f ../Load_Script/locustfile.py --host=http://localhost --headless -u 100 -r 0.5 --run-time=300 2>&1 --csv=test_one_locust --csv-full-history
