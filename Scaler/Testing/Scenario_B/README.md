Run load test with Smart HPA on cluster.
Delete all pods of frontend-manager every 30 seconds.
Microservice Managers restore their state during init.

Prerequisite:
- Run reduced benchmark application: 8.
- Run Adaptive Resource Manager.
- ServiceAccount god has been deployed.

Number of microservices = 8

one experiments:
Total runtime: 500s

Microservice resource allocate:
- min_rep = 1
- max_rep = 3
- request_cpu = 15m
- request_memory = 120Mi
- limit_cpu = 20m
- limit_memory = 200Mi
- target_cpu_utilization = 80%
-> max cpu allowed = 0.8 * 15 = 12m

No replication of MM, MCA.
Each MM, MCA has: 150m, 100Mi


Locust config:
- total_runtime = 500
- max_user = 150
- spawn_rate = 0.7
-> No incorrect


two, three experiments:  
Total runtime: 600s

Microservice resource allocate:
- min_rep = 1
- max_rep = 3
- request_cpu = 15m
- request_memory = 120Mi
- limit_cpu = 20m
- limit_memory = 200Mi
- target_cpu_utilization = 80%
-> max cpu allowed = 0.8 * 15 = 12m

No replication of MM, MCA.
Each MM, MCA has: 150m, 100Mi


Locust config:
- total_runtime = 600
- max_user = 200
- spawn_rate = 0.7

-> Incorrect, maybe the manager dies after update running state and before update disk state.


=> Other pods dies unexpectedly: increase liveness/readiness deadline, increase resource limit to avoid restarting during runtime because of high work load.
