#!/usr/bin/env python

"""
Converts notebooks to interactive HTML pages with Juniper + Binder.

Standalone usage:
  nbjuniper TARGET (+ optional flags below)

  `nbjuniper example_notebook.ipynb` converts example_notebook.ipynb into
  example_notebook.html.

Jupyter-book usage:
  nbjuniper -j TARGET (+ optional flags below)

  `nbjuniper -j docs/` recursively adds a "Juniper" button to the dropdown menu
  of all HTML files under docs/. Clicking the button will convert all code cells
  to juniper cells.

Arguments:
  TARGET                     IPython notebook to convert. If TARGET is a
                             directory, nbjuniper will render all .ipynb files
                             in that directory (non-recursively by default).

Options:
  -h --help                  Show this screen.

  -j                         switch mode from "normal" (default) to 
                             "jupyter-book". "jupyter-book" recursively converts
                             a folder full of already-built (by `jupyter-book
                             build`) html files into juniper-enabled html files.

  -f FILENAME                yaml file containing specific settings for the
                             Juniper client. See
                             https://github.com/ines/juniper for all
                             possibilities, and this project's README.md for an
                             example.

  -r TARGET                  Recursively render all .ipynb files within TARGET
                             (should be a directory)

  --no-head                  Skip writing the HTML head to the page.

  --decapitate               Write the HTML head to a separate file
                             (juniper_head.html).

  --binderhub BINDERHUB      BinderHub instance to which to connect (default
                             is https://mybinder.org).

  --repo REPO                Github repository used to build Binder Docker
                             image on the BinderHub. (default is the very
                             minimal ashtonmv/python_binder).

  --theme THEME              Default theme is monokai. Must be a theme under
                             nbjuniper/cdn/styles
"""

import os
import json
import yaml
import sys
from markdown import markdown


CDN_RELEASE = "0.3.1"


def collect_notebooks(directory, extension, recursive=False):
    if recursive:
        paths = []
        for root, dirs, files in os.walk(directory):
            for name in files:
                path = os.path.join(root, name)
                if os.path.isfile(path) and path.endswith(extension):
                    paths.append(path)
    else:
        paths = [os.path.join(directory, nb) for nb in
                   os.listdir(directory) if nb.endswith(extension)]
    return paths


def get_settings():

    # Defaults
    settings = {
        "url": "https://mybinder.org",
        "repo": "ashtonmv/python_binder",
        "theme": "monokai",
        "msgLoading": " ",
        "useStorage": True,
        "isolateCells": False
    }

    for i, arg in enumerate(sys.argv):
        if arg.lower() == "-f":
            with open(sys.argv[i+1]) as f:
                settings.update(yaml.safe_load(f))

        elif arg.lower() == "--binderhub":
            settings.update({"url": sys.argv[i+1]})

        elif arg.lower() == "--repo":
            settings.update({"repo": sys.argv[i+1]})

        elif arg.lower() == "--theme":
            settings.update({"theme": sys.argv[i+1]})

    return settings


