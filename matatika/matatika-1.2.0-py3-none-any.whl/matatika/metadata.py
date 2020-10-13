# pylint: disable=too-many-instance-attributes, invalid-name

"""metadata module"""

from dataclasses import dataclass, asdict
import json


@dataclass
class Metadata:
    """Class for keeping track of publish options"""

    dataset_id: str
    alias: str
    workspace_id: str
    category: str
    title: str
    description: str
    questions: str
    rawData: str
    visualisation: str
    metadata: str
    query: str

    def to_json(self):
        """Converts the Metadata class structure to a JSON string"""
        return json.dumps(asdict(self))


class Dataset:
    """Class for storing a dataset"""

    def __init__(self):
        self.dataset_id = ''
        self.alias = ''
        self.workspace_id = ''
        self.category = ''
        self.title = ''
        self.description = ''
        self.questions = ''
        self.rawData = ''
        self.visualisation = ''
        self.metadata = ''
        self.query = ''

    # getter methods
    @property
    def dataset_id(self):
        """Gets the dataset_id property"""

        return self._dataset_id

    @property
    def alias(self):
        """Gets the alias property"""

        return self._alias

    @property
    def workspace_id(self):
        """Gets the workspace_id property"""

        return self._workspace_id

    @property
    def category(self):
        """Gets the category property"""

        return self._category

    @property
    def title(self):
        """Gets the title property"""

        return self._title

    @property
    def description(self):
        """Gets the description property"""

        return self._description

    @property
    def questions(self):
        """Gets the questions property"""

        return self._questions

    @property
    def rawData(self):
        """Gets the rawData property"""

        return self._rawData

    @property
    def visualisation(self):
        """Gets the visualisation property"""

        return self._visualisation

    @property
    def metadata(self):
        """Gets the metadata property"""

        return self._metadata

    @property
    def query(self):
        """Gets the query property"""

        return self._query

    # setter methods
    @dataset_id.setter
    def dataset_id(self, value):
        """Sets the dataset_id property"""

        self._dataset_id = value

    @alias.setter
    def alias(self, value):
        """Sets the alias property"""

        self._alias = value

    @workspace_id.setter
    def workspace_id(self, value):
        """Sets the workspace_id property"""

        self._workspace_id = value

    @category.setter
    def category(self, value):
        """Sets the category property"""

        self._category = value

    @title.setter
    def title(self, value):
        """Sets the title property"""

        self._title = value

    @description.setter
    def description(self, value):
        """Sets the description property"""

        self._description = value

    @questions.setter
    def questions(self, value):
        """Sets the questions property"""

        self._questions = value

    @rawData.setter
    def rawData(self, value):
        """Sets the rawData property"""

        self._rawData = value

    @visualisation.setter
    def visualisation(self, value):
        """Sets the visualisation property"""

        self._visualisation = value

    @metadata.setter
    def metadata(self, value):
        """Sets the metadata property"""

        self._metadata = value

    @query.setter
    def query(self, value):
        """Sets the query property"""

        self._query = value

    def to_json(self):
        """Converts the dataset to a JSON string"""

        metadata = Metadata(
            dataset_id=self.dataset_id,
            alias=self.alias,
            workspace_id=self.workspace_id,
            category=self.category,
            title=self.title,
            description=self.description,
            questions=self.questions,
            rawData=self.rawData,
            visualisation=self.visualisation,
            metadata=self.metadata,
            query=self.query
        )
        return metadata.to_json()


# Only for testing
# TODO remove later
if __name__ == "__main__":
    dataset = Dataset()
    print(dataset.to_json())
