Run load test with Smart HPA on cluster.
Delete all pods of frontend-manager every 30 seconds.

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

-> deleting frontend-manager by a new thread has no effect?


two experiments:  
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
- total_runtime = 500
- max_user = 150
- spawn_rate = 0.7

-> deleting frontend-manager by a new thread has no effect?

=> deleting frontend-manager by a new thread DOES HAS EFFECT.
=> just because the I/O and/or the delay in executing delete.
=> that why not show "Delete" in the first incorrect but
=> in fact, it recovered and then respond with user-defined
=> but not marked as failed.
=> check one.log 1352 and two.log 1803

=> other pod dies (not setup) -> increase readiness/liveness probe
                              -> increase resource limit avoid restarting during runtime
