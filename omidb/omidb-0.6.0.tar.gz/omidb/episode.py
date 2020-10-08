import datetime
from dataclasses import dataclass
from typing import Optional, List
import enum
from .events import Events, SideOpinion
from .study import Study
from .lesion import Lesion


@enum.unique
class Type(enum.Enum):
    """Type of episode"""

    CA = "Continued Assessment"
    CD = "Delayed Treatment"
    CF = "Follow-up after treatment"
    CI = "Interval case"
    CR = "Local Recurrence"
    F = "First Call"
    G = "GP Referral"
    H = "Higher Risk"
    N = "Non-rout Recall"
    R = "Routine Recall"
    S = "Self Referral"
    X = "Other"


@enum.unique
class Action(enum.Enum):
    """Episode action"""

    EC = "Early Recall for Clinic"
    ES = "Early Recall for Screening"
    FN = "Fine Needle Aspiration"
    FP = "Follow-up (Post-treatment)"
    FV = "Further X-ray views"
    IP = "Inpatient biopsy"
    MT = "Medical Treatment"
    NA = "No Action from this procedure"
    R2 = "Routine second film opinion (obsolete)"
    RC = "Review in clinic"
    RF = "Referral to consultant/GP"
    RR = "Routine recall for screening"
    ST = "Surgical Treatment"
    TR = "Repeat Film (technical)"
    WB = "Wide Bore Needle"


@enum.unique
class Status(enum.Enum):
    """
    Summarises the overall status of an episode according to the event opinions
    and the episode type.
    """

    B = "Benign"
    M = "Malignant"
    N = "Normal"
    CI = "Interval Cancer"


@dataclass
class Episode:
    """
    An episode contains a set of medical procedures or events associated with
    the treatment or diagnosis of a clinical condition. Medical imaging studies
    are included with each episode, and are typically (but not always) linked
    to one or more events.

    :param id: NBSS episode identifier, only unique within client
    :param events: A set of medical procedures associated with the episode
    :param studies: List of :class:`omidb.study.Study` s where collections of
        screening and diagnostic images reside
    :param type: Enumeration defining the type of episode
    :param action: Enumeration defining the action outcome of the episode
    :param opened_date: Date that the episode opened
    :param closed_date: Date that the episode closed
    :param is_closed: boolean signifying whether the episode is closed
    :param lesions: A list of :class:`omidb.lesion.Lesion` s, examined in the
        episode
    """

    id: str
    events: Events
    studies: Optional[List[Study]] = None
    type: Optional[Type] = None
    action: Optional[Action] = None
    opened_date: Optional[datetime.date] = None
    closed_date: Optional[datetime.date] = None
    is_closed: Optional[bool] = None
    lesions: Optional[List[Lesion]] = None

    @property
    def has_benign_opinions(self) -> bool:
        """
        Returns ``True`` if the container ``e.events`` contains a
        :class:`omidb.events.Events.surgery` or
        :class:`omidb.events.Events.biopsy_wide` event where the left or right
        opinion is benign (:class:`omidb.events.SideOpinion.OB`)
        """

        for event in (self.events.surgery, self.events.biopsy_wide):
            if event and (
                event.left_opinion == SideOpinion.OB
                or event.right_opinion == SideOpinion.OB
            ):
                return True

        return False

    @property
    def has_malignant_opinions(self) -> bool:
        """
        Returns ``True`` if the container ``e.events`` contains a
        :class:`omidb.events.Events.surgery` or
        :class:`omidb.events.Events.biopsy_wide` event where the left or right
        opinion is malignant (:class:`omidb.events.SideOpinion.OM`)
        """

        for event in (self.events.surgery, self.events.biopsy_wide):
            if event and (
                event.left_opinion == SideOpinion.OM
                or event.right_opinion == SideOpinion.OM
            ):
                return True

        return False
