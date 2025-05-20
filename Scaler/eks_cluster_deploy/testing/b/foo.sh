ms=("cartservice" "checkoutservice" "currencyservice" "frontend" "paymentservice" "redis-cart" "shippingservice" "productcatalogservice")

target_ip=$1

# run a simple load test to benchmark application
# to ensure currencyservice does not die
test_ms() {
    locust -f locustfile.py --host=http://"$target_ip" --headless -u 50 -r 1 --run-time=50
    ms_ok=1
    for name in "${ms[@]}"; do
        pods=$(kubectl get deployment "$name" -o jsonpath='{.status.availableReplicas}')
        echo "$pods"
        if [[ -z "$pods" || "$pods" -lt 1 ]]; then
            ms_ok=0
            kubectl delete deployment "$name"
            sleep 15
            kubectl apply -f manifest/Reduced_Application/"$name".yaml
            sleep 30
        fi
    done
    
    # rerun
    if [[ ms_ok -eq 0 ]]; then
        test_ms
    fi
}

# b problem - default load - one
mkdir result/one_one
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One # B = ASolution + injection
sleep 100 
./run.sh one_one "$1"
sleep 30 # ensure everything is clean


rm -rf result/one_two
mkdir result/one_two
kubectl apply -f manifest/Reduced_Application
sleep 100
kubectl apply -f manifest/Microservice_Manager_One # B = ASolution + injection
sleep 20
./run.sh one_two "$1"
sleep 30 # ensure everything is clean


rm -rf result/one_three
mkdir result/one_three
kubectl apply -f manifest/Reduced_Application
sleep 100
kubectl apply -f manifest/Microservice_Manager_One # B = ASolution + injection
sleep 20
./run.sh one_three "$1"
sleep 30 # ensure everything is clean

rm -rf result/one_four
mkdir result/one_four
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One # B = ASolution + injection
sleep 100
./run.sh one_four "$1"
sleep 30 # ensure everything is clean

rm -rf result/one_five
mkdir result/one_five
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One # B = ASolution + injection
sleep 100
./run.sh one_five "$1"
sleep 30 # ensure everything is clean

# b problem - default load - two
rm -rf result/two_one
mkdir result/two_one
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run.sh two_one "$1"
sleep 30

rm -rf result/two_two
mkdir result/two_two
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run.sh two_two "$1"
sleep 30

rm -rf result/two_three
mkdir result/two_three
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run.sh two_three "$1"
sleep 30

rm -rf result/two_four
mkdir result/two_four
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run.sh two_four "$1"
sleep 30

rm -rf result/two_five
mkdir result/two_five
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run.sh two_five "$1"
sleep 30

# b problem - doublewave load - one
mkdir result/doublewave_one_one
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave.sh doublewave_one_one "$1"
sleep 30

mkdir result/doublewave_one_two
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave.sh doublewave_one_two "$1"
sleep 30


mkdir result/doublewave_one_three
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave.sh doublewave_one_three "$1"
sleep 30

mkdir result/doublewave_one_four
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave.sh doublewave_one_four "$1"
sleep 30

mkdir result/doublewave_one_five
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave.sh doublewave_one_five "$1"
sleep 30

# b problem - doublewave load - two
mkdir result/doublewave_two_one
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave.sh doublewave_two_one "$1"
sleep 30

mkdir result/doublewave_two_two
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave.sh doublewave_two_two "$1"
sleep 30

mkdir result/doublewave_two_three
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave.sh doublewave_two_three "$1"
sleep 30

mkdir result/doublewave_two_four
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave.sh doublewave_two_four "$1"
sleep 30

mkdir result/doublewave_two_five
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave.sh doublewave_two_five "$1"
sleep 30

# b solution - default load - one
mkdir result/bsolution_one_one
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_solution.sh bsolution_one_one "$1"
sleep 30

mkdir result/bsolution_one_two
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_solution.sh bsolution_one_two "$1"
sleep 30

mkdir result/bsolution_one_three
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_solution.sh bsolution_one_three "$1"
sleep 30

mkdir result/bsolution_one_four
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_solution.sh bsolution_one_four "$1"
sleep 30

mkdir result/bsolution_one_five
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_solution.sh bsolution_one_five "$1"
sleep 30

# b solution - default load - two
mkdir result/bsolution_two_one
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_solution.sh bsolution_two_one "$1"
sleep 30

mkdir result/bsolution_two_two
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_solution.sh bsolution_two_two "$1"
sleep 30

mkdir result/bsolution_two_three
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_solution.sh bsolution_two_three "$1"
sleep 30

mkdir result/bsolution_two_four
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_solution.sh bsolution_two_four "$1"
sleep 30

mkdir result/bsolution_two_five
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_solution.sh bsolution_two_five "$1"
sleep 30

# b solution - doublewave load - one
mkdir result/bsolution_doublewave_one_one
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_one_one "$1"
sleep 30

mkdir result/bsolution_doublewave_one_two
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_one_two "$1"
sleep 30

mkdir result/bsolution_doublewave_one_three
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_one_three "$1"
sleep 30


mkdir result/bsolution_doublewave_one_four
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_one_four "$1"
sleep 30

mkdir result/bsolution_doublewave_one_five
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_One
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_one_five "$1"
sleep 30

# b solution - doublewave load - two
mkdir result/bsolution_doublewave_two_one
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_two_one "$1"
sleep 30

mkdir result/bsolution_doublewave_two_two
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_two_two "$1"
sleep 30

mkdir result/bsolution_doublewave_two_three
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_two_three "$1"
sleep 30

mkdir result/bsolution_doublewave_two_four
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_two_four "$1"
sleep 30

mkdir result/bsolution_doublewave_two_five
kubectl apply -f manifest/Reduced_Application
kubectl apply -f manifest/Microservice_Manager_Two
sleep 100
./run_doublewave_solution.sh bsolution_doublewave_two_five "$1"
sleep 30
