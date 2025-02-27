#!/usr/bin/env bash
# generate code for Microservice Manager server
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. microservice_manager.proto

# generate code for Microservice Capacity Analyzer as client
#python3 -m grpc_tools.protoc -I. --python_out=../Microservice_Capacity_Analyzer --grpc_python_out=../Microservice_Capacity_Analyzer microservice_manager.proto
python3 -m grpc_tools.protoc -I. --python_out=../Test --grpc_python_out=../Test microservice_manager.proto
