# Copyright 2020 Aptpod, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import io
import uuid
from distutils.version import LooseVersion

import intdash
from intdash import protocol
from intdash.protocol import filter
from intdash.protocol.pb import data_response_pb2, store_request_pb2


def _create_elems_storedata(units, final, serial_number):
    elems = []

    #
    # specs
    #

    elems.append(protocol.SOSMarker(stream_id=1, serial_number=serial_number))

    for unit in units:
        elems.append(
            protocol.Unit(
                stream_id=1,
                channel=unit.channel,
                elapsed_time=unit.elapsed_time,
                data=unit.data,
            )
        )

    elems.append(
        protocol.EOSMarker(stream_id=1, serial_number=serial_number, final=final)
    )

    return elems


def _create_req_store_protobuf(data_points, final, serial_number, measurement_uuid):
    store_request = store_request_pb2.StoreProto()
    store_request.meas_uuid = measurement_uuid
    store_request.serial_number = serial_number
    store_request.meas_end = final
    store_request.section_end = True  # section status is always True
    store_request.section_total_count.value = 1  # section length is always one

    for dps in data_points:
        data_point = store_request.data_points.add()
        data_point.elapsed_time = dps.elapsed_time.value
        data_point.channel = dps.channel
        data_point.data_type = dps.data_type
        data_point.data_payload = dps.data_payload

    return store_request.SerializeToString()


def _write_req_body(elems):

    bio = io.BytesIO()
    bwr = io.BufferedWriter(bio)
    wr = protocol.Writer(bwr)

    for e in elems:
        wr.write_elem(e)

    return bio.getvalue()


def _read_resp_body(body):
    bio = io.BytesIO(body)
    brd = io.BufferedReader(bio)
    rd = protocol.Reader(brd)

    elems = []
    while True:
        try:
            e = rd.read_elem()
        except EOFError:
            break

        elems.append(e)

    return elems


def _read_resp_body_protobuf(body):

    n = 0
    data_points = []
    while n < len(body):
        len_data = int.from_bytes(body[n : n + 8], byteorder="little")
        n += 8

        data_payload = body[n : n + len_data]
        data_response = data_response_pb2.DataResponseProto()
        data_response.ParseFromString(data_payload)
        data_points.append(data_response)
        n += len_data

    return data_points


def _check_supported(api_version, minimum_version):
    if LooseVersion(api_version) < LooseVersion(minimum_version):
        return False
    else:
        return True


def _create_close_upstream_reqs(stream_id):
    return [
        protocol.UpstreamSpecRequest(
            req_id=0,
            specs=[
                protocol.UpstreamSpec(
                    stream_id=stream_id,
                    store=False,
                    resend=False,
                    src_edge_uuid=uuid.UUID("{00000000-0000-0000-0000-000000000000}"),
                    measurement_uuid=uuid.UUID(
                        "{00000000-0000-0000-0000-000000000000}"
                    ),
                    dst_edge_uuids=[],
                )
            ],
        )
    ]


def _create_open_upstream_reqs(stream_id, spec):
    return [
        protocol.UpstreamSpecRequest(
            req_id=0,
            specs=[
                protocol.UpstreamSpec(
                    stream_id=stream_id,
                    store=spec.store,
                    resend=spec.resend,
                    measurement_uuid=uuid.UUID("{" + spec.measurement_uuid + "}"),
                    src_edge_uuid=uuid.UUID("{" + spec.src_edge_uuid + "}"),
                    dst_edge_uuids=[
                        uuid.UUID("{" + u + "}") for u in spec.dst_edge_uuids
                    ],
                )
            ],
        )
    ]


def _create_close_downstream_reqs(stream_id):
    return [
        protocol.DownstreamSpecRequest(
            req_id=0,
            specs=[
                protocol.DownstreamSpec(
                    stream_id=stream_id,
                    src_edge_uuid=uuid.UUID("{00000000-0000-0000-0000-000000000000}"),
                    dst_edge_uuid=uuid.UUID("{00000000-0000-0000-0000-000000000000}"),
                )
            ],
        )
    ]


