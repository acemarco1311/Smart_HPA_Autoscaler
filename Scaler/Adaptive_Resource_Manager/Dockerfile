# base image
FROM python:3.12.2

# organize container directories
WORKDIR /adaptive_resource_manager/

# install dependencies manually
#TODO: auto detect dependencies
# and add to .txt file
RUN pip install --no-cache-dir grpcio
RUN pip install --no-cache-dir grpcio_tools

# get source code
#TODO: reorganize .proto files
COPY adaptive_resource_manager.proto ./src
COPY adaptive_resource_manager_pb2.py ./src
COPY adaptive_resource_manager_pb2_grpc.py ./src

COPY data_format.py ./src
COPY adaptive_resource_manager.py ./src
COPY server.py ./src

# specify hostname and port in K8s manifests
ENTRYPOINT ["python3", "server.py"]

