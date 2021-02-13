#!/usr/bin/env python3
"""Main application loop for TeaseAI."""
import PySimpleGUI as sG

from options import open_options, OPTIONS
from client import Client
from filebrowser import FileBrowser
from server import Server
from threading import Thread


def main_window():
    """Construct a main program window"""
    sG.theme(OPTIONS['THEME'][3:])

    main_menu = [
        ['&File', ['E&xit']],
        ['&Server', ['Start Server', 'Kill Server', 'Connect to Server']],
        ['&Options', ['Options Menu']]
    ]

    hot_keys = [
        [sG.Button(f"{OPTIONS['HOTKEY_7']}\n7", size=(9, 2), font='ANY 9 bold', k='HOTKEY_7',
                   pad=(4, (15, 2))),
         sG.Button(f"{OPTIONS['HOTKEY_8']}\n8", size=(9, 2), font='ANY 9 bold', k='HOTKEY_8',
                   pad=(5, (15, 2))),
         sG.Button(f"{OPTIONS['HOTKEY_9']}\n9", size=(9, 2), font='ANY 9 bold', k='HOTKEY_9',
                   pad=(4, (15, 2)))],
        [sG.Button(f"{OPTIONS['HOTKEY_4']}\n4", size=(9, 2), font='ANY 9 bold', k='HOTKEY_4',
                   pad=(4, 2)),
         sG.Button(f"{OPTIONS['HOTKEY_5']}\n5", size=(9, 2), font='ANY 9 bold', k='HOTKEY_5',
                   pad=(5, 2)),
         sG.Button(f"{OPTIONS['HOTKEY_6']}\n6", size=(9, 2), font='ANY 9 bold', k='HOTKEY_6',
                   pad=(4, 2))],
        [sG.Button(f"{OPTIONS['HOTKEY_1']}\n1", size=(9, 2), font='ANY 9 bold', k='HOTKEY_1',
                   pad=(4, 2)),
         sG.Button(f"{OPTIONS['HOTKEY_2']}\n2", size=(9, 2), font='ANY 9 bold', k='HOTKEY_2',
                   pad=(5, 2)),
         sG.Button(f"{OPTIONS['HOTKEY_3']}\n3", size=(9, 2), font='ANY 9 bold', k='HOTKEY_3',
                   pad=(4, 2))],
        [sG.Button(f"{OPTIONS['HOTKEY_0']}\n0", size=(38, 3), font='ANY 9 bold', k='HOTKEY_0',
                   pad=(3, 5))],
        [sG.Sizer(0, 10)]
    ]

    media_player_panel = [
        [sG.T('Host Folder:', size=(40, 1), pad=(5, 10))],
        [sG.Input(OPTIONS['HOST_FOLDER'], size=(30, 1), pad=((5, 0), 8),
                  enable_events=True, k='HOST_FOLDER'),
         sG.B('Browse', k='Browse0', metadata='folders', pad=(5, 8))],
        [sG.B('', k='BACK', image_filename='icons/back.png'), 
         sG.B('', k='PAUSE', image_filename='icons/pause.png'),
         sG.B('', k='PLAY', image_filename='icons/play.png'), 
         sG.B('', k='FORWARD', image_filename='icons/forward.png')],
        [sG.Sizer(0, 100)]
    ]

    tab1_layout = hot_keys
    tab2_layout = media_player_panel

    tab_group_layout = [[sG.Tab('Hot Keys', tab1_layout),
                         sG.Tab('Media', tab2_layout)]]

    sidebar = [
        [sG.T(" Online Users:", pad=(3, 2))],
        [sG.Multiline(size=(40, 3), k='ONLINE_USERS', do_not_clear=True,
                      auto_refresh=True, disabled=True)],
        [sG.Multiline("", size=(40, 30), pad=(3, 2), do_not_clear=True,
                      autoscroll=True, write_only=True, auto_refresh=True,
                      disabled=True, reroute_cprint=True, k='CHAT')],
        [sG.Input('', size=(32, 4), do_not_clear=False, pad=(3, 3),
                  k='INPUT'), sG.Submit(size=(5, 1), pad=((2, 3), 3))],
        [sG.TabGroup(tab_group_layout, k='TABS')]
    ]

    # ----- Full layout -----

    media_player = [
        [sG.Image(None, k='IMAGE', pad=(0, 0))]
    ]

    layout = [
        [sG.Menu(main_menu, tearoff=False, pad=(0, 0)),
         sG.Column(media_player, size=(980, 780),
                   element_justification='center',
                   background_color='#000000', pad=(0, 0)),
         sG.Column(sidebar, vertical_alignment='top', pad=(0, 0))],
        [sG.StatusBar('', relief=sG.RELIEF_RIDGE, font='ANY 11',
                      size=(40, 2), pad=(5, (0, 5)), k='SERVER_STATUS'),
         sG.StatusBar('Not connected to any server', relief=sG.RELIEF_RIDGE, font='ANY 11',
                      size=(40, 2), pad=((2, 5), (0, 5)), k='CLIENT_STATUS')]
    ]

    win = sG.Window("TeaseAI", layout, margins=(0, 0), size=(1280, 810),
                    return_keyboard_events=True)
    win.finalize()
    win['INPUT'].expand(expand_y=True)
    win['SERVER_STATUS'].expand(True)
    win['HOST_FOLDER'].expand(True, True)
    win['Browse0'].expand(True)
    win['Browse0'].update()
    win['INPUT'].update()
    win['SERVER_STATUS'].update()
    win['HOST_FOLDER'].update()
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
    win.bind('<Escape>', 'HIDE')
    win.finalize()

    return win


