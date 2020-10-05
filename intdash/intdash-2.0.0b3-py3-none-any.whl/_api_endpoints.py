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

# 　API_VERSIONS only includes endpoints that were added in versions beyond MINIMUN_VERSION.",
API_VERSIONS = {
    "measurements": {
        "get_by_marker": {
            "endpoint": "/api/v1/measurements/markers/{marker_uuid}/measurement",
            "method": "post",
            "version": "1.10.0",
        }
    },
    "measurement_markers": {
        "create": {
            "endpoint": "/api/v1/measurements/{measurement_uuid}/markers",
            "method": "post",
            "version": "1.10.0",
        },
        "get": {
            "endpoint": "/api/v1/measurements/{marker_uuid}/markers",
            "method": "get",
            "version": "1.10.0",
        },
        "update_by_measurement": {
            "endpoint": "/api/v1/measurements/{measurement_uuid}/markers/{marker_uuid}",
            "method": "put",
            "version": "1.10.0",
        },
        "update_by_marker": {
            "endpoint": "/api/v1/measurements/{measurement_uuid}/markers/{marker_uuid}",
            "method": "put",
            "version": "1.10.0",
        },
        "delete_by_measurement": {
            "endpoint": "/api/v1/measurements/{measurement_uuid}/markers/{marker_uuid}",
            "method": "delete",
            "version": "1.10.0",
        },
        "delete_by_marker": {
            "endpoint": "/api/v1/measurements/markers/{marker_uuid}",
            "method": "delete",
            "version": "1.10.0",
        },
        "list": {
            "endpoint": "/api/v1/measurements/{measurement_uuid}/markers",
            "method": "get",
            "version": "1.10.0",
        },
    },
}
