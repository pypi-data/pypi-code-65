# Copyright 2019 Cognite AS

import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import LineRange, MaybeString, get_identifier

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import VolumeRequest
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Seismic, OptionalMap, LineBasedVolume
    from cognite.seismic.protos.types_pb2 import Geometry as GeometryProto, Wkt, GeoJson, Trace, LineDescriptor
    from google.protobuf.wrappers_pb2 import StringValue, Int32Value as i32


class VolumeSeismicAPI(API):
    def __init__(self, query, ingestion, metadata):
        super().__init__(query=query, ingestion=ingestion, metadata=metadata)

    def get_volume(
        self,
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        seismic_store_id: MaybeString = None,
        inline_range: Optional[LineRange] = None,
        xline_range: Optional[LineRange] = None,
        z_range: Optional[LineRange] = None,
        include_trace_header: bool = False,
    ) -> Iterable[Trace]:
        """Retrieve traces from a seismic or seismic store

        Provide one of: the seismic id, the seismic external id, the seismic store id.
        The line ranges are specified as tuples of either (start, end) or (start, end, step).
        If a line range is not specified, the maximum ranges will be assumed.

        Args:
            id (int | None): The id of the seismic to query
            external_id (str | None): The external id of the seismic to query
            seismic_store_id (id | None): The id of the seismic store to query
            inline_range ([int, int] | [int, int, int] | None): The inline range
            xline_range ([int, int] | [int, int, int] | None): The crossline range
            z_range ([int, int] | [int, int, int]): The zline range
            include_trace-header (bool): Whether to include trace header info in the response.
        """
        inline = into_line_range(inline_range)
        xline = into_line_range(xline_range)
        zline = into_line_range(z_range)
        lbs = LineBasedVolume(iline=inline, xline=xline, z=zline)
        req = VolumeRequest(volume=lbs, include_trace_header=include_trace_header)
        if seismic_store_id:
            req.seismic_store_id = seismic_store_id
        else:
            req.seismic.MergeFrom(get_identifier(id, external_id))
        return self.query.GetVolume(req, metadata=self.metadata)


def into_line_range(linerange: Optional[LineRange]) -> LineDescriptor:
    "Converts a tuple of two or three values into a LineDescriptor"
    if linerange is None:
        return None
    if len(linerange) == 2:
        start, stop = linerange
        return LineDescriptor(min=i32(value=start), max=i32(value=stop))
    if len(linerange) == 3:
        start, stop, step = linerange
        return LineDescriptor(min=i32(value=start), max=i32(value=stop), step=i32(value=step))
    raise Exception("A line range should be None, (int, int), or (int, int, int).")
