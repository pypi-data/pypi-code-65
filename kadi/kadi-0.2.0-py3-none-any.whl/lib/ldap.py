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
import ldap3 as ldap
from flask import current_app


def bind(connection):
    """Try to authenticate with a server given an LDAP connection.

    Per default, LDAP connections are anonymous. The BIND operation establishes an
    authentication state between a client and a server.

    :param connection: The connection object, see also :func:`make_connection`.
    :return: ``True`` if the BIND operation was successful, ``False``
        otherwise.
    """
    try:
        return connection.bind()
    except Exception as e:
        current_app.logger.exception(e)
        unbind(connection)
        return False


def unbind(connection):
    """Disconnect a given LDAP connection.

    :param connection: The connection object, see also :func:`make_connection`.
    """
    try:
        connection.unbind()
    except Exception:
        pass


def make_server(hosts, strategy="FIRST", active=2, exhaust=60, **kwargs):
    r"""Create a new LDAP ``ServerPool`` object.

    :param hosts: The host names to use in the form of ``"ldap(s)://<host>:<port>"``,
        either as a single string or a list of strings for multiple hosts.
    :param strategy: (optional) The high availability strategy for the server pool. One
        of ``"FIRST"``, ``"ROUND_ROBIN"`` or ``"RANDOM"``.
    :param active: (optional) Maximum number of cycles to check each server for
        availability in the pool before giving up.
    :param exhaust: (optional) Number of seconds an unreachable server in the pool will
        be considered offline.
    :param \**kwargs: Additional keyword arguments to initialize each ``Server`` object
        with.
    :return: The new ``ServerPool`` object.
    """
    if not isinstance(hosts, list):
        hosts = [hosts]

    servers = []
    for host in hosts:
        try:
            server = ldap.Server(host, **kwargs)
            servers.append(server)
        except ldap.core.exceptions.LDAPInvalidServerError:
            pass

    if not servers:
        return None

    return ldap.ServerPool(
        servers, getattr(ldap, strategy, ldap.FIRST), active=active, exhaust=exhaust
    )


def make_connection(
    server, version=3, user=None, password=None, read_only=True, **kwargs
):
    r"""Create a new LDAP ``Connection`` object.

    :param server: The server pool to use for the connection. See :func:`make_server`.
    :param version: (optional) The LDAP protocol version.
    :param user: (optional) The user name for simple BIND.
    :param password: (optional) The password for simple BIND.
    :param read_only: (optional) Flag to indicate if operations that modify data should
        be permitted.
    :param \**kwargs: Additional keyword arguments to pass to the ``Connection`` object.
    :return: The new ``Connection`` object.
    """
    return ldap.Connection(
        server,
        version=version,
        user=user,
        password=password,
        read_only=read_only,
        **kwargs
    )


def search(
    connection, search_base, search_filter, attribute_map, keep_list_attrs=False
):
    """Perform a search in an LDAP database given a connection.

    :param connection: The LDAP connection. See :func:`make_connection`.
    :param search_base: The base of the search request.
    :param search_filter: The filter of the search request.
    :param attribute_map: A dictionary mapping arbitrary names to LDAP attribute names.
        The former names specify the keys to use for each search result (e.g.
        ``"firstname"``), while the latter names specify the name of the attribute that
        should be extracted from the resulting LDAP entry (e.g. ``"givenName"``).
    :param keep_list_attrs: (optional) Flag to indicate if results that have multiple
        values should be returned as lists or not. If not, only the first value of a
        result will be returned.
    :return: A dictionary similar to the given ``attribute_map``. The LDAP attribute
        names will be replaced by the respective result value(s) or with ``None`` if the
        attribute could not be found.
    """
    if not connection.bound and not bind(connection):
        return None

    connection.search(search_base, search_filter, attributes=ldap.ALL_ATTRIBUTES)

    if len(connection.entries) != 1:
        return None

    entry = connection.entries[0]

    results = {}
    for attr, ldap_attr in attribute_map.items():
        try:
            value = entry[ldap_attr].value
            if isinstance(value, list) and not keep_list_attrs:
                value = value[0]

            results[attr] = value
        except ldap.core.exceptions.LDAPKeyError:
            results[attr] = None

    return results
