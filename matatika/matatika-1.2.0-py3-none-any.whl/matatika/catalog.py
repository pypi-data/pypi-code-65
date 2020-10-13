"""catalog module"""

import jwt
import requests
from matatika.metadata import Dataset
from matatika.dataset_fields import DatasetItems
from matatika.exceptions import WorkspaceNotFoundError
from matatika.exceptions import MatatikaException

class Catalog:
    """Class to handle authorisation with the Matatika API"""

    def __init__(self, client):
        self._headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + client.auth_token
        }

        auth_token_payload = jwt.decode(client.auth_token, algorithms='RS256', verify=False)

        self._profile_url = client.endpoint_url + '/profiles/' + auth_token_payload['sub']
        self._workspaces_url = client.endpoint_url + '/workspaces'

        if client.workspace_id:
            self._workspace_id = client.workspace_id
            self._datasets_url = client.endpoint_url + '/workspaces/' + self._workspace_id  \
                + '/datasets'

    def _parse_dataset(self, alias, dataset):
        """Parses data into a dataset object"""

        parsed_dataset = Dataset()
        parsed_dataset.alias = alias
        parsed_dataset.workspace_id = self._workspace_id

        for field in dataset:
            if field == DatasetItems.CATEGORY.value:
                parsed_dataset.category = dataset[field]
            elif field == DatasetItems.DESCRIPTION.value:
                parsed_dataset.description = dataset[field]
            elif field == DatasetItems.TITLE.value:
                parsed_dataset.title = dataset[field]
            elif field == DatasetItems.QUERY.value:
                parsed_dataset.query = dataset[field]
            elif field == DatasetItems.QUESTIONS.value:
                parsed_dataset.questions = dataset[field]
            elif field == DatasetItems.RAWDATA.value:
                parsed_dataset.rawData = dataset[field]
            elif field == DatasetItems.VERSION.value:
                print(field)
            elif field == DatasetItems.VISUALISATION.value:
                parsed_dataset.visualisation = dataset[field]
            elif field == DatasetItems.METADATA.value:
                parsed_dataset.metadata = dataset[field]

        return parsed_dataset

    def post_datasets(self, datasets):
        """Publishes a dataset into a workspace"""

        publish_responses = []

        for dataset_alias in datasets:
            parsed_dataset = self._parse_dataset(dataset_alias, datasets[dataset_alias])
            dataset_json = parsed_dataset.to_json()
            response = requests.post(self._datasets_url, headers=self._headers, data=dataset_json)

            if response.status_code == 404:
                raise WorkspaceNotFoundError(self._workspace_id)

            if response.status_code not in [201, 200]:
                raise MatatikaException("An unexpected error occurred while publishing dataset [%s]"
                                        % response.status_code)

            publish_responses.append(response)

        return publish_responses

    def get_workspaces(self):
        """Returns all workspaces the user profile is a member of"""

        response = requests.get(self._workspaces_url, headers=self._headers)
        if response.status_code not in [200]:
            raise MatatikaException("An unexpected error occurred while fetching workspaces [%s]"
                                    % response.status_code)
        json_data = response.json()
        workspaces = json_data['_embedded']['workspaces']

        return workspaces

    def get_profile(self):
        """Returns the user profile"""

        response = requests.get(self._profile_url, headers=self._headers)

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()
