#!/usr/bin/env python3
import sys
import json
import os

if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg



def load_config():
    options = {}
    try:
        with open("config.json", "r") as file:
            options = json.load(file)
            file.close()
            return options
    except FileNotFoundError:
        sg.popup_ok('No config file found\nUsing configuration defaults.', modal=True)
        '''Default Config'''
        OPTIONS = {}
        OPTIONS['DOMME_NAME'] = 'Domme' #done
        OPTIONS['SUB_NAME'] = 'Sub' #done
        OPTIONS['THEME'] = 'DarkAmber' #done
        OPTIONS['RANDOMIZE'] = False  #done
        OPTIONS['DOMME_IMAGE_DIR'] = os.environ['HOME'] #done
        OPTIONS['ADV_METHOD'] = 'ADV_METHOD_AI'
        OPTIONS['SLIDESHOW_INCREMENT'] = 5 #done
        OPTIONS['HOTKEY_7'] = 'Safe Word'
        OPTIONS['HOTKEY_8'] = 'Yes'
        OPTIONS['HOTKEY_9'] = 'No'
        OPTIONS['HOTKEY_4'] = 'Stop'
        OPTIONS['HOTKEY_5'] = 'Faster'
        OPTIONS['HOTKEY_6'] = 'Slower'
        OPTIONS['HOTKEY_1'] = 'Greeting'
        OPTIONS['HOTKEY_2'] = 'May I cum?'
        OPTIONS['HOTKEY_3'] = 'Stroke'
        OPTIONS['HOTKEY_0'] = 'O N  T H E  E D G E'
        OPTIONS['USERNAME'] = ''
        OPTIONS['PASSWORD'] = ''
        OPTIONS['SAVE_CREDENTIALS'] = True
        OPTIONS['CHAT_NAME'] = ''
        OPTIONS['SERVER_PORT'] = None
        OPTIONS['SERVER_ADDRESS'] = ''
        OPTIONS['HOSTNAME'] = '0.0.0.0'
        OPTIONS['HOST_PORT'] = None
        OPTIONS['HOST_FOLDER'] = ''
        options=OPTIONS
    except json.decoder.JSONDecodeError:
        sg.popup_ok('Config file is invalid.\nUsing configuration defaults.', modal=True)
        OPTIONS = {}
        OPTIONS['DOMME_NAME'] = 'Domme' #done
        OPTIONS['SUB_NAME'] = 'Sub' #done
        OPTIONS['THEME'] = 'DarkAmber' #done
        OPTIONS['RANDOMIZE'] = False  #done
        OPTIONS['DOMME_IMAGE_DIR'] = os.environ['HOME'] #done
        OPTIONS['ADV_METHOD'] = 'ADV_METHOD_AI'
        OPTIONS['SLIDESHOW_INCREMENT'] = 5 #done
        OPTIONS['HOTKEY_7'] = 'Safe Word'
        OPTIONS['HOTKEY_8'] = 'Yes'
        OPTIONS['HOTKEY_9'] = 'No'
        OPTIONS['HOTKEY_4'] = 'Stop'
        OPTIONS['HOTKEY_5'] = 'Faster'
        OPTIONS['HOTKEY_6'] = 'Slower'
        OPTIONS['HOTKEY_1'] = 'Greeting'
        OPTIONS['HOTKEY_2'] = 'May I cum?'
        OPTIONS['HOTKEY_3'] = 'Stroke'
        OPTIONS['HOTKEY_0'] = 'O N  T H E  E D G E'
        OPTIONS['USERNAME'] = ''
        OPTIONS['PASSWORD'] = ''
        OPTIONS['SAVE_CREDENTIALS'] = True
        OPTIONS['CHAT_NAME'] = ''
        OPTIONS['SERVER_PORT'] = None
        OPTIONS['SERVER_ADDRESS'] = ''
        OPTIONS['HOSTNAME'] = '0.0.0.0'
        OPTIONS['HOST_PORT'] = None
        OPTIONS['HOST_FOLDER'] = ''
        options = OPTIONS
    finally:
        return options


options = load_config()
OPTIONS = {option: options[option] for option in options}

col = [
    [sg.T('Hostname/IP')],
    [sg.T('Host Port')],
    [sg.T('Host Folder')],
]

col2 = [
    [sg.Input(OPTIONS['HOSTNAME'],size=(20, 1), enable_events=True, k='HOSTNAME')],
    [sg.Input(OPTIONS['HOST_PORT'], size=(20, 1), enable_events=True, k='HOST_PORT')],
    [sg.Input(OPTIONS['HOST_FOLDER'], size=(20, 1), enable_events=True, k='HOST_FOLDER')]
]


