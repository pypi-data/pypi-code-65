import datetime
import dataclasses
import re
import pathlib
import json
from typing import List, Dict, Optional, Iterator, Any, Sequence, Union
from loguru import logger
from . import utilities
from .client import Client, Site
from .episode import Episode
from . import episode
from .study import Study
from .series import Series
from .image import Image
from .mark import (
    BenignClassification,
    Conspicuity,
    MassClassification,
    BoundingBox,
    Mark,
)

from .events import (
    Event,
    Events,
    BreastScreeningData,
    Screening,
    BaseEvent,
    Opinion,
    SideOpinion,
)


class DB:
    """
    OMI-DB parser

    :param root_dir: Root directory of the OMI-DB. The `data` and `images`
        directories should sit somewhere below the root, and can be nested under
        sub-directories, e.g. ``data/sample/omi-db/(data|images)`` is fine.
    :param ignore_missing_images: If ``True``, the existence of dicom images
        belonging to a series will not be checked: parsing is based entirely on the
        JSON representations of the DICOM headers. Set to ``False`` to parse only
        those images for which you have *both* JSON and DICOM files for.
    :param clients: Only parse these clients, if they exist
    :param exclude_clients: Exclude these clients, even if they are in ``clients``
    :param distinct_event_study_links: Only match events to imaging studies
        when distinct (1 to 1 mapping)
    """

    def __init__(
        self,
        root_dir: Union[str, pathlib.Path],
        ignore_missing_images: bool = True,
        clients: Optional[Sequence[str]] = None,
        exclude_clients: Optional[Sequence[str]] = None,
        distinct_event_study_links: bool = True,
    ):

        root_dir = pathlib.Path(root_dir)
        self.ignore_missing_images = ignore_missing_images
        self.distinct_event_study_links = distinct_event_study_links

        # The parent of the DATA/IMAGES directory
        self.real_root_dir = pathlib.Path()
        self._data_dir = pathlib.Path()
        self._image_dir = pathlib.Path()

        data_found = False
        for sub_dir in root_dir.glob("**/"):
            if sub_dir.name in ("data", "DATA"):
                self.real_root_dir = sub_dir.parent
                self._data_dir = sub_dir
                data_found = True
            if sub_dir.name in ("images", "IMAGES"):
                self._image_dir = sub_dir

        if not data_found:
            raise FileNotFoundError(
                f"Failed to parse the given directory. Does {root_dir} contain "
                "the omidb 'data' directory?"
            )

        if not clients:

            clients = []
            for client_path in self._data_dir.glob("*"):
                if client_path.is_dir() and client_path.name[:4] in ("demd", "optm"):
                    clients.append(client_path.name)

        self.clients = set(clients)

        if exclude_clients:
            self.clients = set(clients) - set(exclude_clients)

    def __iter__(self) -> Iterator[Client]:
        """
        Iterates over all parsable clients found in the OMI-DB directory.

        :return: client_it: A :class:`omidb.client.Client` iterator
        """
        for client in self.clients:
            _data_dir = self._data_dir / client
            studies: List[str] = []
            for study in _data_dir.glob("*/**"):

                # Extract study ID from path
                if study.is_dir():
                    match = re.match(r"\d+.", study.name)
                    if match:
                        studies.append(study.name)

            yield self._parse_client(client, studies)

    def _parse_client(self, client: str, studies: List[str]) -> Client:
        try:
            episodes = self._episodes(client, studies)

            site: Site = utilities.enum_lookup(  # type: ignore
                self._imagedb(client)["Site"], Site
            )

            return Client(id=client, episodes=episodes, site=site)

        except Exception as e:  # noqa
            logger.exception(f"omidb: Failed to parse {client}, ")
            raise e

    def _nbss_path(self, client_id: str) -> pathlib.Path:
        """Path of the NBSS json file corresponding to the client with ID
        `client_id`
        """

        p1 = self._data_dir / client_id / ("nbss_" + client_id + ".json")

        if not p1.exists():
            p1 = self._data_dir / client_id / ("NBSS_" + client_id + ".json")

        return p1

    def _nbss(self, client_id: str) -> Dict[str, Any]:
        """NBSS data corresponding to the client with ID `client_id`"""

        with open(self._nbss_path(client_id)) as f:
            nbss: Dict[str, Any] = json.load(f)
        return nbss

    def _imagedb(self, client_id: str) -> Dict[str, Any]:
        """IMAGEDB data corresponding to the client with ID `client_id`"""

        p1 = self._data_dir / client_id / ("imagedb_" + client_id + ".json")

        if not p1.exists():
            p1 = self._data_dir / client_id / ("IMAGEDB_" + client_id + ".json")

        with open(p1) as f:
            imagedb: Dict[str, Any] = json.load(f)

        return imagedb

    def _has_studies(self, client_id: str) -> bool:
        imagedb = self._imagedb(client_id)

        if ("STUDIES" not in imagedb) or (not isinstance(imagedb["STUDIES"], dict)):
            logger.error(f"No studies listed in IMAGEDB for client {client_id}")

            return False

        return True

    def _parse_mark(self, mark_data: Dict[str, Any]) -> Mark:

        args: Dict[str, Any] = {}
        for param_name, key in zip(
            (
                "architectural_distortion",
                "dystrophic_calcification",
                "fat_necrosis",
                "focal_asymmetry",
                "mass",
                "suspicious_calcifications",
                "milk_of_calcium",
                "other_benign_cluster",
                "plasma_cell_mastitis",
                "benign_skin_feature",
                "calcifications",
                "suture_calcification",
                "vascular_feature",
            ),
            (
                "ArchitecturalDistortion",
                "Dystrophic",
                "FatNecrosis",
                "FocalAsymmetry",
                "Mass",
                "SuspiciousCalcifications",
                "MilkOfCalcium",
                "OtherBenignCluster",
                "PlasmaCellMastitis",
                "Skin",
                "WithCalcification",
                "SutureCalcification",
                "Vascular",
            ),
        ):

            args[param_name] = True if mark_data.get(key) else None

        args["benign_classification"] = utilities.enum_lookup(
            str(mark_data.get("BenignClassification")), BenignClassification
        )

        args["conspicuity"] = utilities.enum_lookup(
            str(mark_data.get("Conspicuity")), Conspicuity
        )

        args["mass_classification"] = utilities.enum_lookup(
            str(mark_data.get("MassClassification")), MassClassification
        )

        args["lesion_id"] = str(mark_data["LinkedNBSSLesionNumber"])

        args["id"] = str(mark_data["MarkID"])

        args["boundingBox"] = BoundingBox(
            x1=int(mark_data["X1"]),
            y1=int(mark_data["Y1"]),
            x2=int(mark_data["X2"]),
            y2=int(mark_data["Y2"]),
        )

        return Mark(**args)

    def _parse_series(
        self, client_id: str, study: str, study_data: Dict[str, Any]
    ) -> List[Series]:

        series_list = []
        for series, series_dic in study_data.items():

            if not isinstance(series_dic, dict):
                continue

            image_list = list(series_dic.keys())

            images = []
            for image in image_list:

                dcm_path = self._image_dir / client_id / study / (image + ".dcm")

                json_path = self._data_dir / client_id / study / (image + ".json")

                # Due to inconsistency in file naming
                if not json_path.exists():
                    json_path = json_path.with_suffix(".dcm.json")

                if not json_path.exists():
                    logger.error(
                        f"Image metadata {json_path} does not exist, skipping."
                    )
                    continue

                # Skip this image if no dcm file
                if not self.ignore_missing_images:
                    if not dcm_path.is_file():
                        logger.error(f"Image {dcm_path} of does not exist, skipping.")
                        continue

                marks: List[Mark] = []

                image_marks_data = series_dic.get(image)
                if isinstance(image_marks_data, dict):

                    for mark_id, mark_data in image_marks_data.items():
                        try:
                            marks.append(self._parse_mark(mark_data))
                        except Exception:
                            logger.exception(
                                f"Failed to parse mark data of {client_id} "
                                f"{image}.dcm"
                            )
                            continue

                images.append(Image(image, dcm_path, json_path, marks))

            series_list.append(Series(id=series, images=images))

        return series_list

    def _parse_events(self, episode_data: Dict[str, Any]) -> Events:
        event_kwargs = {
            "screening": episode_data.get("SCREENING", None),
            "assessment": episode_data.get("ASSESSMENT", None),
            "biopsy_wide": episode_data.get("BIOPSYWIDE", None),
            "biopsy_fine": episode_data.get("BIOPSYFINE", None),
            "clinical": episode_data.get("CLINICAL", None),
            "surgery": episode_data.get("SURGERY", None),
        }

        for key, value in event_kwargs.items():

            if not value:
                continue

            # SCREENING must exist in order to parse OTHERSCREENING
            if key == "screening":
                event_kwargs["screening"] = [self._parse_screening_event(value)]

                other_screening = episode_data.get("OTHERSCREENING", None)
                if other_screening is not None:
                    for screen_id, screen in other_screening.items():
                        event_kwargs["screening"].append(
                            self._parse_screening_event(screen)
                        )
            else:
                event_kwargs[key] = self._parse_base_event(value)

        return Events(**event_kwargs)

    def _parse_base_event(self, data: Dict[str, Any]) -> BaseEvent:

        dates: List[datetime.date] = []

        for i, side in enumerate(["L", "R"]):

            side_data = data.get(side)

            if not side_data:
                continue

            for lesion_id, lesion in side_data.items():
                if lesion.get("DatePerformed"):
                    date = utilities.str_to_date(lesion["DatePerformed"])
                    if date not in dates:
                        dates.append(date)

        # Some events may not have lesions due to null ID
        # so add higher-level dateperformed to improve linking
        if data.get("dateperformed"):
            date = utilities.str_to_date(data["dateperformed"])
            if date not in dates:
                dates.append(date)

        left_opinion: SideOpinion = utilities.enum_lookup(  # type: ignore
            str(data.get("left_opinion")), SideOpinion
        )

        right_opinion: SideOpinion = utilities.enum_lookup(  # type: ignore
            str(data.get("right_opinion")), SideOpinion
        )

        return BaseEvent(
            left_opinion=left_opinion, right_opinion=right_opinion, dates=dates
        )

    def _parse_screening_event(self, data: Dict[str, Any]) -> Screening:

        breast_data: List[Optional[BreastScreeningData]] = [None, None]
        dates: List[datetime.date] = []

        for i, side in enumerate(["L", "R"]):

            side_data = data.get(side)

            if not side_data:
                continue

            date: Optional[datetime.date] = None
            if side_data.get("DateTaken"):
                date = utilities.str_to_date(side_data["DateTaken"])
                if date not in dates:
                    dates.append(date)

            opinion: Optional[Opinion] = utilities.enum_lookup(  # type: ignore
                side_data.get("Opinion"), Opinion
            )

            breast_data[i] = BreastScreeningData(
                date=date,
                equipment_make_model=side_data.get("EquipmentMakeModel"),
                opinion=opinion,
            )

        left_opinion: Optional[SideOpinion] = utilities.enum_lookup(  # type: ignore
            str(data.get("left_opinion")), SideOpinion
        )

        right_opinion: Optional[SideOpinion] = utilities.enum_lookup(  # type: ignore
            str(data.get("right_opinion")), SideOpinion
        )

        return Screening(
            left_opinion=left_opinion,
            right_opinion=right_opinion,
            left=breast_data[0],
            right=breast_data[1],
            dates=dates,
        )

    def _episodes(self, client_id: str, studies: Optional[List[str]]) -> List[Episode]:
        """
        Prepare and instantiate all objects required for this client and the
        associated studies.

        Clinical data will be extracted from NBSS even if there are no
        imaging studies listed in IMAGEDB.
        """

        nbss = self._nbss(client_id)
        imagedb = self._imagedb(client_id)

        # Events for each episode
        events: Dict[str, Events] = {}
        for episode_id, nbss_episode in nbss.items():
            if isinstance(nbss_episode, dict):
                events[episode_id] = self._parse_events(nbss_episode)

        studies = [] if studies is None else studies

        # Studies for each episode
        episode_studies: Dict[str, List[Study]] = {}

        if self._has_studies(client_id):

            for study_id, study_data in imagedb["STUDIES"].items():

                if study_id not in studies:  # These exist locally
                    if not study_id:
                        logger.error(
                            f"Empty study listed in IMAGEDB for client "
                            f"{client_id}...skipping"
                        )

                    else:

                        logger.error(
                            f"{client_id}/{study_id} directory does not exist "
                            "but listed in IMAGEDB...skipping"
                        )

                    continue

                series_list = self._parse_series(client_id, study_id, study_data)

                study_date = (
                    utilities.str_to_date(study_data["StudyDate"])
                    if study_data.get("StudyDate")
                    else None
                )

                if study_data is None:
                    logger.warning(f"{client_id}/{study_id} has no study date")
                # Try to extract episode ID by study-date <->event-date
                elif (
                    ("EpisodeID" not in study_data)
                    or (not study_data["EpisodeID"])
                    or (study_data["EpisodeID"] not in nbss)
                ):
                    logger.warning(
                        f"Episode {study_data.get('EpisodeID')} not found in NBSS "
                        f"for {client_id}/{study_id}, "
                        f"attempting link via event dates (will replace episode ID)"
                    )

                    for episode_id, episode_events in events.items():
                        for field in dataclasses.fields(episode_events):
                            event = getattr(episode_events, field.name)
                            if event is None:
                                continue

                            if isinstance(event, list):
                                event_dates = [date for e in event for date in e.dates]
                            else:
                                event_dates = event.dates

                            if event and (study_date in event_dates):
                                study_data["EpisodeID"] = episode_id
                                logger.info(
                                    f"Linked study {study_id} to episode "
                                    f"{episode_id}"
                                )
                                break

                # If still not episode ID, skip
                if ("EpisodeID" not in study_data) or (not study_data["EpisodeID"]):

                    logger.error(
                        f"EpisodeID not found for {client_id}/{study_id}, skipping"
                    )

                    continue

                """"
                if event and (study_date in event_dates): fallback to episode id
                """
                matched_events: List[Event] = []
                if study_data["EpisodeID"] in events:

                    episode_events = events[study_data["EpisodeID"]]

                    for field in dataclasses.fields(episode_events):
                        event_list = getattr(episode_events, field.name)
                        if not event_list:
                            break

                        if not isinstance(event_list, list):
                            event_list = [event_list]

                        for e in event_list:
                            if study_date in e.dates:
                                matched_events.append(getattr(Event, field.name))

                    if not matched_events:
                        logger.warning(
                            f"No events in episode "
                            f"{study_data['EpisodeID']} match study date of "
                            f"{client_id}/{study_id}"
                        )

                        for field in dataclasses.fields(episode_events):
                            event = getattr(episode_events, field.name)
                            if event is None:
                                continue
                            matched_events.append(getattr(Event, field.name))
                            logger.warning(
                                f"Linked {field.name} event to "
                                f"{client_id}/{study_id} via episode "
                                f"{study_data['EpisodeID']} only"
                            )

                    if len(matched_events) > 1:
                        logger.warning(
                            f"{client_id}/{study_id}: Multiple events linked"
                        )

                        if self.distinct_event_study_links:
                            logger.info("Dropping matched events as not distinct")
                            matched_events = []
                else:
                    logger.warning(
                        f"Episode {study_data['EpisodeID']} has no events "
                        "(episode not found in NBSS)"
                    )
                    continue

                # Now add studies to the episode
                study = Study(
                    id=study_id,
                    series=series_list,
                    date=study_date,
                    event_type=matched_events,
                )

                if study_data["EpisodeID"] not in episode_studies:
                    episode_studies[study_data["EpisodeID"]] = [study]
                else:
                    episode_studies[study_data["EpisodeID"]].append(study)

        # Complete episode
        out = []

        for episode_id, episode_events in events.items():

            this_episodes_studies = episode_studies.get(episode_id, None)

            if not this_episodes_studies:
                logger.warning(f"{episode_id} in NBSS but not in IMAGEDB")
            elif self.distinct_event_study_links:
                for idx, study1 in enumerate(this_episodes_studies):
                    for study2 in this_episodes_studies[idx:]:
                        if study1 == study2:
                            continue

                        # Two studies have the same date, drop any links
                        if study1.date == study2.date:
                            logger.warning(
                                "Dropping events linked to "
                                f"{client_id}/{study1.id} and "
                                f"{client_id}/{study2.id} as same date "
                            )
                            study1.event_type = []
                            study2.event_type = []
                            continue

                        # Two studies have the different dates, but linked to same event
                        if study1.event_type and study1.event_type == study2.event_type:
                            event_list = getattr(
                                episode_events, study1.event_type[0].name
                            )

                            if not isinstance(event_list, list):
                                event_list = [event_list]

                            # Pool the dates if multiple screens...
                            event_dates = [date for e in event_list for date in e.dates]

                            if study1.date not in event_dates:
                                logger.warning(
                                    "Dropping events linked to "
                                    f"{client_id}/{study1.id}"
                                )

                                study1.event_type = []

                            if study2.date not in event_dates:
                                logger.warning(
                                    "Dropping events linked to "
                                    f"{client_id}/{study2.id}"
                                )
                                study2.event_type = []

            nbss_episode = nbss[episode_id]
            is_closed = True if nbss_episode.get("EpisodeIsClosed") == "Y" else False

            ep_type: Optional[episode.Type] = utilities.enum_lookup(  # type: ignore
                nbss_episode.get("EpisodeType"), episode.Type
            )

            ep_action: Optional[episode.Action] = utilities.enum_lookup(  # type: ignore
                nbss_episode.get("EpisodeAction"), episode.Action
            )

            opened = (
                utilities.str_to_date(nbss_episode["EpisodeOpenedDate"])
                if nbss_episode.get("EpisodeOpenedDate")
                else None
            )
            closed = (
                utilities.str_to_date(nbss_episode["EpisodeClosedDate"])
                if nbss_episode.get("EpisodeClosedDate")
                else None
            )
            out.append(
                Episode(
                    id=episode_id,
                    events=episode_events,
                    studies=this_episodes_studies,
                    type=ep_type,
                    action=ep_action,
                    opened_date=opened,
                    closed_date=closed,
                    is_closed=is_closed,
                )
            )

        return out
