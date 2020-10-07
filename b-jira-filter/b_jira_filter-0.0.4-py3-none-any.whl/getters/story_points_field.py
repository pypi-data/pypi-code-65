from typing import Dict, Any

from jira import JIRA


class StoryPointsField:
    """
    Class that works with JIRA fields and exposes story points field.
    """
    def __init__(self, jira: JIRA):
        self.__jira = jira

    def get_field(self) -> Dict[str, Any]:
        """
        Gets a field which is considered to be a "story points" field.

        :return: Story points field data.
        """
        return [field for field in self.__jira.fields() if field['name'] == 'Story Points'][0]

    def get_field_id(self):
        """
        Gets story points field id.

        :return: Story points field id.
        """
        return self.get_field()['id']
