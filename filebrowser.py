#!/usr/bin/env python3
"""Custom filebrowser class and associated functions."""
import os

import PySimpleGUI as sg

from options import OPTIONS

sg.theme(OPTIONS['THEME'])


class FileBrowser():
    """Class for custom file browser widget."""

    def __init__(self, path):
        """Args- path: full path to folder to launch the file browser in."""
        self.history = [path]
        self.path = path
        self.treedata = sg.TreeData()
        self._add_folder('', self.path)
        self.layout = [
            [sg.B('<<', k='BACK'), sg.B('^', k='UP'), sg.B('>>', k='RIGHT'),
             sg.Input(path, size=(40, 1), k='PATH', enable_events=True)],
            [sg.Tree(data=self.treedata, headings=[], justification='left',
                     auto_size_columns=True, num_rows=20, col0_width=25,
                     key='FILES'),
             sg.Canvas(None, k='PREVIEW', background_color='#000000')],
            [sg.B('Select'), sg.B('Cancel')]
        ]
        self.window = sg.Window('', layout=self.layout)

    def _add_folder(self, parent, path):
        """Add a folder to the tree - internal method only."""
        file_icon = 'file.png'
        folder_icon = 'folder.png'
        files = []
        folders = []
        for item in os.listdir(path):
            if os.path.isdir(item):
                folders.append(item)
            else:
                files.append(item)
        for folder in sorted(folders):
            fqp = os.path.join(self.path, folder)
            self.treedata.insert(parent, fqp, folder, folder_icon)
        for file in sorted(files):
            fqp = os.path.join(self.path, file)
            self.treedata.insert(parent, fqp, file, [], file_icon)

    def show(self):
        """Show the file browser window."""
        self.window.finalize()
        self.window['PATH'].expand(expand_x=True, expand_y=True)
        while True:
            event = self.window.read(timeout=50)[0]
            if event in ['Cancel', sg.WIN_CLOSED]:
                break
            if event != '__TIMEOUT__':
                print(event)
        self.window.close()


gimme = FileBrowser('/home/michael/projects/teaseai')
gimme.show()
