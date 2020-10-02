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
from marshmallow import fields

from kadi.lib.schemas import KadiSchema
from kadi.modules.accounts.schemas import UserSchema


class TaskSchema(KadiSchema):
    """Schema to represent tasks.

    See :class:`.Task`.
    """

    id = fields.String(dump_only=True)

    name = fields.String(dump_only=True)

    arguments = fields.Raw(dump_only=True)

    state = fields.String(dump_only=True)

    progress = fields.Integer(dump_only=True)

    result = fields.Raw(dump_only=True)

    creator = fields.Nested(UserSchema, dump_only=True)

    created_at = fields.DateTime(dump_only=True)

    last_modified = fields.DateTime(dump_only=True)
