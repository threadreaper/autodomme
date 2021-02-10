#!/usr/bin/env python
import sys
import os
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

folder_icon = 'folder.png'
file_icon = 'file.png'

STARTING_PATH = sg.PopupGetFolder('Folder to display')

treedata = sg.TreeData()


def add_files_in_folder(parent, dirname):
    for root, dirs, files in os.walk(dirname):
        for f in files:
            fullname = os.path.join(root, f)    
            treedata.Insert(parent, fullname, f, values=[
            ], icon=file_icon)
        for f in dirs:
            fullname = os.path.join(root, f)
            treedata.Insert(parent, fullname, f, values=[
            ], icon=folder_icon)
            add_files_in_folder(fullname, fullname)



add_files_in_folder('', STARTING_PATH)


layout = [[sg.Text('File and folder browser Test')],
          [sg.Tree(data=treedata, headings=['col1', 'col2', 'col3'], auto_size_columns=True, num_rows=20, col0_width=30, key='_TREE_', show_expanded=False,),
           ],
          [sg.Button('Ok'), sg.Button('Cancel')]]

window = sg.Window('Tree Element Test').Layout(layout)


while True:     # Event Loop
    event, values = window.Read()
    if event in (None, 'Cancel'):
        break
    print(event, values)
