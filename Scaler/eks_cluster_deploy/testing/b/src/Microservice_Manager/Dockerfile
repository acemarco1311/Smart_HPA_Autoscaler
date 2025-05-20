# base image
FROM python:3.12.2

ENV PYTHONUNBUFFERED=1
# organize container's directories
WORKDIR /microservice_manager

# install dependencies manually
#TODO: auto detect dependencies and update 
# in dependencies.txt

# no cache use -> run latest version
RUN pip install --no-cache-dir grpcio
RUN pip install --no-cache-dir grpcio-tools
RUN pip install --no-cache-dir grpcio-health-checking
RUN pip install --no-cache-dir tenacity
RUN pip install --no-cache-dir kubernetes
RUN pip install --no-cache-dir pyyaml


# copy source code to microservice_manager/src
#TODO: reorganize protofiles
COPY microservice_manager.proto ./src/microservice_manager.proto
COPY microservice_manager_pb2.py ./src/microservice_manager_pb2.py
COPY microservice_manager_pb2_grpc.py ./src/microservice_manager_pb2_grpc.py


COPY data_format.py ./src/data_format.py
COPY subroutine.py ./src/subroutine.py
COPY microservice_manager.py ./src/microservice_manager.py
COPY server.py ./src/server.py


# set up to run `kubectl` command
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN mv kubectl /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl

# run with args from K8s deployment `args`
# for different instances of MS Manager
ENTRYPOINT ["python3", "./src/server.py"]
