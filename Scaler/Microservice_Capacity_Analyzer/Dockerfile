FROM python:3.12.2

WORKDIR /microservice_capacity_analyzer

RUN pip install --no-cache-dir grpcio
RUN pip install --no-cache-dir grpcio-tools
RUN pip install --no-cache-dir tenacity

# grpc runtime files
COPY microservice_manager_pb2.py ./src/microservice_manager_pb2.py
COPY microservice_manager_pb2_grpc.py ./src/microservice_manager_pb2_grpc.py
COPY adaptive_resource_manager_pb2.py ./src/adaptive_resource_manager_pb2.py
COPY adaptive_resource_manager_pb2_grpc.py ./src/adaptive_resource_manager_pb2_grpc.py

# core files
COPY data_format.py ./src/data_format.py
COPY subroutine.py ./src/subroutine.py
COPY microservice_capacity_analyzer.py ./src/microservice_capacity_analyzer.py

# run directly as it's not server
CMD ["python3", "./src/microservice_capacity_analyzer.py"]
