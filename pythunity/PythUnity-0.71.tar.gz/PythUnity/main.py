import pygame
import copy 
from PythUnity import Classes
from PythUnity import Variables
from PythUnity import Functions
from datetime import datetime

def init():
  pygame.init()
  #Screen######
  global screen
  screen = pygame.display.set_mode(Variables.var.screenRect)
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
      rect = None
      if(not(i.text is None)):
        font = pygame.font.Font(i.text.font + ".ttf", i.text.fontSize) 
        text = font.render(i.text.text, True, i.text.fontColor, i.text.backgroundColor)
        rect = font.size((i.text.text))
        rect = pygame.Rect(i.rect.left + offset[0], i.rect.top + offset[1], rect[0], rect[1])
        #print(rect)
        screen.blit(text, rect)
      elif(not(i.image is None)):
        rect = i.rect.Copy()
        rect.left = rect.left + offset[0]
        rect.top = rect.top + offset[1]
        screen.blit(i._Object__transformedImage, rect.ToPygameRect())
      elif(not(i.color is None)):
        rect = i.rect.Copy()
        rect.left = rect.left + offset[0]
        rect.top = rect.top + offset[1]
        if(len(i.color) == 3):
          pygame.draw.rect(screen, i.color, rect.ToPygameRect())
        elif(len(i.color) == 4):
          s = pygame.Surface((rect.width, rect.height))
          s.set_alpha(i.color[3])
          s.fill((i.color[0], i.color[1], i.color[2]))
          screen.blit(s, (rect.left, rect.top))
        elif(len(i.color) != 0):
          raise ValueError("Object has invalid color can be in formats: RGB and RGBA, or as ()")
      else:
        rect = i.rect.Copy()
        rect.left = rect.left + offset[0]
        rect.top = rect.top + offset[1]
      ########################################
      #GET BUTTON PRESSES#####################
      hovering = Touching(rect, Variables.var.mousePosition)
      global clicked
      type = None
      if(i.button != None):
        touching = mousePressed[0] and hovering
        if(touching):
          if(i.button.onClick != None):
            type = 0
            i.button._Button__dragging = True
        elif(mouseScrolling[0] and not i.button.dragging and hovering):
          if(i.button.onScroll != None):
            type = 1
        elif(i.button.dragging and (hovering or i.button.enableDragOff) and Variables.var.mouseDragging):
          if(i.button.onDrag != None):
            type = 2
        elif((not hovering and not i.button.enableDragOff) or not Variables.var.mouseDragging):
          if(i.button.onClickOff != None and i.button.dragging == True):
            type = 3
          i.button._Button__dragging = False
        if(type != None or hovering):
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
  while True:
    startTime = datetime.now()#Set Start Time
    #GetMousePos##############################
    mousePressed = (False, "")
    mouseScrolling = (False, 0)
    mouseUp = ""
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
    ##########################################
    screen.fill(Variables.var.backgroundColor)
    clicked = []
    for i in Variables.var.parts:
      MainFunction(i, (0, 0))
    #RUN BUTTON PRESSES#####################
    group = None
    for i in clicked:
      if(not i[0].destroyed):
        if(group == None or group == i[0].clickGroup):
          group = i[0].clickGroup
          if(i[1] == 0):
            i[0].button.onClick(i[0], mousePressed[1])
          elif(i[1] == 1):
            i[0].button.onScroll(i[0], mouseScrolling[1])
          elif(i[1] == 2):
            i[0].button.onDrag(i[0])
          elif(i[1] == 3):
            i[0].button.onClickOff(i[0], mouseUp)
        else:
          if(i[0].button.dragging and i.button.enableDragOff):
            i[0].button.onDrag(i[0])
          elif(i[0].button.dragging):
            i[0].button._Button__dragging = False
            i[0].button.onClickOff(i[0], mouseUp)
    ########################################
    for i in Variables.var.parts:
      Update(i)
    Variables.var._Var__deltaTime = (datetime.now()-startTime).total_seconds()#Set DeltaTime
    pygame.display.flip()
  #################