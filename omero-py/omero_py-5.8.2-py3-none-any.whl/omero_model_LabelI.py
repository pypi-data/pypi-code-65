"""
   /*
   **   Generated by blitz/resources/templates/combined.vm
   **
   **   Copyright 2007, 2008 Glencoe Software, Inc. All rights reserved.
   **   Use is subject to license terms supplied in LICENSE.txt
   **
   */
"""
try:
   unicode
except NameError:
   # Python 3: "unicode" is built-in
   unicode = str
import Ice
import IceImport
import omero
IceImport.load("omero_model_DetailsI")
IceImport.load("omero_model_Label_ice")
from omero.rtypes import rlong
from collections import namedtuple
_omero = Ice.openModule("omero")
_omero_model = Ice.openModule("omero.model")
__name__ = "omero.model"
class LabelI(_omero_model.Label):

      # Property Metadata
      _field_info_data = namedtuple("FieldData", ["wrapper", "nullable"])
      _field_info_type = namedtuple("FieldInfo", [
          "x",
          "y",
          "textValue",
          "theZ",
          "theT",
          "theC",
          "roi",
          "locked",
          "transform",
          "fillColor",
          "fillRule",
          "strokeColor",
          "strokeDashArray",
          "strokeWidth",
          "fontFamily",
          "fontSize",
          "fontStyle",
          "annotationLinks",
          "details",
      ])
      _field_info = _field_info_type(
          x=_field_info_data(wrapper=omero.rtypes.rdouble, nullable=True),
          y=_field_info_data(wrapper=omero.rtypes.rdouble, nullable=True),
          textValue=_field_info_data(wrapper=omero.rtypes.rstring, nullable=True),
          theZ=_field_info_data(wrapper=omero.rtypes.rint, nullable=True),
          theT=_field_info_data(wrapper=omero.rtypes.rint, nullable=True),
          theC=_field_info_data(wrapper=omero.rtypes.rint, nullable=True),
          roi=_field_info_data(wrapper=omero.proxy_to_instance, nullable=False),
          locked=_field_info_data(wrapper=omero.rtypes.rbool, nullable=True),
          transform=_field_info_data(wrapper=omero.proxy_to_instance, nullable=True),
          fillColor=_field_info_data(wrapper=omero.rtypes.rint, nullable=True),
          fillRule=_field_info_data(wrapper=omero.rtypes.rstring, nullable=True),
          strokeColor=_field_info_data(wrapper=omero.rtypes.rint, nullable=True),
          strokeDashArray=_field_info_data(wrapper=omero.rtypes.rstring, nullable=True),
          strokeWidth=_field_info_data(wrapper=omero.proxy_to_instance, nullable=True),
          fontFamily=_field_info_data(wrapper=omero.rtypes.rstring, nullable=True),
          fontSize=_field_info_data(wrapper=omero.proxy_to_instance, nullable=True),
          fontStyle=_field_info_data(wrapper=omero.rtypes.rstring, nullable=True),
          annotationLinks=_field_info_data(wrapper=omero.proxy_to_instance, nullable=True),
          details=_field_info_data(wrapper=omero.proxy_to_instance, nullable=True),
      )  # end _field_info
      X =  "ome.model.roi.Label_x"
      Y =  "ome.model.roi.Label_y"
      TEXTVALUE =  "ome.model.roi.Label_textValue"
      THEZ =  "ome.model.roi.Label_theZ"
      THET =  "ome.model.roi.Label_theT"
      THEC =  "ome.model.roi.Label_theC"
      ROI =  "ome.model.roi.Label_roi"
      LOCKED =  "ome.model.roi.Label_locked"
      TRANSFORM =  "ome.model.roi.Label_transform"
      FILLCOLOR =  "ome.model.roi.Label_fillColor"
      FILLRULE =  "ome.model.roi.Label_fillRule"
      STROKECOLOR =  "ome.model.roi.Label_strokeColor"
      STROKEDASHARRAY =  "ome.model.roi.Label_strokeDashArray"
      STROKEWIDTH =  "ome.model.roi.Label_strokeWidth"
      FONTFAMILY =  "ome.model.roi.Label_fontFamily"
      FONTSIZE =  "ome.model.roi.Label_fontSize"
      FONTSTYLE =  "ome.model.roi.Label_fontStyle"
      ANNOTATIONLINKS =  "ome.model.roi.Label_annotationLinks"
      DETAILS =  "ome.model.roi.Label_details"
      def errorIfUnloaded(self):
          if not self._loaded:
              raise _omero.UnloadedEntityException("Object unloaded:"+str(self))

      def throwNullCollectionException(self,propertyName):
          raise _omero.UnloadedEntityException(""+
          "Error updating collection:" + propertyName +"\n"+
          "Collection is currently null. This can be seen\n" +
          "by testing \""+ propertyName +"Loaded\". This implies\n"+
          "that this collection was unloaded. Please refresh this object\n"+
          "in order to update this collection.\n")

      def _toggleCollectionsLoaded(self, load):
          if load:
              self._annotationLinksSeq = []
              self._annotationLinksLoaded = True;
          else:
              self._annotationLinksSeq = []
              self._annotationLinksLoaded = False;

          pass

      def __init__(self, id=None, loaded=None):
          super(LabelI, self).__init__()
          if id is not None and isinstance(id, (str, unicode)) and ":" in id:
              parts = id.split(":")
              if len(parts) != 2:
                  raise Exception("Invalid proxy string: %s", id)
              if parts[0] != self.__class__.__name__ and \
                 parts[0]+"I" != self.__class__.__name__:
                  raise Exception("Proxy class mismatch: %s<>%s" %
                  (self.__class__.__name__, parts[0]))
              self._id = rlong(parts[1])
              if loaded is None:
                  # If no loadedness was requested with
                  # a proxy string, then assume False.
                  loaded = False
          else:
              # Relying on omero.rtypes.rlong's error-handling
              self._id = rlong(id)
              if loaded is None:
                  loaded = True  # Assume true as previously
          self._loaded = loaded
          if self._loaded:
             self._details = _omero_model.DetailsI()
             self._toggleCollectionsLoaded(True)

      def unload(self, current = None):
          self._loaded = False
          self.unloadX( )
          self.unloadY( )
          self.unloadTextValue( )
          self.unloadTheZ( )
          self.unloadTheT( )
          self.unloadTheC( )
          self.unloadRoi( )
          self.unloadLocked( )
          self.unloadTransform( )
          self.unloadFillColor( )
          self.unloadFillRule( )
          self.unloadStrokeColor( )
          self.unloadStrokeDashArray( )
          self.unloadStrokeWidth( )
          self.unloadFontFamily( )
          self.unloadFontSize( )
          self.unloadFontStyle( )
          self.unloadAnnotationLinks( )
          self.unloadDetails( )

      def isLoaded(self, current = None):
          return self._loaded
      def unloadCollections(self, current = None):
          self._toggleCollectionsLoaded( False )
      def isGlobal(self, current = None):
          return  False ;
      def isMutable(self, current = None):
          return  True ;
      def isAnnotated(self, current = None):
          return  False ;
      def isLink(self, current = None):
          return  False ;
      def shallowCopy(self, current = None):
            if not self._loaded: return self.proxy()
            copy = LabelI()
            copy._id = self._id;
            copy._version = self._version;
            copy._details = None  # Unloading for the moment.
            raise omero.ClientError("NYI")
      def proxy(self, current = None):
          if self._id is None: raise omero.ClientError("Proxies require an id")
          return LabelI( self._id.getValue(), False )

      def getDetails(self, current = None):
          self.errorIfUnloaded()
          return self._details

      def unloadDetails(self, current = None):
          self._details = None

      def getId(self, current = None):
          return self._id

      def setId(self, _id, current = None):
          self._id = _id

      def checkUnloadedProperty(self, value, loadedField):
          if value == None:
              self.__dict__[loadedField] = False
          else:
              self.__dict__[loadedField] = True

      def getVersion(self, current = None):
          self.errorIfUnloaded()
          return self._version

      def setVersion(self, version, current = None):
          self.errorIfUnloaded()
          self._version = version

      def unloadX(self, ):
          self._xLoaded = False
          self._x = None;

      def getX(self, current = None):
          self.errorIfUnloaded()
          return self._x

      def setX(self, _x, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.x.wrapper is not None:
              if _x is not None:
                  _x = self._field_info.x.wrapper(_x)
          self._x = _x
          pass

      def unloadY(self, ):
          self._yLoaded = False
          self._y = None;

      def getY(self, current = None):
          self.errorIfUnloaded()
          return self._y

      def setY(self, _y, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.y.wrapper is not None:
              if _y is not None:
                  _y = self._field_info.y.wrapper(_y)
          self._y = _y
          pass

      def unloadTextValue(self, ):
          self._textValueLoaded = False
          self._textValue = None;

      def getTextValue(self, current = None):
          self.errorIfUnloaded()
          return self._textValue

      def setTextValue(self, _textValue, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.textValue.wrapper is not None:
              if _textValue is not None:
                  _textValue = self._field_info.textValue.wrapper(_textValue)
          self._textValue = _textValue
          pass

      def unloadTheZ(self, ):
          self._theZLoaded = False
          self._theZ = None;

      def getTheZ(self, current = None):
          self.errorIfUnloaded()
          return self._theZ

      def setTheZ(self, _theZ, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.theZ.wrapper is not None:
              if _theZ is not None:
                  _theZ = self._field_info.theZ.wrapper(_theZ)
          self._theZ = _theZ
          pass

      def unloadTheT(self, ):
          self._theTLoaded = False
          self._theT = None;

      def getTheT(self, current = None):
          self.errorIfUnloaded()
          return self._theT

      def setTheT(self, _theT, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.theT.wrapper is not None:
              if _theT is not None:
                  _theT = self._field_info.theT.wrapper(_theT)
          self._theT = _theT
          pass

      def unloadTheC(self, ):
          self._theCLoaded = False
          self._theC = None;

      def getTheC(self, current = None):
          self.errorIfUnloaded()
          return self._theC

      def setTheC(self, _theC, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.theC.wrapper is not None:
              if _theC is not None:
                  _theC = self._field_info.theC.wrapper(_theC)
          self._theC = _theC
          pass

      def unloadRoi(self, ):
          self._roiLoaded = False
          self._roi = None;

      def getRoi(self, current = None):
          self.errorIfUnloaded()
          return self._roi

      def setRoi(self, _roi, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.roi.wrapper is not None:
              if _roi is not None:
                  _roi = self._field_info.roi.wrapper(_roi)
          self._roi = _roi
          pass

      def unloadLocked(self, ):
          self._lockedLoaded = False
          self._locked = None;

      def getLocked(self, current = None):
          self.errorIfUnloaded()
          return self._locked

      def setLocked(self, _locked, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.locked.wrapper is not None:
              if _locked is not None:
                  _locked = self._field_info.locked.wrapper(_locked)
          self._locked = _locked
          pass

      def unloadTransform(self, ):
          self._transformLoaded = False
          self._transform = None;

      def getTransform(self, current = None):
          self.errorIfUnloaded()
          return self._transform

      def setTransform(self, _transform, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.transform.wrapper is not None:
              if _transform is not None:
                  _transform = self._field_info.transform.wrapper(_transform)
          self._transform = _transform
          pass

      def unloadFillColor(self, ):
          self._fillColorLoaded = False
          self._fillColor = None;

      def getFillColor(self, current = None):
          self.errorIfUnloaded()
          return self._fillColor

      def setFillColor(self, _fillColor, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.fillColor.wrapper is not None:
              if _fillColor is not None:
                  _fillColor = self._field_info.fillColor.wrapper(_fillColor)
          self._fillColor = _fillColor
          pass

      def unloadFillRule(self, ):
          self._fillRuleLoaded = False
          self._fillRule = None;

      def getFillRule(self, current = None):
          self.errorIfUnloaded()
          return self._fillRule

      def setFillRule(self, _fillRule, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.fillRule.wrapper is not None:
              if _fillRule is not None:
                  _fillRule = self._field_info.fillRule.wrapper(_fillRule)
          self._fillRule = _fillRule
          pass

      def unloadStrokeColor(self, ):
          self._strokeColorLoaded = False
          self._strokeColor = None;

      def getStrokeColor(self, current = None):
          self.errorIfUnloaded()
          return self._strokeColor

      def setStrokeColor(self, _strokeColor, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.strokeColor.wrapper is not None:
              if _strokeColor is not None:
                  _strokeColor = self._field_info.strokeColor.wrapper(_strokeColor)
          self._strokeColor = _strokeColor
          pass

      def unloadStrokeDashArray(self, ):
          self._strokeDashArrayLoaded = False
          self._strokeDashArray = None;

      def getStrokeDashArray(self, current = None):
          self.errorIfUnloaded()
          return self._strokeDashArray

      def setStrokeDashArray(self, _strokeDashArray, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.strokeDashArray.wrapper is not None:
              if _strokeDashArray is not None:
                  _strokeDashArray = self._field_info.strokeDashArray.wrapper(_strokeDashArray)
          self._strokeDashArray = _strokeDashArray
          pass

      def unloadStrokeWidth(self, ):
          self._strokeWidthLoaded = False
          self._strokeWidth = None;

      def getStrokeWidth(self, current = None):
          self.errorIfUnloaded()
          return self._strokeWidth

      def setStrokeWidth(self, _strokeWidth, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.strokeWidth.wrapper is not None:
              if _strokeWidth is not None:
                  _strokeWidth = self._field_info.strokeWidth.wrapper(_strokeWidth)
          self._strokeWidth = _strokeWidth
          pass

      def unloadFontFamily(self, ):
          self._fontFamilyLoaded = False
          self._fontFamily = None;

      def getFontFamily(self, current = None):
          self.errorIfUnloaded()
          return self._fontFamily

      def setFontFamily(self, _fontFamily, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.fontFamily.wrapper is not None:
              if _fontFamily is not None:
                  _fontFamily = self._field_info.fontFamily.wrapper(_fontFamily)
          self._fontFamily = _fontFamily
          pass

      def unloadFontSize(self, ):
          self._fontSizeLoaded = False
          self._fontSize = None;

      def getFontSize(self, current = None):
          self.errorIfUnloaded()
          return self._fontSize

      def setFontSize(self, _fontSize, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.fontSize.wrapper is not None:
              if _fontSize is not None:
                  _fontSize = self._field_info.fontSize.wrapper(_fontSize)
          self._fontSize = _fontSize
          pass

      def unloadFontStyle(self, ):
          self._fontStyleLoaded = False
          self._fontStyle = None;

      def getFontStyle(self, current = None):
          self.errorIfUnloaded()
          return self._fontStyle

      def setFontStyle(self, _fontStyle, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.fontStyle.wrapper is not None:
              if _fontStyle is not None:
                  _fontStyle = self._field_info.fontStyle.wrapper(_fontStyle)
          self._fontStyle = _fontStyle
          pass

      def unloadAnnotationLinks(self, current = None):
          self._annotationLinksLoaded = False
          self._annotationLinksSeq = None;

      def _getAnnotationLinks(self, current = None):
          self.errorIfUnloaded()
          return self._annotationLinksSeq

      def _setAnnotationLinks(self, _annotationLinks, current = None, wrap=False):
          self.errorIfUnloaded()
          if wrap and self._field_info.annotationLinksSeq.wrapper is not None:
              if _annotationLinks is not None:
                  _annotationLinks = self._field_info.annotationLinksSeq.wrapper(_annotationLinks)
          self._annotationLinksSeq = _annotationLinks
          self.checkUnloadedProperty(_annotationLinks,'annotationLinksLoaded')

      def isAnnotationLinksLoaded(self):
          return self._annotationLinksLoaded

      def sizeOfAnnotationLinks(self, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: return -1
          return len(self._annotationLinksSeq)

      def copyAnnotationLinks(self, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          return list(self._annotationLinksSeq)

      def iterateAnnotationLinks(self):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          return iter(self._annotationLinksSeq)

      def addShapeAnnotationLink(self, target, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          self._annotationLinksSeq.append( target );
          target.setParent( self )

      def addAllShapeAnnotationLinkSet(self, targets, current = None):
          self.errorIfUnloaded()
          if  not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          self._annotationLinksSeq.extend( targets )
          for target in targets:
              target.setParent( self )

      def removeShapeAnnotationLink(self, target, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          self._annotationLinksSeq.remove( target )
          target.setParent( None )

      def removeAllShapeAnnotationLinkSet(self, targets, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          for elt in targets:
              elt.setParent( None )
              self._annotationLinksSeq.remove( elt )

      def clearAnnotationLinks(self, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          for elt in self._annotationLinksSeq:
              elt.setParent( None )
          self._annotationLinksSeq = list()

      def reloadAnnotationLinks(self, toCopy, current = None):
          self.errorIfUnloaded()
          if self._annotationLinksLoaded:
              raise omero.ClientError("Cannot reload active collection: annotationLinksSeq")
          if not toCopy:
              raise omero.ClientError("Argument cannot be null")
          if toCopy.getId().getValue() != self.getId().getValue():
             raise omero.ClientError("Argument must have the same id as this instance")
          if toCopy.getDetails().getUpdateEvent().getId().getValue() < self.getDetails().getUpdateEvent().getId().getValue():
             raise omero.ClientError("Argument may not be older than this instance")
          copy = toCopy.copyAnnotationLinks() # May also throw
          for elt in copy:
              elt.setParent( self )
          self._annotationLinksSeq = copy
          toCopy.unloadAnnotationLinks()
          self._annotationLinksLoaded = True

      def getAnnotationLinksCountPerOwner(self, current = None):
          return self._annotationLinksCountPerOwner

      def linkAnnotation(self, addition, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          link = _omero_model.ShapeAnnotationLinkI()
          link.link( self, addition );
          self.addShapeAnnotationLinkToBoth( link, True )
          return link

      def addShapeAnnotationLinkToBoth(self, link, bothSides):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          self._annotationLinksSeq.append( link )

      def findShapeAnnotationLink(self, removal, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          result = list()
          for link in self._annotationLinksSeq:
              if link.getChild() == removal: result.append(link)
          return result

      def unlinkAnnotation(self, removal, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          toRemove = self.findShapeAnnotationLink(removal)
          for next in toRemove:
              self.removeShapeAnnotationLinkFromBoth( next, True )

      def removeShapeAnnotationLinkFromBoth(self, link, bothSides, current = None):
          self.errorIfUnloaded()
          if not self._annotationLinksLoaded: self.throwNullCollectionException("annotationLinksSeq")
          self._annotationLinksSeq.remove( link )

      def linkedAnnotationList(self, current = None):
          self.errorIfUnloaded()
          if not self.annotationLinksLoaded: self.throwNullCollectionException("AnnotationLinks")
          linked = []
          for link in self._annotationLinksSeq:
              linked.append( link.getChild() )
          return linked


      def ice_postUnmarshal(self):
          """
          Provides additional initialization once all data loaded
          """
          pass # Currently unused


      def ice_preMarshal(self):
          """
          Provides additional validation before data is sent
          """
          pass # Currently unused

      def __getattr__(self, name):
          """
          Reroutes all access to object.field through object.getField() or object.isField()
          """
          if "_" in name:  # Ice disallows underscores, so these should be treated normally.
              return object.__getattribute__(self, name)
          field  = "_" + name
          capitalized = name[0].capitalize() + name[1:]
          getter = "get" + capitalized
          questn = "is" + capitalized
          try:
              self.__dict__[field]
              if hasattr(self, getter):
                  method = getattr(self, getter)
                  return method()
              elif hasattr(self, questn):
                  method = getattr(self, questn)
                  return method()
          except:
              pass
          raise AttributeError("'%s' object has no attribute '%s' or '%s'" % (self.__class__.__name__, getter, questn))

      def __setattr__(self, name, value):
          """
          Reroutes all access to object.field through object.getField(), with the caveat
          that all sets on variables starting with "_" are permitted directly.
          """
          if name.startswith("_"):
              self.__dict__[name] = value
              return
          else:
              field  = "_" + name
              setter = "set" + name[0].capitalize() + name[1:]
              if hasattr(self, field) and hasattr(self, setter):
                  method = getattr(self, setter)
                  return method(value)
          raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, setter))

_omero_model.LabelI = LabelI
