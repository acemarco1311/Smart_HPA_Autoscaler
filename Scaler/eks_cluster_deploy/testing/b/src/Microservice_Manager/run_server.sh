#!/usr/bin/env bash
python3 server.py --hostname=test --port=5001 --microservice_name=adservice --min_reps=1 --max_reps=5 --target_cpu_utilization=70

