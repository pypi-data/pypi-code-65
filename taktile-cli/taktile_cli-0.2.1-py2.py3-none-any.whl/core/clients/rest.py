from tktl.core.clients import Client


class RestClient(Client):

    TRANSPORT = "rest"

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def predict(self):
        pass

    def list_endpoints(self):
        pass

    def list_deployments(self):
        pass

    def get_sample_data(self):
        pass

    def get_schema(self):
        pass
