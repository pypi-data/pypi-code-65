from tkinter import *
from tkinter import messagebox

from aihelper import Browse, Popup, OkButton

from nrkext import PTRCalibration
from nrkext import initial


def looper():
    root = Tk()

    file = Browse(
        root,
        type="dir",
        title="Select Directory with User Planning",
        initial=initial,
    )
    OkButton(root, function=lambda: close(file_path=file, root=root))
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(parent=root))
    root.mainloop()


def on_closing(parent):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        parent.destroy()


def close(file_path, root):
    try:
        file_path = file_path.get()
        data = PTRCalibration(path=file_path)
        data.extract_data()
        data.save()
        permission = data.permission
        if permission:
            permission.insert(
                0,
                "The following log files are open. The data will not reflect their logs",
            )
            unable_to_fetch = "\n".join(permission)
            Popup(text=unable_to_fetch, parent=root)
        else:
            Popup(text="All done", parent=root)
    except Exception as e:
        Popup(
            text=f"Something I failed to account for came up. Good luck {e}",
            parent=root,
        )


if __name__ == "__main__":
    looper()
