#!/usr/bin/env python3
"""Load/Save user options and spawn the options window"""
import os
import json
from json.decoder import JSONDecodeError
import PySimpleGUI as sG


load_defaults = {
    'THEME': '5. BrownBlue',
    'HOTKEY_7': 'Safe Word',
    'HOTKEY_8': 'Yes',
    'HOTKEY_9': 'No',
    'HOTKEY_4': 'Stop',
    'HOTKEY_5': 'Faster',
    'HOTKEY_6': 'Slower',
    'HOTKEY_1': 'Greeting',
    'HOTKEY_2': 'May I cum?',
    'HOTKEY_3': 'Stroke',
    'HOTKEY_0': 'O N   T H E   E D G E',
    'USERNAME': None,
    'PASSWORD': None,
    'SAVE_CREDENTIALS': True,
    'CHAT_NAME': None,
    'SERVER_PORT': 1337,
    'SERVER_ADDRESS': None,
}


def load_options():
    """Load the config file or load defaults"""
    opts = sG.UserSettings('config.json', os.getcwd())
    try:
        with open('config.json', 'r') as file:
            opts.dict = json.load(file)
        return opts
    except (FileNotFoundError, JSONDecodeError):
        sG.popup_ok('Config file missing or invalid.\n'
                    'Using configuration defaults.', modal=True)
        for option in load_defaults:
            opts[option] = load_defaults[option]
        return opts


OPTIONS = load_options()


"""

OPTIONS['RANDOMIZE'] = False
OPTIONS['ADV_METHOD'] = 'ADV_METHOD_AI'
OPTIONS['SLIDESHOW_INCREMENT'] = 5
"""


def calc_vscroll():
    """
    Calculates and returns the vertical scroll offset for the theme listbox.

    :return: The vertical scroll offset
    :rtype: float
    """
    offset = OPTIONS['THEME'].split('.')[0]
    themes = len(sG.theme_list())
    return round(int(offset) / themes, 2) - .05


def open_options(server):
    """Open the options menu"""
    sG.theme(OPTIONS['THEME'].split()[1])

    gen_col_one = [
        [sG.T('General Options')],
        [sG.T('Username for Chat:')],
        [sG.In(OPTIONS['CHAT_NAME'], enable_events=True, size=(20, 1),
               k='CHAT_NAME')],
        [sG.HorizontalSeparator()],
        [sG.T('Client Options')],
        [sG.T('Server Address', size=(20, 1)),
         sG.In(OPTIONS['SERVER_ADDRESS'], size=(20, 1), enable_events=True,
               k='SERVER_ADDRESS')],
        [sG.T('Server Port', size=(20, 1)),
         sG.In(OPTIONS['SERVER_PORT'], size=(20, 1), enable_events=True,
               k='SERVER_PORT')],
        [sG.HorizontalSeparator()],
        [sG.Checkbox('Randomize Slideshow Order', default=OPTIONS['RANDOMIZE'],
                     k='RANDOMIZE', tooltip='When enabled, randomizes the \
                     order of image slideshows', enable_events=True)],
        [sG.T('Slideshow Advances:')],
        [sG.Radio('Manually', "ADV_METHOD", enable_events=True,
                  default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL',
                  k='ADV_METHOD_MANUAL')],
        [sG.Radio('Every', "ADV_METHOD", enable_events=True,
                  default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_INCREMENTAL',
                  k='ADV_METHOD_INCREMENTAL'),
         sG.Spin(list(range(30)), k='SLIDESHOW_INCREMENT', pad=(0, None),
                 initial_value=OPTIONS['SLIDESHOW_INCREMENT'], size=(3, 1),
                 enable_events=True),
         sG.T('Seconds', pad=(3, 0))],
        [sG.Radio('AI Controlled', "ADV_METHOD", k='ADV_METHOD_AI',
                  default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_AI',
                  enable_events=True)],
        [sG.HorizontalSeparator()],
        [sG.T("Theme Options:")],
        [sG.T('This window will refresh to preview your chosen theme.\n'
              'Restart the program to apply your theme to all windows.')],
        [sG.Listbox(values=[str(i+1)+'. '+x for i, x in
                            enumerate(sG.theme_list())], enable_events=True,
                    select_mode=sG.LISTBOX_SELECT_MODE_BROWSE, size=(20, 12),
                    default_values=OPTIONS['THEME'], k='THEME',)],
    ]

    gen_col_two = [
        [sG.T('Boss key:')],
        [sG.In('ESCAPE', disabled=True, k='BOSS_KEY', size=(20, 1)),
         sG.B('Bind', k='BIND_BOSS_KEY', disabled=True)],
        [sG.Sizer(0, 500)]
    ]

    general_options = [
        [sG.Col(gen_col_one),
         sG.VerticalSeparator(),
         sG.Col(gen_col_two)]
    ]

    hotkey_options = [
        [sG.T('Hotkeys')],
        [sG.T('Configure number pad hotkeys for "lazy chat"')],

    ]

    for i in range(9):
        key_list = [sG.T('Hotkey %s' % i),
                    sG.In(OPTIONS['HOTKEY_%s' % i], size=(20, 1),
                          k='HOTKEY_%s' % i, enable_events=True)]
        hotkey_options.append(key_list)

    server_options = [
        [sG.T('Host Options')],
        [sG.T('Hostname/IP', size=(15, 1)),
         sG.In(server.opt_get('hostname'), size=(20, 1),
               enable_events=True, k='SRV_hostname')],
        [sG.T('Host Port', size=(15, 1)),
         sG.In(server.opt_get('port'), size=(20, 1),
               enable_events=True, k='SRV_port')],
        [sG.T('Host Folder', size=(15, 1)),
         sG.In(server.opt_get('folder'), size=(20, 1),
               enable_events=True, k='SRV_folder'),
         sG.B('Browse', k='Browse0', metadata='folders')],
        [sG.HorizontalSeparator()],
        [sG.T("Domme's Name:", size=(15, 1)),
         sG.In(server.opt_get('domme-name'), size=(20, 1),
               k='SRV_domme-name', enable_events=True)],
    ]

    tab_group_layout = [[sG.Tab('General', general_options),
                         sG.Tab('Hotkeys', hotkey_options),
                         sG.Tab('Server', server_options)]]

    layout = [[sG.TabGroup(tab_group_layout)]]

    dialog = sG.Window("Options", layout, finalize=True)
    dialog['THEME'].set_vscroll_position(calc_vscroll())

    return dialog
