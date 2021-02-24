#!/usr/bin/env python3
"""Custom filebrowser class and associated functions."""
import os
from io import BytesIO

import PySimpleGUI as sG
from PIL import Image, ImageOps

from options import OPTIONS
from client import Client
from server import Server
import threading


def open_server_browser(client, path=None, history=None):
    browser = ServerBrowser(client, OPTIONS['THEME'].split()[1], path, history)
    threading.Thread(target=browser.show()).start()


class ServerBrowser():
    """Class for custom file browser widget."""

    def __init__(self, client: Client, theme, path=None, filetype=None,
                 history=None):
        """Args- path: full path to folder to launch the file browser in."""
        self.theme = theme
        sG.theme(self.theme)
        self.history = history
        self.client = client
        self.path = self.client.session.srv_folder if path is None else path
        self.filetype = filetype
        self.treedata = sG.TreeData()
        self.die = False
        self._request_folder(self.path)

        self.layout = [
            [
                sG.B('<<', k='BACK', disabled=(False, True)[
                    self.history is None]),
                sG.B('^', k='UP', disabled=(False, True)[self.path == '/']),
                sG.Input(self.path, size=(40, 1), text_color='#000000',
                         k='PATH', disabled=True),
            ],
            [
                sG.Tree(
                    data=self.treedata,
                    headings=[],
                    justification='left',
                    num_rows=20,
                    col0_width=40,
                    key='FILES',
                    enable_events=True,
                ),
                sG.Image(None, None, '#000000', (400, 400), k='IMAGE')
            ],
            [sG.Sizer(650, 1), sG.B('Select'), sG.B('Cancel')],
        ]

        self.window = sG.Window(self.path,
                                layout=self.layout, finalize=True)
        self.window['IMAGE'].expand(True, True)
        self.preview_frame = self.window['IMAGE'].get_size()
        self.window['PATH'].expand(expand_x=True, expand_y=True)
        self.window['FILES'].bind('<Double-Button-1>', '_double_clicked')

    def _request_folder(self, path):
        self.client.send_message('PATH:%s' % path)
        folders = self.client.session.browser_folders
        files = self.client.session.browser_files
        while len(folders) < 1 and len(files) < 1:
            folders = self.client.session.browser_folders
            files = self.client.session.browser_files
        self.client.session.browser_folders = []
        self.client.session.browser_files = []
        self._add_folder(path, folders, files)

    def _add_folder(self, path, folders, files):
        """Add a folder to the tree - internal method only."""
        folder_icon = 'folder.png'
        parent = '' if path == client.session.srv_folder else path
        for folder in sorted(folders, key=str.lower):
            fqp = os.path.join(path, folder)
            self.treedata.insert(parent, fqp, '  ' + folder, [fqp],
                                 icon=folder_icon)
            self._request_folder(fqp)
        file_icon = 'file.png'
        for file in sorted(files):
            fqp = os.path.join(path, file)
            self.treedata.insert(parent, fqp, '  ' +
                                 file, [], icon=file_icon)

    def _change_path(self, path):
        new = ServerBrowser(client, self.theme, path, self.path)
        threading.Thread(target=new.show()).start()
        self.window.close()

    def preview(self, image, size):
        """Display an image in the preview pane."""
        img = Image.open(image)
        img = ImageOps.pad(img, size=size)
        with BytesIO() as bio:
            img.save(bio, format="PNG")
            del img
            self.window['IMAGE'].update(data=bio.getvalue())

    def show(self):
        """Show the file browser window."""
        while not self.die:
            event, values = self.window.read(timeout=50)
            print(event)
            if event in ['Cancel', None]:
                break
            if event == 'UP':
                path = self.path.split('/')
                if path[-1] == '':
                    path.pop()
                print(path)
                new_path = ''
                new_path += ''.join(x + '/' for x in path if x != path[-1])
                self._change_path(new_path)
                break
            if event == 'BACK':
                self._change_path(self.history)
                break
            if event == 'Select':
                self.path = values['PATH']
                break
            elif event == 'FILES_double_clicked':
                node = self.treedata.tree_dict[values['FILES'][0]]
                if str(node.icon).startswith('folder'):
                    self.die = True
                    threading.Thread(target=open_server_browser(
                        self.client, node.key, self.path)).start()
                    break
                if self.die:
                    break
                elif str(node.icon).startswith('file'):
                    self.client._request_file(str(node.key))
            else:
                print(event, values)
        else:
            self.window.close()


if __name__ == "__main__":
    server = Server()
    server.set_up_server()
    client = Client()
    client.connect()
    while client.session.srv_folder == '':
        pass
    threading.Thread(target=open_server_browser(client), daemon=True).start()
