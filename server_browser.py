#!/usr/bin/env python3
"""Custom server browser class and associated functions."""
from __future__ import annotations

import os
from io import BytesIO


from server import Server
import PySimpleGUI as sG


class ServerBrowser():
    """Class for custom server browser widget."""

    def __init__(self, client, path: str = '',
                 history: str = '') -> None:
        """
        Initializes the server browser.

        :param client: An instance of the `Client` class.
        :type client: :class:`Client`
        :param path: The path to open the server browser in.
        :type path: :type:`str`
        :param history: The previous path of the server browser to\
            accomodate the functionality of the back button.
        :type history::type:`str`
        """
        self.history = history
        self.client = client
        self.path = str(self.client.session.srv_folder) if path == '' else path
        self.treedata = sG.TreeData()
        folders, files = self._request_folder(self.path)
        self._add_folder(self.path, folders, files)

        self.layout = [
            [sG.B('', image_filename='icons/browse_back.png', k='BACK',
                  disabled=(False, True)[self.history == '']),
             sG.B('', image_filename='icons/up.png', k='UP',
                  disabled=(False, True)[self.path == '/']),
             sG.Input(self.path, size=(40, 1), text_color='#000000', k='PATH',
                      disabled=(False, True)[self.history is None])],
            [sG.Tree(data=self.treedata, headings=[], justification='left',
                     num_rows=20, col0_width=40, k='FILES',
                     enable_events=True),
             sG.Image(None, None, '#000000', (400, 400), k='IMAGE')],
            [sG.Sizer(650, 1), sG.B('Select'), sG.B('Cancel')],
        ]

        self.window = sG.Window(self.path, layout=self.layout, finalize=True)
        self.window['IMAGE'].expand(True, True)
        self.preview_frame = self.window['IMAGE'].get_size()
        if self.client.window is not None:
            self.media_player = self.client.window['IMAGE'].get_size()
        self.window['PATH'].expand(expand_x=True, expand_y=True)
        self.window['FILES'].bind('<Double-Button-1>', '_double_clicked')

    def _request_folder(self, path: str) -> tuple[list[str], list[str]]:
        """
        Request a listing of folder contents from the server and return a\
            list of folders and files at the given path.

        :param path: The path to request the contents of.
        :type path: str
        :returns: A list of folders and a list of files at the given path.
        :rtype: tuple[list[str], list[str]]
        """
        self.client.send_message('PATH:%s' % path)
        folders = self.client.session.browser_folders
        files = self.client.session.browser_files
        while folders[0] == 'None' or files[0] == 'None':
            folders = self.client.session.browser_folders
            files = self.client.session.browser_files
        self.client.session.browser_folders = ['None']
        self.client.session.browser_files = ['None']
        return (folders, files)

    def _add_folder(self, path: str, folders: list[str],
                    files: list[str]) -> None:
        """
        Add a folder to the tree.

        :param path: The path to populate on the tree.
        :type path: string
        :param folders: The list of folders to add.
        :type folders: list[str]
        :param files: The list of files to add.
        :type files: list[str]
        """
        folder_icon = 'icons/folder.png'
        parent = ''
        for folder in sorted(folders, key=str.lower):
            fqp = os.path.join(path, folder)
            if folder != 'NULL':
                self.treedata.insert(parent, fqp, '  ' + folder, [fqp],
                                     icon=folder_icon)
            else:
                self.treedata.insert(parent, None, '...', [], None)
        file_icon = 'icons/file.png'
        for file in sorted(files):
            fqp = os.path.join(path, file)
            if file != 'NULL':
                self.treedata.insert(parent, fqp, '  ' +
                                     file, [fqp], icon=file_icon)
            else:
                self.treedata.insert(parent, None, '...', [], None)

    def _change_path(self, path: str) -> None:
        """
        Changes the path of the server browser.

        :param path: The path to change to.
        :type path: string
        """
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

    def preview(self, img: str) -> None:
        """
        Display an image in the preview pane.

        :param img: Path to the image file to be displayed.
        :type img: string
        """
        self.client.recv_lock.acquire()
        image = self.client._request_file(img, self.preview_frame)
        self.client.recv_lock.release()
        with BytesIO() as bio:
            image.save(bio, format="PNG")
            self.window['IMAGE'].update(data=bio.getvalue())

    def select_folder(self, values: dict) -> str:
        """
        Returns the selected folder.

        :param values: The dict of values from the browser window.
        :type values: dict
        :return: The selected folder.
        :rtype: string
        """
        if len(values['FILES']) <= 0:
            return values['PATH']

        node = self.treedata.tree_dict[values['FILES'][0]]
        if str(node.icon).startswith('folder'):
            return values['FILES'][0]
        else:
            return values['PATH']

    def show(self) -> str:
        """Show the file browser window."""
        while True:
            event, values = self.window.read()
            if event in ['Cancel', None]:
                return self.path
            elif event == 'UP':
                self._change_path(os.path.dirname(self.path))
            elif event == 'BACK':
                self._change_path(self.history)
            elif event == 'Select':
                return self.select_folder(values)
            elif event == 'FILES_double_clicked':
                node = self.treedata.tree_dict[values['FILES'][0]]
                if str(node.icon).startswith('icons/folder'):
                    self._change_path(node.key)
                else:
                    self.client.recv_lock.acquire()
                    img = self.client._request_file(str(node.key),
                                                    (980, 780))
                    self.client.recv_lock.release()
                    with BytesIO() as bio:
                        img.save(bio, format="PNG")
                        self.client.window['IMAGE'].update(data=bio.getvalue())
            elif len(values['FILES']) > 0:
                node = self.treedata.tree_dict[values['FILES'][0]]
                if str(node.icon).startswith('icons/file'):
                    self.preview(node.values[0])


if __name__ == "__main__":
    from main import Client
    server = Server()
    server.set_up_server()
    client = Client()
    client.connect()
    srv_folder = client.session.srv_folder
    while srv_folder == '':
        srv_folder = client.session.srv_folder
    browser = ServerBrowser(client, srv_folder)
    browser.show()