def main():

    notebooks = {}
    settings = get_settings()

    css_base = "juniperpage"
    if "-j" in sys.argv or "jupyter-book" in sys.argv:
        mode = "jupyter-book"
        css_base = "juniperbook"
    else:
        mode = "normal"

    directory = None

    if len([arg for arg in sys.argv if os.path.isdir(arg)]) != 0:
        directory = [arg for arg in sys.argv if os.path.isdir(arg)][0]

    for i, arg in enumerate(sys.argv):

        if i == 1:

            if arg.lower() in ["-h", "--help"]:
                print(__doc__)
                return

            elif mode == "normal":
                
                if os.path.isfile(arg):
                    with open(arg) as f:
                        notebooks[arg] = json.load(f)

                elif directory:
                    notebooks = {}
                    recursive = "-r" in sys.argv

                    paths = collect_notebooks(
                        directory,
                        extension=".ipynb",
                        recursive=recursive
                    )

                    for path in paths:
                        with open(path) as f:
                            notebooks[path] = json.load(f)

            elif mode == "jupyter-book":
                notebooks = [
                    nb for nb in collect_notebooks(
                        directory,
                        extension=".html",
                        recursive=True
                    )
                    if "cell docutils container" in open(nb).read()
                ]

    if len(notebooks) == 0:
        raise ValueError(
            "No convertable notebooks were found at the specified location."
            + " Please try nbjuniper -h for more information."
        )

    theme = settings["theme"]

    for k, v in settings.items():
        if type(v) != bool:
            settings[k] = f"'{v}'"
        else:
            settings[k] = str(v).lower()

    juniper_json = ", ".join(
        [f"{key}: {value}" for key, value in settings.items()]
    ) 

    juniper_init = (
        "<script>function juniperInit() {"
        + "if (! $('.juniper-cell').length) {"
        + "for (var i=0; i<$('div.highlight').length; i++) {"
        + "var codeBlock = $('div.highlight')[i];"
        + "if ($(codeBlock).parent().parent().hasClass('cell_input')) {"
        + "var pre = $(codeBlock).find('pre').first();"
        + "$(pre).attr({'data-executable': true});"
        + "var copyBtn = $(codeBlock).find('.copybtn').first();"
        + "$(copyBtn).hide(); } }"
        + "$('.cell_output').hide();"
        + f"var juniper = new Juniper({{ {juniper_json} }});"
        + "startKernel(juniper);"
        + "} };</script>"
    )

    juniper_button = (
        "<script>$(document).ready( function() {"
        + "var dropdown = $(document).find('.dropdown-buttons').last();"
        + "$(\"<a class='dropdown-buttons' onclick='juniperInit()'>"
        + "<button type='button' class='btn btn-secondary topbarbtn' title=''"
        + "data-toggle='tooltip' data-placement='left'"
        + "data-original-title='Initialize Juniper'><i class='fas fa-bolt'></i>"
        + "Juniper</button></a>\").appendTo(dropdown);"
        + "});</script>"
    )

    head = [
        f"<script type='text/javascript' src='https://cdn.jsdelivr.net/gh/ashtonmv/nbjuniper@{CDN_RELEASE}/cdn/juniper.min.js'></script>",
        f"<script type='text/javascript' src='https://cdn.jsdelivr.net/gh/ashtonmv/nbjuniper@{CDN_RELEASE}/cdn/events.min.js'></script>",
        "<script type='text/javascript' src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML'></script>",
        f"<link rel='stylesheet' href='https://cdn.jsdelivr.net/gh/ashtonmv/nbjuniper@{CDN_RELEASE}/cdn/styles/{css_base}.min.css'></link>",
        f"<link rel='stylesheet' href='https://cdn.jsdelivr.net/gh/ashtonmv/nbjuniper@{CDN_RELEASE}/cdn/styles/{theme}.min.css'></link>",
    ]

    if mode == "normal":
        head.insert(0, "<script type='text/javascript' src='https://code.jquery.com/jquery-3.5.1.min.js'></script>")
        head.insert(4, f"<script>$(document).ready(function() {{var juniper = new Juniper({{ {juniper_json} }}); startKernel(juniper);}});</script>",
)
        for filename in notebooks:
            notebook = notebooks[filename]
            body = ["<body>"]
            body.append("<div class='juniper-notebook'>")
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    body.append("<pre data-executable>")
                    body.append("".join(cell["source"]))
                    body.append("</pre>")
                else:
                    body.append(markdown("".join(cell["source"])))
            body.append("</div>")
            body.append("</body>")

            if "--no-head" not in sys.argv and "--decapitate" not in sys.argv:
                with open(filename.replace("ipynb", "html"), "w") as o:
                    o.write("<head>")
                    o.write("\n".join(head))
                    o.write("</head>")
                    o.write("\n".join(body))
            else:
                with open(filename.replace("ipynb", "html"), "w") as o:
                    o.write("\n".join(body))

        if "--no-head" not in sys.argv:
            with open("juniper_head.html", "w") as o:
                o.write("\n".join(head))

    elif mode == "jupyter-book":

        head.insert(0, "<!-- begin nbjuniper head -->")
        head.insert(4, juniper_init)
        head.append(juniper_button)
        head.append("<!-- end nbjuniper head -->")

        for filename in notebooks:
            raw_lines = open(filename).readlines()
            with open(filename, "w") as f:
                write = True
                for line in raw_lines:
                    if "begin nbjuniper head" in line:
                        write = False
                    if write:
                        if "</head>" in line:
                            f.write("\n".join(head))
                            f.write("\n")
                        f.write(line)
                    if "end nbjuniper head" in line:
                        write = True


if __name__ == "__main__":
    main()
