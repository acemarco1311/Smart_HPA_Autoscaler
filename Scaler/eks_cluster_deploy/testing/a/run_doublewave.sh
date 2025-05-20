#!/usr/bin/env bash

# arguments
# dir log name: if one -> save one.log into result/one/
# save knowledge base in result/one/kb
#
# target ip address


# deploy MCA
kubectl apply -f manifest/microservice-capacity-analyzer.yaml

# ensure the deployment has been ready
kubectl wait --for=condition=Available deployment/microservice-capacity-analyzer --timeout=120s
sleep 90 # wait for leader to be chosen


# get pod id of microservice capacity 
script=$(kubectl get pods -l app=microservice-capacity-analyzer,role=leader)
# get pod id
result=$(echo -e "$script" | awk 'NR==2 {print $1}')

# get log from MCA pod
# store into result/$1 
path="result/$1/$1.log"
kubectl logs -f "$result" >> "$path" &

# run load test
locust_path="result/$1/$1"
target_ip=$2
locust -f locustfile_custom.py --host=http://"$target_ip" --headless 2>&1 --csv="$locust_path" --csv-full-history

sleep 120
kubectl delete deployment microservice-capacity-analyzer

# get pod id from productcatalogserver manager
product_script=$(kubectl get pods -l app=productcatalogservice-manager,role=leader)
productcatalog_mm_id=$(echo -e "$product_script" | awk 'NR==2  {print $1}')

# copy Microservice Manager knowledge base for result analysis
# save efs knowledge_base/ to result/$1/kb dir
kubectl cp default/"$productcatalog_mm_id":knowledge_base/ result/"$1"/kb/


# clean up knowledge base and state of this experiment
ms=("cartservice" "checkoutservice" "currencyservice" "frontend" "paymentservice" "redis-cart" "shippingservice" "productcatalogservice")
for name in "${ms[@]}"; do
    kubectl exec -it "$productcatalog_mm_id" -- rm knowledge_base/"$name".txt
    kubectl exec -it "$productcatalog_mm_id" -- rm state/"$name".txt
    kubectl delete deployment "$name"
    kubectl delete deployment "$name"-manager
    kubectl delete service "$name"
    kubectl delete service "$name"-manager
done






