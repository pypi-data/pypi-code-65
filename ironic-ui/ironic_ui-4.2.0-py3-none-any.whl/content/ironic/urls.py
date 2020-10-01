# Copyright 2016 Cisco Systems, Inc.
# Copyright (c) 2016 Hewlett Packard Enterprise Development Company LP
# Copyright (c) 2016 Cray Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import url

import ironic_ui.api.ironic_rest_api  # noqa
from ironic_ui.content.ironic import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^([^/]+)/$', views.DetailView.as_view(), name='detail'),
]
