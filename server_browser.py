#!/usr/bin/env python3
"""Custom filebrowser class and associated functions."""
import os
from io import BytesIO

import PySimpleGUI as sG

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
        folders, files = self._request_folder(self.path)
        self._add_folder(self.path, folders, files)

        self.layout = [
            [
                sG.B('', image_filename='icons/browse_back.png', k='BACK',
                     disabled=(False, True)[self.history is None]),
                sG.B('', image_filename='icons/up.png', k='UP',
                     disabled=(False, True)[self.path == '/']),
                sG.Input(self.path, size=(40, 1), text_color='#000000',
                         k='PATH',
                         disabled=(False, True)[self.history is None]),
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
        while folders[0] == 'None' or files[0] == 'None':
            folders = self.client.session.browser_folders
            files = self.client.session.browser_files
        self.client.session.browser_folders = ['None']
        self.client.session.browser_files = ['None']
        return (folders, files)

    def _add_folder(self, path, folders, files):
        """Add a folder to the tree - internal method only."""
        folder_icon = 'folder.png'
        parent = ''
        for folder in sorted(folders, key=str.lower):
            fqp = os.path.join(path, folder)
            if folder != 'NULL':
                self.treedata.insert(parent, fqp, '  ' + folder, [fqp],
                                     icon=folder_icon)
            else:
                self.treedata.insert(parent, None, '...', [], None)
        file_icon = 'file.png'
        for file in sorted(files):
            fqp = os.path.join(path, file)
            if file != 'NULL':
                self.treedata.insert(parent, fqp, '  ' +
                                     file, [fqp], icon=file_icon)
            else:
                self.treedata.insert(parent, None, '...', [], None)

    def _change_path(self, path):
        self.history = self.path
        self.path = path
        self.treedata = sG.TreeData()
        folders, files = self._request_folder(path)
        self._add_folder(path, folders, files)
        self.window['FILES'].update(values=self.treedata)
        self.window['PATH'].update(value=path)
        self.window['UP'].update(disabled=(False, True)[self.path == '/'])
        self.window['BACK'].update(disabled=(
            False, True)[self.history is None])

    def preview(self, img):
        """Display an image in the preview pane."""
        self.client.recv_lock.acquire()
        image = self.client._request_file(img, (400, 400))
        self.client.recv_lock.release()
        with BytesIO() as bio:
            image.save(bio, format="PNG")
            self.window['IMAGE'].update(data=bio.getvalue())

    def show(self):
        """Show the file browser window."""
        while True:
            event, values = self.window.read()
            if event in ['Cancel', None]:
                break
            if event == 'UP':
                path = self.path.split('/')
                if path[-1] == '':
                    path.pop()
                new_path = ''
                new_path += ''.join(x + '/' for x in path if x != path[-1])
                if new_path[-1] == '/' and len(new_path) > 1:
                    new_path = new_path[0:-1]
                self._change_path(new_path)
            if event == 'BACK':
                self._change_path(self.history)
            if event == 'Select':
                self.path = values['PATH']
                break
            elif event == 'FILES_double_clicked':
                node = values['FILES'][0]
                node = self.treedata.tree_dict[node]
                if str(node.icon).startswith('folder'):
                    self._change_path(node.key)
                elif str(node.icon).startswith('file'):
                    self.client._request_file(str(node.key))
            elif len(values['FILES']) > 0:
                node = values['FILES'][0]
                node = self.treedata.tree_dict[node]
                if str(node.icon).startswith('file'):
                    self.preview(node.values[0])
        self.window.close()


if __name__ == "__main__":
    server = Server()
    server.set_up_server()
    client = Client()
    client.connect()
    while client.session.srv_folder == '':
        pass
    threading.Thread(target=open_server_browser(client), daemon=True).start()
