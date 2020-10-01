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
# Generated from file `IProjection.ice'
#
# Warning: do not edit this file.
#
# </auto-generated>
#

from sys import version_info as _version_info_
import Ice, IcePy
import omero_ModelF_ice
import omero_ServicesF_ice
import omero_Collections_ice
import omero_Constants_ice

# Included module omero
_M_omero = Ice.openModule('omero')

# Included module omero.model
_M_omero.model = Ice.openModule('omero.model')

# Included module Ice
_M_Ice = Ice.openModule('Ice')

# Included module Glacier2
_M_Glacier2 = Ice.openModule('Glacier2')

# Included module omero.sys
_M_omero.sys = Ice.openModule('omero.sys')

# Included module omero.api
_M_omero.api = Ice.openModule('omero.api')

# Included module omero.grid
_M_omero.grid = Ice.openModule('omero.grid')

# Included module omero.constants
_M_omero.constants = Ice.openModule('omero.constants')

# Included module omero.constants.cluster
_M_omero.constants.cluster = Ice.openModule('omero.constants.cluster')

# Included module omero.constants.annotation
_M_omero.constants.annotation = Ice.openModule('omero.constants.annotation')

# Included module omero.constants.annotation.file
_M_omero.constants.annotation.file = Ice.openModule('omero.constants.annotation.file')

# Included module omero.constants.data
_M_omero.constants.data = Ice.openModule('omero.constants.data')

# Included module omero.constants.metadata
_M_omero.constants.metadata = Ice.openModule('omero.constants.metadata')

# Included module omero.constants.namespaces
_M_omero.constants.namespaces = Ice.openModule('omero.constants.namespaces')

# Included module omero.constants.analysis
_M_omero.constants.analysis = Ice.openModule('omero.constants.analysis')

# Included module omero.constants.analysis.flim
_M_omero.constants.analysis.flim = Ice.openModule('omero.constants.analysis.flim')

# Included module omero.constants.jobs
_M_omero.constants.jobs = Ice.openModule('omero.constants.jobs')

# Included module omero.constants.permissions
_M_omero.constants.permissions = Ice.openModule('omero.constants.permissions')

# Included module omero.constants.projection
_M_omero.constants.projection = Ice.openModule('omero.constants.projection')

# Included module omero.constants.topics
_M_omero.constants.topics = Ice.openModule('omero.constants.topics')

# Included module omero.constants.categories
_M_omero.constants.categories = Ice.openModule('omero.constants.categories')

# Start of module omero
__name__ = 'omero'

# Start of module omero.api
__name__ = 'omero.api'

