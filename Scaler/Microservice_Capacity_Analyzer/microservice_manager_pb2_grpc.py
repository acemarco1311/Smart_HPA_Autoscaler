# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import microservice_manager_pb2 as microservice__manager__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in microservice_manager_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MicroserviceManagerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ExtractResourceData = channel.unary_unary(
                '/microservice_manager.MicroserviceManager/ExtractResourceData',
                request_serializer=microservice__manager__pb2.ResourceDataRequest.SerializeToString,
                response_deserializer=microservice__manager__pb2.ResourceData.FromString,
                _registered_method=True)
        self.ExecuteScaling = channel.unary_unary(
                '/microservice_manager.MicroserviceManager/ExecuteScaling',
                request_serializer=microservice__manager__pb2.ARMDecision.SerializeToString,
                response_deserializer=microservice__manager__pb2.ScalingStatus.FromString,
                _registered_method=True)
        self.GetMaxReps = channel.unary_unary(
                '/microservice_manager.MicroserviceManager/GetMaxReps',
                request_serializer=microservice__manager__pb2.MaxRepRequest.SerializeToString,
                response_deserializer=microservice__manager__pb2.MaxRepResponse.FromString,
                _registered_method=True)


class MicroserviceManagerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ExtractResourceData(self, request, context):
        """call to get resource data
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecuteScaling(self, request, context):
        """execute scaling instruction
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMaxReps(self, request, context):
        """get the current updated max reps
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MicroserviceManagerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ExtractResourceData': grpc.unary_unary_rpc_method_handler(
                    servicer.ExtractResourceData,
                    request_deserializer=microservice__manager__pb2.ResourceDataRequest.FromString,
                    response_serializer=microservice__manager__pb2.ResourceData.SerializeToString,
            ),
            'ExecuteScaling': grpc.unary_unary_rpc_method_handler(
                    servicer.ExecuteScaling,
                    request_deserializer=microservice__manager__pb2.ARMDecision.FromString,
                    response_serializer=microservice__manager__pb2.ScalingStatus.SerializeToString,
            ),
            'GetMaxReps': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMaxReps,
                    request_deserializer=microservice__manager__pb2.MaxRepRequest.FromString,
                    response_serializer=microservice__manager__pb2.MaxRepResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'microservice_manager.MicroserviceManager', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('microservice_manager.MicroserviceManager', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MicroserviceManager(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ExtractResourceData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/microservice_manager.MicroserviceManager/ExtractResourceData',
            microservice__manager__pb2.ResourceDataRequest.SerializeToString,
            microservice__manager__pb2.ResourceData.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ExecuteScaling(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/microservice_manager.MicroserviceManager/ExecuteScaling',
            microservice__manager__pb2.ARMDecision.SerializeToString,
            microservice__manager__pb2.ScalingStatus.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetMaxReps(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/microservice_manager.MicroserviceManager/GetMaxReps',
            microservice__manager__pb2.MaxRepRequest.SerializeToString,
            microservice__manager__pb2.MaxRepResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
