#!/usr/bin/env python3
"""Custom filebrowser class and associated functions."""
import os
from io import BytesIO

import PySimpleGUI as sG
from PIL import Image, ImageOps

from options import OPTIONS
from server import Server


class FileBrowser():
    """Class for custom file browser widget."""

    def __init__(self, path, theme, filetype=None, history=None):
        """Args- path: full path to folder to launch the file browser in."""
        self.theme = theme
        sG.theme(self.theme)
        self.history = history
        self.path = path
        self.filetype = filetype
        self.treedata = sG.TreeData()

        self.layout = [
            [
                sG.B('<<', k='BACK', disabled=(False, True)[
                    self.history is None]),
                sG.B('^', k='UP', disabled=(False, True)[self.path == '/']),
                sG.Input(path, size=(40, 1), text_color='#000000',
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

        self.window = sG.Window('Browse for %s' % self.filetype,
                                layout=self.layout, finalize=True)
        self.window['IMAGE'].expand(True, True)
        self.preview_frame = self.window['IMAGE'].get_size()
        self.window['PATH'].expand(expand_x=True, expand_y=True)
        self.window['FILES'].bind('<Double-Button-1>', '_double_clicked')
        self._add_folder(self.path)

    def _add_folder(self, path):
        """Add a folder to the tree - internal method only."""
        parent = '' if path == self.path else path
        files = []
        folders = []
        try:
            for item in os.listdir(path):
                if not item.startswith('.'):
                    fqp = os.path.join(path, item)
                    if os.path.isdir(fqp):
                        folders.append(item)
                    elif item.endswith(('jpg', 'jpeg', 'gif', 'png', 'bmp')):
                        files.append(item)
        except PermissionError:
            pass
        folder_icon = 'folder.png'
        for folder in sorted(folders, key=str.lower):
            fqp = os.path.join(path, folder)
            self.treedata.insert(parent, fqp, '  ' + folder, [fqp],
                                 icon=folder_icon)
            if parent in os.listdir(self.path) or parent == '':
                self._add_folder(fqp)
        if self.filetype != 'folders':
            file_icon = 'file.png'
            for file in sorted(files):
                fqp = os.path.join(path, file)
                self.treedata.insert(parent, fqp, '  ' +
                                     file, [], icon=file_icon)
        self.window['FILES'].update(values=self.treedata)

    def _change_path(self, path):
        """Change path of the file browser - Internal use only"""
        self.history = self.path
        self.path = path
        self.treedata = sG.TreeData()
        self._add_folder(path)
        self.window['FILES'].update(values=self.treedata)
        self.window['PATH'].update(value=path)
        self.window['UP'].update(disabled=(False, True)[self.path == '/'])
        self.window['BACK'].update(disabled=(
            False, True)[self.history is None])

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
        while True:
            event, values = self.window.read()
            if event in ['Cancel', sG.WIN_CLOSED]:
                break
            if event == 'UP':
                self._change_path(os.path.dirname(self.path))
            if event == 'BACK':
                self._change_path(self.history)
            if event == 'Select':
                OPTIONS['HOST_FOLDER'] = values['PATH']
                break
            elif len(values['FILES']) > 0:
                if os.path.isfile(values[event][0]):
                    self.preview(values[event][0], self.preview_frame)
            elif event == 'FILES_double_clicked':
                node = values['FILES'][0]
                node = self.treedata.tree_dict[node]
                if str(node.icon).startswith('folder'):
                    self._change_path(node.key)
        self.window.close()


if __name__ == "__main__":
    server = Server()
    win = FileBrowser(server.opt_get('folder'), 'DarkAmber')
    win.show()
