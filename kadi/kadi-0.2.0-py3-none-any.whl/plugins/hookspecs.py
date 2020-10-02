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
from pluggy import HookspecMarker


hookspec = HookspecMarker("kadi")


@hookspec
def kadi_register_blueprints(app):
    """Hook for registering blueprints.

    :param app: The application object.
    """


@hookspec
def kadi_template_index_before():
    """Template hook for prepending snippets to the index page.

    Used in :file:`modules/main/templates/main/index.html`.
    """


@hookspec
def kadi_template_home_before():
    """Template hook for prepending snippets to the home page.

    Used in :file:`modules/main/templates/main/home.html`.
    """


@hookspec
def kadi_template_base_footer_nav_before():
    """Template hook for prepending additional footer navigation items.

    Used in :file:`templates/base.html`.
    """


@hookspec
def kadi_template_base_footer_nav_after():
    """Template hook for appending additional footer navigation items.

    Used in :file:`templates/base.html`.
    """


@hookspec
def kadi_template_about_before():
    """Template hook for prepending snippets to the about page.

    Used in :file:`modules/main/templates/main/about.html`.
    """


@hookspec
def kadi_template_about_after():
    """Template hook for appending snippets to the about page.

    Used in :file:`modules/main/templates/main/about.html`.
    """


@hookspec
def kadi_template_help_nav_before():
    """Template hook for prepending navigation items to the help page.

    Used in :file:`modules/main/templates/main/help.html`.
    """


@hookspec
def kadi_template_help_nav_after():
    """Template hook for appending navigation items to the help page.

    Used in :file:`modules/main/templates/main/help.html`.
    """


@hookspec
def kadi_template_help_content_before():
    """Template hook for prepending snippets to the help page.

    Used in :file:`modules/main/templates/main/help.html`.
    """


@hookspec
def kadi_template_help_content_after():
    """Template hook for appending snippets to the help page.

    Used in :file:`modules/main/templates/main/help.html`.
    """
