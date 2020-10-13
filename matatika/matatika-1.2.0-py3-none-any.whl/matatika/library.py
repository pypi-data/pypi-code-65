'''
library module
'''

from matatika.catalog import Catalog

class MatatikaClient():
    '''Class to handle client context'''

    def __init__(self, auth_token, endpoint_url, workspace_id):
        self._auth_token = auth_token
        self._endpoint_url = endpoint_url
        self._workspace_id = workspace_id

    # getter methods
    @property
    def auth_token(self):
        '''Returns the client auth token'''

        return self._auth_token

    @property
    def endpoint_url(self):
        '''Returns the client endpoint URL'''

        return self._endpoint_url

    @property
    def workspace_id(self):
        '''Returns the client workspace ID'''

        return self._workspace_id

    # setter methods
    @auth_token.setter
    def auth_token(self, value):
        '''Sets the client auth token'''

        self._auth_token = value

    @endpoint_url.setter
    def endpoint_url(self, value):
        '''Sets the client endpoint URL'''

        self._endpoint_url = value

    @workspace_id.setter
    def workspace_id(self, value):
        '''Sets the client workspace ID'''

        self._workspace_id = value

    def profile(self):
        '''Returns the client profile'''

        catalog = Catalog(self)
        return catalog.get_profile()


    def publish(self, datasets):
        '''Publishes a dictionary of datasets to a workspace'''

        catalog = Catalog(self)
        return catalog.post_datasets(datasets)

    def list_workspaces(self):
        '''Returns a list of workspace'''

        catalog = Catalog(self)
        return catalog.get_workspaces()
