# base image
FROM python:3.12.2

# organize container directories
WORKDIR /adaptive_resource_manager

# install dependencies manually
#TODO: auto detect dependencies
# and add to .txt file
RUN pip install --no-cache-dir grpcio
RUN pip install --no-cache-dir grpcio_tools

# get source code
#TODO: reorganize .proto files

# dot represent the relative path to WORKDIR
# no need first dot for build context, assume
# current directory

# if copy each file, must define the dest file name
COPY adaptive_resource_manager.proto ./src/adaptive_resource_manager.proto
COPY adaptive_resource_manager_pb2.py ./src/adaptive_resource_manager_pb2.py
COPY adaptive_resource_manager_pb2_grpc.py ./src/adaptive_resource_manager_pb2_grpc.py

COPY data_format.py ./src/data_format.py
COPY adaptive_resource_manager.py ./src/adaptive_resource_manager.py
COPY server.py ./src/server.py

# specify hostname and port in K8s manifests
ENTRYPOINT ["python3", "./src/server.py"]

