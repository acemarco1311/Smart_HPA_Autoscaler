# get pod id from productcatalogserver manager
product_script=$(kubectl get pods -l app=productcatalogservice-manager)
productcatalog_mm_id=$(echo -e "$product_script" | awk 'NR==2  {print $1}')

ms_array=("cartservice" "checkoutservice" "frontend" "paymentservice" "productcatalogservice" "redis-cart" "shippingservice")
for ms in "${ms_array[@]}"; do
    kubectl exec -it "$productcatalog_mm_id" -- cat "knowledge_base/$ms.txt" > result/"$1"/kb/"$ms".txt
done
