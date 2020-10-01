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
# Generated from file `LightEmittingDiode.ice'
#
# Warning: do not edit this file.
#
# </auto-generated>
#

from sys import version_info as _version_info_
import Ice, IcePy
import omero_model_IObject_ice
import omero_RTypes_ice
import omero_model_RTypes_ice
import omero_System_ice
import omero_Collections_ice
import omero_model_LightSource_ice

# Included module omero
_M_omero = Ice.openModule('omero')

# Included module omero.model
_M_omero.model = Ice.openModule('omero.model')

# Included module Ice
_M_Ice = Ice.openModule('Ice')

# Included module omero.sys
_M_omero.sys = Ice.openModule('omero.sys')

# Included module omero.api
_M_omero.api = Ice.openModule('omero.api')

# Start of module omero
__name__ = 'omero'

# Start of module omero.model
__name__ = 'omero.model'

if 'Power' not in _M_omero.model.__dict__:
    _M_omero.model._t_Power = IcePy.declareClass('::omero::model::Power')
    _M_omero.model._t_PowerPrx = IcePy.declareProxy('::omero::model::Power')

if 'Instrument' not in _M_omero.model.__dict__:
    _M_omero.model._t_Instrument = IcePy.declareClass('::omero::model::Instrument')
    _M_omero.model._t_InstrumentPrx = IcePy.declareProxy('::omero::model::Instrument')

if 'LightSourceAnnotationLink' not in _M_omero.model.__dict__:
    _M_omero.model._t_LightSourceAnnotationLink = IcePy.declareClass('::omero::model::LightSourceAnnotationLink')
    _M_omero.model._t_LightSourceAnnotationLinkPrx = IcePy.declareProxy('::omero::model::LightSourceAnnotationLink')

if 'Annotation' not in _M_omero.model.__dict__:
    _M_omero.model._t_Annotation = IcePy.declareClass('::omero::model::Annotation')
    _M_omero.model._t_AnnotationPrx = IcePy.declareProxy('::omero::model::Annotation')

if 'Details' not in _M_omero.model.__dict__:
    _M_omero.model._t_Details = IcePy.declareClass('::omero::model::Details')
    _M_omero.model._t_DetailsPrx = IcePy.declareProxy('::omero::model::Details')

if 'LightEmittingDiode' not in _M_omero.model.__dict__:
    _M_omero.model.LightEmittingDiode = Ice.createTempClass()
    class LightEmittingDiode(_M_omero.model.LightSource):
        def __init__(self, _id=None, _details=None, _loaded=False, _version=None, _manufacturer=None, _model=None, _power=None, _lotNumber=None, _serialNumber=None, _instrument=None, _annotationLinksSeq=None, _annotationLinksLoaded=False, _annotationLinksCountPerOwner=None):
            if Ice.getType(self) == _M_omero.model.LightEmittingDiode:
                raise RuntimeError('omero.model.LightEmittingDiode is an abstract class')
            _M_omero.model.LightSource.__init__(self, _id, _details, _loaded, _version, _manufacturer, _model, _power, _lotNumber, _serialNumber, _instrument, _annotationLinksSeq, _annotationLinksLoaded, _annotationLinksCountPerOwner)

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::omero::model::IObject', '::omero::model::LightEmittingDiode', '::omero::model::LightSource')

        def ice_id(self, current=None):
            return '::omero::model::LightEmittingDiode'

        def ice_staticId():
            return '::omero::model::LightEmittingDiode'
        ice_staticId = staticmethod(ice_staticId)

        def __str__(self):
            return IcePy.stringify(self, _M_omero.model._t_LightEmittingDiode)

        __repr__ = __str__

    _M_omero.model.LightEmittingDiodePrx = Ice.createTempClass()
    class LightEmittingDiodePrx(_M_omero.model.LightSourcePrx):

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_omero.model.LightEmittingDiodePrx.ice_checkedCast(proxy, '::omero::model::LightEmittingDiode', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_omero.model.LightEmittingDiodePrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

        def ice_staticId():
            return '::omero::model::LightEmittingDiode'
        ice_staticId = staticmethod(ice_staticId)

    _M_omero.model._t_LightEmittingDiodePrx = IcePy.defineProxy('::omero::model::LightEmittingDiode', LightEmittingDiodePrx)

    _M_omero.model._t_LightEmittingDiode = IcePy.declareClass('::omero::model::LightEmittingDiode')

    _M_omero.model._t_LightEmittingDiode = IcePy.defineClass('::omero::model::LightEmittingDiode', LightEmittingDiode, -1, (), True, False, _M_omero.model._t_LightSource, (), ())
    LightEmittingDiode._ice_type = _M_omero.model._t_LightEmittingDiode

    _M_omero.model.LightEmittingDiode = LightEmittingDiode
    del LightEmittingDiode

    _M_omero.model.LightEmittingDiodePrx = LightEmittingDiodePrx
    del LightEmittingDiodePrx

# End of module omero.model

__name__ = 'omero'

# End of module omero