def _create_open_downstream_reqs(stream_id, spec):
    reqs = []

    #
    # specs
    #

    reqs.append(
        protocol.DownstreamSpecRequest(
            req_id=0,
            specs=[
                protocol.DownstreamSpec(
                    stream_id=stream_id,
                    src_edge_uuid=uuid.UUID("{" + spec.src_edge_uuid + "}"),
                    dst_edge_uuid=uuid.UUID("{" + spec.dst_edge_uuid + "}"),
                )
            ],
        )
    )

    #
    # filts
    #

    specs_map = {}

    for df in spec.filters:

        key = (df.data_type, df.channel)
        if key not in specs_map:
            specs_map[key] = []

        spec.accept = True
        specs_map[key].append(df.data_id)

    dfilts = []
    for (data_type, channel), ids in specs_map.items():

        if data_type == intdash.DataType.generic.value:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.Generic.from_ids(ids)
                )
            )

        elif data_type == intdash.DataType.can.value:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.Can.from_ids(ids)
                )
            )

        elif data_type == intdash.DataType.general_sensor.value:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.GeneralSensor.from_ids(ids)
                )
            )

        elif data_type == intdash.DataType.nmea.value:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.Nmea.from_ids(ids)
                )
            )

        elif data_type == intdash.DataType.bytes.value:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.Bytes.from_ids(ids)
                )
            )

        elif data_type == intdash.DataType.string.value:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.String.from_ids(ids)
                )
            )

        elif data_type == intdash.DataType.int.value:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.Int.from_ids(ids)
                )
            )

        elif data_type == intdash.DataType.float.value:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.Float.from_ids(ids)
                )
            )

        else:
            dfilts.append(
                protocol.DownstreamDataFilter(
                    channel=channel, filter=filter.Any(data_type=data_type)
                )
            )

    reqs.append(
        protocol.DownstreamFilterRequest(
            req_id=1,
            filters=[
                protocol.DownstreamFilter(
                    stream_id=stream_id, downstream_data_filters=dfilts
                )
            ],
        )
    )

    return reqs


def _create_req_upstream(specs):
    reqs = []

    #
    # specs
    #

    uspecs = []
    for i, spec in specs.items():
        uspecs.append(
            protocol.UpstreamSpec(
                stream_id=i,
                store=spec.store,
                resend=spec.resend,
                measurement_uuid=uuid.UUID("{" + spec.measurement_uuid + "}"),
                src_edge_uuid=uuid.UUID("{" + spec.src_edge_uuid + "}"),
                dst_edge_uuids=[uuid.UUID("{" + u + "}") for u in spec.dst_edge_uuids],
            )
        )

    reqs.append(protocol.UpstreamSpecRequest(req_id=0, specs=uspecs))

    return reqs


def _create_req_downstream(specs):
    reqs = []

    #
    # specs
    #

    dspecs = []
    for i, spec in specs.items():
        dspecs.append(
            protocol.DownstreamSpec(
                stream_id=i,
                src_edge_uuid=uuid.UUID("{" + spec.src_edge_uuid + "}"),
                dst_edge_uuid=uuid.UUID("{" + spec.dst_edge_uuid + "}"),
            )
        )

    reqs.append(protocol.DownstreamSpecRequest(req_id=0, specs=dspecs))

    #
    # filts
    #

    sfilts = []
    for i, spec in specs.items():

        dfilts = []

        specs_map = {}
        for df in spec.filters:

            key = (df.data_type, df.channel)
            if key not in specs_map:
                specs_map[key] = []

            spec.accept = True
            specs_map[key].append(df.data_id)

        dfilts = []
        for (data_type, channel), ids in specs_map.items():

            if data_type == intdash.DataType.generic.value:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.Generic.from_ids(ids)
                    )
                )

            elif data_type == intdash.DataType.can.value:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.Can.from_ids(ids)
                    )
                )

            elif data_type == intdash.DataType.general_sensor.value:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.GeneralSensor.from_ids(ids)
                    )
                )

            elif data_type == intdash.DataType.nmea.value:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.Nmea.from_ids(ids)
                    )
                )

            elif data_type == intdash.DataType.bytes.value:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.Bytes.from_ids(ids)
                    )
                )

            elif data_type == intdash.DataType.string.value:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.String.from_ids(ids)
                    )
                )

            elif data_type == intdash.DataType.int.value:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.Int.from_ids(ids)
                    )
                )

            elif data_type == intdash.DataType.float.value:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.Float.from_ids(ids)
                    )
                )

            else:
                dfilts.append(
                    protocol.DownstreamDataFilter(
                        channel=channel, filter=filter.Any(data_type=data_type)
                    )
                )

        sfilts.append(
            protocol.DownstreamFilter(stream_id=i, downstream_data_filters=dfilts)
        )

    reqs.append(protocol.DownstreamFilterRequest(req_id=1, filters=sfilts))

    return reqs
