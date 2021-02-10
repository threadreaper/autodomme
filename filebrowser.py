#!/usr/bin/env python3
''' Custom filebrowser class and associated functions '''
import os

import PySimpleGUI as sg


class FileBrowser():
    """ Class for custom file browser widget """
    def __init__(self, path):
        self.history = [path]
        self.path = path
        self.treedata = sg.TreeData()
        self.add_files_in_folder('', self.path)
        self.layout = [
            [sg.B('<<', k='BACK'), sg.B('^', k='UP'), sg.B('>>', k='RIGHT'),
             sg.Input(path, size=(40, 1), k='PATH', enable_events=True)],
            [sg.Tree(data=self.treedata, headings=[],
                     auto_size_columns=True, num_rows=20, col0_width=30, key='_TREE_', show_expanded=False),
             sg.Canvas(None, k='PREVIEW', background_color='#000000')],
            [sg.B('Select'), sg.B('Cancel')]
        ]
        self.window = sg.Window('', layout=self.layout)

        """
        def _append_row(self, item):
            folder_icon = 'folder.png'
            file_icon = 'file.png'
            fqp = os.path.join(self.path, item)
            self.col.append(
                [sg.Image((file_icon, folder_icon)[os.path.isdir(fqp)],
                          key=fqp),
                sg.T(item, key=fqp)]
            )
        """

    def _clear_column(self):
        for item in self.col:
            item[0].update(visible=False)
            item[1].update(visible=False)
        self.col = []

    def _refresh_column(self):
        for item in self.col:
            item[0].update(visible=True)
            item[1].update(visible=True)

    def add_files_in_folder(self, parent, dirname):
        file_icon = 'file.png'
        folder_icon = 'folder.png'
        for root, dirs, files in os.walk(dirname):
            for f in files:
                fullname = os.path.join(root, f)
                self.treedata.Insert(parent, fullname, f, values=[
                ], icon=file_icon)
            for f in dirs:
                fullname = os.path.join(root, f)
                self.treedata.Insert(parent, fullname, f, values=[
                ], icon=folder_icon)

    '''
    def _get_files(self):
        files = []
        folders = []
        for item in os.listdir(self.path):
            fqp = os.path.join(self.path, item)
            if os.path.isdir(fqp):
                folders.append(item)
            else:
                files.append(item)
        for item in sorted(folders):
            self._append_row(item)
        for item in sorted(files):
            self._append_row(item)
    '''

    def show(self):
        """ Show the file browser window
        self.window.finalize()
        self.window['PATH'].expand(expand_x=True, expand_y=True)
        """
        while True:
            event = self.window.read(timeout=50)[0]
            if event in ['Cancel', sg.WIN_CLOSED]:
                break
            elif event != '__TIMEOUT__':
                print(event)
        self.window.close()


gimme = FileBrowser('/home/michael/projects/teaseai')
gimme.show()
