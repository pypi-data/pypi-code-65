from utils.utils import TransferFile
from os import path
import locations.vscode as vscode
import locations.intellij as intellij
import locations.pycharm as pycharm
import locations.goland as goland

def pull(remote_path, app_type, local_path=None):
    if local_path is None:
        local_path = path.basename(remote_path).split('-')[1]

    trans = TransferFile(local_path, remote_path)
    trans.download()


def push(local_path, app_type,  remote_path=None):
    if remote_path is None:
        remote_path = path.join('/share',  "%s-%s" %
                                (app_type, path.basename(local_path)))
    trans = TransferFile(local_path, remote_path)
    trans.upload()


class AppType:
    def __init__(self, apptype):
        self.apptype = apptype
        if self.apptype == 'vscode':
            self.settings_path = vscode.settings_path
            self.shortcuts_path = vscode.shortcuts_path
        elif self.apptype == 'intellij':
            self.settings_path = intellij.settings_path 
            self.shortcuts_path = intellij.shortcuts_path 
        elif self.apptype == 'pycharm':
            self.settings_path = pycharm.settings_path 
            self.shortcuts_path = pycharm.shortcuts_path 
        elif self.apptype == 'goland':
            self.settings_path = goland.settings_path 
            self.shortcuts_path = goland.shortcuts_path 
        else:
            raise Exception('apptype wrong (vscode/intellj/pycharm/goland)')

    def _action(self, action, type_):
        if action == 'push':
            if type_ == 'setting':
                push(self.settings_path, self.apptype)
            elif type_ == 'keybinding':
                push(self.shortcuts_path, self.apptype)
            else:
                raise Exception("type_: setting/keybinding")
        else:
            if type_ == 'setting':
                pull(self.settings_path, self.apptype, self.settings_path)
            elif type_ == 'keybinding':
                pull(self.shortcuts_path, self.apptype, self.shortcuts_path)
            else:
                raise Exception("action: push/pull")

    def push_setting(self):
        self._action('push', 'setting')

    def push_keybinding(self):
        self._action('push', 'keybinding')

    def pull_setting(self):
        self._action('pull', 'setting')

    def pull_keybinding(self):
        self._action('pull', 'keybinding')

    def push(self):
        self.push_setting()
        self.push_keybinding()

    def pull(self):
        self.pull_setting()
        self.pull_keybinding()
