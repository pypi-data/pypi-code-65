# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import logging

from datetime import datetime, timezone

from thetaetl.service.graph_operations import GraphOperations, OutOfBoundsError, Point
from thetaetl.json_rpc_requests import generate_get_blocks_by_range_json_rpc,generate_get_status_json_rpc
from thetaetl.utils import rpc_response_to_result
from thetaetl.mappers.block_mapper import ThetaBlockMapper
from thetaetl.mappers.status_mapper import ThetaStatusMapper

class ThetaService(object):
    def __init__(self, theta_provider):
        self._graph = BlockTimestampGraph(theta_provider)
        self._graph_operations = GraphOperations(self._graph)
        self.logger = logging.getLogger('ThetaService')

    def get_block_range_for_date(self, date):
        start_datetime = datetime.combine(date, datetime.min.time().replace(tzinfo=timezone.utc))
        # end_datetime = datetime.combine(date, datetime.min.time().replace(tzinfo=timezone.utc))
        end_datetime = datetime.combine(date, datetime.max.time().replace(tzinfo=timezone.utc))
        latest_timestamp = self._graph.get_last_point().y
        return self.get_block_range_for_timestamps(start_datetime.timestamp(), min(latest_timestamp, end_datetime.timestamp()))

    def get_block_range_for_timestamps(self, start_timestamp, end_timestamp):
        start_timestamp = int(start_timestamp)
        end_timestamp = int(end_timestamp)
        if start_timestamp > end_timestamp:
            raise ValueError('start_timestamp must be greater or equal to end_timestamp')

        try:
            start_block_bounds = self._graph_operations.get_bounds_for_y_coordinate(start_timestamp)
        except OutOfBoundsError:
            start_block_bounds = (0, 0)

        try:
            end_block_bounds = self._graph_operations.get_bounds_for_y_coordinate(end_timestamp)
        except OutOfBoundsError as e:
            raise OutOfBoundsError('The existing blocks do not completely cover the given time range') from e

        if start_block_bounds == end_block_bounds and start_block_bounds[0] != start_block_bounds[1]:
            self.logger.info("end_block_bounds[0] %d,  end_block_bounds[1] : %d, start_block_bounds[0] %d, start_block_bounds[1] %d \n", 
                end_block_bounds[0], end_block_bounds[1], start_block_bounds[0], start_block_bounds[1])
            raise ValueError('The given timestamp range does not cover any blocks')

        start_block = start_block_bounds[1]
        end_block = end_block_bounds[0]

        # Theta do not support index 0
        if start_block == 0:
            start_block = 1
        if end_block == 0:
            end_block = 1

        return start_block, end_block


class BlockTimestampGraph(object):
    def __init__(self, theta_provider):
        self._theta_provider= theta_provider
        self.block_mapper = ThetaBlockMapper()
        self.status_mapper = ThetaStatusMapper()
        self.logger = logging.getLogger('BlockTimestampGraph')

    def get_first_point(self):
        # Ignore the genesis block as its timestamp is 0
        return Point(1, 1581035055)

    def get_last_point(self):
#        return block_to_point(self._theta_provider.eth.getBlock('latest'))  
        #return Point(2184972, 1596678993) #TODO: query status to get latest
        status_rpc = generate_get_status_json_rpc()
        response = self._theta_provider.make_request(json.dumps(status_rpc))
        result = rpc_response_to_result(response)
        status = self.status_mapper.json_dict_to_status(result)
        return self.get_point(int(status.latest_finalized_block_height))

    def get_point(self, x):
#        return block_to_point(self._theta_provider.eth.getBlock(x))
        response = self._theta_provider.make_request(
            json.dumps(generate_get_blocks_by_range_json_rpc(x, x, False))
            )
        results = rpc_response_to_result(response)
        blocks = [self.block_mapper.json_dict_to_block(result) for result in results]
        if (len(blocks) == 0) :
            self.logger.info("failed to get block : %d\n", x)
            return Point(x, -1)
        self.logger.info("succeed to get block : %d, timestamp is %s \n", x, blocks[0].timestamp)
        return block_to_point(blocks[0])


def block_to_point(block):
    return Point(int(block.height), int(block.timestamp))
