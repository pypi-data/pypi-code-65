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
# Generated from file `TermAnnotation.ice'
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
import omero_model_BasicAnnotation_ice

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

if 'AnnotationAnnotationLink' not in _M_omero.model.__dict__:
    _M_omero.model._t_AnnotationAnnotationLink = IcePy.declareClass('::omero::model::AnnotationAnnotationLink')
    _M_omero.model._t_AnnotationAnnotationLinkPrx = IcePy.declareProxy('::omero::model::AnnotationAnnotationLink')

if 'Annotation' not in _M_omero.model.__dict__:
    _M_omero.model._t_Annotation = IcePy.declareClass('::omero::model::Annotation')
    _M_omero.model._t_AnnotationPrx = IcePy.declareProxy('::omero::model::Annotation')

if 'Details' not in _M_omero.model.__dict__:
    _M_omero.model._t_Details = IcePy.declareClass('::omero::model::Details')
    _M_omero.model._t_DetailsPrx = IcePy.declareProxy('::omero::model::Details')

if 'TermAnnotation' not in _M_omero.model.__dict__:
    _M_omero.model.TermAnnotation = Ice.createTempClass()
    class TermAnnotation(_M_omero.model.BasicAnnotation):
        def __init__(self, _id=None, _details=None, _loaded=False, _version=None, _ns=None, _name=None, _description=None, _annotationLinksSeq=None, _annotationLinksLoaded=False, _annotationLinksCountPerOwner=None, _termValue=None):
            if Ice.getType(self) == _M_omero.model.TermAnnotation:
                raise RuntimeError('omero.model.TermAnnotation is an abstract class')
            _M_omero.model.BasicAnnotation.__init__(self, _id, _details, _loaded, _version, _ns, _name, _description, _annotationLinksSeq, _annotationLinksLoaded, _annotationLinksCountPerOwner)
            self._termValue = _termValue

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::omero::model::Annotation', '::omero::model::BasicAnnotation', '::omero::model::IObject', '::omero::model::TermAnnotation')

        def ice_id(self, current=None):
            return '::omero::model::TermAnnotation'

        def ice_staticId():
            return '::omero::model::TermAnnotation'
        ice_staticId = staticmethod(ice_staticId)

        def getTermValue(self, current=None):
            pass

        def setTermValue(self, theTermValue, current=None):
            pass

        def __str__(self):
            return IcePy.stringify(self, _M_omero.model._t_TermAnnotation)

        __repr__ = __str__

    _M_omero.model.TermAnnotationPrx = Ice.createTempClass()
    class TermAnnotationPrx(_M_omero.model.BasicAnnotationPrx):

        def getTermValue(self, _ctx=None):
            return _M_omero.model.TermAnnotation._op_getTermValue.invoke(self, ((), _ctx))

        def begin_getTermValue(self, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_omero.model.TermAnnotation._op_getTermValue.begin(self, ((), _response, _ex, _sent, _ctx))

        def end_getTermValue(self, _r):
            return _M_omero.model.TermAnnotation._op_getTermValue.end(self, _r)

        def setTermValue(self, theTermValue, _ctx=None):
            return _M_omero.model.TermAnnotation._op_setTermValue.invoke(self, ((theTermValue, ), _ctx))

        def begin_setTermValue(self, theTermValue, _response=None, _ex=None, _sent=None, _ctx=None):
            return _M_omero.model.TermAnnotation._op_setTermValue.begin(self, ((theTermValue, ), _response, _ex, _sent, _ctx))

        def end_setTermValue(self, _r):
            return _M_omero.model.TermAnnotation._op_setTermValue.end(self, _r)

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_omero.model.TermAnnotationPrx.ice_checkedCast(proxy, '::omero::model::TermAnnotation', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_omero.model.TermAnnotationPrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

        def ice_staticId():
            return '::omero::model::TermAnnotation'
        ice_staticId = staticmethod(ice_staticId)

    _M_omero.model._t_TermAnnotationPrx = IcePy.defineProxy('::omero::model::TermAnnotation', TermAnnotationPrx)

    _M_omero.model._t_TermAnnotation = IcePy.declareClass('::omero::model::TermAnnotation')

    _M_omero.model._t_TermAnnotation = IcePy.defineClass('::omero::model::TermAnnotation', TermAnnotation, -1, (), True, False, _M_omero.model._t_BasicAnnotation, (), (('_termValue', (), _M_omero._t_RString, False, 0),))
    TermAnnotation._ice_type = _M_omero.model._t_TermAnnotation

    TermAnnotation._op_getTermValue = IcePy.Operation('getTermValue', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (), (), ((), _M_omero._t_RString, False, 0), ())
    TermAnnotation._op_setTermValue = IcePy.Operation('setTermValue', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (((), _M_omero._t_RString, False, 0),), (), None, ())

    _M_omero.model.TermAnnotation = TermAnnotation
    del TermAnnotation

    _M_omero.model.TermAnnotationPrx = TermAnnotationPrx
    del TermAnnotationPrx

# End of module omero.model

__name__ = 'omero'

# End of module omero
