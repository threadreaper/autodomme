import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import RELIEF_SUNKEN, TITLE_LOCATION_TOP
from PySide2 import QtWidgets
import sys
import time as t
#from client import Client
#from functions import chat, hotkey
from tags import popup
from images import SlideShow
from options import OPTIONS, open_options, save_config
from authenticate import authenticate


sg.theme(OPTIONS['THEME'])
sg.set_options(suppress_raise_key_errors=False, suppress_error_popups=True, suppress_key_guessing=True)

main_menu = [
    ['&File', ['E&xit']],
    ['&Tags', ['Image Tagging']],
    ['&Options', ['Options Menu']],
    ['&Debug', ['BLANK']],
    ['&About', ['BLANK']]
]

if authenticate() == 1:
    save_config()
    sys.exit()

ONLINE_USERS = [
    [sg.T(OPTIONS['DOMME_NAME'], k='DOMME_NAME', size = (40, 1))],
    [sg.T(OPTIONS['SUB_NAME'], k='SUB_NAME', size = (40, 1))]
]

sidebar = [
    [sg.T(" Online Users:", pad = (3, 2))],
    [sg.Frame(None, ONLINE_USERS, title_location=TITLE_LOCATION_TOP, 
    relief=RELIEF_SUNKEN, k='ONLINE_USERS', pad = (3, 2))],
    [sg.Multiline("", size=(40, 38), pad=(3, 2), 
    do_not_clear=True, autoscroll=True, write_only=True, auto_refresh=True,
    disabled=True, reroute_cprint=True, k='CHAT')],
    [sg.Input('', size=(32, 4), do_not_clear=False, pad=(3, (2,4)), k='INPUT'),
    sg.Submit(size=(5, 1), pad=(1, (1.5)))],
    [sg.Button(f"{OPTIONS['HOTKEY_7']}\n\n7", size=(9, 3), k='HOTKEY_7', pad=(4, (5,2))), 
    sg.Button(f"{OPTIONS['HOTKEY_8']}\n\n8", size=(9, 3), k='HOTKEY_8', pad=(5, (5,2))), 
    sg.Button(f"{OPTIONS['HOTKEY_9']}\n\n9", size=(9, 3), k='HOTKEY_9', pad=(4, (5,2)))],
    [sg.Button(f"{OPTIONS['HOTKEY_4']}\n\n4", size=(9, 3), k='HOTKEY_4', pad=(4, 2)), 
    sg.Button(f"{OPTIONS['HOTKEY_5']}\n\n5", size=(9, 3), k='HOTKEY_5', pad=(5, 2)), 
    sg.Button(f"{OPTIONS['HOTKEY_6']}\n\n6", size=(9, 3), k='HOTKEY_6', pad=(4, 2))], 
    [sg.Button(f"{OPTIONS['HOTKEY_1']}\n\n1", size=(9, 3), k='HOTKEY_1', pad=(4, 2)), 
    sg.Button(f"{OPTIONS['HOTKEY_2']}\n\n2", size=(9, 3), k='HOTKEY_2', pad=(5, 2)), 
    sg.Button(f"{OPTIONS['HOTKEY_3']}\n\n3", size=(9, 3), k='HOTKEY_3', pad=(4, 2))],
    [sg.Button(f"{OPTIONS['HOTKEY_0']}\n\n0", size=(38, 3), k='HOTKEY_0', pad=(3, 5))]
]

# ----- Full layout -----

media_player = [
    [sg.Image(None, k='IMAGE', pad=(0,0))]
]

layout = [
    [   
        sg.Menu(main_menu, tearoff=False, pad=(0, 0)),
        sg.Column(media_player, size=(1300, 900), element_justification='center', background_color='#000000', pad=(0, 0)), 
        sg.Column(sidebar, vertical_alignment='top', pad=(0, 0))
    ]
]

window = sg.Window("TeaseAI", layout, margins=(0, 0), size=(1600,900), return_keyboard_events=True)
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
#slideshow = SlideShow(OPTIONS['DOMME_IMAGE_DIR'], window)
#if len(slideshow.images) > 0: 
 #   slideshow.show()
time = t.time()


# Run the Event Loop
while True:
    #message = chat.update()
    #if message:
     #   sg.cprint(message)
   # dt = t.time() - time
   # slideshow.update(dt)
    time = t.time()
    event, values = window.read(timeout=50)
    if event == 'Image Tagging':
   #     popup()
        pass
    if event == "Options Menu":
        options = open_options()
        while True:
            opt_event, opt_vals = options.read()
            if opt_event == "Exit" or opt_event == sg.WIN_CLOSED:
                break
            elif opt_event == 'Browse':
                dialog = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Folder", OPTIONS['DOMME_IMAGE_DIR'])
                OPTIONS['DOMME_IMAGE_DIR'] = dialog
                options['DOMME_IMAGE_DIR'].update(OPTIONS['DOMME_IMAGE_DIR'])
            if opt_event == 'THEME':
                sg.theme(opt_vals[opt_event][0])
                old = options
                options = open_options()
                old.close()      
            elif opt_event in OPTIONS:
                OPTIONS[opt_event] = opt_vals[opt_event]
                if window[opt_event]:
                    if isinstance(window[opt_event], sg.Text):
                        window[opt_event].update(opt_vals[opt_event])
                    elif isinstance(window[opt_event], sg.Button):
                        window[opt_event].update(text=f"{OPTIONS[opt_event]}\n\n{opt_event[-1]}")
                else:
                    pass                                 
            elif 'ADV_METHOD' in (opt_event):
                OPTIONS['ADV_METHOD'] = str(opt_event)
            else:
                print(f'Event: {opt_event}')
        options.close()
    elif event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == 'Right:114' and OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL':
   #     slideshow.next()
        pass
    elif event == 'Left:113' and OPTIONS['ADV_METHOD'] == 'ADV_METHOD_MANUAL':
   #     slideshow.back()
        pass
    elif event == 'Submit':
    #    chat.push(f'{OPTIONS["SUB_NAME"]}:{window["INPUT"].get()}')
   #     chat.respond(window['INPUT'].get())
        window['INPUT'].update(value='')
        pass
    elif 'HOTKEY' in event:
        if window.find_element_with_focus() != window['INPUT']:
     #       hotkey(event)
            window['INPUT'].update('')
        
    else:
        if event != '__TIMEOUT__':
            print(f'Event: {event}')

save_config()
window.close()
sys.exit(app.exec_)
