from typing import List
from footballbrainz_data_models.models.primary_key import PrimaryKey
from footballbrainz_data_models.models.attribute_definition import AttributeDefinition


class Team(dict):
    """
    Team data model for footballbrainz
    """

    def __init__(self, **kwargs):

        self.primary_keys = [PrimaryKey(name="team_id")]
        self.attribute_definitions = [AttributeDefinition(name="team_id", attribute_type="N")]

        if kwargs:
            self.team_id: int = kwargs.get("team_id")
            self.results: List[Result] = [Result(**r) for r in kwargs.get("results", [])]
            dict.__init__(self, **self.__dict__)


class Result(dict):
    """
    Team results data model for footballbrainz
    """

    def __init__(self, **kwargs):
        if kwargs:
            self.league_id: str = kwargs.get("league_id")
            self.season: int = kwargs.get("season")
            self.goals_for: int = kwargs.get("goals_for")
            self.goals_against: int = kwargs.get("goals_against")
            self.home: bool = kwargs.get("home")
            self.away: bool = kwargs.get("away")
            self.game_datetime_epoch: int = kwargs.get("game_datetime_epoch")
            dict.__init__(self, **self.__dict__)
