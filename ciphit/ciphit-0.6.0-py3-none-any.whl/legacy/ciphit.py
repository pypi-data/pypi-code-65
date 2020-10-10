import os
import sys
import argparse
from pathlib import Path

# sys.path.insert(0,
#    os.path.dirname(os.path.dirname(
#        os.path.abspath(__file__))))

try:
    import aes
    from asciimatics.event import KeyboardEvent
    from asciimatics.widgets import (
        Frame,
        ListBox,
        Layout,
        FileBrowser,
        Divider,
        Text,
        Button,
        TextBox,
        Widget,
        Label,
        PopUpDialog,
    )
    from asciimatics.scene import Scene
    from asciimatics.screen import Screen
    from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
except ImportError:
    print("ERROR: Couldn't find required modules!")
    if input("Do you want to install them now? (y/n): ") == "y":
        os.system("pip3 install asciimatics pycrypto")
        raise SystemExit
    raise SystemExit

__author__ = "sgrkmr"
__version__ = "0.1.3"


def win_ansi_init():
    if __import__("platform").system().lower() == "windows":
        from ctypes import windll, c_int, byref

        stdout_h = windll.kernel32.GetStdHandle(c_int(-11))
        mode = c_int(0)
        windll.kernel32.GetConsoleMode(c_int(stdout_h), byref(mode))
        mode = c_int(mode.value | 4)
        windll.kernel32.SetConsoleMode(c_int(stdout_h), mode)


class CryptModel:
    src = None
    key = None
    res = None


class Simple_Crypt(Frame):
    def __init__(self, screen, desc):
        super(Simple_Crypt, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            can_scroll=False,
            title="ciphit",
        )
        self.set_theme("monochrome")
        self.crypt = aes.Crypt()
        self.desc = desc
        self._main()

    def _main(self):
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        self.src = TextBox(
            Widget.FILL_FRAME,
            f"{self.desc}:",
            self.desc.lower(),
            as_string=True,
            line_wrap=True,
        )
        self.key = Text("Key:", "key", hide_char="*")
        layout.add_widget(self.src)
        layout.add_widget(self.key)
        layout.add_widget(Divider())
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 1)
        self.fix()

    def _ok(self):
        CryptModel.src = self.src.value
        CryptModel.key = self.key.value
        if self.desc.lower() == "encrypt":
            CryptModel.res = self.crypt.Encode(repr(CryptModel.src), CryptModel.key)
        else:
            CryptModel.res = "\n".join(
                self.crypt.Decode(CryptModel.src, CryptModel.key)
                .strip("'")
                .split("\\n")
            )
        raise NextScene("end")

    @staticmethod
    def _cancel():
        raise StopApplication("")


class Simple_Crypt_Res(Frame):
    def __init__(self, screen, desc):
        super(Simple_Crypt_Res, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            on_load=self._reload,
            hover_focus=True,
            can_scroll=False,
            title="ciphit",
        )
        self.set_theme("monochrome")
        self.desc = desc
        self._main()

    def _main(self):
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        self.src = TextBox(
            Widget.FILL_FRAME,
            f"{self.desc}ed:",
            self.desc.lower(),
            as_string=True,
            line_wrap=True,
        )
        layout.add_widget(self.src)
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Divider(), 0)
        layout2.add_widget(Divider(), 1)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Copy", self._cpy), 1)
        self.fix()

    def _reload(self):
        # self.src.disabled = True
        self.src.value = CryptModel.res

    def _cpy(self):
        if __import__("platform").system().lower() == "windows":
            import win32clipboard

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(
                CryptModel.res, win32clipboard.CF_UNICODETEXT
            )
            win32clipboard.CloseClipboard()

    def _ok(self):
        raise StopApplication("")


