import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import LineRange, MaybeString, Metadata, get_identifier, get_search_spec
from google.protobuf.struct_pb2 import Struct
from google.protobuf.wrappers_pb2 import Int32Value as i32
from google.protobuf.wrappers_pb2 import StringValue

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        SearchSeismicsRequest,
        CreateSeismicRequest,
        EditSeismicRequest,
        DeleteSeismicRequest,
        DeleteSeismicResponse,
        VolumeRequest,
    )
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import (
        Seismic,
        OptionalMap,
        Identifier,
        TextHeader as pTextHeader,
        BinaryHeader as pBinaryHeader,
    )
    from cognite.seismic.protos.types_pb2 import Geometry as GeometryProto, CRS as CRSProto, Wkt, GeoJson
else:
    from cognite.seismic._api.shims import Seismic, Geometry as GeometryProto, Identifier


class VolumeDef:
    def __init__(self, volumedef: str):
        self.volumedef = volumedef


class Geometry:
    """Represents a CRS + shape, in either a WKT format or a GeoJSON."""

    def __init__(self, crs: str, *, geojson: Union[Struct, None] = None, wkt: Union[str, None] = None):
        if (geojson is None) and (wkt is None):
            raise Exception("You must specify one of: geojson, wkt")
        if (geojson is not None) and (wkt is not None):
            raise Exception("You must specify either of: geojson, wkt")
        self.crs = crs
        self.geojson = geojson
        self.wkt = wkt

    def to_proto(self):
        crs_proto = CRSProto(crs=self.crs)
        if self.geojson is not None:
            return GeometryProto(crs=crs_proto, geo=GeoJson(json=self.geojson))
        if self.wkt is not None:
            return GeometryProto(crs=crs_proto, wkt=Wkt(geometry=self.wkt))


class TextHeader:
    """A representation of text headers used to create or edit existing headers."""

    def __init__(self, *, header: MaybeString = None, raw_header: MaybeString = None):
        """Create a text header.

        Specify either header or raw_header.
        
        Args:
            header (String | None): The text content of a header
            raw_header (String | None): The raw bytes of a header
        """
        self.header = header
        self.raw_header = raw_header

    def into_proto(self):
        return pTextHeader(header=self.header, raw_header=self.raw_header)


class BinaryHeader:
    """A representation of binary headers used to create or edit existing headers.
    
    BinaryHeader.FIELDS contains the list of valid fields. to set after the object is constructed.
    """

    FIELDS = [
        "traces",
        "trace_data_type",
        "fixed_length_traces",
        "segy_revision",
        "auxtraces",
        "interval",
        "interval_original",
        "samples",
        "samples_original",
        "ensemble_fold",
        "vertical_sum",
        "trace_type_sorting_code",
        "sweep_type_code",
        "sweep_frequency_start",
        "sweep_frequency_end",
        "sweep_length",
        "sweep_channel",
        "sweep_taper_start",
        "sweep_taper_end",
        "sweep_taper_type",
        "correlated_traces",
        "amplitude_recovery",
        "original_measurement_system",
        "impulse_signal_polarity",
        "vibratory_polarity_code",
    ]

    def __init__(self, *args, raw_header: Union[bytes, None] = None, **kwargs):
        """Initialize.
        
        Args:
            *args (int): An optional list of arguments. The fields are assigned to the binary_header fields in sequential order, and missing fields are assigned None.
            **kwargs (int): An optional key-value mapping of arguments, which overwrite any values from *args.
            raw_header (bytes | None): Optional raw header.            
        """
        for i, field in enumerate(BinaryHeader.FIELDS):
            val = args[i] if i < len(args) else None
            val = kwargs[field] if field in kwargs else val
            setattr(self, field, val)
        self.raw_header = raw_header

    def into_proto(self):
        return pBinaryHeader(
            traces=self.traces,
            trace_data_type=self.trace_data_type,
            fixed_length_traces=self.fixed_length_traces,
            segy_revision=self.segy_revision,
            auxtraces=self.auxtraces,
            interval=self.interval,
            interval_original=self.interval_original,
            samples=self.samples,
            samples_original=self.samples_original,
            ensemble_fold=self.ensemble_fold,
            vertical_sum=self.vertical_sum,
            trace_type_sorting_code=self.trace_type_sorting_code,
            sweep_type_code=self.sweep_type_code,
            sweep_frequency_start=self.sweep_frequency_start,
            sweep_frequency_end=self.sweep_frequency_end,
            sweep_length=self.sweep_length,
            sweep_channel=self.sweep_channel,
            sweep_taper_start=self.sweep_taper_start,
            sweep_taper_end=self.sweep_taper_end,
            sweep_taper_type=self.sweep_taper_type,
            correlated_traces=self.correlated_traces,
            amplitude_recovery=self.amplitude_recovery,
            original_measurement_system=self.original_measurement_system,
            impulse_signal_polarity=self.impulse_signal_polarity,
            vibratory_polarity_code=self.vibratory_polarity_code,
            raw_header=self.raw_header,
        )


