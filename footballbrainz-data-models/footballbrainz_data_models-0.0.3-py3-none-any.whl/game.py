from typing import List
from footballbrainz_data_models.models.primary_key import PrimaryKey
from footballbrainz_data_models.models.attribute_definition import AttributeDefinition
from footballbrainz_data_models.models.attribute_projection import AttributeProjection
from footballbrainz_data_models.models.db_index import DbIndex


class Game(dict):
    """
    Game data model for footballbrainz
    """

    def __init__(self, **kwargs):

        self.primary_keys = [PrimaryKey(name="team_id")]
        self.attribute_definitions = [AttributeDefinition(name="team_id", attribute_type="N")]

        attribute_projection = AttributeProjection(non_key_attributes=[], projection_type="ALL")
        gsi_primary_keys = [PrimaryKey(name="game_date")]
        self.global_secondary_indexes = [
            DbIndex(
                index_name="GameIndex",
                key_schema=gsi_primary_keys,
                projection=attribute_projection,
            )
        ]

        if kwargs:
            self.game_id: int = kwargs.get("game_id")
            self.game_datetime_epoch: int = kwargs.get("game_datetime_epoch")
            self.game_date: str = kwargs.get("game_date")
            self.game_datetime_string: str = kwargs.get("game_datetime_string")
            self.leauge_id: int = kwargs.get("leauge_id")
            self.has_bookmaker_odds: bool = kwargs.get("has_bookmaker_odds")
            self.season: int = kwargs.get("season")
            self.round: int = kwargs.get("round")
            self.status: str = kwargs.get("status")
            self.home: TeamGameStats = TeamGameStats(**kwargs.get("home", None))
            self.away: TeamGameStats = TeamGameStats(**kwargs.get("away", None))
            self.safest_bet: GameBet = GameBet(**kwargs.get("safest_bet", None))
            self.riskiest_bet: GameBet = GameBet(**kwargs.get("riskiest_bet", None))
            self.odds: List[Odd] = [Odd(**o) for o in kwargs.get("odds", [])]
            dict.__init__(self, **self.__dict__)


class TeamGameStats(dict):
    """
    TeamGameStats results data model for footballbrainz
    """

    def __init__(self, **kwargs):
        if kwargs:
            self.team_id: int = kwargs.get("team_id")
            self.name: str = kwargs.get("name")
            self.logo: str = kwargs.get("logo")
            self.goals: int = kwargs.get("goals")
            dict.__init__(self, **self.__dict__)


class GameBet(dict):
    """
    GameBet results data model for footballbrainz
    """

    def __init__(self, **kwargs):
        if kwargs:
            self.bet_display: str = kwargs.get("bet_display")
            self.bet_index: int = kwargs.get("bet_index")
            self.odd: str = kwargs.get("odd")
            self.recommended_safe_bet: bool = kwargs.get("recommended_safe_bet")
            self.won: bool = kwargs.get("won")
            dict.__init__(self, **self.__dict__)


class Odd(dict):
    """
    Odd results data model for footballbrainz
    """

    def __init__(self, **kwargs):
        if kwargs:
            self.name: str = kwargs.get("name")
            self.display_name: str = kwargs.get("display_name")
            self.odd_values: List[OddValues] = [OddValues(**o) for o in kwargs.get("odd_values", None)]
            dict.__init__(self, **self.__dict__)


class OddValues(dict):
    """
    OddValues results data model for footballbrainz
    """

    def __init__(self, **kwargs):
        if kwargs:
            self.value: str = kwargs.get("value")
            self.odd: str = kwargs.get("odd")
            self.bookmaker_odd: str = kwargs.get("bookmaker_odd")
            self.is_correct: bool = kwargs.get("is_correct")
            dict.__init__(self, **self.__dict__)
