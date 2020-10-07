from PythUnity import Variables
from PythUnity import Functions
import copy
import pygame
import types
import numba as nb
import numpy as np
class Object:
  def __init__(self, rect, image, onClick = None, onDrag = None, onClickOff = None, onScroll = None, enableDragOff = False, clickGroup = 0):
    self.__destroyed = False
    self.__parent = None
    self.__children = []
    self.__variables = {}
    self.__image = None
    self.__transformedImage = None
    self.__text = None
    self.__color = None
    self.__components = []
    self.__clickGroup = None
    self.__velocity = (0, 0)
    self.__index = None
    self.__rect = None
    self.rect = rect
    self.clickGroup = clickGroup
    if(type(image) is tuple):
      self.color = image
    elif(type(image) is String):
      self.text = copy.deepcopy(image)
    elif(type(image) is pygame.Surface):
      self.image = image
    if onClick != None or onDrag != None or onScroll != None:
      self.__button = Button(onClick, onDrag, onClickOff, onScroll, enableDragOff)
    else:
      self.__button = None
    Functions.AddObject(self)
    #for att in dir(self):
    #    print(att)
    #print("////////////")
  #####
  @property
  def rect(self):
      return self.__rect
  @rect.setter
  def rect(self, value):
    Functions.TypeCheck(value, Rect, "rect")
    self.__rect = value
    self.__rect._Rect__owner = self
    TransformImage(self)
  @property
  def image(self):
    return self.__image
  @image.setter
  def image(self, value):
    Functions.TypeCheck(value, pygame.Surface, "image")
    self.__image = value
    TransformImage(self, changeColor=True)
  @property
  def destroyed(self):
    return self.__destroyed
  @destroyed.setter
  def destroyed(self, value):
    Functions.Err("Cant set Object.destroyed")
  @property
  def index(self):
    return self.__index
  @index.setter
  def index(self, value):
    Functions.Err("Cant set Object.index")
  @property
  def parent(self):
    return self.__parent
  @parent.setter
  def parent(self, value):
    Functions.Err("Cant set Object.parent")
  @property
  def children(self):
    return self.__children
  @children.setter
  def children(self, value):
    Functions.Err("Cant set Object.children")
  @property
  def components(self):
    return self.__components
  @components.setter
  def components(self, value):
    Functions.Err("Cant set Object.components, use Object.AddComp or Object.DelComp")
  @property
  def variables(self):
    return self.__variables
  @variables.setter
  def variables(self, value):
    Functions.Err("Cant set Object.variables, add each variable individualy")
  @property
  def transformedImage(self):
    return self.__transformedImage
  @transformedImage.setter
  def transformedImage(self, value):
    Functions.Err("Cant set Object.transformedImage")
  ##
  @property
  def text(self):
      return self.__text
  @text.setter
  def text(self, value):
    Functions.TypeCheck(value, [String, type(None)], "text")
    self.__text = value
  @property
  def color(self):
      return self.__color
  @color.setter
  def color(self, value):
    Functions.TypeCheck(value, [tuple, type(None)], "color")
    if(value == None or len(value) == 4):
        self.__color = (float(value[0]), float(value[1]), float(value[2]), float(value[3]))
    elif(len(value) == 3):
        self.__color = (float(value[0]), float(value[1]), float(value[2]), 255.0)
    else:
        Functions.Err("Object.color must have a length of 3 or 4 in RGBA or RGB format")
    TransformImage(self, changeColor=True)
  @property
  def clickGroup(self):
      return self.__clickGroup
  @clickGroup.setter
  def clickGroup(self, value):
    Functions.TypeCheck(value, int, "clickGroup")
    self.__clickGroup = value
  @property
  def velocity(self):
      return self.__velocity
  @velocity.setter
  def velocity(self, value):
    Functions.TypeCheck(value, tuple, "velocity")
    self.__velocity = value
  @property
  def button(self):
      return self.__button
  @button.setter
  def button(self, value):
    Functions.TypeCheck(value, [Button, type(None)], "button")
    self.__button = value
  #####
  def __getitem__(self, i):
    self.__Throw("children.getitem")
    return self.__children[i]
  def __len__(self):
    self.__Throw("children.len")
    return len(self.__children)
  #####
  def Decendants(self):
    self.__Throw("Object.Decendants")
    indexes = []
    for i in self.__children:
      indexes.append(i)
      indexes.extend(Variables.var.parts[i].Decendants())
    return indexes
  def Move(self, newIndex):#components can have their update function skipped on accident if ran in another comp.update
    self.__Throw("Object.Move")
    children = self.GetParentChildren()
    if(newIndex < 0):
        Functions.Err("Object.Move failed, index less than 0")
    elif(newIndex > len(children)):
        Functions.Warn("Object.Move incorrect, index is greater than parent.children count")
    oldIndex = self.index
    self.__index = newIndex
    del children[oldIndex]
    children.insert(newIndex, self)
    i = oldIndex
    if(newIndex > oldIndex):
      while(i < newIndex):
        children[i]._Object__index = i
        i = i + 1
    elif(newIndex < oldIndex):
      while(i >= newIndex):
        children[i]._Object__index = i
        i = i - 1
  def SetParent(self, newParent):
    self.__Throw("Object.SetParent")
    children = self.GetParentChildren()
    self.Move(len(children))#make it so other children have their indexes fixed
    del children[self.index]
    self.__parent = newParent
    self.__parent.children.append(self)
    self.__index = len(self.__parent.children) - 1
  def GetParentChildren(self):
    self.__Throw("Object.GetParentChildren")
    children = None
    if(self.__parent != None):
      children = self.__parent.children
    else:
      children = Variables.var.parts
    return children
  def Copy(self):
    self.__Throw("Object.Copy")
    oldParent = self.parent
    parChildren = self.GetParentChildren()
    CopyHelp(self)
    copied = copy.deepcopy(self)
    copied._Object__index = len(parChildren)
    parChildren.append(copied)
    copied._Object__parent = oldParent
    copied.Move(self.index + 1)
    CopyUnHelp(self, oldParent)
    CopyUnHelp(copied, oldParent)
    CopyHelp2(copied)
    return copied
  def Destroy(self):
    self.__Throw("Object.Destroy")
    children = self.GetParentChildren()
    self.Move(len(children))
    del children[self.index]
    self.__index = -1 #will cause Functions.Error if used incorrectly, did this on purpous
    self.__destroyed = True
    for i in self.__children:
      i.Destroy()
  def AddComp(self, comp):
    self.__Throw("Object.AddComp")
    self.__components.append(comp)
    if(comp[0] != None):
        comp[0](self)
  def DelComp(self, index):
      self.__Throw("Object.DelComp")
      if(len(self.__components) > index):
          del self.__components[index]
      else:
          Functions.Err("Object.DelComp failed, index greater than comp index")
  def SetClickGroup(self, number):
      self.clickGroup = number
      for i in self.children:
          SetClickGroup(i)
  def __Throw(self, action = ""):
    if(self.__destroyed):
      if(action == ""):
        Functions.Err("Object was destroyed")
      else:
        Functions.Err("Object was destroyed while " + action + "() was happening")
