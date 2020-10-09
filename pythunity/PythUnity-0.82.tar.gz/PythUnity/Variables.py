from PythUnity.Functions import Err
from PythUnity.Functions import TypeCheck
class Var:
    def  __init__(self):
        self.__parts = []
        self.__deltaTime = 0
        self.__prefabs = {}
        self.__starts = []
        self.__backgroundColor = (255, 255, 255)
        self.__mousePosition = (0, 0)
        self.__oldMousePosition = (0, 0)
        self.__screenRect = (800, 600)
        self.__mouseDragging = False
    ######
    @property
    def parts(self):
      return self.__parts
    @parts.setter
    def parts(self, value):
      Err("cant set PythUnity.v.parts, use PythUnity.Object() to create and Object.Destroy() to remove, this is only for getting objects at index, run PythUnity.help() for help")
    @property
    def deltaTime(self):
      return self.__deltaTime
    @deltaTime.setter
    def deltaTime(self, value):
      Err("cant set PythUnity.v.deltaTime, use this to see how much time passed since the last Update call")
    @property
    def prefabs(self):
      return self.__prefabs
    @prefabs.setter
    def prefabs(self, value):
      Err("cant set PythUnity.v.prefabs, use PythUnity.AddPrefab() and PythUnity.GetPrefab(), for more information on this run PythUnity.help()")
    @property
    def starts(self):
      return self.__starts
    @starts.setter
    def starts(self, value):
      Err("cant set PythUnity.v.starts, add each start function individually")
    @property
    def mousePosition(self):
      return self.__mousePosition
    @mousePosition.setter
    def mousePosition(self, value):
      Err("cant set PythUnity.v.mousePosition, use this to get the position of the mouse")
    @property
    def oldMousePosition(self):
      return self.__oldMousePosition
    @oldMousePosition.setter
    def oldMousePosition(self, value):
      Err("cant set PythUnity.v.oldMousePosition, use this to get the last position of the mouse")
    @property
    def mouseDragging(self):
      return self.__mouseDragging
    @mouseDragging.setter
    def mouseDragging(self, value):
      Err("cant set PythUnity.v.mouseDragging, use this to see if the mouse is calling Button.Drag functions")
    ###
    @property
    def backgroundColor(self):
      return self.__backgroundColor
    @backgroundColor.setter
    def backgroundColor(self, value):
      TypeCheck(value, tuple, "backgroundColor", "v.")
      self.__backgroundColor = value
    @property
    def screenRect(self):
      return self.__screenRect
    @screenRect.setter
    def screenRect(self, value):
      TypeCheck(value, tuple, "", "screenRect")
      self.__screenRect = value
###
global var
var = Var()