import os

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
def cls():os.system('cls' if os.name=='nt' else 'clear')
def border():
  print("///////////////////////////")
def option(number, text):
  print(str(number) + ". " + text)
def options(array):
    border()
    if(len(array) >= 2):
      print(array[0] + ": ")
      print(array[1])
    for i in range(len(array[2])):
        if(type(array[2][i]) == tuple):
            option(i, array[2][i][0])
        else:
            option(i, array[2][i])
    if(len(array[2]) != 0):
        user = input("Type the number choice or press {ENTER} to go back: ")
        while(user != "" and (not RepresentsInt(user) or int(user) >= len(array[2]))):
           if(not RepresentsInt(user)):
             print("incorrect format")
           else:
             print("option out of range")
           user = input("Type the number choice or press {ENTER} to go back: ")
        if(user != ""):
          cls()
          if(len(array[2][int(user)]) == 3):
            options(array[2][int(user)])
            cls()
            options(array)
          else:
            input("type {ENTER} to continue: ")
          border()
          return False
    else:
      input("type {ENTER} to continue: ")
    border()
    return True
cls()
print("Run PythUnity.help() for help")
border()
def help():
    array = ("Help Options", "", [
        ("Startup", "to start up its very simple\nheres an example of a startup:\n\nimport PythUnity\n#PythUnity.help()\ndef Start():\n   print(\"started\")\nPythUnity.starts.append(Start)\nPythUnity.init()\n\nAnd thats all you have to do, \nyou can put whatever you want before PythUnity.init() runs but after you run PythUnity.init() the rest of your code wont run,\nso you'll have to use buttons and components to get what you need done, \nas you go throught this help section you'll learn how to do so", []),
        ("Creating Objects", "You can create GameObjects just like in Unity! by using PythUnity.Object(), choose one of the options too learn more\nnote: going in order is recommended", [
            ("Creating Rectangles", "to create a rectange you must do PythUnity.Object(transform, color) \nthe transform parameter is an instance of the PythUnity.Rect() value, \ninstantiating the Rect values looks like this PythUnity.Rect(dist_from_left, dist_from_top, width, height)\n\nThe color parameter is a tuple ie. (255, 255, 255) or (255, 255, 255, 50) for semi transparency\nthe two formats you can use are RGB and RGBA", []), 
            ("Creating Images", "if you dont know how to make a rectange I would recommend going back\nmaking an image is alot like making a rectange\nthe difference is instead of using a color you do a PythUnity.Surface\nan example is PythUnity.Object(transform, PythUnity.image(image_path_string))\nthe code above will make an object with an image from that filepath", []), 
            ("Creating Text", "Creating text takes more space but is just as easy as the others, select one of the options to learn more", [
                ("Format", "the format for creating text looks like this:\nPythUnity.Object(transform, PythUnity.String(message, font_size, font, font_color, background_color))", []),
                ("PythUnity.String", "this is the type that stores data on how the text is displayed on the screen", []),
            ("Example", "this will create a highlighted text saying hi: \ntext = PythUnity.String(\"hi\", 24, \"freesansbold\", (255, 255, 0), (0, 255, 255))\nPythUnity.Object(PythUnity.Rect(280, 150, 100, 200), text)", []),
            ("Creating Buttons", "when instantiating the Object class there are additional parameters that allow you to make buttons\n these additional parameters are Object(onClick, onDrag, onClickOff, onScroll, enableDragOff, clickGroup)", [
                ("onClick", "is a method, whenever you click the object this function will run", []),
                ("onDrag", "is a method, whenever you hold the mouse button on the object this function will run", []),
                ("onClickOff", "is a method, whenever you click off the object this function will run", []),
                ("onScroll", "is a method, whenever you use the scroll button while hovering over the Object this will run", []),
                ("enableDragOff", "is a boolean, if enabled if your mouse stops hovering over the object while your dragging \nit will still run the drag funciton till you let go", []),
        ("Object Methods", "Objects come with many built in tools, some you will need to know, some will be useful to know\nHeres a list of all the functions, its recommended to go in order", [
            ("Object.Move(index)", "this function moves the object around the layer\nimagine you have a stack of papers and you move the 56th page down to the 30th page, thats what .Move does, it moves the page to the index'th page", []),
            ("Object.SetParent(target)", "this function sets the parent of an object to another\nimagine you have a russian doll and you put another doll into it, thats what .SetParent does, \nit takes the doll out of one doll and then puts it into another, and in this case the other doll is the target variable", []),
            ("Object.GetParentChildren()", "this function get the children of the parent, remember the russian doll example? the children are the smaller dolls", []),
                ("clickGroup", "talked about in the Variables module, keep reading and you will find this", []),])])]),
            ("Object.Copy()", "this makes a copy of the Object and returns the copy, the copy will have all the same attriutes of the old one, including position so make sure to move it", []),
            ("Object.Destroy()", "this will destroy the object its run on, \nthis will cause it to no longer be rendered or in the child list of the parent, \nrunning functions on destroyed objects will cause the program to crash", []),
            ("Object.AddComp(comp)", "this will add a component,\na component is like a script, just like Unity it has a Start(), and Update() function\nan example you can run is:\nrandObj = PythUnity.Object(PythUnity.Rect(500, 500, 750, 300), (255, 0, 0))\ndef Banana(self):\n   print(\"banana start\")\ndef Apple(self):\n   print(\"apple update\")\nrandObj.AddComp((Banana, Apple))", []),
            ("Object.DelComp(index)", "this will remove a component from the component list at an index,\nfor example if we took the example from AddComp and then ran: \nrandObj.DelComp(0)\nit wouldve removed the component we just added", []),
            ("Object.Decendants()", "this will get all the children of the object your running it on, \naswell as the children of those children and so on and so on", []), 
            ("Variables", "the Object class also comes with variables", [
                ("children", "an array of all the children an Object has", []),
                ("destroyed", "says whether an Object is destroyed or not", []),
                ("parent", "returns the parent of the object, if the object doesnt have a parent it will return None", []),
                ("variables", "a dictionary where components store their variables", []),
                ("image", "if you created an Object with an image it will show here", []),
                ("transformedImage", "will return the image variable after scale and color are applied to it", []),
                ("text", "if you created an Object with text it will show here", []),
                ("color", "if you created an Object with a color it will show here", []),
                ("components", "shows a list of all of your Objects components", []),
                ("clickGroup", "an int that allows you to set the clickGroup of the Object, \nobjects in the same clickGroup wont block eachoher from being clicked\nuseful if you have an image over a button and you dont want the button to get blocked by the image\n(Not Applied Yet)", []),
                ("velocity", "a tuple for the x and y speed of an object, represented as (x, y)", []),
                ("button", "hold information on the onClick and OnDrag etc of the Object, it is a PythUnity.Button type, \nif you didnt add any button functions this value will be set to None", [
                    ("Methods", "", [
                        ("onClick", "its the same as the onClick in the Object parameters", []),
                        ("onClickOff", "its the same as the onClickOff in the Object parameters", []),
                        ("onDrag", "its the same as the onDrag in the Object parameters", []),
                        ("onScroll", "its the same as the onScroll in the Object parameters", [])]),
                    ("Variables", "", [
                        ("enableDragOff", "its the same as the enableDragOff in the Object parameters", []),
                        ("dragging", "says if the Object is currently being dragged", [])])])])]),
        ("Prefabs", "A prefab is a blueprint to create an object", [
            ("AddPrefab", "you can use PythUnity.AddPrefab(\"name\", part) \nto create a prefab from a part and store it at the name string\nheres an example: \npart = PythUnity.Object(PythUnity.Rect(0, 0, 100, 100), (255, 0, 0))\nPythUnity.AddPrefab(\"Square\", part)", []),
            ("GetPrefab", "you can use PythUnity.GetPrefab(\"name\") \nto create a part from a prefab that is stored at the name string\nheres an example: \npart = PythUnity.GetPrefab(\"Square\")", [])])])
    while(True):
      cls()
      if(options(array)):
        if(input("Do you want to Exit? Y/N: ") == "Y"):
          break
    cls()