class Button:
  def __init__(self, onClick, onDrag, onClickOff, onScroll, enableDragOff):
    self.__onClick = None
    self.__onClickOff = None
    self.__onDrag = None
    self.__onScroll = None
    self.__dragging = False
    self.__enableDragOff = False
    self.onClick = onClick
    self.onClickOff = onClickOff
    self.onDrag = onDrag
    self.onScroll = onScroll
  @property
  def dragging(self):
      return self.__dragging
  @dragging.setter
  def dragging(self, value):
      Functions.Err("You cant set PythUnity.Button.dragging, you can only get it")
  ##
  @property
  def enableDragOff(self):
      return self.__enableDragOff
  @enableDragOff.setter
  def enableDragOff(self, value):
      Functions.TypeCheck(value, bool, "enableDragOff", "Button")
      self.__enableDragOff = value
  @property
  def onClick(self):
      return self.__onClick
  @onClick.setter
  def onClick(self, value):
      Functions.TypeCheck(value, [types.FunctionType, type(None)], "onClick", "Button")
      self.__onClick = value
  @property
  def onClickOff(self):
      return self.__onClickOff
  @onClickOff.setter
  def onClickOff(self, value):
      Functions.TypeCheck(value, [types.FunctionType, type(None)], "onClickOff", "Button")
      self.__onClickOff = value
  @property
  def onDrag(self):
      return self.__onDrag
  @onDrag.setter
  def onDrag(self, value):
      Functions.TypeCheck(value, [types.FunctionType, type(None)], "onDrag", "Button")
      self.__onDrag = value
  @property
  def onScroll(self):
      return self.__onScroll
  @onScroll.setter
  def onScroll(self, value):
      Functions.TypeCheck(value, [types.FunctionType, type(None)], "onScroll", "Button")
      self.__onScroll = value