class File_Select(Frame):
    def __init__(self, screen, *args):
        super(File_Select, self).__init__(
            screen, screen.height, screen.width, has_border=False, name="ciphit"
        )

        self.set_theme("monochrome")
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        self._list = FileBrowser(
            Widget.FILL_FRAME,
            os.path.abspath("."),
            name="mc_list",
            on_select=self.popup,
        )
        layout.add_widget(
            Label("Please select the file to {}.".format(args[0].lower()))
        )
        layout.add_widget(Divider())
        layout.add_widget(self._list)
        layout.add_widget(Divider())
        layout.add_widget(Label("Press Enter to select or `q` to quit."))

        self.fix()

    def popup(self):
        CryptModel.src = self._list.value
        raise NextScene("end")

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord("q"), ord("Q"), Screen.ctrl("c")]:
                raise StopApplication("User quit")

        return super(File_Select, self).process_event(event)


class File_Crypt(Frame):
    def __init__(self, screen, desc):
        super(File_Crypt, self).__init__(
            screen,
            screen.height // 5,
            screen.width // 2,
            hover_focus=True,
            can_scroll=False,
            title="ciphit",
        )
        self.set_theme("monochrome")
        self.crypt = aes.Crypt()
        self.desc = desc
        self._main()

    def _main(self):
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        self.key = Text("Key:", "key", hide_char="*")
        layout.add_widget(self.key)
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Divider(), 0)
        layout2.add_widget(Divider(), 1)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 1)
        self.fix()

    def _ok(self):
        try:
            if CryptModel.src is None:
                src = args.path
            else:
                src = CryptModel.src
            with open(src, "r+", encoding="utf-8") as f:
                CryptModel.key = self.key.value
                if self.desc.lower() == "encrypt":
                    CryptModel.src = f.readlines()
                    enc = self.crypt.Encode(
                        repr("\n".join([i.strip("\n") for i in CryptModel.src])),
                        CryptModel.key,
                    )
                else:
                    CryptModel.src = f.read()
                    enc = "\n".join(
                        self.crypt.Decode(CryptModel.src.strip(), CryptModel.key)
                        .strip("'")
                        .split("\\n")
                    )
                f.truncate(0)
                f.seek(0)
                f.write(enc)
            if enc != None:
                raise EOFError
        except EOFError:
            raise NextScene("pass")
        except:
            raise NextScene("fail")

    @staticmethod
    def _cancel():
        raise StopApplication("")


class Crypt_Bubble(Frame):
    def __init__(self, screen, msg):
        super(Crypt_Bubble, self).__init__(
            screen,
            screen.height // 5,
            screen.width // 2,
            on_load=self._load,
            hover_focus=True,
            can_scroll=False,
        )
        self.msg = msg
        if self.msg.lower() == "failure":
            self.set_theme("warning")
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        self.msgbox = Label("", align="^")
        layout.add_widget(self.msgbox)
        layout2 = Layout([100])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        self.fix()

    def _load(self):
        self.msgbox.text = self.msg

    @staticmethod
    def _ok():
        raise StopApplication("")


class File_Edit_Auth(File_Crypt):
    def _ok(self):
        CryptModel.key = self.key.value
        raise NextScene("edit")


class File_Edit(Frame):
    def __init__(self, screen, desc):
        super(File_Edit, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            on_load=self._reload,
            hover_focus=True,
            can_scroll=False,
            title="ciphit",
        )
        self.set_theme("monochrome")
        self.crypt = aes.Crypt()
        self.desc = desc
        self._main()

    def _main(self):
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        self.src = TextBox(
            Widget.FILL_FRAME,
            f"{self.desc}:",
            self.desc.lower(),
            as_string=True,
            line_wrap=True,
        )
        layout.add_widget(self.src)
        layout.add_widget(Divider())
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 1)
        self.fix()

    def _reload(self):
        try:
            if args.path != dcon:
                self.srcf, CryptModel.src = args.path, args.path
            else:
                raise Exception
        except:
            self.srcf = CryptModel.src
        finally:
            if not (CryptModel.src is None or CryptModel.key is None):
                with open(self.srcf, "r+", encoding="utf-8") as f:
                    dec = f.read()
                    dec = "\n".join(
                        self.crypt.Decode(dec.strip(), CryptModel.key)
                        .strip("'")
                        .split("\\n")
                    )
                self.src.value = dec

    def _ok(self):
        with open(self.srcf, "w", encoding="utf-8") as f:
            print(self.src.value)
            wrt = self.crypt.Encode(
                repr("\n".join([i.strip("\n") for i in self.src.value.split("\n")])),
                CryptModel.key,
            )
            f.write(wrt)
        raise StopApplication("")

    @staticmethod
    def _cancel():
        raise StopApplication("")


