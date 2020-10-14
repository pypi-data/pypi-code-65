import pygame
import copy 
from PythUnity import Classes
from PythUnity import Variables
from PythUnity import Functions
from datetime import datetime
global nextFrameKeys
nextFrameKeys = {}

specialKeys = {304: "LeftShift", 303: "RightShift", 306: "LeftControl", 
305: "RightControl", 300: "NumLock", 301: "CapsLock", 308: "LeftAlt", 307: "RightAlt", 9: "Tab", 
273: "ArrowUp", 274: "ArrowDown", 275: "ArrowRight", 276: "ArrowLeft", 27: "Escape", 8: "Backspace", 13: "Enter", 271: "NumpadEnter", 311: "Windows", 319: "ContextMenu",
279: "End", 281: "PageDown", 280: "PageUp", 278: "Home", 127: "Delete", 266: "NumpadDecimal", 19: "Pause", 316: "PrintScreen",
267: "NumpadDivide", 268: "NumpadMultiply", 269: "NumpadSubtract", 270: "NumpadAdd"}
for i in range(1, 13):#add all F's
  specialKeys[281 + i] = "f" + str(i)
for i in range(0, 10):#add all Numpad
  specialKeys[256 + i] = "Numpad" + str(i)
def KeyToString(key):
  if(key in specialKeys.keys()):
    return specialKeys[key]
  else:
    return chr(key)
def init():
  pygame.init()
  #Screen######
  global screen
  screen = pygame.display.set_mode(Variables.var.screenRect)
  pygame.display.set_icon(Variables.var.icon)
  pygame.display.set_caption(Variables.var.appName)
  #############

  #FUNCTIONS##################
  def Touching(rect, pos):
    return rect.left+rect.width > pos[0] > rect.left and rect.top+rect.height > pos[1] > rect.top
  ############################
  for i in Variables.var.starts:
    i()#run start
  ###Variables.var##########
  mousePressed = (False, "")
  mouseScrolling = (False, 0)
  mouseUp = ""
  global clicked
  clicked = []
  #########################################
  #MAIN FUNCTION###########################
  def MainFunction(i, offset):
    #SET RECT##############################
    rect = i.rect.Copy()
    rect.left = rect.left + offset[0]
    rect.top = rect.top + offset[1]
    if(not(i.image is None) or not(i.text is None)):
      screen.blit(i.transformedImage, rect.ToPygameRect())
    elif(not(i.color is None)):
      if(i.color[3] == 255):
        pygame.draw.rect(screen, i.color, rect.ToPygameRect())
      else:
        s = pygame.Surface((rect.width, rect.height))
        s.set_alpha(i.color[3])
        s.fill((i.color[0], i.color[1], i.color[2]))
        screen.blit(s, (rect.left, rect.top))
    ########################################
    #GET BUTTON PRESSES#####################
    hovering = Touching(rect, Variables.var.mousePosition)
    global clicked
    type = []
    if(i.button != None):
      touching = mousePressed[0] and hovering
      if(touching):
        type = [0]
      elif(mouseScrolling[0] and not i.button.dragging and hovering):
        if(i.button.onScroll != None):
          type = [1]
      elif(i.button.dragging and (hovering or i.button.enableDragOff) and Variables.var.mouseDragging):
        if(i.button.onDrag != None):
          type = [2]
      elif((not hovering and not i.button.enableDragOff) or not Variables.var.mouseDragging):
        if(i.button.dragging == True):
          type = [3]
      if(hovering):
        type.append(4)
      elif(not hovering and i.button._Button__hovering):
        i.button._Button__hovering = False
        if(i.button.onHoverOff != None):
          type.append(5)
    if(len(type) != 0 or hovering):
      clicked.insert(0, (i, type))
    ########################################
    for iChild in i.children:
      MainFunction(iChild, (rect.left, rect.top))
    i.rect.left = i.rect.left + i.velocity[0] * Variables.var.deltaTime
    i.rect.top = i.rect.top + i.velocity[1] * Variables.var.deltaTime
    ########################################
