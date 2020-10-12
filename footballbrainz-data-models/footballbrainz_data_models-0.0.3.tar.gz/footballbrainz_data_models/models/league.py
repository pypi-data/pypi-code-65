from typing import List
from footballbrainz_data_models.models.primary_key import PrimaryKey
from footballbrainz_data_models.models.attribute_definition import AttributeDefinition


class League(dict):
    """
    League data model for footballbrainz
    """

    def __init__(self, **kwargs):

        self.primary_keys = [PrimaryKey(name="leauge_id")]
        self.attribute_definitions = [AttributeDefinition(name="leauge_id", attribute_type="N")]

        if kwargs:
            self.leauge_id: int = kwargs.get("leauge_id")
            self.country: str = kwargs.get("country")
            self.logo: str = kwargs.get("logo")
            self.name: str = kwargs.get("name")
            self.season: str = kwargs.get("season")
            self.season_start: str = kwargs.get("season_start")
            self.season_end: str = kwargs.get("season_end")
            self.flag: str = kwargs.get("flag")
            self.is_current_season: bool = kwargs.get("is_current_season")
            self.has_bookmaker_odds: bool = kwargs.get("has_bookmaker_odds")
            self.season: str = kwargs.get("season")
            self.standings: List[Standing] = [Standing(**s) for s in kwargs.get("standings", [])]
            dict.__init__(self, **self.__dict__)


class Standing(dict):
    """
    Standing data model for footballbrainz
    """

    def __init__(self, **kwargs):
        if kwargs:
            self.rank: int = kwargs.get("rank")
            self.team_id: int = kwargs.get("team_id")
            self.team_name: str = kwargs.get("team_name")
            self.logo: str = kwargs.get("logo")
            self.form: str = kwargs.get("form")
            self.away: bool = kwargs.get("away")
            self.game_datetime_epoch: int = kwargs.get("game_datetime_epoch")
            self.home: TeamStats = TeamStats(**kwargs.get("home", None))
            self.away: TeamStats = TeamStats(**kwargs.get("away", None))
            self.all: TeamStats = TeamStats(**kwargs.get("all", None))
            dict.__init__(self, **self.__dict__)


class TeamStats(dict):
    """
    TeamStats data model for footballbrainz
    """

    def __init__(self, **kwargs):
        if kwargs:
            self.match_played: int = kwargs.get("match_played")
            self.win: int = kwargs.get("win")
            self.draw: int = kwargs.get("draw")
            self.loss: int = kwargs.get("loss")
            self.goals_for: int = kwargs.get("goals_for")
            self.goals_against: int = kwargs.get("goals_against")
            self.goal_diff: int = kwargs.get("goal_diff")
            dict.__init__(self, **self.__dict__)
