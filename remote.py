from __future__ import annotations

import PySimpleGUIWeb as sG
from options import OPTIONS

sG.theme('DarkGrey6')

keys = []
for i in [7, 8, 9, 4, 5, 6, 1, 2, 3, 0]:
    button = sG.B(f"{i}. {OPTIONS['HOTKEY_%s' % i]}",
                  size=(32 if i == 0 else 10, 2),
                  key='HOTKEY_%s' % i, font='Helvetica 12 bold',
                  pad=(5, 5))
    keys.append(button)
keys[:] = [keys[0:3]] + [keys[3:6]] + [keys[6:9]] + [keys[9:]]

media_player_panel = [
    [sG.B('<<', key='BACK', image_filename='icons/back.png'),
     sG.B('||', key='PAUSE', image_filename='icons/pause.png'),
     sG.B('>', key='PLAY', image_filename='icons/play.png'),
     sG.B('>>', key='FORWARD', image_filename='icons/forward.png')]]

layout = [
    [item for item in keys[0]],
    [item for item in keys[1]],
    [item for item in keys[2]],
    [item for item in keys[3]],
    [sG.Image('icons/back.png', key='BACK', enable_events=True),
     sG.Image('icons/pause.png', key='PAUSE', enable_events=True),
     sG.Image('icons/play.png', key='PLAY', enable_events=True),
     sG.Image('icons/forward.png', key='FORWARD', enable_events=True)]]

win = sG.Window('TeaseAI Remote Control', layout, finalize=True)

while True:
    event, values = win.read()
    if event in ["Exit", sG.WIN_CLOSED]:
        break
    else:
        print(event)