if 'IProjection' not in _M_omero.api.__dict__:
    _M_omero.api.IProjection = Ice.createTempClass()
    class IProjection(_M_omero.api.ServiceInterface):
        """
        Provides methods for performing projections of Pixels sets.
        """
        def __init__(self):
            if Ice.getType(self) == _M_omero.api.IProjection:
                raise RuntimeError('omero.api.IProjection is an abstract class')

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::omero::api::IProjection', '::omero::api::ServiceInterface')

        def ice_id(self, current=None):
            return '::omero::api::IProjection'

        def ice_staticId():
            return '::omero::api::IProjection'
        ice_staticId = staticmethod(ice_staticId)

        def projectStack_async(self, _cb, pixelsId, pixelsType, algorithm, timepoint, channelIndex, stepping, start, end, current=None):
            """
            Performs a projection through the optical sections of a
            particular wavelength at a given time point of a Pixels set.
            Arguments:
            _cb -- The asynchronous callback object.
            pixelsId -- The source Pixels set Id.
            pixelsType -- The destination Pixels type. If null, the source Pixels set pixels type will be used.
            algorithm -- MAXIMUM_INTENSITY, MEAN_INTENSITY or SUM_INTENSITY. NOTE: When performing a SUM_INTENSITY projection, pixel values will be pinned to the maximum pixel value of the destination Pixels type.
            timepoint -- Timepoint to perform the projection.
            channelIndex -- Index of the channel to perform the projection.
            stepping -- Stepping value to use while calculating the projection. For example, stepping=1 will use every optical section from start to end where stepping=2 will use every other section from start to end to perform the projection.
            start -- Optical section to start projecting from.
            end -- Optical section to finish projecting.
            current -- The Current object for the invocation.
            Throws:
            ValidationException -- Where: algorithm is unknown timepoint is out of range channelIndex is out of range start is out of range end is out of range start is greater than end the Pixels set qualified by pixelsId is not locatable.
            """
            pass

        def projectPixels_async(self, _cb, pixelsId, pixelsType, algorithm, tStart, tEnd, channelList, stepping, zStart, zEnd, name, current=None):
            """
            Performs a projection through selected optical sections and
            optical sections for a given set of time points of a Pixels
            set. The Image which is linked to the Pixels set will be
            copied using
            {@code omero.api.IPixels.copyAndResizeImage}.
            Arguments:
            _cb -- The asynchronous callback object.
            pixelsId -- The source Pixels set Id.
            pixelsType -- The destination Pixels type. If null, the source Pixels set pixels type will be used.
            algorithm -- MAXIMUM_INTENSITY, MEAN_INTENSITY or SUM_INTENSITY. NOTE: When performing a SUM_INTENSITY projection, pixel values will be pinned to the maximum pixel value of the destination Pixels type.
            tStart -- Timepoint to start projecting from.
            tEnd -- Timepoint to finish projecting.
            channelList -- List of the channel indexes to use while calculating the projection.
            stepping -- Stepping value to use while calculating the projection. For example, stepping=1 will use every optical section from start to end where stepping=2 will use every other section from start to end to perform the projection.
            zStart -- Optical section to start projecting from.
            zEnd -- Optical section to finish projecting.
            name -- Name for the newly created image. If null the name of the Image linked to the Pixels qualified by pixelsId will be used with a Projection suffix. For example, GFP-H2B Image of HeLa Cells will have an Image name of GFP-H2B Image of HeLa Cells Projection used for the projection.
            current -- The Current object for the invocation.
            Throws:
            ValidationException -- Where: algorithm is unknown tStart is out of range tEnd is out of range tStart is greater than tEnd channelList is null or has indexes out of range zStart is out of range zEnd is out of range zStart is greater than zEnd the Pixels set qualified by pixelsId is not locatable.
            """
            pass

        def __str__(self):
            return IcePy.stringify(self, _M_omero.api._t_IProjection)

        __repr__ = __str__

    _M_omero.api.IProjectionPrx = Ice.createTempClass()
    class IProjectionPrx(_M_omero.api.ServiceInterfacePrx):

        """
        Performs a projection through the optical sections of a
        particular wavelength at a given time point of a Pixels set.
        Arguments:
        pixelsId -- The source Pixels set Id.
        pixelsType -- The destination Pixels type. If null, the source Pixels set pixels type will be used.
        algorithm -- MAXIMUM_INTENSITY, MEAN_INTENSITY or SUM_INTENSITY. NOTE: When performing a SUM_INTENSITY projection, pixel values will be pinned to the maximum pixel value of the destination Pixels type.
        timepoint -- Timepoint to perform the projection.
        channelIndex -- Index of the channel to perform the projection.
        stepping -- Stepping value to use while calculating the projection. For example, stepping=1 will use every optical section from start to end where stepping=2 will use every other section from start to end to perform the projection.
        start -- Optical section to start projecting from.
        end -- Optical section to finish projecting.
        _ctx -- The request context for the invocation.
        Returns: A byte array of projected pixel values whose length is equal to the Pixels set 8         sizeX * sizeY * bytesPerPixel in big-endian format.
        Throws:
        ValidationException -- Where: algorithm is unknown timepoint is out of range channelIndex is out of range start is out of range end is out of range start is greater than end the Pixels set qualified by pixelsId is not locatable.
        """
        def projectStack(self, pixelsId, pixelsType, algorithm, timepoint, channelIndex, stepping, start, end, _ctx=None):
            return _M_omero.api.IProjection._op_projectStack.invoke(self, ((pixelsId, pixelsType, algorithm, timepoint, channelIndex, stepping, start, end), _ctx))

        """
        Performs a projection through the optical sections of a
        particular wavelength at a given time point of a Pixels set.
        Arguments:
        pixelsId -- The source Pixels set Id.
        pixelsType -- The destination Pixels type. If null, the source Pixels set pixels type will be used.
        algorithm -- MAXIMUM_INTENSITY, MEAN_INTENSITY or SUM_INTENSITY. NOTE: When performing a SUM_INTENSITY projection, pixel values will be pinned to the maximum pixel value of the destination Pixels type.
        timepoint -- Timepoint to perform the projection.
        channelIndex -- Index of the channel to perform the projection.
        stepping -- Stepping value to use while calculating the projection. For example, stepping=1 will use every optical section from start to end where stepping=2 will use every other section from start to end to perform the projection.
        start -- Optical section to start projecting from.
        end -- Optical section to finish projecting.
        _response -- The asynchronous response callback.
        _ex -- The asynchronous exception callback.
        _sent -- The asynchronous sent callback.
        _ctx -- The request context for the invocation.
        Returns: An asynchronous result object for the invocation.
        """
        def begin_projectStack(self, pixelsId, pixelsType, algorithm, timepoint, channelIndex, stepping, start, end, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_omero.api.IProjection._op_projectStack.begin(self, ((pixelsId, pixelsType, algorithm, timepoint, channelIndex, stepping, start, end), _response, _ex, _sent, _ctx))

        """
        Performs a projection through the optical sections of a
        particular wavelength at a given time point of a Pixels set.
        Arguments:
        pixelsId -- The source Pixels set Id.
        pixelsType -- The destination Pixels type. If null, the source Pixels set pixels type will be used.
        algorithm -- MAXIMUM_INTENSITY, MEAN_INTENSITY or SUM_INTENSITY. NOTE: When performing a SUM_INTENSITY projection, pixel values will be pinned to the maximum pixel value of the destination Pixels type.
        timepoint -- Timepoint to perform the projection.
        channelIndex -- Index of the channel to perform the projection.
        stepping -- Stepping value to use while calculating the projection. For example, stepping=1 will use every optical section from start to end where stepping=2 will use every other section from start to end to perform the projection.
        start -- Optical section to start projecting from.
        end -- Optical section to finish projecting.
        Returns: A byte array of projected pixel values whose length is equal to the Pixels set 8         sizeX * sizeY * bytesPerPixel in big-endian format.
        Throws:
        ValidationException -- Where: algorithm is unknown timepoint is out of range channelIndex is out of range start is out of range end is out of range start is greater than end the Pixels set qualified by pixelsId is not locatable.
        """
        def end_projectStack(self, _r):
            return _M_omero.api.IProjection._op_projectStack.end(self, _r)

        """
        Performs a projection through selected optical sections and
        optical sections for a given set of time points of a Pixels
        set. The Image which is linked to the Pixels set will be
        copied using
        {@code omero.api.IPixels.copyAndResizeImage}.
        Arguments:
        pixelsId -- The source Pixels set Id.
        pixelsType -- The destination Pixels type. If null, the source Pixels set pixels type will be used.
        algorithm -- MAXIMUM_INTENSITY, MEAN_INTENSITY or SUM_INTENSITY. NOTE: When performing a SUM_INTENSITY projection, pixel values will be pinned to the maximum pixel value of the destination Pixels type.
        tStart -- Timepoint to start projecting from.
        tEnd -- Timepoint to finish projecting.
        channelList -- List of the channel indexes to use while calculating the projection.
        stepping -- Stepping value to use while calculating the projection. For example, stepping=1 will use every optical section from start to end where stepping=2 will use every other section from start to end to perform the projection.
        zStart -- Optical section to start projecting from.
        zEnd -- Optical section to finish projecting.
        name -- Name for the newly created image. If null the name of the Image linked to the Pixels qualified by pixelsId will be used with a Projection suffix. For example, GFP-H2B Image of HeLa Cells will have an Image name of GFP-H2B Image of HeLa Cells Projection used for the projection.
        _ctx -- The request context for the invocation.
        Returns: The Id of the newly created Image which has been projected.
        Throws:
        ValidationException -- Where: algorithm is unknown tStart is out of range tEnd is out of range tStart is greater than tEnd channelList is null or has indexes out of range zStart is out of range zEnd is out of range zStart is greater than zEnd the Pixels set qualified by pixelsId is not locatable.
        """
        def projectPixels(self, pixelsId, pixelsType, algorithm, tStart, tEnd, channelList, stepping, zStart, zEnd, name, _ctx=None):
            return _M_omero.api.IProjection._op_projectPixels.invoke(self, ((pixelsId, pixelsType, algorithm, tStart, tEnd, channelList, stepping, zStart, zEnd, name), _ctx))

        """
        Performs a projection through selected optical sections and
        optical sections for a given set of time points of a Pixels
        set. The Image which is linked to the Pixels set will be
        copied using
        {@code omero.api.IPixels.copyAndResizeImage}.
        Arguments:
        pixelsId -- The source Pixels set Id.
        pixelsType -- The destination Pixels type. If null, the source Pixels set pixels type will be used.
        algorithm -- MAXIMUM_INTENSITY, MEAN_INTENSITY or SUM_INTENSITY. NOTE: When performing a SUM_INTENSITY projection, pixel values will be pinned to the maximum pixel value of the destination Pixels type.
        tStart -- Timepoint to start projecting from.
        tEnd -- Timepoint to finish projecting.
        channelList -- List of the channel indexes to use while calculating the projection.
        stepping -- Stepping value to use while calculating the projection. For example, stepping=1 will use every optical section from start to end where stepping=2 will use every other section from start to end to perform the projection.
        zStart -- Optical section to start projecting from.
        zEnd -- Optical section to finish projecting.
        name -- Name for the newly created image. If null the name of the Image linked to the Pixels qualified by pixelsId will be used with a Projection suffix. For example, GFP-H2B Image of HeLa Cells will have an Image name of GFP-H2B Image of HeLa Cells Projection used for the projection.
        _response -- The asynchronous response callback.
        _ex -- The asynchronous exception callback.
        _sent -- The asynchronous sent callback.
        _ctx -- The request context for the invocation.
        Returns: An asynchronous result object for the invocation.
        """
        def begin_projectPixels(self, pixelsId, pixelsType, algorithm, tStart, tEnd, channelList, stepping, zStart, zEnd, name, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_omero.api.IProjection._op_projectPixels.begin(self, ((pixelsId, pixelsType, algorithm, tStart, tEnd, channelList, stepping, zStart, zEnd, name), _response, _ex, _sent, _ctx))

        """
        Performs a projection through selected optical sections and
        optical sections for a given set of time points of a Pixels
        set. The Image which is linked to the Pixels set will be
        copied using
        {@code omero.api.IPixels.copyAndResizeImage}.
        Arguments:
        pixelsId -- The source Pixels set Id.
        pixelsType -- The destination Pixels type. If null, the source Pixels set pixels type will be used.
        algorithm -- MAXIMUM_INTENSITY, MEAN_INTENSITY or SUM_INTENSITY. NOTE: When performing a SUM_INTENSITY projection, pixel values will be pinned to the maximum pixel value of the destination Pixels type.
        tStart -- Timepoint to start projecting from.
        tEnd -- Timepoint to finish projecting.
        channelList -- List of the channel indexes to use while calculating the projection.
        stepping -- Stepping value to use while calculating the projection. For example, stepping=1 will use every optical section from start to end where stepping=2 will use every other section from start to end to perform the projection.
        zStart -- Optical section to start projecting from.
        zEnd -- Optical section to finish projecting.
        name -- Name for the newly created image. If null the name of the Image linked to the Pixels qualified by pixelsId will be used with a Projection suffix. For example, GFP-H2B Image of HeLa Cells will have an Image name of GFP-H2B Image of HeLa Cells Projection used for the projection.
        Returns: The Id of the newly created Image which has been projected.
        Throws:
        ValidationException -- Where: algorithm is unknown tStart is out of range tEnd is out of range tStart is greater than tEnd channelList is null or has indexes out of range zStart is out of range zEnd is out of range zStart is greater than zEnd the Pixels set qualified by pixelsId is not locatable.
        """
        def end_projectPixels(self, _r):
            return _M_omero.api.IProjection._op_projectPixels.end(self, _r)

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_omero.api.IProjectionPrx.ice_checkedCast(proxy, '::omero::api::IProjection', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_omero.api.IProjectionPrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

        def ice_staticId():
            return '::omero::api::IProjection'
        ice_staticId = staticmethod(ice_staticId)

    _M_omero.api._t_IProjectionPrx = IcePy.defineProxy('::omero::api::IProjection', IProjectionPrx)

    _M_omero.api._t_IProjection = IcePy.defineClass('::omero::api::IProjection', IProjection, -1, (), True, False, None, (_M_omero.api._t_ServiceInterface,), ())
    IProjection._ice_type = _M_omero.api._t_IProjection

    IProjection._op_projectStack = IcePy.Operation('projectStack', Ice.OperationMode.Normal, Ice.OperationMode.Normal, True, None, (), (((), IcePy._t_long, False, 0), ((), _M_omero.model._t_PixelsType, False, 0), ((), _M_omero.constants.projection._t_ProjectionType, False, 0), ((), IcePy._t_int, False, 0), ((), IcePy._t_int, False, 0), ((), IcePy._t_int, False, 0), ((), IcePy._t_int, False, 0), ((), IcePy._t_int, False, 0)), (), ((), _M_Ice._t_ByteSeq, False, 0), (_M_omero._t_ServerError,))
    IProjection._op_projectPixels = IcePy.Operation('projectPixels', Ice.OperationMode.Normal, Ice.OperationMode.Normal, True, None, (), (((), IcePy._t_long, False, 0), ((), _M_omero.model._t_PixelsType, False, 0), ((), _M_omero.constants.projection._t_ProjectionType, False, 0), ((), IcePy._t_int, False, 0), ((), IcePy._t_int, False, 0), ((), _M_omero.sys._t_IntList, False, 0), ((), IcePy._t_int, False, 0), ((), IcePy._t_int, False, 0), ((), IcePy._t_int, False, 0), ((), IcePy._t_string, False, 0)), (), ((), IcePy._t_long, False, 0), (_M_omero._t_ServerError,))

    _M_omero.api.IProjection = IProjection
    del IProjection

    _M_omero.api.IProjectionPrx = IProjectionPrx
    del IProjectionPrx

# End of module omero.api

__name__ = 'omero'

# End of module omero
