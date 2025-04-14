#!/bin/bash

# Ensure correct usage
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <pod_name>"
    exit 1
fi

POD_NAME=$1
SERVICES=(
    "cartservice"
    "frontend"
    "checkoutservice"
    "mca_fail_calls"
    "currencyservice"
    "paymentservice"
    "productcatalogservice"
    "redis-cart"
    "shippingservice"
)

for service in "${SERVICES[@]}"; do
    echo "Removing ${service}.txt from pod $POD_NAME"
    kubectl exec -it "$POD_NAME" -- rm "state/${service}.txt"
done
