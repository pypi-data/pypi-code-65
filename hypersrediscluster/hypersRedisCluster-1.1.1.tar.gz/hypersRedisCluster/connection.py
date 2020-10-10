from urllib.parse import unquote, urlparse

from rediscluster import RedisCluster


class ConnectionFactory(object):
    def __init__(self, options):
        self.options = options
        self.redis_client_cls_kwargs = options.get("REDIS_CLIENT_KWARGS", {})

    def make_connection_params_from_url(self, url, decode_components=False):
        """
        参数扩展的代码
        """
        url = urlparse(url)
        params = {}
        if decode_components:
            password = unquote(url.password) if url.password else None
            hostname = unquote(url.hostname) if url.hostname else None
            port = int(url.port or 7000)
        else:
            password = url.password or None
            hostname = url.hostname
            port = int(url.port or 7000)
        params.update(
            {
                "startup_nodes": [{"host": hostname, "port": port}],
                "decode_responses": False,
            }
        )

        if password:
            params.update(password=password)

        if url.scheme == "rediss":
            self.redis_client_cls_kwargs.update(
                {"ssl": True, "ssl_cert_reqs": None}
            )
        return params

    def make_connection_params(self, url_list):
        """
        参数扩展的代码
        """
        if isinstance(url_list[0], str):
            params = self.make_connection_params_from_url(url_list[0])
        else:
            params = dict(startup_nodes=url_list, decode_responses=False)
        password = self.options.get("PASSWORD", None)
        if password:
            params.update(password=password)
        return params

    def connect(self, url_list):
        """
        连接 rediscluster客户端
        """
        params = self.make_connection_params(url_list)
        connection = self.get_connection(params)
        return connection

    def get_connection(self, params):
        return RedisCluster(**params, **self.redis_client_cls_kwargs)
