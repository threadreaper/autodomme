#!/usr/bin/env python3
"""Classes/functions for handling images"""
import os
from io import BytesIO
from random import randint

import PySimpleGUI as sG
from PIL import Image, ImageOps

from options import OPTIONS

sG.theme(OPTIONS['THEME'])


def convert_to_png(file):
    '''
    given a path to an image file as a string, converts the image to png,
    saves it and deletes the original image
    '''
    if isinstance(file, str):
        img = Image.open(file).convert('RGB')
        os.remove(file)
        filename = file.split('.')
        img.save(f'{filename[0]}.png', 'png')


def convert_directory(folder):
    '''
    given a list of strings containing paths to image files, converts
    all jpg, tiff, and bmp images to png, saves them and deletes the
    original images
    '''
    layout = [
        [sG.T('Some images must be converted to be displayed.\n'
              'Do you wish to permanently convert these images to png?')],
        [sG.B('Convert'), sG.B('Cancel')]
    ]
    popup = sG.Window('Notice', layout, modal=True)
    while True:
        event = popup.read()[0]
        if event == sG.WIN_CLOSED:
            break
        elif event == 'Cancel':
            popup.close()
            for image in folder:
                if image.lower().endswith(('.jpg', '.jpeg', '.tiff', '.bmp')):
                    folder.remove(image)
        elif event == 'Convert':
            popup.close()
            layout = [
                [sG.Text('Image conversion in progress...')],
                [sG.ProgressBar(len(folder), orientation='h',
                                size=(20, 20),
                                key='progressbar')],
                [sG.Cancel()]
            ]
            popup = sG.Window('Notice', layout, modal=True)
            for i, image in enumerate(folder):
                if image.lower().endswith(('.jpg', '.jpeg', '.tiff', '.bmp')):
                    event = popup.read(timeout=10)[0]
                    if event in ['Cancel', sG.WIN_CLOSED]:
                        break
                    convert_to_png(image)
                    popup['progressbar'].UpdateBar(i + 1)
            popup.close()
    popup.close()


def parse_images(folder):
    """Given a directory, returns the list of images within it"""
    files = os.listdir(folder)
    images = [os.path.join(folder, f) for f in files
              if os.path.isfile(os.path.join(folder, f)) and
              f.lower().endswith(('png', 'jpg', 'jpeg', 'tiff', 'bmp'))]
    for image in images:
        if image.lower().endswith(('.jpg', '.jpeg', '.tiff', '.bmp')):
            convert_directory(images)
            images = [os.path.join(folder, f) for f in files if
                      os.path.isfile(os.path.join(folder, f)) and
                      f.lower().endswith(('.png', '.gif'))]
            return images
    return images


class SlideShow():
    """Class for an Image slideshow"""
    def __init__(self, folder, window):
        self.directory = folder
        self.images = parse_images(folder)
        self.index = 0
        self.window = window
        self.time = 0

    def show(self):
        """Start the slideshow"""
        image = Image.open(self.images[self.index])
        image = ImageOps.pad(image, (980, 780))
        with BytesIO() as bio:
            image.save(bio, format="PNG")
            del image
            self.window['IMAGE'].update(data=bio.getvalue())

    def next(self):
        """Advance the slideshow to the next slide"""
        if OPTIONS['RANDOMIZE']:
            self.index = randint(0, len(self.images))
        else:
            if self.index + 1 == len(self.images):
                self.index = 0
            else:
                self.index += 1
        self.show()

    def back(self):
        """Display the slide before the current slide"""
        if OPTIONS['RANDOMIZE']:
            self.index = randint(0, len(self.images))
        else:
            self.index = (len(self.images)-1, self.index-1)[self.index == 0]
        self.show()

    def update(self, delta):
        """Update the slideshow"""
        if OPTIONS['HOST_FOLDER'] != self.directory:
            self.directory = OPTIONS['HOST_FOLDER']
            self.images = parse_images(self.directory)
            self.show()
        self.time += delta
        if OPTIONS['ADV_METHOD'] == 'ADV_METHOD_INCREMENTAL' and OPTIONS[
                'SLIDESHOW_INCREMENT'] < self.time:
            self.time = 0
            self.next()


