# -*- coding: utf-8 -*-
# **********************************************************************
#
# Copyright (c) 2003-2017 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************
#
# Ice version 3.6.4
#
# <auto-generated>
#
# Generated from file `Internal.ice'
#
# Warning: do not edit this file.
#
# </auto-generated>
#

from sys import version_info as _version_info_
import Ice, IcePy

# Start of module omero
_M_omero = Ice.openModule('omero')
__name__ = 'omero'

# Start of module omero.grid
_M_omero.grid = Ice.openModule('omero.grid')
__name__ = 'omero.grid'

if 'ClusterNode' not in _M_omero.grid.__dict__:
    _M_omero.grid.ClusterNode = Ice.createTempClass()
    class ClusterNode(Ice.Object):
        """
        Interface implemented by each server instance. Instances lookup one
        another in the IceGrid registry.
        """
        def __init__(self):
            if Ice.getType(self) == _M_omero.grid.ClusterNode:
                raise RuntimeError('omero.grid.ClusterNode is an abstract class')

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::omero::grid::ClusterNode')

        def ice_id(self, current=None):
            return '::omero::grid::ClusterNode'

        def ice_staticId():
            return '::omero::grid::ClusterNode'
        ice_staticId = staticmethod(ice_staticId)

        def getNodeUuid(self, current=None):
            """
            Each node acquires the uuids of all other active nodes on start
            up. The uuid is an internal value and does not
            correspond to a session.
            Arguments:
            current -- The Current object for the invocation.
            """
            pass

        def down(self, uuid, current=None):
            """
            Let all cluster nodes know that the instance with this
            uuid is going down.
            Arguments:
            uuid -- 
            current -- The Current object for the invocation.
            """
            pass

        def __str__(self):
            return IcePy.stringify(self, _M_omero.grid._t_ClusterNode)

        __repr__ = __str__

    _M_omero.grid.ClusterNodePrx = Ice.createTempClass()
    class ClusterNodePrx(Ice.ObjectPrx):

        """
        Each node acquires the uuids of all other active nodes on start
        up. The uuid is an internal value and does not
        correspond to a session.
        Arguments:
        _ctx -- The request context for the invocation.
        """
        def getNodeUuid(self, _ctx=None):
            return _M_omero.grid.ClusterNode._op_getNodeUuid.invoke(self, ((), _ctx))

        """
        Each node acquires the uuids of all other active nodes on start
        up. The uuid is an internal value and does not
        correspond to a session.
        Arguments:
        _response -- The asynchronous response callback.
        _ex -- The asynchronous exception callback.
        _sent -- The asynchronous sent callback.
        _ctx -- The request context for the invocation.
        Returns: An asynchronous result object for the invocation.
        """
        def begin_getNodeUuid(self, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_omero.grid.ClusterNode._op_getNodeUuid.begin(self, ((), _response, _ex, _sent, _ctx))

        """
        Each node acquires the uuids of all other active nodes on start
        up. The uuid is an internal value and does not
        correspond to a session.
        Arguments:
        """
        def end_getNodeUuid(self, _r):
            return _M_omero.grid.ClusterNode._op_getNodeUuid.end(self, _r)

        """
        Let all cluster nodes know that the instance with this
        uuid is going down.
        Arguments:
        uuid -- 
        _ctx -- The request context for the invocation.
        """
        def down(self, uuid, _ctx=None):
            return _M_omero.grid.ClusterNode._op_down.invoke(self, ((uuid, ), _ctx))

        """
        Let all cluster nodes know that the instance with this
        uuid is going down.
        Arguments:
        uuid -- 
        _response -- The asynchronous response callback.
        _ex -- The asynchronous exception callback.
        _sent -- The asynchronous sent callback.
        _ctx -- The request context for the invocation.
        Returns: An asynchronous result object for the invocation.
        """
        def begin_down(self, uuid, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_omero.grid.ClusterNode._op_down.begin(self, ((uuid, ), _response, _ex, _sent, _ctx))

        """
        Let all cluster nodes know that the instance with this
        uuid is going down.
        Arguments:
        uuid -- 
        """
        def end_down(self, _r):
            return _M_omero.grid.ClusterNode._op_down.end(self, _r)

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_omero.grid.ClusterNodePrx.ice_checkedCast(proxy, '::omero::grid::ClusterNode', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_omero.grid.ClusterNodePrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

        def ice_staticId():
            return '::omero::grid::ClusterNode'
        ice_staticId = staticmethod(ice_staticId)

    _M_omero.grid._t_ClusterNodePrx = IcePy.defineProxy('::omero::grid::ClusterNode', ClusterNodePrx)

    _M_omero.grid._t_ClusterNode = IcePy.defineClass('::omero::grid::ClusterNode', ClusterNode, -1, (), True, False, None, (), ())
    ClusterNode._ice_type = _M_omero.grid._t_ClusterNode

    ClusterNode._op_getNodeUuid = IcePy.Operation('getNodeUuid', Ice.OperationMode.Idempotent, Ice.OperationMode.Idempotent, False, None, (), (), (), ((), IcePy._t_string, False, 0), ())
    ClusterNode._op_down = IcePy.Operation('down', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (((), IcePy._t_string, False, 0),), (), None, ())

    _M_omero.grid.ClusterNode = ClusterNode
    del ClusterNode

    _M_omero.grid.ClusterNodePrx = ClusterNodePrx
    del ClusterNodePrx

# End of module omero.grid

__name__ = 'omero'

# End of module omero
