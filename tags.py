#!/usr/bin/env python3
import PySimpleGUI as sg
from options import OPTIONS
import os
#import requests


""" r = requests.post("https://api.deepai.org/api/nsfw-detector",
    data={'image': 'https://image.shutterstock.com/image-photo/beautiful-naked-womans-back-supple-260nw-771473938.jpg'},
    headers={'api-key': 'b9eeff4f-9fc3-4aaf-8cc7-584335c7831a'})
print(r.json()) """



def popup():
    sg.theme(OPTIONS['THEME'])
    
    col_1 = [
        [sg.T('Image Tagging')],
        [sg.Input(os.environ['HOME'], size=(20, 1), key='IMAGE_DIR', enable_events=True),
        sg.B('Browse')],
        [sg.HorizontalSeparator()],
        [sg.T('Body parts:')],
        [sg.Checkbox('Tits'), sg.Checkbox('Exposed')],
        [sg.Checkbox('Pussy'), sg.Checkbox('Exposed')],
        [sg.Checkbox('Ass'), sg.Checkbox('Exposed')],
        [sg.HorizontalSeparator()],
        [sg.T('Mood')],
        [sg.Checkbox('Smiling'), sg.Checkbox('Glaring')],    
    ]

    image = [[sg.Image(None)]]

    col_2 = [
        [sg.B('<<', k='Back'), sg.B('>>', k='Next'), 
        sg.Frame('', image, size=(800, 800), background_color='#000000')]
    ]

    layout = [
        [sg.Col(col_1)],
        [sg.Col(col_2)]
    ]

    popup = sg.Window('Image Tagging', layout)

    while True:
        event, values = popup.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break