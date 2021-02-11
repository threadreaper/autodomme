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
    'HOSTNAME': '0.0.0.0',
    'HOST_PORT': 1337,
    'HOST_FOLDER': os.path.expanduser("~"),
}


def load_options():
    """Load the config file or load defaults"""
    opts = sG.UserSettings('config.json', os.getcwd())
    try:
        with open(opts.full_filename, 'r') as file:
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
OPTIONS['DOMME_NAME'] = 'Domme'
OPTIONS['SUB_NAME'] = 'Sub'
OPTIONS['THEME'] = 'DarkAmber'
OPTIONS['RANDOMIZE'] = False
OPTIONS['DOMME_IMAGE_DIR'] = os.environ['HOME'] #done
OPTIONS['ADV_METHOD'] = 'ADV_METHOD_AI'
OPTIONS['SLIDESHOW_INCREMENT'] = 5
"""


def open_options():
    """Open the options menu"""
    sG.theme(OPTIONS['THEME'][3:])
    col = [
        [sG.T('Hostname/IP', size=(15, 1))],
        [sG.T('Host Port', size=(15, 1))],
        [sG.T('Host Folder', size=(15, 1), enable_events=True)],
    ]

    col2 = [
        [sG.Input(OPTIONS['HOSTNAME'], size=(20, 1),
                  enable_events=True, k='HOSTNAME')],
        [sG.Input(OPTIONS['HOST_PORT'], size=(20, 1),
                  enable_events=True, k='HOST_PORT')],
        [sG.Input(OPTIONS['HOST_FOLDER'], size=(20, 1),
                  enable_events=True, k='HOST_FOLDER'),
         sG.B('Browse')]
    ]

    general_options = [
        [sG.T('General Options')],
        [
            sG.T('Username for Chat:'),
            sG.Input(OPTIONS['CHAT_NAME'], enable_events=True, k='CHAT_NAME'),
        ],
        [sG.HorizontalSeparator()],
        [sG.T('Host Options')],
        [sG.Column(col), sG.Column(col2)],
        [sG.HorizontalSeparator()],
        [sG.T('Client Options')],
        [
            sG.T('Server Address'),
            sG.Input(
                OPTIONS['SERVER_ADDRESS'],
                size=(20, 1),
                enable_events=True,
                k='SERVER_ADDRESS',
            ),
        ],
        [
            sG.T('Server Port'),
            sG.Input(
                OPTIONS['SERVER_PORT'],
                size=(20, 1),
                enable_events=True,
                k='SERVER_PORT',
            ),
        ],
        [sG.HorizontalSeparator()],
        [
            sG.Checkbox(
                'Randomize Slideshow Order',
                default=OPTIONS['RANDOMIZE'],
                key='RANDOMIZE',
                tooltip='When enabled, randomizes the order'
                ' of image slideshows',
                enable_events=True,
            )
        ],
        [sG.T('Slideshow Advances:')],
        [
            sG.Radio(
                'Manually',
                "ADV_METHOD",
                enable_events=True,
                default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL',
                key='ADV_METHOD_MANUAL',
            )
        ],
        [
            sG.Radio(
                'Every',
                "ADV_METHOD",
                enable_events=True,
                default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_INCREMENTAL',
                key='ADV_METHOD_INCREMENTAL',
            ),
            sG.Spin(
                list(range(30)),
                key='SLIDESHOW_INCREMENT',
                initial_value=OPTIONS['SLIDESHOW_INCREMENT'],
                size=(3, 1),
                pad=(0, None),
                enable_events=True,
            ),
            sG.T('Seconds', pad=(3, 0)),
        ],
        [
            sG.Radio(
                'AI Controlled',
                "ADV_METHOD",
                default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_AI',
                key='ADV_METHOD_AI',
                enable_events=True,
            )
        ],
        [sG.HorizontalSeparator()],
        [sG.T("Theme Options:")],
        [
            sG.T(
                'This window will refresh to preview your chosen theme.\n'
                'Restart the program to apply your theme to all windows.'
            )
        ],
        [
            sG.Listbox(
                values=[str(i+1)+'. '+x for i,
                        x in enumerate(sG.theme_list())],
                select_mode=sG.LISTBOX_SELECT_MODE_BROWSE,
                default_values=OPTIONS['THEME'],
                size=(20, 12),
                key='THEME',
                enable_events=True,
            )
        ],
    ]

    domme_options = [
        [sG.T('Domme Options')],
        [sG.T("Domme's Name:")],
        [sG.Input(OPTIONS['DOMME_NAME'], size=(20, 1),
                  key='DOMME_NAME', enable_events=True)],
        [sG.T("Domme's Image Directory:")],
        [sG.Input(OPTIONS['DOMME_IMAGE_DIR'], size=(20, 1),
                  key='DOMME_IMAGE_DIR', enable_events=True),
         sG.B('Browse')]
    ]

    sub_options = [
        [sG.T('Sub Options')],
        [sG.T("Sub's Name")],
        [sG.Input(OPTIONS['SUB_NAME'], size=(20, 1),
                  key='SUB_NAME', enable_events=True)]
    ]

    hotkey_options = [
        [sG.T('Hotkeys')],
        [sG.T('Configure number pad hotkeys for "lazy chat"')],
        [sG.T('Hotkey 7 ='), sG.Input(OPTIONS['HOTKEY_7'],
                                      size=(20, 1), k='HOTKEY_7',
                                      enable_events=True)],
        [sG.T('Hotkey 8 ='), sG.Input(OPTIONS['HOTKEY_8'],
                                      size=(20, 1), k='HOTKEY_8',
                                      enable_events=True)],
        [sG.T('Hotkey 9 ='), sG.Input(OPTIONS['HOTKEY_9'],
                                      size=(20, 1), k='HOTKEY_9',
                                      enable_events=True)],
        [sG.T('Hotkey 4 ='), sG.Input(OPTIONS['HOTKEY_6'],
                                      size=(20, 1), k='HOTKEY_4',
                                      enable_events=True)],
        [sG.T('Hotkey 5 ='), sG.Input(OPTIONS['HOTKEY_5'],
                                      size=(20, 1), k='HOTKEY_5',
                                      enable_events=True)],
        [sG.T('Hotkey 6 ='), sG.Input(OPTIONS['HOTKEY_4'],
                                      size=(20, 1), k='HOTKEY_6',
                                      enable_events=True)],
        [sG.T('Hotkey 1 ='), sG.Input(OPTIONS['HOTKEY_3'],
                                      size=(20, 1), k='HOTKEY_1',
                                      enable_events=True)],
        [sG.T('Hotkey 2 ='), sG.Input(OPTIONS['HOTKEY_2'],
                                      size=(20, 1), k='HOTKEY_2',
                                      enable_events=True)],
        [sG.T('Hotkey 3 ='), sG.Input(OPTIONS['HOTKEY_1'],
                                      size=(20, 1), k='HOTKEY_3',
                                      enable_events=True)],
        [sG.T('Hotkey 0 ='), sG.Input(OPTIONS['HOTKEY_0'],
                                      size=(20, 1), k='HOTKEY_0',
                                      enable_events=True)]
    ]

    tab1_layout = general_options
    tab2_layout = domme_options
    tab3_layout = sub_options
    tab4_layout = [[sG.T('Script Options')]]
    tab5_layout = hotkey_options

    tab_group_layout = [[sG.Tab('General', tab1_layout),
                         sG.Tab('Domme', tab2_layout),
                         sG.Tab('Sub', tab3_layout),
                         sG.Tab('Scripts', tab4_layout),
                         sG.Tab('Hotkeys', tab5_layout)]]

    layout = [[sG.TabGroup(tab_group_layout)]]

    return sG.Window("Options", layout)
