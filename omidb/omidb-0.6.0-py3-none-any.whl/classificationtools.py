import omidb
from .events import Event
import copy
from typing import List


def has_prior(client: omidb.client.Client) -> bool:
    """
    Returns ``True`` if ``client`` has a non-malignant episode earlier than a
    malignant episode; ``False`` otherwise.

    :param client: A classified client with more than one episode
    """

    if client.status != omidb.client.Status.M:
        return False

    nm_date = None  # earliest non-malignant date
    m_date = None  # most recent malignant date

    for episode in client.episodes:
        if None in (episode.id, episode.opened_date):
            continue

        date = episode.opened_date

        if episode.has_malignant_opinions:
            if (m_date is None) or (date > m_date):
                m_date = date
        else:
            if (nm_date is None) or (date < nm_date):
                nm_date = date

        if nm_date and m_date:
            if nm_date < m_date:
                return True

    return False


def filter_studies_by_event_type(
    client: omidb.client.Client, event_type: List[Event], exact_match: bool = True
) -> omidb.client.Client:
    """
    Remove studies (``omidb.study.Study``) from ``client`` whose event type
    includes one or all (if ``exact_match`` is ``True``) of those listed by
    ``event_type``.

    :param client: A classified client with more than one episode
    :param event_type: A list of event types
    :param exact_match: If ``True`` the event types of a study must all of
        those in ``event_type``.
    """

    client2 = copy.deepcopy(client)

    for idx, episode in enumerate(client.episodes):
        if not episode.studies:
            continue
        for study in episode.studies:
            if study.event_type:
                if exact_match and set(study.event_type) != set(event_type):
                    client2.episodes[idx].studies.remove(study)  # type: ignore
                elif not any([_ in study.event_type for _ in event_type]):
                    client2.episodes[idx].studies.remove(study)  # type: ignore

    return client2
