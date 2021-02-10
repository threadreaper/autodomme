#!/usr/bin/env python3
"""Main application loop for TeaseAI."""
import sqlite3
import time as t

import PySimpleGUI as sG

from client import Client
from filebrowser import FileBrowser
from images import SlideShow
from options import open_options, OPTIONS
from server import Server


def main_window():
    """Construct a main program window"""
    sG.theme(OPTIONS['THEME'][3:])

    main_menu = [
        ['&File', ['E&xit']],
        ['&Server', ['Start Server', 'Kill Server', 'Connect to Server']],
        ['&Options', ['Options Menu']],
        ['&Debug', ['BLANK']],
        ['&About', ['BLANK']]
    ]

    sidebar = [
        [sG.T(" Online Users:", pad=(3, 2))],
        [sG.Multiline(size=(40, 3), k='ONLINE_USERS', do_not_clear=True,
                      auto_refresh=True, disabled=True)],
        [sG.Multiline("", size=(40, 30), pad=(3, 2), do_not_clear=True,
                      autoscroll=True, write_only=True, auto_refresh=True,
                      disabled=True, reroute_cprint=True, k='CHAT')],
        [sG.Input('', size=(32, 4), do_not_clear=False, pad=(3, (2, 4)),
                  k='INPUT'), sG.Submit(size=(5, 1), pad=(1, (1.5)))],
        [sG.Button(f"{OPTIONS['HOTKEY_7']}\n\n7", size=(9, 3), k='HOTKEY_7',
                   pad=(4, (5, 2))),
         sG.Button(f"{OPTIONS['HOTKEY_8']}\n\n8", size=(9, 3), k='HOTKEY_8',
                   pad=(5, (5, 2))),
         sG.Button(f"{OPTIONS['HOTKEY_9']}\n\n9", size=(9, 3), k='HOTKEY_9',
                   pad=(4, (5, 2)))],
        [sG.Button(f"{OPTIONS['HOTKEY_4']}\n\n4", size=(9, 3), k='HOTKEY_4',
                   pad=(4, 2)),
         sG.Button(f"{OPTIONS['HOTKEY_5']}\n\n5", size=(9, 3), k='HOTKEY_5',
                   pad=(5, 2)),
         sG.Button(f"{OPTIONS['HOTKEY_6']}\n\n6", size=(9, 3), k='HOTKEY_6',
                   pad=(4, 2))],
        [sG.Button(f"{OPTIONS['HOTKEY_1']}\n\n1", size=(9, 3), k='HOTKEY_1',
                   pad=(4, 2)),
         sG.Button(f"{OPTIONS['HOTKEY_2']}\n\n2", size=(9, 3), k='HOTKEY_2',
                   pad=(5, 2)),
         sG.Button(f"{OPTIONS['HOTKEY_3']}\n\n3", size=(9, 3), k='HOTKEY_3',
                   pad=(4, 2))],
        [sG.Button(f"{OPTIONS['HOTKEY_0']}\n\n0", size=(38, 3), k='HOTKEY_0',
                   pad=(3, 5))]
    ]

    # ----- Full layout -----

    media_player = [
        [sG.Image(None, k='IMAGE', pad=(0, 0))]
    ]

    layout = [
        [sG.Menu(main_menu, tearoff=False, pad=(0, 0)),
         sG.Column(media_player, size=(980, 800),
                   element_justification='center',
                   background_color='#000000', pad=(0, 0)),
         sG.Column(sidebar, vertical_alignment='top', pad=(0, 0))]
    ]

    win = sG.Window("TeaseAI", layout, margins=(0, 0), size=(1280, 800),
                    return_keyboard_events=True)
    win.finalize()
    win['INPUT'].expand(expand_y=True)
    win['INPUT'].update()
    win.bind('<KP_7>', 'HOTKEY_7')
    win.bind('<KP_8>', 'HOTKEY_8')
    win.bind('<KP_9>', 'HOTKEY_9')
    win.bind('<KP_4>', 'HOTKEY_4')
    win.bind('<KP_5>', 'HOTKEY_5')
    win.bind('<KP_6>', 'HOTKEY_6')
    win.bind('<KP_1>', 'HOTKEY_1')
    win.bind('<KP_2>', 'HOTKEY_2')
    win.bind('<KP_3>', 'HOTKEY_3')
    win.bind('<KP_0>', 'HOTKEY_0')

    return win


window = main_window()

slideshow = SlideShow(OPTIONS['HOST_FOLDER'], window)
if len(slideshow.images) > 0:
    slideshow.show()

server = Server()
client = Client(window)

time = t.time()
conn = sqlite3.connect('teaseai.db')
c = conn.cursor()


while True:
    dt = t.time() - time
    if len(slideshow.images) > 0:
        slideshow.update(dt)
    time = t.time()
    event, values = window.read(timeout=50)
    if event in ["Exit", sG.WIN_CLOSED]:
        break
    elif event == 'Start Server':
        server.set_up_server()
    elif event == 'Kill Server':
        server.exit_event.set()
    elif event == 'Connect to Server':
        client = Client(window)
        client.connect()
    elif event == 'Right:114' and OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL':
        slideshow.next()
    elif event == 'Left:113' and OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL':
        slideshow.back()
    elif event == 'Submit':
        client.send_message(window['INPUT'].get())
        window['INPUT'].update('')
    elif 'HOTKEY_' in event:
        if window.find_element_with_focus() != window['INPUT']:
            client.send_message(event)
            window['INPUT'].update('')
    elif event == "Options Menu":
        sG.set_options(suppress_raise_key_errors=True,
                       suppress_error_popups=True, suppress_key_guessing=True)
        options = open_options()
        while True:
            opt_event, opt_vals = options.read()
            if opt_event in ["Exit", sG.WIN_CLOSED]:
                break
            if opt_event == 'Browse':
                browser = FileBrowser(options['DOMME_IMAGE_DIR'].get(),
                                      OPTIONS['THEME'])
                browser.show()
            if window[opt_event] is not None:
                if isinstance(window[opt_event], sG.Text):
                    window[opt_event].update(opt_vals[opt_event])
                elif isinstance(window[opt_event], sG.Button):
                    window[opt_event].update(
                        text=f"{options[opt_event].get()}\n\n{opt_event[-1]}")
            if 'ADV_METHOD' in opt_event:
                OPTIONS['ADV_METHOD'] = opt_event
            if opt_event == 'THEME':
                OPTIONS['THEME'] = opt_vals[opt_event][0]
                old = [options, window]
                window = main_window()
                options = open_options()
                for x in old:
                    x.close()
            else:
                print(f'Event: {opt_event}')
        options.close()
    elif event != '__TIMEOUT__':
        print(f'Event: {event}')


server.exit_event.set()
window.close()
