#!/usr/bin/env bash
# server side Adaptive Resource Manager
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. adaptive_resource_manager.proto

# client side Microservice Capacity Analyzer
python3 -m grpc_tools.protoc -I. --python_out=../Microservice_Capacity_Analyzer --grpc_python_out=../Microservice_Capacity_Analyzer adaptive_resource_manager.proto

