#!/usr/bin/env python3
"""Custom filebrowser class and associated functions."""
import os

import PySimpleGUI as sG


class FileBrowser():
    """Class for custom file browser widget."""

    def __init__(self, path, theme):
        """Args- path: full path to folder to launch the file browser in."""
        sG.theme(theme)
        self.history = [path]
        self.path = path
        self.treedata = sG.TreeData()
        self._add_folder('', self.path)
        self.layout = [
            [sG.B('<<', k='BACK'), sG.B('^', k='UP'), sG.B('>>', k='RIGHT'),
             sG.Input(path, size=(40, 1), k='PATH', enable_events=True)],
            [sG.Tree(data=self.treedata, headings=[], justification='left',
                     auto_size_columns=True, num_rows=20, col0_width=25,
                     key='FILES', enable_events=True),
             sG.Canvas(None, k='PREVIEW', background_color='#000000')],
            [sG.B('Select'), sG.B('Cancel')]
        ]
        self.window = sG.Window('', layout=self.layout)

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
            self.treedata.insert(parent, fqp, '  ' + folder, [fqp],
                                 folder_icon)
        for file in sorted(files):
            fqp = os.path.join(self.path, file)
            self.treedata.insert(parent, fqp, '  ' + file, [], file_icon)

    def show(self):
        """Show the file browser window."""
        self.window.finalize()
        self.window['PATH'].expand(expand_x=True, expand_y=True)
        while True:
            event, values = self.window.read()
            if event in ['Cancel', sG.WIN_CLOSED]:
                break
            item = values[event][0]
            print(item)
            if os.path.isdir(item):
                self._add_folder(item, item)
        self.window.close()
