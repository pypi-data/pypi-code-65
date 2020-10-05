# dbnomics-fetcher-toolbox
# Toolbox of functions and data types helping writing DBnomics fetchers.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2019 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-fetcher-toolbox
#
# dbnomics-fetcher-toolbox is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-fetcher-toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Functions dealing with file formats like JSON, `JSON Lines`_, XML or HTML.

.. _JSON Lines: https://jsonlines.org/
"""

from pathlib import Path
from typing import Any, Callable, Iterable

import daiquiri
import jsonlines
import ujson
from aiohttp import ClientSession
from lxml import etree
from lxml.etree import Element
from pydantic import BaseModel

logger = daiquiri.getLogger(__name__)


HTML_PARSER = etree.HTMLParser(encoding="utf-8")


async def fetch_xml(
    url: str, session: ClientSession, parser: etree._FeedParser = None
) -> Element:
    """Fetch an XML file from ``url`` using ``session``.

    A custom ``parser`` can be passed to ``etree.parse``.
    """
    async with session.get(url, raise_for_status=True) as response:
        response_text = await response.text()
    return etree.fromstring(response_text, parser=parser)


async def fetch_or_read_html(
    name: str,
    url: str,
    session: ClientSession,
    file: Path,
    force: bool = False,
    on_fetch: Callable[[Element], Element] = None,
) -> Element:
    """Fetch or read HTML.

    Just call :func:`fetch_or_read_xml` with ``parser=HTML_PARSER`` and
    ``xml_declaration=False``.
    """
    return await fetch_or_read_xml(
        name,
        url,
        session,
        file,
        force=force,
        parser=HTML_PARSER,
        on_fetch=on_fetch,
        xml_declaration=False,
    )


async def fetch_or_read_xml(
    name: str,
    url: str,
    session: ClientSession,
    file: Path,
    force: bool = False,
    parser: etree._FeedParser = None,
    on_fetch: Callable[[Element], Element] = None,
    xml_declaration: bool = True,
) -> Element:
    """Fetch or read XML.

    Load XML file from ``file`` or, if it does not exist,
    fetch it from ``url`` using ``session`` then save it to ``file``.
    In any case, read it and return an ``Element``.

    The ``name`` parameter allows to customize logging messages.

    The ``force`` parameter allows to force fetching instead of loading from file,
    even if the file exists.

    A custom ``parser`` can be passed to ``etree.parse``.

    ``on_fetch`` is a callback that takes the fetched ``Element`` and returns another.

    ``xml_declaration`` is passed to ``ElementTree.write``.

    Examples::

        keyfamilies_element = await fetch_or_read_xml(
            name="key families XML file",
            url=urljoin(args.api_base_url,
                        "/restsdmx/sdmx.ashx/GetDataStructure/all/all"),
            session=session,
            file=args.target_dir / "keyfamilies.xml",
            on_fetch=sdmx_v2_0.remove_prepared_date,
        )

        category_tree_element = await fetch_or_read_xml(
            name="category tree HTML file",
            url=args.api_base_url,
            session=session,
            file=args.target_dir / "category_tree.html",
            parser=HTML_PARSER,
            on_fetch=lambda element: element.find(
                './/{*}div[@id="browsethemes"]/ul[@class="treeview"]'
            ),
        )
    """
    if not force and file.is_file():
        logger.debug("%s already exists at %r, skipping", name, str(file))
        element = etree.parse(str(file), parser=parser).getroot()
    else:
        logger.debug("Downloading %s", name)
        element = await fetch_xml(url, session, parser)
        if on_fetch is not None:
            element = on_fetch(element)
        write_xml(file=file, element=element, xml_declaration=xml_declaration)
        logger.debug("%s written to %r", name, str(file))
    return element


def read_html(file: Path) -> Element:
    """Read HTML from ``file`` and return an ``Element``.

    Due to ``lxml.etree.HTMLParser``, the returned ``Element`` always starts with
    a ``<html>`` element so the caller has to call ``Element.find()`` in order to access
    the wanted child element.

    Call :func:`read_xml` with ``parser=HTML_PARSER``.
    """
    return read_xml(file, parser=HTML_PARSER)


def read_xml(file: Path, parser: etree._FeedParser = None) -> Element:
    """Read XML from ``file`` and return an ``Element``.

    A custom ``parser`` can be passed to ``etree.parse``.
    """
    return etree.parse(str(file), parser=parser).getroot()


def write_html(file: Path, element: Element, pretty_print: bool = True):
    """Encode ``element`` to HTML and write it to ``file``.

    ``pretty_print`` is passed to ``ElementTree.write``.
    """
    return write_xml(file, element, pretty_print=pretty_print, xml_declaration=False)


def write_xml(
    file: Path,
    element: Element,
    pretty_print: bool = True,
    xml_declaration: bool = True,
):
    """Encode ``data`` to XML and write it to ``file``.

    ``pretty_print`` and ``xml_declaration`` are passed to ``ElementTree.write``.
    """
    with file.open("wb") as f:
        etree.ElementTree(element).write(
            f,
            encoding="utf-8",
            pretty_print=pretty_print,
            xml_declaration=xml_declaration,
        )


def write_json(file: Path, data: Any):
    """Encode ``data`` to JSON and write it to ``file``."""
    if isinstance(data, BaseModel):
        text = data.json(ensure_ascii=False, indent=2, sort_keys=True)
        file.write_text(text)
        return

    if isinstance(data, str):
        file.write_text(data)
        return

    with file.open("w", encoding="utf-8") as f:
        ujson.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def write_jsonl(file: Path, items: Iterable[Any]):
    """Encode ``items`` to `JSON Lines`_ and write them to ``file``.

    .. _JSON Lines: https://jsonlines.org/
    """

    def dumps(obj):
        return ujson.dumps(obj, sort_keys=True, ensure_ascii=False)

    with jsonlines.open(file, mode="w", dumps=dumps) as writer:
        writer.write_all(items)
