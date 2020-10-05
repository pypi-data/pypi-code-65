# dbnomics-fetcher-toolbox
# Toolbox of functions and data types helping writing DBnomics fetchers.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2019 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-fetcher-toolbox
#
# dbnomics-fetcher-toolbox is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-fetcher-toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Functions and classes defining SDMX v2.0 data model."""

from collections import defaultdict
from enum import Enum
from operator import attrgetter
from typing import Callable, Dict, Iterator, List, Optional, Sequence, Set, Tuple, Union

from lxml.etree import Element
from pydantic import BaseModel, root_validator
from typing_extensions import Literal

from . import data_model
from .data_model import DatasetReference, NoTimeDimensionError, ObservationError
from .parts import Dimensions
from .utils import find, without_empty_values

NAN: Literal["NaN"] = "NaN"

Lang = str


class Code(BaseModel):
    """Represents a ``<Code>`` SDMX element."""

    value: str
    descriptions: Dict[Lang, str]
    parent_code: Optional[str]


class CodeList(BaseModel):
    """Represents a ``<CodeList>`` SDMX element."""

    id: str  # noqa
    names: Dict[Lang, str]
    codes: List[Code]


class Concept(BaseModel):
    """Represents a ``<Concept>`` SDMX element."""

    id: str  # noqa
    names: Dict[Lang, str]


class Dimension(BaseModel):
    """Represents a ``<Dimension>`` SDMX element."""

    codelist_id: str
    concept_id: str


class AttachmentLevel(Enum):
    """Values of the ``attachmentLevel`` attribute of the <Attribute> SDMX element."""

    DATASET = "Dataset"
    SERIES = "Series"
    OBSERVATION = "Observation"


class Attribute(BaseModel):
    """Represents an ``<Attribute>`` SDMX element."""

    codelist_id: str
    concept_id: str
    attachment_level: AttachmentLevel


