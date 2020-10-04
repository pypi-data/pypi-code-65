from enum import Enum, unique


@unique
class EntityType(Enum):
    PERSON = "person"
    COMPANY = "company"
    ORGANISATION = "organisation"
    VESSEL = "vessel"
    AIRCRAFT = "aircraft"


@unique
class FilterListType(Enum):
    SANCTION = "sanction"
    WARNING = "warning"
    FITNESS_PROBITY = "fitness-probity"
    PEP = "pep"
    PEP_CLASS_1 = "pep-class-1"
    PEP_CLASS_2 = "pep-class-2"
    PEP_CLASS_3 = "pep-class-3"
    PEP_CLASS_4 = "pep-class-4"
    ADVERSE_MEDIA = "adverse-media"
    ADVERSE_MEDIA_FINANCIAL_CRIME = "adverse-media-financial-crime"
    ADVERSE_MEDIA_VIOLENT_CRIME = "adverse-media-violent-crime"
    ADVERSE_MEDIA_SEXUAL_CRIME = "adverse-media-sexual-crime"
    ADVERSE_MEDIA_TERRORISM = "adverse-media-terrorism"
    ADVERSE_MEDIA_FRAUD = "adverse-media-fraud"
    ADVERSE_MEDIA_NARCOTICS = "adverse-media-narcotics"
    ADVERSE_MEDIA_GENERAL = "adverse-media-general"


@unique
class SortQueryParam(Enum):
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    ASSIGNEE_ID = "assignee_id"
    SEARCHER_ID = "searcher_id"


@unique
class SortDirQueryParam(Enum):
    ASC = "ASC"
    DEC = "DESC"


@unique
class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


@unique
class MatchStatus(Enum):
    NO_MATCH = "no_match"
    FALSE_POSITIVE = "false_positive"
    POTENTIAL_MATCH = "potential_match"
    TRUE_POSITIVE = "true_positive"
    UNKNOWN = "unknown"


@unique
class MonitoredStatus(Enum):
    SUSPENDED = "suspended"
    UN_SUSPENDED = "un-suspended"
    FALSE = "false"