class String:
  def __init__(self, text, fontSize, font, fontColor, backgroundColor):
    self.__fontSize = None
    self.__text = None
    self.__font = None
    self.__fontColor = None
    self.__backgroundColor = None
    self.fontSize = fontSize
    self.text = text
    self.font = font
    self.fontColor = fontColor
    self.backgroundColor = backgroundColor
  @property
  def fontSize(self):
    return self.__fontSize
  @fontSize.setter
  def fontSize(self, value):
    Functions.TypeCheck(value, int, "fontSize", "String")
    self.__fontSize = value
  @property
  def text(self):
    return self.__text
  @text.setter
  def text(self, value):
    Functions.TypeCheck(value, str, "text", "String")
    self.__text = value
  @property
  def font(self):
    return self.__font
  @font.setter
  def font(self, value):
    Functions.TypeCheck(value, str, "font", "String")
    self.__font = value
  @property
  def fontColor(self):
    return self.__fontColor
  @fontColor.setter
  def fontColor(self, value):
    Functions.TypeCheck(value, [tuple, type(None)], "fontColor", "String")
    self.__fontColor = value
  @property
  def backgroundColor(self):
    return self.__backgroundColor
  @backgroundColor.setter
  def backgroundColor(self, value):
    Functions.TypeCheck(value, [tuple, type(None)], "backgroundColor", "String")
    self.__backgroundColor = value

class Rect: #need to use @property so cant use pygame.rect
    def __init__(self, left, top, width, height):
        self.__owner = None
        self.__left = None
        self.__top = None
        self.__width = None
        self.__height = None
        self.left = left
        self.top = top
        self.width = width
        self.height = height
    @property
    def left(self):
        return self.__left
    @left.setter
    def left(self, value):
      Functions.TypeCheck(value, [float, int], "left", "Rect")
      self.__left = int(value)
      if(self.__owner != None):
        TransformImage(self.__owner)
    @property
    def top(self):
        return self.__top
    @top.setter
    def top(self, value):
      Functions.TypeCheck(value, [float, int], "top", "Rect")
      self.__top = int(value)
      if(self.__owner != None):
        TransformImage(self.__owner)
    @property
    def width(self):
        return self.__width
    @width.setter
    def width(self, value):
      Functions.TypeCheck(value, [float, int], "width", "Rect")
      self.__width = int(value)
      if(self.__owner != None):
        TransformImage(self.__owner)
    @property
    def height(self):
        return self.__height
    @height.setter
    def height(self, value):
      Functions.TypeCheck(value, [float, int], "height", "Rect")
      self.__height = int(value)
      if(self.__owner != None):
        TransformImage(self.__owner)
    ######
    def __getitem__(self, i):
      options = RectItemHelp(self, i)
      return getattr(self, options[i])
    def __setitem__(self, i, newvalue): 
      if(type(newvalue) is not int and type(newvalue) is not float):
        Functions.Err("in PythUnity.Rect[index] = newValue, newValue must be a " + str(int) + " or " + str(float) + " not " + str(type(newvalue)))
      options = RectItemHelp(self, i)
      attr = setattr(self, options[i], newvalue)
    ######
    def ToPygameRect(self):
        return pygame.Rect(self.left, self.top, self.width, self.height)
    def Copy(self):
        return Rect(self.left, self.top, self.width, self.height)

