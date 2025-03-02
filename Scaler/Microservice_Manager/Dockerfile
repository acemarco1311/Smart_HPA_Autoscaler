# base image
FROM python:3.12.2

# organize container's directories
WORKDIR /microservice_manager/

# install dependencies manually
#TODO: auto detect dependencies and update 
# in dependencies.txt

# no cache use -> run latest version
RUN pip install --no-cache-dir grpcio
RUN pip install --no-cache-dir grpcio-tools
RUN pip install --no-cache-dir tenacity


# copy source code to microservice_manager/src
#TODO: reorganize protofiles
COPY microservice_manager.proto ./src
COPY microservice_manager_pb2.py ./src
COPY microservice_manager_pb2_grpc.py ./src


COPY data_format.py ./src
COPY subroutine.py ./src
COPY microservice_manager.py ./src
COPY server.py ./src


# run with args from K8s deployment `args`
# for different instances of MS Manager
ENTRYPOINT ["python3", "server.py"]
