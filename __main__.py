#!/usr/bin/env python3
import sqlite3
import sys
import time as t

from PySide2 import QtWidgets

if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

from client import Client
from filebrowser import FileBrowser
from images import SlideShow
from options import OPTIONS, open_options, save_config
from server import Server

sg.theme(OPTIONS['THEME'])


main_menu = [
    ['&File', ['E&xit']],
    ['&Server', ['Start Server', 'Kill Server', 'Connect to Server']],
    ['&Options', ['Options Menu']],
    ['&Debug', ['BLANK']],
    ['&About', ['BLANK']]
]

sidebar = [
    [sg.T(" Online Users:", pad=(3, 2))],
    [sg.Multiline(size=(40, 3), k='ONLINE_USERS', do_not_clear=True,
     auto_refresh=True, disabled=True)],
    [sg.Multiline("", size=(40, 30), pad=(3, 2), do_not_clear=True,
     autoscroll=True, write_only=True, auto_refresh=True,
     disabled=True, reroute_cprint=True, k='CHAT')],
    [sg.Input('', size=(32, 4), do_not_clear=False, pad=(3, (2, 4)),
     k='INPUT'), sg.Submit(size=(5, 1), pad=(1, (1.5)))],
    [sg.Button(f"{OPTIONS['HOTKEY_7']}\n\n7", size=(9, 3), k='HOTKEY_7',
     pad=(4, (5, 2))),
     sg.Button(f"{OPTIONS['HOTKEY_8']}\n\n8", size=(9, 3), k='HOTKEY_8',
     pad=(5, (5, 2))),
     sg.Button(f"{OPTIONS['HOTKEY_9']}\n\n9", size=(9, 3), k='HOTKEY_9',
     pad=(4, (5, 2)))],
    [sg.Button(f"{OPTIONS['HOTKEY_4']}\n\n4", size=(9, 3), k='HOTKEY_4',
     pad=(4, 2)),
     sg.Button(f"{OPTIONS['HOTKEY_5']}\n\n5", size=(9, 3), k='HOTKEY_5',
     pad=(5, 2)),
     sg.Button(f"{OPTIONS['HOTKEY_6']}\n\n6", size=(9, 3), k='HOTKEY_6',
     pad=(4, 2))],
    [sg.Button(f"{OPTIONS['HOTKEY_1']}\n\n1", size=(9, 3), k='HOTKEY_1',
     pad=(4, 2)),
     sg.Button(f"{OPTIONS['HOTKEY_2']}\n\n2", size=(9, 3), k='HOTKEY_2',
     pad=(5, 2)),
     sg.Button(f"{OPTIONS['HOTKEY_3']}\n\n3", size=(9, 3), k='HOTKEY_3',
     pad=(4, 2))],
    [sg.Button(f"{OPTIONS['HOTKEY_0']}\n\n0", size=(38, 3), k='HOTKEY_0',
     pad=(3, 5))]
]

# ----- Full layout -----

media_player = [
    [sg.Image(None, k='IMAGE', pad=(0, 0))]
]

layout = [
    [sg.Menu(main_menu, tearoff=False, pad=(0, 0)),
     sg.Column(media_player, size=(980, 800), element_justification='center',
     background_color='#000000', pad=(0, 0)),
     sg.Column(sidebar, vertical_alignment='top', pad=(0, 0))]
]

window = sg.Window("TeaseAI", layout, margins=(0, 0), size=(1280, 800),
                   return_keyboard_events=True)
window.finalize()
window['INPUT'].expand(expand_y=True)
window['INPUT'].update()
window.bind('<KP_7>', 'HOTKEY_7')
window.bind('<KP_8>', 'HOTKEY_8')
window.bind('<KP_9>', 'HOTKEY_9')
window.bind('<KP_4>', 'HOTKEY_4')
window.bind('<KP_5>', 'HOTKEY_5')
window.bind('<KP_6>', 'HOTKEY_6')
window.bind('<KP_1>', 'HOTKEY_1')
window.bind('<KP_2>', 'HOTKEY_2')
window.bind('<KP_3>', 'HOTKEY_3')
window.bind('<KP_0>', 'HOTKEY_0')


app = QtWidgets.QApplication([])
slideshow = SlideShow(OPTIONS['DOMME_IMAGE_DIR'], window)
if len(slideshow.images) > 0:
    slideshow.show()

server = Server()

time = t.time()
conn = sqlite3.connect('teaseai.db')
c = conn.cursor()
sg.set_options(suppress_raise_key_errors=True,
               suppress_error_popups=True, suppress_key_guessing=True)


while True:
    dt = t.time() - time
    slideshow.update(dt)
    time = t.time()
    event, values = window.read(timeout=50)
    if event in ["Exit", sg.WIN_CLOSED]:
        break
    elif event == 'Start Server':
        server.set_up_server()
    elif event == 'Kill Server':
        server.exit_event.set()
    elif event == 'Connect to Server':
        client = Client(window)
    elif event == 'Right:114' and OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL':
        slideshow.next()
    elif event == 'Left:113' and OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL':
        slideshow.back()
    elif event == 'Submit':
        client.send_message(window['INPUT'].get())
        window['INPUT'].update('')
    elif 'HOTKEY_' in event:
        if window.find_element_with_focus() != window['INPUT']:
            client.send_message(OPTIONS[event])
            window['INPUT'].update('')
    elif event == "Options Menu":
        options = open_options()
        while True:
            opt_event, opt_vals = options.read()
            print(opt_event)
            if opt_event in ["Exit", sg.WIN_CLOSED]:
                break
            elif opt_event == 'Browse':
                browser = FileBrowser(options['DOMME_IMAGE_DIR'].get())
                browser.show()
                """
                dialog = QtWidgets.QFileDialog.getExistingDirectory(
                None, "Select Folder", OPTIONS['DOMME_IMAGE_DIR'])
                OPTIONS['DOMME_IMAGE_DIR'] = dialog
                options['DOMME_IMAGE_DIR'].update(OPTIONS['DOMME_IMAGE_DIR'])
                """
            elif opt_event == 'THEME':
                sg.theme(opt_vals[opt_event][0])
                old = options
                options = open_options()
                old.close()
            elif opt_event in OPTIONS.keys():
                OPTIONS[opt_event] = opt_vals[opt_event]
                if window[opt_event]:
                    if isinstance(window[opt_event], sg.Text):
                        window[opt_event].update(opt_vals[opt_event])
                    elif isinstance(window[opt_event], sg.Button):
                        window[opt_event].update(
                            text=f"{OPTIONS[opt_event]}\n\n{opt_event[-1]}")

            elif 'ADV_METHOD' in opt_event:
                OPTIONS['ADV_METHOD'] = opt_event
            else:
                print(f'Event: {opt_event}')
        options.close()
    elif event != '__TIMEOUT__':
        print(f'Event: {event}')


server.exit_event.set()
save_config()
window.close()
sys.exit(app.exec_)
