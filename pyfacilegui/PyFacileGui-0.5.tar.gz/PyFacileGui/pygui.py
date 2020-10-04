import pyautogui
import keyboard
from datetime import datetime
import os
import yagmail
import touchid
from tkinter import *
import rumps

def type(phrase, key_interval=0.0):
    """
    Performs a key press down, and release, for each of the characters in the messege.
    The messege will be a string.

    :param key_interval is the time interval between each presses, in secondas, default=0.0.

    Usage:
        pygui.type('YOUR MESSEGE')

    Params:
        :param: key_interval
    """
    pyautogui.typewrite(phrase, interval=key_interval)

def press(key):
    """
    Performs a hotkey press, and release.

    Usage:
        pygui.press('HOTKEY')
    """
    keyboard.press_and_release(key)

def pause_and_wait(key):
    """
    Pauses the program until the giving key is pressed, if no param is given, the program will be blocked forever.

    Usage:
        pygui.pause_and_wait('KEY')
    """
    keyboard.wait(key)

def alert(title='', text=''):
    """
    Shows a alert box with a Ok button.

    Usage:
        pygui.alert('TITLE', 'TEXT')
    """
    pyautogui.alert(text, title)

def entry(text='', title=''):
    """
    Shows a window with title, text, text box, and ok, cancel buttons.
    Returns with text entered, or None if cancel clicked.

    Usage:
        pygui.prompt('TEXT', 'TITLE')

    """
    pyautogui.prompt(text, title)

def time(show_dialog=False):
    """
    Gets the time now and converts into str. Formatted into hh:mm.
    Default is set to False for show_dialog param.

    If :param: show_dialog=False, the time will be shown in the console.
    If :param: show_dialog=True, the time will be shown in a dialog box

    Ussge:
        pygui.time()

    Params:
        :param: show_dialog=False
    """
    time_now = str(datetime.now())
    filtered = time_now[11:16]
    if show_dialog == True:
        pyautogui.alert(title='Time', text=filtered)
    elif show_dialog == False:
        return filtered

def user():
    """
    This function gets the username of the current user.

    There is no param for this function.

    Usage:
        pygui.user()
    """
    return os.getlogin()

def send_email(sender_email='', sender_password='', from_address='', to='', subject='', body=''):
    """
    This function sends an email to a specific address from an email address of your choice.

    Params:
        :param: sender_email
        :param: sender_password
        :param: from_address
        :param: to
        :param: subject
        :param: body
    
    Usage:
        pygui.send_email(from_address, to, subject, body)
    """
    with yagmail.SMTP(sender_email, sender_password) as yag:
        yag.send(to, subject, body)

def touchid_authenticate(reason='authenticate via Touch ID'):
    """
    Touch ID authenticate on macbook pros that supports touch id.

    Usage:
        pygui.authenticate(reason='authenticate via Touch ID')
    """
    touchid.authenticate(reason)

def touchid_is_avalible():
    """
    This function checks if your macbook supports touch id.

    Usage:
        pygui.is_avalible()
    """
    touchid.is_available()

def left_click():
    """
    Performs a left click and release.

    Usage:
        pygui.left_click()
    """
    pyautogui.leftClick()

def right_click():
    """
    Performs a right click and release.

    Usage:
        pygui.right_click()
    """
    pyautogui.rightClick()

def scroll(scrolls=1):
    """
    Acts as a mouse scrollwheel.
    
    Param scrolls is the amount of scrolling. Default 1.

    Params:
        :param: scrolls

    Usage:
        pygui.scroll()
    """
    pyautogui.scroll(scrolls)

def password(text='', title=''):
    """
    Shows a dialog box with a title, text, password entry, and ok, cancel buttons.

    Assigning a varible to this function will return the password, or None if cancel is clicked.
    
    Note:
        Password entry displays * when typing the password.

    Params:
        :param: text
        :param: title

    Usage:
        pygui.password(text='YOUR TEXT', title='YOUR TITLE')

    """
    pyautogui.password()