def RectItemHelp(self, i):
  options = ["left", "top", "width", "height"]
  if(type(i) is not int):
    Functions.Err("in PythUnity.Rect[index], index must be a " + str(int) + " not " + str(type(i)))
  if(i > 4 or i < 0):
    Functions.Err("in PythUnity.Rect[index], index must be between values 0 and " + str(len(options)))
  return options
def CopyHelp(self):
  if(self.image != None):
    self._Object__image = (pygame.image.tostring(self._Object__image, 'RGBA'), self._Object__image.get_size())
    self._Object__transformedImage = (pygame.image.tostring(self._Object__transformedImage, 'RGBA'), self._Object__transformedImage.get_size())
  self.rect._Rect__owner = None
  self._Object__parent = None
  for i in self.children:
    CopyHelp(i)

def CopyUnHelp(self, parent):
  if(self._Object__image != None):
    self._Object__image = pygame.image.fromstring(self._Object__image[0], self._Object__image[1], 'RGBA')
    self._Object__transformedImage = pygame.image.fromstring(self._Object__transformedImage[0], self._Object__transformedImage[1], 'RGBA')
  self.rect._Rect__owner = self
  self._Object__parent = parent
  for i in self.children:
    CopyUnHelp(i, self)
def CopyHelp2(self):
  atts = dir(self)
  for att in atts:
    attObj = getattr(self, att)
    if(att[0] != "_" or att[1] == "O"):#if its a _Object__ atribute still copy
        attType = type(attObj)
        if(attType is not types.MethodType and attType is not list and attType is not type(None) and attType is not Object and attType is not pygame.Surface and attType is not Rect):
            if(("_Object__" + att) not in atts):
              setattr(self, att, copy.deepcopy(attObj))
  for i in self.children:
    CopyHelp2(i)

def TransformImage(self, changeColor = False):
  if(self.image != None):
      ratio = self.image.get_size()
      if(type(self.color) is not type(None) and changeColor):
          #self._Object__transformedImage = pygame.Surface((ratio[0], ratio[1]))
          #print("a " + str(ratio[0]*ratio[1]))
          #array = MultColor(np.array(self.color), pygame.PixelArray(self.image), self.image, self.image.get_size())
          #print("z")
          #pygame.surfarray.blit_array(self._Object__transformedImage, array)
          #print("z2")
          #commented section too slow so replaced it till later
          self._Object__transformedImage = self.image
      elif(type(self.color) is type(None)):
          self._Object__transformedImage = self.image
      ratio = self.image.get_size()
      max = ratio[0]
      if(max < ratio[1]):
        max = ratio[1]
      ratio = (float(ratio[0] / max), float(ratio[1] / max))
      ratio = (int(ratio[0] * self.rect.width), int(ratio[1] * self.rect.height))
      self._Object__transformedImage = pygame.transform.scale(self._Object__transformedImage, ratio)
  else:
    self._Object__transformedImage = None
@nb.jit(forceobj=True)
def MultColor(color, array, image, rect):
  multColor = (color[0]/255, color[1]/255, color[2]/255, color[3]/255)
  width = rect[0]
  height = rect[1]
  arr = np.empty((width, height), dtype=float)
  for x in nb.prange(width):
    for y in nb.prange(height):
       newColor = image.unmap_rgb(array[x, y])
       arr[x, y] = image.map_rgb((newColor[0] * multColor[0], newColor[1] * multColor[1], newColor[2] * multColor[2], newColor[3] * multColor[3]))
  return arr