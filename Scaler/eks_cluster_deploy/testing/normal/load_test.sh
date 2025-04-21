#!/usr/bin/env bash
target_ip=$1
locust_path=$2
locust -f locustfile.py --host="http://$target_ip" --headless -u 200 -r 1 --run-time=600 2>&1 --csv="$locust_path" --csv-full-history