class DatasetStructure(BaseModel):
    """Represents a ``<Structure>`` SDMX element as used to describe one dataset.

    The ``<Components>`` SDMX element is flatten: its children
    ``<Dimension>`` and ``<Attribute>`` are directly available
    under ``dimensions`` and ``attributes``.
    """

    id: str  # noqa
    names: Dict[Lang, str]
    codelists: List[CodeList]
    concepts: List[Concept]
    dimensions: List[Dimension]
    attributes: List[Attribute]

    @root_validator
    def dimension_codelists_exist(cls, values):  # noqa
        dimensions = values.get("dimensions")
        if dimensions:
            codelist_ids = [codelist.id for codelist in values.get("codelists") or []]
            for dimension in dimensions:
                if dimension.codelist_id not in codelist_ids:
                    raise ValueError(
                        f"Dimension {dimension.concept_id!r} references "
                        f"a codelist {dimension.codelist_id!r} that was not found"
                    )
        return values

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Return the concept correponsing to ``concept_id``."""
        return find(lambda concept: concept.id == concept_id, self.concepts)

    def get_codelist(self, codelist_id: str) -> CodeList:
        """Return the codelist correponsing to ``codelist_id``."""
        codelist = find(lambda codelist: codelist.id == codelist_id, self.codelists)
        if codelist is not None:
            return codelist
        # should not happen, validated by "dimension_codelists_exist"
        assert False  # noqa: B011

    def get_dimension(self, concept_id: str) -> Optional[Dimension]:
        """Return the dimension correponsing to ``concept_id``."""
        return find(
            lambda dimension: dimension.concept_id == concept_id, self.dimensions
        )


class KeyFamily(BaseModel):
    """Represents a ``<KeyFamily>`` SDMX element."""

    id: str  # noqa
    names: Dict[Lang, str]


def build_dimension_mask(structure: DatasetStructure, dimensions: Dimensions) -> str:
    """Build a dimension mask.

    Return a string representing a selection of dimensions, as often used in SDMX APIs.
    This is useful to search series by dimension.

    Raise ``ValueError`` if a dimension of ``dimensions`` can't be found.
    """

    def iter_parts():
        for code, value_codes in dimensions.items():
            dimension = structure.get_dimension(code)
            if dimension is None:
                raise ValueError(f"Could not find dimension with concept_id={code!r}")
            codelist = structure.get_codelist(dimension.codelist_id)
            total = len(codelist.codes)
            yield "" if len(value_codes) == total else "+".join(value_codes)

    return ".".join(iter_parts())


class Value(BaseModel):
    """Represents a ``<Value>`` SDMX element."""

    concept_id: str
    value: str


def find_value_value(concept_id: str, values: Sequence[Value]) -> Optional[str]:
    """Find the value of the items in ``values`` identified by ``concept_id``."""
    found = find(lambda value: value.concept_id == concept_id, values)
    return None if found is None else found.value


ObsValue = Union[Literal["NaN"], float]


class Obs(BaseModel):
    """Represents an ``<Obs>`` SDMX element."""

    value: ObsValue
    time: Optional[str]  # example: dataset AFRICAPOLIS of OECD
    attributes: List[Value]

    def find_attribute_value(self, concept_id: str) -> Optional[str]:
        """Find the value of the attribute identified by ``concept_id``."""
        return find_value_value(concept_id, self.attributes)


class Series(BaseModel):
    """Represents a ``<Series>`` SDMX element."""

    key: List[Value]
    attributes: List[Value]
    observations: List[Obs]

    @property
    def key_str(self) -> str:
        """Return ``Series.key`` as a ``str``.

        For each ``Value`` item of the ``key`` list, take ``Value.value``,
        and join them all by a ``"."``.

        >>> series = Series(key=[
        ...     Value(concept_id='FREQ', value='A'),
        ...     Value(concept_id='COUNTRY', value='FR'),
        ... ], attributes=[], observations=[])
        >>> series.key_str
        'A.FR'
        """
        return ".".join(value.value for value in self.key)

    def find_attribute_value(self, concept_id: str) -> Optional[str]:
        """Find the value of the attribute identified by ``concept_id``."""
        return find_value_value(concept_id, self.attributes)

    def find_key_value(self, concept_id: str) -> Optional[str]:
        """Find the value of the key identified by ``concept_id``."""
        return find_value_value(concept_id, self.key)


class Dataset(BaseModel):
    """Represents a ``<Dataset>`` SDMX element."""

    series: List[Series]


ATTRIBUTE_TAG = "{*}Attribute"
ATTRIBUTES_TAG = "{*}Attributes"
CODE_TAG = "{*}Code"
CODELIST_TAG = "{*}CodeList"
CODELISTS_TAG = "{*}CodeLists"
CONCEPT_TAG = "{*}Concept"
CONCEPTS_TAG = "{*}Concepts"
DATASET_TAG = "{*}DataSet"
DESCRIPTION_TAG = "{*}Description"
DIMENSION_TAG = "{*}Dimension"
KEYFAMILIES_TAG = "{*}KeyFamilies"
KEYFAMILY_TAG = "{*}KeyFamily"
NAME_TAG = "{*}Name"
OBS_TAG = "{*}Obs"
OBS_VALUE_TAG = "{*}ObsValue"
SERIES_KEY_TAG = "{*}SeriesKey"
SERIES_TAG = "{*}Series"
TIME_TAG = "{*}Time"
VALUE_TAG = "{*}Value"

LANG_ATTRIBUTE = "{http://www.w3.org/XML/1998/namespace}lang"


def load_dataset_structure(structure_element: Element) -> DatasetStructure:
    """Return a ``DatasetStructure`` built from given XML element."""
    keyfamily_elements = structure_element.findall(
        f"./{KEYFAMILIES_TAG}/{KEYFAMILY_TAG}"
    )
    if len(keyfamily_elements) > 1:
        raise ValueError(
            f"Expected one KeyFamily element but {len(keyfamily_elements)} were found"
        )
    keyfamily_element = keyfamily_elements[0]
    return DatasetStructure(
        id=keyfamily_element.attrib["id"],
        names=_load_lang_dict(keyfamily_element, tag=NAME_TAG),
        codelists=list(_iter_codelists(structure_element.find(f"./{CODELISTS_TAG}"))),
        concepts=list(_iter_concepts(structure_element.find(f"./{CONCEPTS_TAG}"))),
        dimensions=list(
            _iter_dimensions(keyfamily_element.iterfind(f".//{DIMENSION_TAG}"))
        ),
        attributes=list(
            _iter_attributes(keyfamily_element.iterfind(f".//{ATTRIBUTE_TAG}"))
        ),
    )


def iter_keyfamilies(structure_element: Element) -> Iterator[KeyFamily]:
    """Yield :class:`KeyFamily` objects found in ``structure_element``."""
    for keyfamily_element in structure_element.iterfind(
        f"./{KEYFAMILIES_TAG}/{KEYFAMILY_TAG}"
    ):
        yield KeyFamily(
            id=keyfamily_element.attrib["id"],
            names=_load_lang_dict(keyfamily_element, tag=NAME_TAG),
        )


def _iter_codelists(codelists_element: Element) -> Iterator[CodeList]:
    for codelist_element in codelists_element.iterfind(f"./{CODELIST_TAG}"):
        yield CodeList(
            id=codelist_element.attrib["id"],
            names=_load_lang_dict(codelist_element, tag=NAME_TAG),
            codes=list(map(_load_code, codelist_element.iterfind(f"./{CODE_TAG}"))),
        )


def _iter_concepts(concepts_element: Element) -> Iterator[Concept]:
    for concept_element in concepts_element.iterfind(f"./{CONCEPT_TAG}"):
        yield Concept(
            id=concept_element.attrib["id"],
            names=_load_lang_dict(concept_element, tag=NAME_TAG),
        )


def _iter_dimensions(dimension_elements: Sequence[Element]) -> Iterator[Dimension]:
    for dimension_element in dimension_elements:
        yield Dimension(
            codelist_id=dimension_element.attrib["codelist"],
            concept_id=dimension_element.attrib["conceptRef"],
        )


def _iter_attributes(attribute_elements: Sequence[Element]) -> Iterator[Attribute]:
    for attribute_element in attribute_elements:
        yield Attribute(
            codelist_id=attribute_element.attrib["codelist"],
            concept_id=attribute_element.attrib["conceptRef"],
            attachment_level=attribute_element.attrib["attachmentLevel"],
        )


def _load_lang_dict(element: Element, tag: str) -> Dict[Lang, str]:
    return {
        child_element.attrib[LANG_ATTRIBUTE]: child_element.text
        for child_element in element.iterfind(f"./{tag}")
        if child_element.text
    }


def _load_code(code_element: Element) -> Code:
    return Code(
        value=code_element.attrib["value"],
        descriptions=_load_lang_dict(code_element, tag=DESCRIPTION_TAG),
        parent_code=code_element.attrib.get("parentCode"),
    )


def load_dataset(dataset_element: Element) -> Dataset:
    """Return a ``Dataset`` built from the given XML element."""
    return Dataset(series=list(_iter_series(dataset_element)))


def _iter_series(dataset_element: Element) -> Iterator[Series]:
    for series_element in dataset_element.iterfind(f"./{SERIES_TAG}"):
        attribute_element = series_element.find(f"./{ATTRIBUTES_TAG}")
        attributes = (
            list(_iter_values(attribute_element))
            if attribute_element is not None
            else []
        )
        yield Series(
            key=list(_iter_values(series_element.find(f"./{SERIES_KEY_TAG}"))),
            attributes=attributes,
            observations=list(_iter_obs(series_element)),
        )


def _iter_values(element: Element) -> Iterator[Value]:
    for value_element in element.iterfind(f"./{VALUE_TAG}"):
        yield Value(
            concept_id=value_element.attrib["concept"],
            value=value_element.attrib["value"],
        )


def _iter_obs(series_element: Element) -> Iterator[Obs]:
    for obs_element in series_element.iterfind(f"./{OBS_TAG}"):
        time_element = obs_element.find(f"./{TIME_TAG}")
        time = time_element.text if time_element is not None else None
        value = parse_observation_value(
            obs_element.find(f"./{OBS_VALUE_TAG}").attrib["value"]
        )
        attributes_element = obs_element.find(f"./{ATTRIBUTES_TAG}")
        attributes = (
            list(_iter_values(attributes_element))
            if attributes_element is not None
            else []
        )
        yield Obs(time=time, value=value, attributes=attributes)


def parse_observation_value(value: str) -> ObsValue:
    """Parse ``str`` and return a ``float`` or the literal string ``"NaN"``.

    If ``value`` can't be converted to a ``float`` and is different from ``"NaN"``,
    raise a ``ValueError``.

    >>> parse_observation_value(NAN)
    'NaN'
    >>> parse_observation_value(1.2)
    1.2
    >>> parse_observation_value('Hello')
    Traceback (most recent call last):
        ...
    ValueError: Invalid value 'Hello' for a SDMX observation
    """
    if value == NAN:
        return NAN
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid value {value!r} for a SDMX observation") from exc


def remove_prepared_date(element: Element) -> Element:
    """Remove ``prepared date`` from XML element.

    This is sometimes useful to avoid triggering a false commit in source data.

    Mutate ``element`` and return it to ease using that function as a callback,
    for example with :func:`dbnomics_fetcher_toolbox.formats.fetch_or_read_xml`.
    """
    element.find("./{*}Header/{*}Prepared").text = "1111-11-11T11:11:11"
    return element


def get_one_name(
    names: Dict[Lang, str], lang_candidates: Sequence[str] = None
) -> Optional[str]:
    """Return a name among ``names``.

    ``lang_candidates`` can be used to choose a preferred language.
    Default value is ``None``, which means that the first available name
    will be returned.
    """
    for lang in lang_candidates or []:
        name = names.get(lang)
        if name is not None:
            return name
    langs = list(names.keys())
    return names[langs[0]] if langs else None


# Convert SDMX v2.0 models to DBnomics data model as JSON files or objects.


def keyfamily_to_dataset_references(
    keyfamily: KeyFamily, lang_candidates: Sequence[str] = None
) -> DatasetReference:
    """Convert a SDMX 2.0 KeyFamily into a DBnomics dataset reference.

    Return a :class:`dbnomics_fetcher_toolbox.data_model.DatasetReference`
    built from ``keyfamily``.

    Use ``lang_candidates`` to choose a preferred language.
    It is forwarded to :func:`get_one_name`.
    """
    return DatasetReference(
        code=keyfamily.id, name=get_one_name(keyfamily.names, lang_candidates)
    )


def structure_to_dataset_json(
    dataset_code: str,
    structure: DatasetStructure,
    lang_candidates: Sequence[str] = None,
    all_series: Sequence[Series] = None,
) -> dict:
    """Return a ``dict`` representing a dataset, following DBnomics data model.

    Use ``lang_candidates`` to choose a preferred language.
    It is forwarded to :func:`get_one_name`.

    Use ``all_series`` to write only the dimensions and the attributes actually used
    by the series.
    """

    def build_used_codes(
        all_series: Sequence[Series],
        get_values: Callable[[Series], Sequence[Value]],
    ) -> Dict[str, Set[str]]:
        used_codes: Dict[str, Set[str]] = defaultdict(set)
        for series in all_series:
            values = get_values(series)
            for value in values:
                used_codes[value.concept_id].add(value.value)
        return used_codes

    def iter_labels(
        items: Sequence[Union[Dimension, Attribute]], used_codes: Set[str] = None
    ) -> Iterator[Tuple[str, str]]:
        for item in items:
            if used_codes is not None and item.concept_id not in used_codes:
                continue
            concept = structure.get_concept(item.concept_id)
            if concept is not None:
                name = get_one_name(concept.names, lang_candidates)
                if name is not None:
                    yield concept.id, name

    def iter_value_labels(
        items: Sequence[Union[Dimension, Attribute]],
        used_codes: Dict[str, Set[str]] = None,
    ) -> Iterator[Tuple[str, Dict[str, str]]]:
        def _iter_values(
            item: Union[Dimension, Attribute], used_value_codes: Set[str] = None
        ):
            codelist = structure.get_codelist(item.codelist_id)
            for code in codelist.codes:
                if used_value_codes is not None and code.value not in used_value_codes:
                    continue
                description = get_one_name(code.descriptions, lang_candidates)
                if description is not None:
                    yield code.value, description

        for item in items:
            used_value_codes = (
                used_codes.get(item.concept_id) if used_codes is not None else None
            )
            if not used_value_codes:
                continue
            yield item.concept_id, dict(_iter_values(item, used_value_codes))

    used_attribute_codes = (
        build_used_codes(all_series, attrgetter("attributes"))
        if all_series is not None
        else None
    )
    used_dimension_codes = (
        build_used_codes(all_series, attrgetter("key"))
        if all_series is not None
        else None
    )

    return without_empty_values(
        {
            "code": dataset_code,
            "name": get_one_name(structure.names, lang_candidates),
            "attributes_labels": dict(
                iter_labels(
                    structure.attributes,
                    used_codes=set(used_attribute_codes.keys())
                    if used_attribute_codes is not None
                    else None,
                )
            ),
            "attributes_values_labels": without_empty_values(
                dict(
                    iter_value_labels(
                        structure.attributes, used_codes=used_attribute_codes
                    )
                )
            ),
            "dimensions_codes_order": [
                dimension.concept_id for dimension in structure.dimensions
            ],
            "dimensions_labels": dict(
                iter_labels(
                    structure.dimensions,
                    used_codes=set(used_dimension_codes.keys())
                    if used_dimension_codes is not None
                    else None,
                )
            ),
            "dimensions_values_labels": without_empty_values(
                dict(
                    iter_value_labels(
                        structure.dimensions, used_codes=used_dimension_codes
                    )
                )
            ),
        }
    )


def series_to_series_json(series: Series) -> dict:
    """Return a ``dict`` representing a series, following DBnomics data model."""

    def get_attribute_headers(observations: List[Obs]) -> List[str]:
        """Return a list of all attribute concept IDs in the order they are encountered.

        Raise :exc:`dbnomics_fetcher_toolbox.data_model.NoTimeDimensionError`
        if series has no time dimension.
        """
        attribute_headers: List[str] = []
        for observation in series.observations:
            if observation.time is None:
                raise NoTimeDimensionError(
                    f"Series observation has no time dimension: {observation.json()}"
                )
            for value in observation.attributes:
                if value.concept_id not in attribute_headers:
                    attribute_headers.append(value.concept_id)
        return attribute_headers

    def to_dbnomics_value(value: ObsValue) -> data_model.Value:
        if value == NAN:
            return data_model.NA
        if isinstance(value, str):
            raise ObservationError(f"Invalid value for an observation: {value!r}")
        return value

    attributes = {
        attribute.concept_id: attribute.value for attribute in series.attributes
    }
    dimensions = [value.value for value in series.key]

    # First, gather all observation attributes concept IDs.
    obs_attributes = get_attribute_headers(series.observations)

    # Sort observations by period because some providers scramble them in XML,
    # or reverse order.
    rows = sorted(
        [
            observation.time,
            to_dbnomics_value(observation.value),
            # For each DBnomics observation, mention all previously gathered attributes.
            *[
                observation.find_attribute_value(concept_id=attribute)
                for attribute in obs_attributes
            ],
        ]
        for observation in series.observations
    )

    headers = ["PERIOD", "VALUE", *obs_attributes]

    return without_empty_values(
        {
            "code": series.key_str,
            "attributes": attributes,
            "dimensions": dimensions,
            "observations": [headers, *rows],
        }
    )
