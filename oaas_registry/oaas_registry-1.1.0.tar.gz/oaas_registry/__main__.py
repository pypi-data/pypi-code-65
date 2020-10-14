# we import these two, to expose the oaas-registry service
import oaas

from oaas_registry.oaas_grpc_registry import noop

from oaas_grpc.client.client import OaasGrpcClient
from oaas_grpc.server import OaasGrpcServer


noop()  # we have this function call so the optimize
# import keeps the registry definition


def main():
    oaas.register_server_provider(OaasGrpcServer())
    oaas.register_client_provider(OaasGrpcClient())

    oaas.serve()
    oaas.join()


if __name__ == "__main__":
    main()
