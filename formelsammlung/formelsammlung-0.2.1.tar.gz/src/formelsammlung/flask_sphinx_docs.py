# noqa: D205,D208,D400
"""
    formelsammlung.flask_sphinx_docs
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Serve sphinx docs in your flask app.

    :copyright: (c) Christian Riedel
    :license: GPLv3
"""
from typing import Optional

from flask import Flask, Response


class SphinxDocServer:  # pylint: disable=R0903
    """Serve your sphinx docs under `/docs/` on your own flask app.

    .. highlight:: python

    You can either include the plugin directly::

        app = Flask(__name__)
        SphinxDocServer(app, doc_dir="../../docs/build/html")

    or you can invoke it in your app factory::

        sds = SphinxDocServer()

        def create_app():
            app = Flask(__name__)
            sds.init_app(app, doc_dir="../../docs/build/html"))
            return app

    .. highlight:: default
    """

    def __init__(self, app: Optional[Flask] = None, **kwargs) -> None:
        """Init SphinxDocServer."""
        if app is not None:
            self.init_app(app, **kwargs)

    @staticmethod
    def init_app(app: Flask, doc_dir: str, index_file: str = "index.html") -> None:
        """Add the `/docs/` route to the `app` object.

        :param app: Flask object to add the route to.
        :param doc_dir: The base directory holding the sphinx docs to serve.
        :param index_file: The html file containing the base toctree.
            Default: "index.html"
        """

        @app.route("/docs/", defaults={"filename": index_file})
        @app.route("/docs/<path:filename>")
        def web_docs(filename: str) -> Response:  # pylint: disable=W0612
            """Route the given doc page.

            :param filename: File name from URL
            :return: Requested doc page
            """
            app.static_folder = doc_dir
            doc_file = app.send_static_file(filename)
            app.static_folder = "static"
            return doc_file