window = main_window()
tray_menu = [
    ['Exit'], 
    ['Unhide']
]
tray = sG.SystemTray(tray_menu, filename='icons/forward.png')

server = Server()
client = Client(window)
HIDDEN = False

while True:
    tray_event = tray.read(timeout=10)[0]
    if tray_event in ['Exit', sG.WIN_CLOSED]:
        window.close()
        break
    elif 'U' in tray_event and HIDDEN:
        window.un_hide()
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
    elif event == 'Submit':
        client.send_message(window['INPUT'].get())
        window['INPUT'].update('')
    elif event == 'HIDE':
        if not HIDDEN:
            window.hide()
            HIDDEN = True
        else:
            window.un_hide()
            HIDDEN = False
    elif 'Browse' in event:
        host_browse = FileBrowser(server.path,
                                  OPTIONS['THEME'][3:])
        host_browse.show()
    elif 'HOTKEY_' in event:
        if window.find_element_with_focus() != window['INPUT']:
            client.send_message(OPTIONS[event])
            window['INPUT'].update('')
    elif event == "Options Menu":
        opts = open_options()
        while True:
            opt_event, opt_vals = opts.read()
            if opt_event in ["Exit", sG.WIN_CLOSED]:
                break
            if opt_event in OPTIONS.dict.keys():
                OPTIONS[opt_event] = opt_vals[opt_event]
            if str(opt_event).startswith('Browse'):
                filetype = opts[opt_event].metadata
                browser = FileBrowser(opts['HOST_FOLDER'].get(),
                                      OPTIONS['THEME'][3:],
                                      filetype)
                browser.show()
                opts['HOST_FOLDER'].update(OPTIONS['HOST_FOLDER'])
            if 'HOTKEY_' in opt_event:
                window[opt_event].update(
                    text=f"{opts[opt_event].get()}\n{opt_event[-1]}")
            if 'ADV_METHOD' in opt_event:
                OPTIONS['ADV_METHOD'] = opt_event
            if opt_event == 'THEME':
                OPTIONS['THEME'] = opt_vals[opt_event][0]
                old = [opts, window]
                window = main_window()
                opts = open_options()
                for expired in old:
                    expired.close()
            else:
                print(f'Event: {opt_event}')
        opts.close()
    elif event != '__TIMEOUT__':
        print(f'Event: {event}')
    if not server.queue.empty():
        status = server.queue.get(False)
        window['SERVER_STATUS'].update(status)


server.exit_event.set()
window.close()