#########################################
  def Update(i):
      if(not i.destroyed):
        for iComp in i.components:
          if(i.destroyed):
            break
          if(iComp[1] != None):
            iComp[1](i)
        for iChild in i.children:
          Update(iChild)
  global nextFrameKeys
  keys = Variables.var.keys
  while True:
    startTime = datetime.now()#Set Start Time
    #GetMousePos##############################
    mousePressed = (False, "")
    mouseScrolling = (False, 0)
    mouseUp = ""
    deleteKeys = []
    for key in keys.keys():
      state = keys[key]
      if(state == "Pressed"):
        keys[key] = "Held"
      elif(state == "Off"):
        deleteKeys.append(key)
    for i in deleteKeys:
      del keys[i]
    for key in nextFrameKeys.keys():
      keys[key] = nextFrameKeys[key]
    nextFrameKeys = {}
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN: 
        if event.button == 1:
            Variables.var._Var__mousePosition = pygame.mouse.get_pos()
            mousePressed = (True, "Left")
            Variables.var._Var__mouseDragging = True
        elif event.button == 3:
            Variables.var._Var__mousePosition = pygame.mouse.get_pos()
            mousePressed = (True, "Right")
            Variables.var._Var__mouseDragging = True
        elif event.button == 2:
            Variables.var._Var__mousePosition = pygame.mouse.get_pos()
            mousePressed = (True, "Middle")
            Variables.var._Var__mouseDragging = True
        elif event.button == 5:
            mouseScrolling = (True, mouseScrolling[1] + 1)
        elif event.button == 4:
            mouseScrolling = (True, mouseScrolling[1] - 1)
      elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            mouseUp = "Left"
        elif event.button == 3:
            mouseUp = "Right"
        elif event.button == 2:
            mouseUp = "Middle"
        Variables.var._Var__mouseDragging = False
      elif event.type == pygame.MOUSEMOTION:
        Variables.var._Var__oldMousePosition = Variables.var.mousePosition
        Variables.var._Var__mousePosition = event.pos
      elif event.type == pygame.KEYDOWN:
        key = KeyToString(event.key)
        keys[key] = "Pressed"
      elif event.type == pygame.KEYUP:
        key = KeyToString(event.key)
        if(keys[key] == "Pressed"):
          nextFrameKeys[key] = "Off"
        else:
          keys[key] = "Off"
    ##########################################
    screen.fill(Variables.var.backgroundColor)
    clicked = []
    for i in Variables.var.parts:
      MainFunction(i, (0, 0))
    #RUN BUTTON PRESSES#####################
    group = None
    for i in clicked:
      if(not i[0].destroyed):
        #print(i[0].index)
        if(group == None or group == i[0].clickGroup):
          group = i[0].clickGroup
          for type in i[1]:
            if(type == 0):
              i[0].button._Button__dragging = True
              if(i[0].button.onClick != None):
                i[0].button.onClick(i[0], mousePressed[1])
            elif(type == 1):
              i[0].button.onScroll(i[0], mouseScrolling[1])
            elif(type == 2):
              i[0].button.onDrag(i[0])
            elif(type == 3):   
              i[0].button._Button__dragging = False
              if(i[0].button.onClickOff != None):
                upButton = mouseUp
                if(upButton == ""):
                    upButton = "Off"
                i[0].button.onClickOff(i[0], upButton)
            elif(type == 4):
              if(not i[0].button.hovering):
                i[0].button._Button__hovering = True
                if(i[0].button.onHoverOn != None):
                  i[0].button.onHoverOn(i[0])
              else:
                if(i[0].button.onHover != None):
                  i[0].button.onHover(i[0])
            elif(type == 5):
              i[0].button.onHoverOff(i[0], "Off")
        else:
          if(i[0].button != None):
              if(3 in i[1] and i[0].button._Button__dragging and i[0].button.enableDragOff):
                i[0].button._Button__dragging = False
                if(i[0].button.onClickOff != None):
                  i[0].button.onClickOff(i[0], mouseUp)
              elif(i[0].button.dragging and i[0].button.enableDragOff):
                if(i[0].button.onDrag != None):
                  i[0].button.onDrag(i[0])
              elif(i[0].button.dragging and not i[0].button.enableDragOff):
                i[0].button._Button__dragging = False
                if(i[0].button.onClickOff != None):
                  i[0].button.onClickOff(i[0], "Blocked")         
              if(i[0].button.hovering):
                i[0].button._Button__hovering = False
                if(i[0].button.onHoverOff != None):
                  i[0].button.onHoverOff(i[0], "Blocked")
    ########################################
    for i in Variables.var.parts:
      Update(i)
    Variables.var._Var__deltaTime = (datetime.now()-startTime).total_seconds()#Set DeltaTime
    pygame.display.flip()
  #################