def __show__(func):
    def inner(*args, **kwargs):
        last_scene = None
        while True:
            try:
                Screen.wrapper(func, catch_interrupt=True, arguments=[last_scene])
                raise SystemExit
            except ResizeScreenError as e:
                last_scene = e.scene

    return inner


def start(desc, *args, **kwargs):
    try:
        if kwargs["end"]:
            pass
    except:
        kwargs["end"] = None
    try:
        if kwargs["add"]:
            pass
    except:
        kwargs["add"] = None

    @__show__
    def _init(screen, scene):
        scenes = [Scene([kwargs["start"](screen, desc)], -1, name="main")]
        if not kwargs["end"] is None:
            scenes.append(Scene([kwargs["end"](screen, desc)], -1, name="end"))
        if not kwargs["add"] is None:
            for i in kwargs["add"]:
                scenes.append(Scene([i[0](screen, i[2])], -1, name=i[1]))

        screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

    _init()


def main():
    global args, dcon
    try:
        rnd = lambda size=8, chars=__import__(
            "string"
        ).ascii_letters + "0123456789@#&$": "".join(
            __import__("random").choice(chars) for _ in range(size)
        )
        dcon = rnd(size=16)
        parser = argparse.ArgumentParser(
            description=f"ciphit -  a cryptography tool by {__author__}", prog="ciphit"
        )
        group = parser.add_mutually_exclusive_group()
        parser.add_argument(
            "-V",
            "--version",
            help="show version",
            action="version",
            version=f"%(prog)s {__version__}",
        )
        group.add_argument("-e", help="plain text encryption", action="store_true")
        group.add_argument("-d", help="plain text decryption", action="store_true")
        group.add_argument("-t", help="edit encrypted files", action="store_true")
        parser.add_argument("-p", "--path", help="specify path", nargs="?", const=dcon)
        args = parser.parse_args()
        if args.e and not args.path:
            start("Encrypt", start=Simple_Crypt, end=Simple_Crypt_Res)
        elif args.d and not args.path:
            start("Decrypt", start=Simple_Crypt, end=Simple_Crypt_Res)
        elif args.e and not args.path == dcon:
            if not Path(args.path).is_file():
                raise FileNotFoundError
            else:
                start(
                    "Encrypt",
                    start=File_Crypt,
                    add=[
                        [Crypt_Bubble, "pass", "SUCCESS"],
                        [Crypt_Bubble, "fail", "FAILURE"],
                    ],
                )
        elif args.d and not args.path == dcon:
            if not Path(args.path).is_file():
                raise FileNotFoundError
            else:
                start(
                    "Decrypt",
                    start=File_Crypt,
                    add=[
                        [Crypt_Bubble, "pass", "SUCCESS"],
                        [Crypt_Bubble, "fail", "FAILURE"],
                    ],
                )
        elif args.t and (not args.path or args.path == dcon):
            start(
                "Edit",
                start=File_Select,
                end=File_Edit_Auth,
                add=[[File_Edit, "edit", "Edit"]],
            )
        elif args.t and args.path:
            if not Path(args.path).is_file():
                raise FileNotFoundError
            else:
                start("Edit", start=File_Edit_Auth, add=[[File_Edit, "edit", "Edit"]])
        elif args.e and args.path == dcon:
            start(
                "Encrypt",
                start=File_Select,
                end=File_Crypt,
                add=[
                    [Crypt_Bubble, "pass", "SUCCESS"],
                    [Crypt_Bubble, "fail", "FAILURE"],
                ],
            )
        elif args.d and args.path == dcon:
            start(
                "Decrypt",
                start=File_Select,
                end=File_Crypt,
                add=[
                    [Crypt_Bubble, "pass", "SUCCESS"],
                    [Crypt_Bubble, "fail", "FAILURE"],
                ],
            )
        else:
            parser.print_help()
            exit(1)
    except FileNotFoundError:
        print(f'ERROR: "{args.path}" No such file or directory exists.')
        exit(1)


if __name__ == "__main__":
    win_ansi_init()
    main()
