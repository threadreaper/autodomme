#!/usr/bin/env python3
"""Main application loop for TeaseAI."""
import time as t

import PySimpleGUI as sG

from client import Client
from filebrowser import FileBrowser
from options import OPTIONS, open_options
from server import Server
from server_browser import ServerBrowser
from solitaire import MyGame, arcade


def main_window():
    """Construct a main program window"""
    sG.theme(OPTIONS['THEME'].split()[1])

    main_menu = [
        ['&File', ['E&xit']],
        ['&Server', ['Start Server', 'Kill Server', 'Connect to Server']],
        ['&Options', ['Options Menu']]
    ]

    keys = []
    for i in [7, 8, 9, 4, 5, 6, 1, 2, 3, 0]:
        button = sG.B(f"{OPTIONS['HOTKEY_%s' % i]}\n{i}",
                      size=(38 if i == 0 else 9, 3 if i == 0 else 2),
                      k='HOTKEY_%s' % i, font='ANY 9 bold',
                      pad=(3, (15, 3) if i in [7, 8, 9] else 3))
        keys.append(button)
    keys[:] = [keys[0:3]] + [keys[3:6]] + [keys[6:9]] + [keys[9:]]

    media_player_panel = [
        [sG.T('Host Folder:', size=(40, 1), pad=(5, 10))],
        [sG.Input(OPTIONS['HOST_FOLDER'], size=(30, 1), pad=((5, 0), 8),
                  enable_events=True, k='HOST_FOLDER'),
         sG.B('Browse', k='HOST_BROWSE', metadata='folders', pad=(5, 8))],
        [sG.B('', k='BACK', image_filename='icons/back.png'),
         sG.B('', k='PAUSE', image_filename='icons/pause.png'),
         sG.B('', k='PLAY', image_filename='icons/play.png'),
         sG.B('', k='FORWARD', image_filename='icons/forward.png')],
        [sG.Sizer(0, 100)]
    ]

    try:
        srv_folder = client.session.srv_folder if client.connected \
            else 'Not connected'
    except NameError:
        srv_folder = 'Not connected'

    server_media = [
        [sG.T('Server Folder:', size=(40, 1), pad=(5, 10))],
        [sG.Input(srv_folder, size=(30, 1), pad=((5, 0), 8),
                  enable_events=True, k='SRV_FOLDER'),
         sG.B('Browse', k='SRV_BROWSE', pad=(5, 8))],
        [sG.B('', k='SRV_BACK', image_filename='icons/back.png'),
         sG.B('', k='SRV_PAUSE', image_filename='icons/pause.png'),
         sG.B('', k='SRV_PLAY', image_filename='icons/play.png'),
         sG.B('', k='SRV_FORWARD', image_filename='icons/forward.png')],
        [sG.Sizer(0, 100)]
    ]

    tab1_layout = keys
    tab2_layout = media_player_panel
    tab3_layout = server_media

    tab_group_layout = [[sG.Tab('Hot Keys', tab1_layout),
                         sG.Tab('My Media', tab2_layout),
                         sG.Tab('Server Media', tab3_layout)]]

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
         sG.StatusBar('Not connected to any server', relief=sG.RELIEF_RIDGE,
                      font='ANY 11', size=(40, 2), pad=((2, 5), (0, 5)),
                      k='CLIENT_STATUS')]
    ]

    win = sG.Window("TeaseAI", layout, margins=(0, 0), size=(1280, 810),
                    return_keyboard_events=True)
    win.finalize()
    win['INPUT'].expand(expand_y=True)
    win['SERVER_STATUS'].expand(True)
    win['HOST_FOLDER'].expand(True, True)
    win['SRV_FOLDER'].expand(True, True)
    win['HOST_BROWSE'].expand(True)
    win['SRV_BROWSE'].expand(True)
    for i in range(9):
        win.bind('<KP_%s>' % i, 'HOTKEY_%s' % i)
    win.bind('<Escape>', 'HIDE')
    win.finalize()

    return win


window = main_window()
server = Server()
client = Client(window)
slideshow = server.slideshow

time = t.time()

while True:
    delta = t.time() - time
    time = t.time()
    event, values = window.read(timeout=50)
    if event in ["Exit", sG.WIN_CLOSED]:
        break
    elif event == 'Start Server':
        server.set_up_server()
    elif event == 'Kill Server':
        server.kill()
    elif event == 'Connect to Server':
        client = Client(window)
        client.connect()
        window['SRV_FOLDER'].update(value=client.session.srv_folder)
    elif event == 'PLAY':
        slideshow.start()
    elif event == 'PAUSE':
        slideshow.stop()
    elif event == 'BACK':
        slideshow.back()
    elif event == 'FORWARD':
        slideshow.next()
    elif event == 'Submit':
        if client.connected is True:
            client.send_message(window['INPUT'].get())
            window['INPUT'].update('')
        else:
            sG.cprint('Error: Not connected to server')
    elif event == 'HIDE':
        x, y = window.current_location()
        window.hide()
        solitaire = MyGame(window)
        solitaire.setup()
        solitaire.set_location(x, y)
        arcade.run()
    elif 'SRV_BROWSE' in event:
        browser = ServerBrowser(client, OPTIONS['THEME'].split()[1])
        browser.show()
    elif 'HOTKEY_' in event:
        if (
            client.connected is True
            and window.find_element_with_focus() != window['INPUT']
        ):
            client.send_message(OPTIONS[event])
            window['INPUT'].update('')
    elif event == "Options Menu":
        opts = open_options(server)
        while True:
            opt_event, opt_vals = opts.read()
            if opt_event in ["Exit", sG.WIN_CLOSED]:
                break
            if opt_event in OPTIONS.dict.keys():
                OPTIONS[opt_event] = opt_vals[opt_event]
            if 'SRV' in opt_event:
                server.opt_set(opt_event.split('_')[1],
                               opt_vals[opt_event])
            if opt_event == 'SERV_BROWSE':
                filetype = opts[opt_event].metadata
                browser = FileBrowser(server.opt_get('folder'),
                                      OPTIONS['THEME'][3:],
                                      filetype)
                browser.show()
                opts['SRV_folder'].update(server.opt_get('folder'))
            if 'HOTKEY_' in opt_event:
                window[opt_event].update(
                    text=f"{opts[opt_event].get()}\n{opt_event[-1]}")
            if 'ADV_METHOD' in opt_event:
                OPTIONS['ADV_METHOD'] = opt_event
            if opt_event == 'THEME':
                OPTIONS['THEME'] = opt_vals[opt_event][0]
                old = [opts, window]
                window = main_window()
                client.window = window
                opts = open_options(server)
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

if server.started is True:
    server.kill()
if client.connected is True:
    client.send_message('/quit')
window.close()
