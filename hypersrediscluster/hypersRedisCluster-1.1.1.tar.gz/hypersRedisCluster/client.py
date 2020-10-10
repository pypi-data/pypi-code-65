from django_redis.client import DefaultClient
from hypersRedisCluster.connection import ConnectionFactory


class RedisClusterClient(DefaultClient):
    """redis集群客户端"""

    def __init__(self, server, params, backend):
        super(RedisClusterClient, self).__init__(server, params, backend)
        self._options = params.get("OPTIONS", {})
        self.connection_factory = ConnectionFactory(options=self._options)
        self.client = None

    def get_client(self, write=True, tried=(), show_index=False):
        if self.client is None:
            self.client = self.connect()
        if show_index:
            return self.client, 0
        else:
            return self.client

    def connect(self):
        return self.connection_factory.connect(self._server)
