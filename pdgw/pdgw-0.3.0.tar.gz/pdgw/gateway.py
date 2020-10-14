import urllib.parse

from .client import Client


class Node:

    def __init__(self, name: str, class_: str, instances: int, config: dict):
        self.name = name
        self.class_ = class_
        self.instances = instances
        self.config = config
        self._next_node = None

    def __rshift__(self, other: "Node") -> "Node":
        print(f"{self.name} >> {other.name}")
        self._next_node = other
        self.config["forward"] = other.name
        return other

    def _as_config(self):
        config = {
            "instances": self.instances
        }
        if self.class_:
            config["class"] = self.class_
        config["config"] = self.config
        return config


class Gateway:

    def __init__(self, addr="localhost:9000", *, org_id="default", app_id="default", api_key: str):
        parsed_addr = urllib.parse.urlparse(addr)
        self.org_id = org_id
        self.app_id = app_id
        self.api_key = api_key
        self.beacon_host = parsed_addr.hostname
        self.beacon_port = parsed_addr.port
        self.start_nodes = []

    @classmethod
    def _beacon_addr(cls, addr: str) -> (str, int):
        for proto in ["https://", "http://"]:
            if addr.startswith(proto):
                addr = addr[len(proto):]
                break
        if addr.find("://") >= 0:
            raise RuntimeError(f"Invalid beacon address: {addr}")
        try:
            if ":" in addr:
                host, port = addr.split(":", 2)
                host = host or "localhost"
                port = int(port)
                return host, port
            host = addr
            return host, 9000
        except (ValueError, TypeError):
            raise RuntimeError(f"Invalid beacon address: {addr}")

    def node(self, name, class_="", instances=1, **config) -> Node:
        node = Node(name, class_, instances, config)
        self.start_nodes.append(node)
        return node

    def update(self):
        pass

    def client(self) -> Client:
        return Client(
            org_id=self.org_id,
            app_id=self.app_id,
            api_key=self.api_key,
            beacon_host=self.beacon_host,
            beacon_port=self.beacon_port
        )

    def _config(self):
        nodes = {}
        for start_node in self.start_nodes:
            node = start_node
            while node:
                nodes[node.name] = node._as_config()
                node = node._next_node
        return {
            "nodes": nodes,
        }

    def __enter__(self):
        print("CTX ENTER")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("CTX EXIT")
        print(f"config: {self._config()}")
        # self.update()
