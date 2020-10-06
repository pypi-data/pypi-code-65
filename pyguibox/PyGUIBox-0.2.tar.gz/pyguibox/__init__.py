import sys
import ctypes

#--------------------------------#
# PyGUIBox Coded By Matin Najafi
# https://github.com/matin-me
#--------------------------------#

class PyGuiBoxException(Exception):
    pass

if(sys.platform == 'win32'):
    try:
        import tkinter as tk
        from tkinter import simpledialog
    except:
        raise PyGuiBoxException("There was an error import tkinter.")

    def messagebox(message, title=None, mode=1, icon=None):
        """Displays the box message that you have customized.
        You can customize the icons and buttons in this section.

        Acceptable icons = 1, 2, 3
        Acceptable modes = 1, 2, 3, 4, 5

        -----[Icons]-----
        1 : Warning icon
        2 : Info icon
        3 : Error icon

        -----[Modes Buttons]-----
        1 : Ok
        2 : Ok, Cancel
        3 : Yes, No, Cancel
        4 : Yes, No
        5 : Ok, Help


        Example : messagebox(message="What is your name?", title="Enter name", mode=3, icon=2)

        Returns the text of the button clicked on."""
        acceptable_icons = {1:0x30, 2:0x40, 3:0x10}
        acceptable_modes = {1:0x0, 2:0x01, 3:0x03, 4:0x04, 5:0x4000}

        if(icon in acceptable_icons): ALERT_ICON = acceptable_icons[icon];
        elif(icon == None): ALERT_ICON = None;
        else: raise PyGuiBoxException("Unknown icon number");


        if(mode in acceptable_modes): ALERT_MB = acceptable_modes[mode];
        else: raise PyGuiBoxException("Unknown mode number");
            
        if(ALERT_ICON == None): MSG_BOX = ctypes.windll.user32.MessageBoxW(0, message, title, ALERT_MB);
        else: MSG_BOX = ctypes.windll.user32.MessageBoxW(0, message, title, ALERT_MB | ALERT_ICON);
        if(MSG_BOX == 1): return "OK";
        elif(MSG_BOX == 2): return "Cancel";
        elif(MSG_BOX == 6): return "Yes";
        elif(MSG_BOX == 7): return "No";
        else: return MSG_BOX;
        

    def alert(message, title=None):
        """Displays a simple message box with text and a single OK button.
        Returns the text of the button clicked on.
        """
        if(title == None): title = " ";
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x0);
        return "OK";

    def confirm(message, title=None, mode=1):
        """Displays a simple confirm box.
        You can customize the text and title of this message box.
        This message box also has the ability to change the mode.
        Mode 1 buttons: OK, Cancel
        Mode 2 buttons: Yes, No, Cancel
        
        Returns the text of the button clicked on.
        """
        if(mode == 1): CONFIRM_MODE = 0x01;
        elif(mode == 2): CONFIRM_MODE = 0x03;
        else: raise PyGuiBoxException("Unknown mode number");
        if(title == None): title = " ";
        MSG_BOX = ctypes.windll.user32.MessageBoxW(0, message, title, CONFIRM_MODE)
        if(MSG_BOX == 6): return "Yes";
        elif(MSG_BOX == 7): return "No";
        elif(MSG_BOX == 2): return "Cancel";
        else: return "OK";

    def prompt(message, title=None):
        """Displays a message box with text input.
        You can customize the text and title of this message box.
        Returns text entered by the user.

        (None return: The user has not entered anything)
        (Cancel return: The user has clicked the cancel button)
        """

        PROMPT_BOX = tk.Tk()
        PROMPT_BOX.resizable(0, 0)
        PROMPT_BOX.withdraw()

        if(title == None): title = " ";
        PROMPT_RESULT = simpledialog.askstring(title=title, prompt=message)

        if(PROMPT_RESULT == None): return "Cancel";
        elif(PROMPT_RESULT == ""): return None;
        else: return PROMPT_RESULT

    def password(message, title=None):
        """Displays a message box with text input.
        (The text entered by the user is displayed as *)

        You can customize the text and title of this message box.
        Returns text entered by the user.
        
        (None return: The user has not entered anything)
        (Cancel return: The user has clicked the cancel button)
        """

        PASSWORD_BOX = tk.Tk()
        PASSWORD_BOX.resizable(0, 0)
        PASSWORD_BOX.withdraw()

        if(title == None): title = " ";
        PROMPT_RESULT = simpledialog.askstring(title=title, prompt=message, show="*")

        if(PROMPT_RESULT == None): return "Cancel";
        elif(PROMPT_RESULT == ""): return None;
        else: return PROMPT_RESULT
    
else:
    def errorLoadFunctions():
        raise PyGuiBoxException(
            "You can only use (messagebox, alert, confirm, prompt, password) functions in Windows."
        )

    alert = confirm = prompt = password = errorLoadFunctions