class SeismicAPI(API):
    def __init__(self, query, ingestion, metadata):
        super().__init__(query=query, ingestion=ingestion, metadata=metadata)

    def create(
        self,
        *,
        external_id: str,
        name: MaybeString = None,
        partition_identifier: Union[int, str],
        seismic_store_id: int,
        volumedef: Union[str, None] = None,
        geometry: Union[Geometry, None] = None,
        metadata: Union[Metadata, None] = None,
        text_header: Union[TextHeader, None] = None,
        binary_header: Union[BinaryHeader, None] = None,
    ) -> Seismic:
        """Create a new Seismic.
        
        If neither volumedef nor geometry are specified, the new Seismic will be able to access the entire seismic store it is derived from.

        Args:
            externaL_id (str): The external id of the new Seismic
            name (str | None): (Optional) If specified, the name of the new Seismic
            partition_identifier (int | str): Either the partition id or external_id that the Seismic is part of
            seismic_store_id (int): The seismic store that the new Seismic is derived from
            volumedef (str | None): (Optional) If specified, uses a VolumeDef as the shape of the Seismic
            geometry (Geometry | None): (Optional) If specified, uses a Geometry (either a WKT or GeoJson) as the shape of the Seismic
            text_header (TextHeader | None): (Optional) If specified, sets the provided text header on the new seismic
            binary_header (BinaryHeader | None): (Optional) If specified, sets the provided binary header on the new seismic

        Returns:
            Seismic: The newly created Seismic with minimal data. Use search() to retrieve all data.
        """
        if type(partition_identifier) == int:
            identifier = Identifier(id=partition_identifier)
        elif type(partition_identifier) == str:
            identifier = Identifier(external_id=partition_identifier)
        else:
            raise Exception("partition_identifier should be an int or a str.")

        request = CreateSeismicRequest(external_id=external_id, partition=identifier, seismic_store_id=seismic_store_id)
        if volumedef is not None:
            request.volume_def.MergeFrom(volumedef)
        elif geometry is not None:
            request.geometry.MergeFrom(geometry.to_proto())

        if name is not None:
            request.name = name

        if metadata is not None:
            request.metadata.MergeFrom(OptionalMap(data=metadata))

        if text_header is not None:
            request.text_header.MergeFrom(text_header.into_proto())

        if binary_header is not None:
            request.binary_header.MergeFrom(binary_header.into_proto())

        return self.query.CreateSeismic(request, metadata=self.metadata)

    def search(
        self,
        mode: str = "seismic",
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        external_id_substring: MaybeString = None,
        name: MaybeString = None,
        name_substring: MaybeString = None,
        include_text_header: bool = False,
        include_binary_header: bool = False,
        include_line_range: bool = False,
        include_volume_definition: bool = False,
        include_seismic_store: bool = False,
        include_partition: bool = False,
        get_all: bool = False,
    ) -> Iterable[Seismic]:
        """Search for seismics.
        
        Can search all seismics included in surveys, partitions, or directly search seismics,
        specified by id, external_id, name, or substrings of external_id or name. 
        Only one search method should be specified. The behaviour when multiple are specified is undefined.

        Args:
            mode (str): One of "survey", "seismic" or "partition".
            id (int|None): id to search by
            external_id (str|None): external id to search by
            external_id_substring (str|None): Substring of external id to search by
            name (str|None): Name to search by
            name_substring (str|None): Substring of name to search by

            include_text_header (bool): If true, includes the text header in the responses
            include_binary_header (bool): If true, includes the binary header in the responses
            include_line_range (bool): If true, includes the line range in the responses
            include_volume_definition (bool): If true, includes the volume def in the responses
            include_seismic_store (bool): If true, include the seismic store info in the responses
            include_partition (bool): If true, include the partition info in the responses

            get_all (bool): Whether to instead retrieve all visible Seismic. Equivalent to list().
        
        Returns:
            Iterable[Seismic]: The list of matching Seismics
        """
        if get_all:
            req = SearchSeismicsRequest()
        else:
            spec = get_search_spec(id, external_id, external_id_substring, name, name_substring)
            if mode == "seismic":
                req = SearchSeismicsRequest(seismic=spec)
            elif mode == "survey":
                req = SearchSeismicsRequest(survey=spec)
            elif mode == "partition":
                req = SearchSeismicsRequest(partition=spec)
            else:
                raise Exception("mode should be one of: survey, seismic, partition")

        req.include_text_header = include_text_header
        req.include_binary_header = include_binary_header
        req.include_line_range = include_line_range
        req.include_volume_definition = include_volume_definition
        req.include_seismic_store = include_seismic_store
        req.include_partition = include_partition

        return self.query.SearchSeismics(req, metadata=self.metadata)

    def list(self) -> Iterable[Seismic]:
        return self.search(get_all=True)

    def get(self, *, id: Union[int, None] = None, external_id: MaybeString = None) -> Seismic:
        """Get a seismic by id or external id.

        Equivalent to search("seismic", id=) or search("seismic", external_id=), returning all info.

        Args:
            id (int | None): id of seismic to get
            external_id (str | None): external id of seismic to get
        
        Returns:
            Seismic: The matching seismic.
        """
        if id is None and external_id is None:
            raise Exception("Need to provide either the seismic id or external id")

        result = [
            x
            for x in self.search(
                "seismic",
                id=id,
                external_id=external_id,
                include_text_header=True,
                include_binary_header=True,
                include_line_range=True,
                include_seismic_store=True,
                include_partition=True,
            )
        ]

        if len(result) > 1:
            print(result)
            raise Exception("Multiple seismics found. Please contact support")
        elif len(result) == 0:
            if id is not None:
                msg = f"Seismic with id '{id}'' not found"
            else:
                msg = f"Seismic with external id '{external_id}' not found"
            raise Exception(msg)
        return result[0]

    def edit(
        self,
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        name: MaybeString = None,
        metadata: Union[Metadata, None] = None,
    ) -> Seismic:
        """Edit an existing seismic.
        
        Either the id or the external_id should be provided in order to identify the seismic.
        The editable fields are name and metadata. Providing a name or metadata field will replace the existing data with the new data. Providing an empty string as the name will delete the seismic name.
        
        Args:
            id (int | None): The id of the seismic
            external_id (str | None): The external id of the seismic
            name (str | None): (Optional) The new name of the seismic
            metadata (Dict[str, str] | None): (Optional) The new metadata for the seismic
        
        Returns:
            Seismic: The edited Seismic with minimal data. Use search() to retrieve all data.
        """
        identifier = get_identifier(id, external_id)
        request = EditSeismicRequest(seismic=identifier)
        if name is not None:
            request.name.CopyFrom(StringValue(value=name))
        if metadata is not None:
            request.metadata.MergeFrom(OptionalMap(data=metadata))

        return self.query.EditSeismic(request, metadata=self.metadata)

    def delete(self, *, id: Union[int, None] = None, external_id: MaybeString = None) -> bool:
        """Delete a seismic

        Either the id or the external id should be provided in order to identify the seismic.
        
        Args:
            id (int | None): The id of the seismic
            external_id (str | None): The external id of the seismic
        
        Returns:
            bool: True if successful
        """
        identifier = get_identifier(id, external_id)
        request = DeleteSeismicRequest(seismic=identifier)

        return self.query.DeleteSeismic(request, metadata=self.metadata).succeeded
