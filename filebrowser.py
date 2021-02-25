#!/usr/bin/env python3
"""Custom filebrowser class and associated functions."""
import os
from io import BytesIO

import PySimpleGUI as sG
from PIL import Image, ImageOps

from options import OPTIONS


class FileBrowser():
    """Class for custom file browser widget."""

    def __init__(self, path: str, history: str = '') -> None:
        """
        Initializes the file browser.

        :param path: The path to start the file browser in.
        :type path: string
        :param history: The previous path of the file browser to accomodate\
            the functionality of the back button.
        :type history: string
        """
        sG.theme(OPTIONS['THEME'].split()[1])
        self.history = history
        self.path = path
        self.treedata = sG.TreeData()
        self.layout = [
            [sG.B('<<', k='BACK',
                  disabled=(False, True)[self.history == '']),
             sG.B('^', k='UP', disabled=(False, True)[self.path == '/']),
             sG.Input(path, size=(40, 1), text_color='#000000', k='PATH',
                      disabled=True)],
            [sG.Tree(data=self.treedata, headings=[], justification='left',
                     num_rows=20, col0_width=40, k='FILES',
                     enable_events=True),
             sG.Image(None, None, '#000000', (400, 400), k='IMAGE')],
            [sG.Sizer(650, 1), sG.B('Select'), sG.B('Cancel')],
        ]

        self.window = sG.Window('File Browser', layout=self.layout,
                                finalize=True)
        self.window['IMAGE'].expand(True, True)
        self.preview_frame = self.window['IMAGE'].get_size()
        self.window['PATH'].expand(expand_x=True, expand_y=True)
        self.window['FILES'].bind('<Double-Button-1>', '_double_clicked')
        self._add_folder(self.path)

    def _add_folder(self, path: str) -> None:
        """
        Add a folder to the tree.

        :param path: The folder to be added to the tree.
        :type path: str
        """
        parent = '' if path == self.path else path
        files = []
        folders = []
        try:
            for item in os.listdir(path):
                if item.startswith('.'):
                    continue
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
        file_icon = 'file.png'
        for file in sorted(files, key=str.lower):
            fqp = os.path.join(path, file)
            self.treedata.insert(parent, fqp, '  ' + file, [], icon=file_icon)

    def _change_path(self, path: str) -> None:
        """
        Change path of the file browser - Internal use only

        :param path: The path to change to.
        :type path: string
        """
        self.history = self.path
        self.path = path
        self.treedata = sG.TreeData()
        self._add_folder(path)
        self.window['FILES'].update(values=self.treedata)
        self.window['PATH'].update(value=path)
        self.window['UP'].update(disabled=(False, True)[self.path == '/'])
        self.window['BACK'].update(disabled=(
            False, True)[self.history is None])

    def preview(self, image: str, size: tuple[int, int]) -> None:
        """
        Display an image in the preview pane.

        :param image: The path to the image file to preview.
        :type image: string
        :param size: The size to scale the image to. (width, height)
        :type size: tuple[int, int]
        """
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
            elif event == 'FILES_double_clicked':
                node = values['FILES'][0]
                node = self.treedata.tree_dict[node]
                if str(node.icon).startswith('folder'):
                    self._change_path(node.key)
            elif len(values['FILES']) > 0 and os.path.isfile(values[event][0]):
                self.preview(values[event][0], self.preview_frame)
        self.window.close()


if __name__ == "__main__":
    win = FileBrowser(str(os.path.expanduser))
    win.show()
