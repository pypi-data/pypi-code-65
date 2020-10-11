"""
This module contains classes associated with making a simple filtered http
web server that will vend whitelisted files.
"""
import logging
import urllib.parse
import os
import io
from functools import partial
from threading import Thread
import html
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import HTTPStatus


class FilteredHTTPRequestHandler(SimpleHTTPRequestHandler):
    """
    Handler for filtered requests
    """

    def __init__(
        self,
        *args,
        whitelist=None,
        whitelist_case_sensitive=False,
        allow_listing=True,
        **kwargs,
    ):
        self.allow_listing = allow_listing
        self.whitelist = whitelist
        self.whitelist_case_sensitive = whitelist_case_sensitive
        super().__init__(*args, **kwargs)

    def send_head(self):
        """
        Common code for GET and HEAD commands.
        """
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)

            if not parts.path.endswith("/"):
                # Browser redirect
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + "/", parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None

            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)

        # Reject non whitelisted files if given a whitelist
        if self.whitelist:
            parts = self.path.split("/")
            if self.whitelist_case_sensitive:
                part = parts[-1]
            else:
                part = parts[-1].lower()

            if part not in self.whitelist:
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return None

        # Return the content
        content_type = self.guess_type(path)
        try:
            content = open(path, "rb")
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            file_stats = os.fstat(content.fileno())
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", content_type)
            self.send_header("Content-Length", str(file_stats[6]))
            self.send_header(
                "Last-Modified", self.date_time_string(file_stats.st_mtime)
            )
            self.end_headers()
            return content
        except:
            content.close()
            raise

    def list_directory(self, path):  # pylint:disable=too-many-locals
        """
        Helper to produce a directory listing (absent index.html).

        Filter out any non-white listed files in the directory.
        """
        # Shortcut return none if not allowed to list
        if not self.allow_listing:
            self.send_error(HTTPStatus.NOT_FOUND, "No permission to list directory")
            return None

        try:
            directory_listing = os.listdir(path)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "No permission to list directory")
            return None
        directory_listing.sort(key=lambda a: a.lower())

        # Keep only whitelisted files
        if self.whitelist:
            filtered_list = []
            for file in directory_listing:
                if not self.whitelist_case_sensitive:
                    file_check = file.lower()
                else:
                    file_check = file
                if file_check in self.whitelist:
                    filtered_list.append(file)
            directory_listing = filtered_list

        body = []
        try:
            display_path = urllib.parse.unquote(self.path, errors="surrogatepass")
        except UnicodeDecodeError:
            display_path = urllib.parse.unquote(path)

        display_path = html.escape(display_path, quote=False)
        enc = sys.getfilesystemencoding()
        title = "Directory listing for %s" % display_path
        body.append(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
            '"http://www.w3.org/TR/html4/strict.dtd">'
        )
        body.append("<html>\n<head>")
        body.append(
            '<meta http-equiv="Content-Type" ' 'content="text/html; charset=%s">' % enc
        )
        body.append("<title>%s</title>\n</head>" % title)
        body.append("<body>\n<h1>%s</h1>" % title)
        body.append("<hr>\n<ul>")

        for name in directory_listing:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            body.append(
                '<li><a href="%s">%s</a></li>'
                % (
                    urllib.parse.quote(linkname, errors="surrogatepass"),
                    html.escape(displayname, quote=False),
                )
            )
        body.append("</ul>\n<hr>\n</body>\n</html>\n")
        encoded = "\n".join(body).encode(enc, "surrogateescape")
        out_stream = io.BytesIO()
        out_stream.write(encoded)
        out_stream.seek(0)

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        return out_stream


class FilteredWebServer(Thread):
    """
    This is a simple web server that also has a white listing mechanism
    """

    def __init__(
        self,
        host="0.0.0.0",
        host_port=80,
        host_directory=os.getcwd(),
        whitelist=None,
        allow_listing=True,
        whitelist_case_sensitive=False,
    ):
        """
        Simple Filtered Web Server allows vending files from a directory with
        a whitelist of allowed files.

        :param str host: host address to listen on
        :param int host_port: port to serve from
        :param str host_directory: directory to serve from
        :param list whitelist: a list of filenames to whitelist from the
            host directory.
        :param bool allow_listing: allow listing the index of the webserver
        :param bool whitelist_case_sensitive: whether or not to treat the white
            list as case sensitive (otherwise the list items will be put to
            lowercase)
        """
        self.logger = logging.getLogger(f"FilteredWebServer_{host_port}")
        self.logger.info("Initialising web server...")
        self.host = host
        self.host_port = host_port
        self.host_directory = host_directory

        # Clean whitelisted files based on case sensitivity
        if not whitelist_case_sensitive:
            self.whitelist = [file.lower().strip() for file in whitelist]
        else:
            self.whitelist = [file.trim() for file in whitelist]

        self.allow_listing = allow_listing
        self.server_address = (self.host, self.host_port)

        self.handler = partial(
            FilteredHTTPRequestHandler,
            whitelist=self.whitelist,
            whitelist_case_sensitive=whitelist_case_sensitive,
            allow_listing=self.allow_listing,
            directory=self.host_directory,
        )
        self.httpd_server = HTTPServer(self.server_address, self.handler)

        super().__init__()

    def run(self):
        """
        Run the server
        """
        self.logger.info(
            "Starting Server on port %s out of directory %s",
            self.host_port,
            self.host_directory,
        )
        if self.whitelist is not None:
            self.logger.info("Serving the following white listed files:")
            for file in self.whitelist:
                self.logger.info("\t- %s", file)
        self.httpd_server.serve_forever()

    def stop(self):
        """
        Stop the server
        """
        self.httpd_server.shutdown()