def open_options():
    general_options = [
        [sg.T('General Options')],
        [
            sg.T('Username for Chat:'),
            sg.Input(OPTIONS['CHAT_NAME'], enable_events=True, k='CHAT_NAME'),
        ],
        [sg.HorizontalSeparator()],
        [sg.T('Host Options')],
        [sg.Column(col), sg.Column(col2)],
        [sg.HorizontalSeparator()],
        [sg.T('Client Options')],
        [
            sg.T('Server Address'),
            sg.Input(
                OPTIONS['SERVER_ADDRESS'],
                size=(20, 1),
                enable_events=True,
                k='SERVER_ADDRESS',
            ),
        ],
        [
            sg.T('Server Port'),
            sg.Input(
                OPTIONS['SERVER_PORT'],
                size=(20, 1),
                enable_events=True,
                k='SERVER_PORT',
            ),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Checkbox(
                'Randomize Slideshow Order',
                default=OPTIONS['RANDOMIZE'],
                key='RANDOMIZE',
                tooltip='When enabled, randomizes the order of image slideshows',
                enable_events=True,
            )
        ],
        [sg.T('Slideshow Advances:')],
        [
            sg.Radio(
                'Manually',
                "ADV_METHOD",
                enable_events=True,
                default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL',
                key='ADV_METHOD_MANUAL',
            )
        ],
        [
            sg.Radio(
                'Every',
                "ADV_METHOD",
                enable_events=True,
                default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_INCREMENTAL',
                key='ADV_METHOD_INCREMENTAL',
            ),
            sg.Spin(
                list(range(30)),
                key='SLIDESHOW_INCREMENT',
                initial_value=OPTIONS['SLIDESHOW_INCREMENT'],
                size=(3, 1),
                pad=(0, None),
                enable_events=True,
            ),
            sg.T('Seconds', pad=(3, 0)),
        ],
        [
            sg.Radio(
                'AI Controlled',
                "ADV_METHOD",
                default=OPTIONS['ADV_METHOD'] == 'ADV_METHOD_AI',
                key='ADV_METHOD_AI',
                enable_events=True,
            )
        ],
        [sg.HorizontalSeparator()],
        [sg.T("Theme Options:")],
        [
            sg.T(
                'This window will refresh to preview your chosen theme.\n'
                'Restart the program to apply your theme to all windows.'
            )
        ],
        [
            sg.Listbox(
                values=sg.theme_list(),
                default_values=OPTIONS['THEME'],
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                size=(20, 12),
                key='THEME',
                enable_events=True,
            )
        ],
    ]

    domme_options = [
        [sg.T('Domme Options')],
        [sg.T("Domme's Name:")],
        [sg.Input(OPTIONS['DOMME_NAME'], size=(20, 1), key='DOMME_NAME', enable_events=True)],
        [sg.T("Domme's Image Directory:")],
        [sg.Input(OPTIONS['DOMME_IMAGE_DIR'], size=(20, 1), key='DOMME_IMAGE_DIR', enable_events=True),
        sg.B('Browse')]
    ]

    sub_options = [
        [sg.T('Sub Options')],
        [sg.T("Sub's Name")],
        [sg.Input(OPTIONS['SUB_NAME'], size=(20, 1), key='SUB_NAME', enable_events=True)]
    ]

    hotkey_options = [
        [sg.T('Hotkeys')],
        [sg.T('Configure number pad hotkeys for "lazy chat"')],
        [sg.T('Hotkey 7 ='), sg.Input(OPTIONS['HOTKEY_7'], size=(20, 1), k='HOTKEY_7', enable_events=True)],
        [sg.T('Hotkey 8 ='), sg.Input(OPTIONS['HOTKEY_8'], size=(20, 1), k='HOTKEY_8', enable_events=True)],
        [sg.T('Hotkey 9 ='), sg.Input(OPTIONS['HOTKEY_9'], size=(20, 1), k='HOTKEY_9', enable_events=True)],
        [sg.T('Hotkey 4 ='), sg.Input(OPTIONS['HOTKEY_6'], size=(20, 1), k='HOTKEY_4', enable_events=True)],
        [sg.T('Hotkey 5 ='), sg.Input(OPTIONS['HOTKEY_5'], size=(20, 1), k='HOTKEY_5', enable_events=True)],
        [sg.T('Hotkey 6 ='), sg.Input(OPTIONS['HOTKEY_4'], size=(20, 1), k='HOTKEY_6', enable_events=True)],
        [sg.T('Hotkey 1 ='), sg.Input(OPTIONS['HOTKEY_3'], size=(20, 1), k='HOTKEY_1', enable_events=True)],
        [sg.T('Hotkey 2 ='), sg.Input(OPTIONS['HOTKEY_2'], size=(20, 1), k='HOTKEY_2', enable_events=True)],
        [sg.T('Hotkey 3 ='), sg.Input(OPTIONS['HOTKEY_1'], size=(20, 1), k='HOTKEY_3', enable_events=True)],
        [sg.T('Hotkey 0 ='), sg.Input(OPTIONS['HOTKEY_0'], size=(20, 1), k='HOTKEY_0', enable_events=True)]
    ]
    # The tab 1, 2, 3 layouts - what goes inside the tab
    tab1_layout = general_options
    tab2_layout = domme_options
    tab3_layout = sub_options
    tab4_layout = [[sg.T('Script Options')]]
    tab5_layout = hotkey_options

    # The TabgGroup layout - it must contain only Tabs
    tab_group_layout = [[sg.Tab('General', tab1_layout),
                        sg.Tab('Domme', tab2_layout),
                        sg.Tab('Sub', tab3_layout),
                        sg.Tab('Scripts', tab4_layout),
                        sg.Tab('Hotkeys', tab5_layout)]]

    # The window layout - defines the entire window
    layout = [[sg.TabGroup(tab_group_layout)]]
    return sg.Window("Options", layout, size=(1280,720))

def save_config():
    with open("config.json", 'w') as file:
        config = json.dumps(OPTIONS)
        file.write(config)
        file.close()

