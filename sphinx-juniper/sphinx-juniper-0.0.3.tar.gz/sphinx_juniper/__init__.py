"""A small sphinx extension to add "copy" buttons to code blocks."""
import os
from sphinx.util import logging
from docutils.parsers.rst import Directive, directives
from docutils import nodes
import json

from pathlib import Path


__version__ = "0.0.1"

logger = logging.getLogger(__name__)


def st_static_path(app):
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "_static"))
    app.config.html_static_path.append(static_path)


def init_juniper_core(app, env):
    if app.config["juniper"]:

        # defaults
        config_juniper = {
            "url": "https://mybinder.org",
            "repo": "ashtonmv/python_binder",
            "theme": "monokai",
            "isolateCells": "false",
            "useStorage": "true",
            "msgLoading": " ",
        }

        # user settings
        if isinstance(app.config["juniper"], dict):
            config_juniper.update(app.config["juniper"])

    else:
        logger.warning("Didn't find `juniper` in conf.py, add to use juniper")
        return

    # Add core libraries
    opts = {"async": "async"}
    app.add_js_file(filename="https://cdn.jsdelivr.net/gh/ashtonmv/nbjuniper@latest/cdn/juniper.min.js", **opts)

    theme = config_juniper["theme"]
    app.add_css_file(f"sphinx-juniper-base.css")
    static = os.path.realpath(__file__).replace("__init__.py", "_static")
    if os.path.isfile(os.path.join(static, f"sphinx-juniper-{theme}.css")):
        app.add_css_file(f"sphinx-juniper-{theme}.css")
    else:
        logger.warning(
            f"Selected juniper theme '{theme}' not supported."
            + " Falling back to default (monokai)."
        )
        config_juniper["theme"] = "monokai"
        app.add_css_file(f"sphinx-juniper-monokai.css")

    for k, v in config_juniper.items():
        if type(v) == bool or v.lower() in ["true", "false"]:
            config_juniper[k] = str(v).lower()
        else:
            config_juniper[k] = f"'{v}'"

    juniper_json = ", ".join(
        [f"{key}: {value}" for key, value in config_juniper.items()]
    ) 

    # Add configuration variables
    juniper_init = f"""
        function juniperInit() {{
            if (! $('.juniper-cell').length) {{
                for (var i=0; i<$('div.highlight').length; i++) {{
                    var codeBlock = $('div.highlight')[i];
                    if ($(codeBlock).parent().parent().hasClass('cell_input')) {{
                        var pre = $(codeBlock).find('pre').first();
                        $(pre).attr({{'data-executable': true}});
                        var copyBtn = $(codeBlock).find('.copybtn').first();
                        $(copyBtn).hide();
                    }}
                }}
                $('.cell_output').hide();
                $('div.cell').css('border', 'none');
                $('div.cell_input').css('border', 'none');
                const juniper = new Juniper({{ {juniper_json} }});
                startKernel(juniper);
            }}
        }}
    """
    app.add_js_file(None, body=juniper_init)
    app.add_js_file(filename="sphinx-juniper.js", **opts)


# Used to render an element node as HTML
def visit_element_html(self, node):
    self.body.append(node.html())
    raise nodes.SkipNode


# Used for nodes that do not need to be rendered
def skip(self, node):
    raise docutils.nodes.SkipNode


def setup(app):
    logger.verbose("Adding copy buttons to code blocks...")
    # Add our static path
    app.connect("builder-inited", st_static_path)

    # Include Juniper core files
    app.connect("env-updated", init_juniper_core)

    # Set default values for the configuration
    app.add_config_value("juniper", {}, "html")
    # override=True in case Jupyter Sphinx has already been loaded

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
