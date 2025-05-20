kubectl delete deployment microservice-capacity-analyzer
# get pod id from productcatalogserver manager
product_script=$(kubectl get pods -l app=productcatalogservice-manager,role=leader)
productcatalog_mm_id=$(echo -e "$product_script" | awk 'NR==2  {print $1}')
# clean up knowledge base and state of this experiment
ms=("cartservice" "checkoutservice" "currencyservice" "frontend" "paymentservice" "redis-cart" "shippingservice" "productcatalogservice")
for name in "${ms[@]}"; do
    echo "Delete KB"
    kubectl exec -it "$productcatalog_mm_id" -- rm knowledge_base/"$name".txt
    echo "Delete state"
    kubectl exec -it "$productcatalog_mm_id" -- rm state/"$name".txt
    echo "Delete ms deployment"
    kubectl delete deployment "$name"
    echo "Delete ms manager deployment"
    kubectl delete deployment "$name"-manager
    echo "Delete ms service"
    kubectl delete service "$name"
    echo "Delete ms manager service"
    kubectl delete service "$name"-manager
done