parse_images('/home/michael/projects/teaseai/icons')

"""
    Demo program that reroutes stdout and stderr.
    Type something in the input box and click Print
    Whatever you typed is "printed" using a standard print statement
    Use the Output Element in your window layout to reroute stdout
    You will see the output of the print in the Output Element in the center of the window
    
"""


layout = [
    [sg.Text('Type something in input field and click print')],
    [sg.Input()],
    [sg.Output()],
    [sg.Button('Print')]
]

window = sg.Window('Reroute stdout', layout)

while True:     # Event Loop
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    print('You typed: ', values[0])
window.close()

"""
    Demo - the PySimpleGUI helpers (emojis)
    The list of characters available to you to use in your messages.
    They are used internally when you get an error or as the icon for windows like
    the SDK help window.
    
    Copyright 2021 PySimpleGUI
"""


import PySimpleGUI as sg

layout = [[sg.Text('The PySimpleGUI Helpers', font='_ 20')],
          [sg.Text('Sometimes frustrated or tired....', font='_ 15')],
          [sg.Image(data=emoji) for emoji in sg.EMOJI_BASE64_SAD_LIST],
          [sg.Text('But they are usually happy!', font='_ 15')],
          [sg.Image(data=emoji) for emoji in sg.EMOJI_BASE64_HAPPY_LIST],
          [sg.Button('Bad Key'), sg.Button('Hello'), sg.Button('Exit')]  ]

window = sg.Window('The PySimpleGUI Helpers', layout, icon=sg.EMOJI_BASE64_HAPPY_JOY, keep_on_top=True)

while True:             # Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Bad Key':
        elem = window['-IM-']
    elif event == 'Hello':
        sg.popup('Hi!', image=sg.EMOJI_BASE64_HAPPY_JOY, keep_on_top=True)

window.close()

import PySimpleGUI as sg

'''
A simple send/response chat window.  Add call to your send-routine and print the response
If async responses can come in, then will need to use a different design that uses PySimpleGUI async design pattern
'''

sg.theme('GreenTan') # give our window a spiffy set of colors

layout = [[sg.Text('Your output will go here', size=(40, 1))],
          [sg.Output(size=(110, 20), font=('Helvetica 10'))],
          [sg.Multiline(size=(70, 5), enter_submits=False, key='-QUERY-', do_not_clear=False),
           sg.Button('SEND', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=True),
           sg.Button('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]

window = sg.Window('Chat window', layout, font=('Helvetica', ' 13'), default_button_element_size=(8,2), use_default_focus=False)

while True:     # The Event Loop
    event, value = window.read()
    if event in (sg.WIN_CLOSED, 'EXIT'):            # quit if exit button or X
        break
    if event == 'SEND':
        query = value['-QUERY-'].rstrip()
        # EXECUTE YOUR COMMAND HERE
        print('The command you entered was {}'.format(query), flush=True)

window.close()


"""TKOutput word wrap"""
layout = [
    [sg.Text('GameFinder', font=('Helvetica', 24, 'bold'))],
    [sg.In(key='-IN-', size=(40,1)), sg.Button('Search')],
    [sg.Output(key='-OUT-', size=(80, 20))],
]

window = sg.Window('Game Finder', layout, element_justification='center').finalize()
window['-OUT-'].TKOut.output.config(wrap='word') # set Output element word wrapping

print('''
i am using PySimpleGUI as a tkinter wrapper and it works like a charm, but:

When i am printing something to the output element it performs a linebreak whenever the given character limit per line is reached.

Can i somehow change it to break line when it can't display the current word fully with the remaining line length?

Cheers
''')

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

window.close()
