# -*- coding: utf-8 -*-
"""
    sphinxcontrib.mscgenjs
    ~~~~~~~~~~~~~~~~~~~~~~

    Allow mscgen-formatted :abbr:`MSC (Message Sequence Chart)` graphs to be
    included in Sphinx-generated documents inline.
"""

from pathlib import Path

import pkg_resources
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.errors import SphinxError
from sphinx.util.fileutil import copy_asset_file
from sphinx.writers.html import HTMLTranslator

JS_FILENAME = 'mscgen-inpage.js'
JS_FILE_PATH = '_static/%s' % JS_FILENAME
LANGUAGES = (
    'json',
    'msgenny',
    'xu',
)


class MscgenJsError(SphinxError):
    category = 'mscgenjs error'


class MscgenJsNode(nodes.General, nodes.Element):
    pass


def is_language(argument):
    return directives.choice(argument, LANGUAGES)


class MscgenJs(Directive):
    """
    Directive to insert arbitrary mscgen markup for HTML documents.

    It will be embedded using mscgen.js_

    .. _mscgen.js: https://mscgen.js.org/embed.html#package
    """
    has_content = True
    required_arguments = 0
    option_spec = {
        "language": is_language
    }
    optional_arguments = len(option_spec)
    final_argument_whitespace = False

    def run(self):
        node = MscgenJsNode()
        node['code'] = '\n'.join(self.content)
        if "language" in self.options:
            node["language"] = self.options["language"]
        return [node]


def html_visit_mscgen(self: HTMLTranslator, node: MscgenJsNode):
    """
    Creates an html node with the user's MSC code that can be rendered by mscgen.js
    """
    options = {
        "class": "mscgen_js"
    }
    if "language" in node:
        options["data-language"] = node["language"]
    self.body.append(self.starttag(node, 'div', **options))
    self.body.append(node['code'])
    self.body.append('</div>\n')
    raise nodes.SkipNode


def copy_mscgen_js(app: Sphinx):
    """
    Copies the JS files that does the live rendering of MSC code

    Taken from `Theming guide <https://www.sphinx-doc.org/en/master/development/theming.html#add-your-own-static-files-to-the-build-assets>`_
    """
    _format = app.builder.format
    if _format == 'html':
        static_dir = Path(app.builder.outdir) / "_static"
        source_path = pkg_resources.resource_filename("sphinxcontrib.mscgenjs", JS_FILE_PATH)
        target_path = static_dir / JS_FILENAME
        if not target_path.exists():
            static_dir.mkdir(parents=True, exist_ok=True)
            copy_asset_file(source_path, static_dir)

        # defer: Needs to be loaded after all nodes are loaded in order to find them
        app.add_js_file(JS_FILENAME, defer="defer")


def setup(app: Sphinx) -> None:
    app.connect('builder-inited', copy_mscgen_js)
    app.add_node(MscgenJsNode,
                 html=(html_visit_mscgen, None),
                 )
    app.add_directive('mscgenjs', MscgenJs)
    # TODO review how this works
    # TODO: https://www.sphinx-doc.org/en/master/extdev/index.html#dev-extensions
    app.add_config_value('mscgenjs', 'mscgenjs', 'html')
    app.add_config_value('mscgenjs_args', [], 'html')