def tkinter_window(window_title='', window_size='500x300'):
    """
    tkinter application building makes easy.

    Default window size is 500x300

    Usage:
        pygui.tkinter_window(window_title='TITLE', window_size='WINDOW SIZE')

    Params:
        :param: window_size
    """
    root = Tk()
    root.title(window_title)
    root.geometry(window_size)
    root.mainloop()

def sleep(seconds=1):
    """
    Pauses the program for :param: seconds of time.

    Default time for sleep is 1 seconds.

    Usage:
        pygui.sleep(seconds=TIME OF SLEEP)
    """

def move_to(x=None, y=None):
    """
    Moves the cursor to a specific point on the screen.

    Location can be determined by entering x and y varibles in the function.

    Note:
        This function currently only works with primary screen, so any secondary screens won't work.

    Params:
        :param: x
        :param: y
    """
    pyautogui.moveTo(x, y)

def time_seconds(show_dialog=False):
    """
    Shows the time now with seconds as format: hh:mm:ss. If param show_dialog is true the time will be displayed into a dialog window.

    Default for show_dialog is False.

    Param:
        :param: show_dialog

    Usage:
        pygui.time_seconds(show_dialog=False)
    """
    time_now = str(datetime.now())
    filtered = time_now[11:19]
    if show_dialog == True:
        pyautogui.alert(title='Time', text=filtered)
    elif show_dialog == False:
        return filtered

def date(show_dialog=False):
    """
    Displays the current date in format: yyyy-mm-dd.

    Default for show_dialog param is False.

    Param:
        :param: show_dialog

    Usage:
        pygui.date(show_dialog=False)
    """
    time_now = str(datetime.now())
    filtered = time_now[0:10]
    if show_dialog == True:
        pyautogui.alert(title='Time', text=filtered)
    elif show_dialog == False:
        return filtered

def notification(title='', subtitle='', body='', sound=True, other_buttons=None, reply_button=False):
    """
    Shows a notification in MacOS.

    Usage:
        pygui.notification(title='TITLE', subtitle='SUBTITLE', body='BODY', sound=True, other_buttons=None, reply_button=False)
    """
    rumps.notification(title, subtitle, message=body, other_button=other_buttons, has_reply_button=reply_button)

def password_check(password='', text='', title=''):
    """
    Creates a password window that submits a password and automatically checks if the password is the same as param password. If not, returns False. If same, returns True.


    Usage:
        pygui.password_check(password='')
    """
    password_guess = pyautogui.password(text, title)
    if password_guess == password:
        return True
    elif password_guess != password:
        return False

def cursor_position():
    """
    This function displays the current cursor position and the RGB of the cursor.

    Usage:
        pygui.cursor_position()
    """
    pyautogui.displayMousePosition()

def about():
    pyautogui.alert(text='''
    Created using Python
    
    Developer by Jerry Hu
    
    © 2020 Jerry Hu''', title='About')

def encrypt(Password=''):
    password = Password
    password_len = len(password) - 1
    shu1 = password[password_len] + password[1:password_len] + password[0]
    shu2 = shu1[0] + shu1[password_len - 1] + shu1[2:password_len - 1] + shu1[1] + password[0]

    shu2_len = len(shu2) - 1

    encrypted = shu2[shu2_len] + shu2[1:9] + shu2[0]

    return password, shu1, shu2, encrypted

def decrypt(encrypted=''):
    password = encrypted
    password_len = len(password) - 1
    shu1 = password[password_len] + password[1:password_len] + password[0]
    shu2 = shu1[0] + shu1[password_len - 1] + shu1[2:password_len - 1] + shu1[1] + password[0]

    shu2_len = len(shu2) - 1

    encrypted = shu2[shu2_len] + shu2[1:9] + shu2[0]

    return password, shu1, shu2, encrypted