# Copyright 2020 Karlsruhe Institute of Technology
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
from functools import partial

from flask_login import login_required

from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import json_response
from kadi.lib.web import url_for


route = partial(bp.route, methods=["GET"])


@route("")
@login_required
def index():
    """Get all (public) base API endpoints."""
    endpoints = {
        "records": url_for("api.get_records"),
        "collections": url_for("api.get_collections"),
        "groups": url_for("api.get_groups"),
        "users": url_for("api.get_users"),
        "templates": url_for("api.get_templates"),
    }

    return json_response(200, endpoints)
