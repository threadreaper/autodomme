#!/usr/bin/env python3
from random import randint
from PIL import Image, ImageOps
from options import OPTIONS
import os
from io import BytesIO
import PySimpleGUI as sg


#sg.theme(OPTIONS['THEME'])

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

def convert_directory(dir):
    '''
    given a list of strings containing paths to image files, converts 
    all jpg, tiff, and bmp images to png, saves them and deletes the
    original images
    '''
    layout = [
            [sg.T('Some images need to be converted before they can be displayed.\n'
            'Do you wish to convert these images, or remove them from the list?')],
            [sg.B('Convert'), sg.B('Remove')]            
        ]
    popup = sg.Window('Notice', layout, modal=True)
    while True:
        event = popup.read()[0]
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Remove':
            popup.close()
            for image in dir:
                if image.lower().endswith(('.jpg', '.jpeg', '.tiff', '.bmp')):
                    dir.remove(image)
        elif event == 'Convert':
            popup.close()
            layout = [
                    [sg.Text('Image conversion in progress...')],
                    [sg.ProgressBar(len(dir), orientation='h', size=(20, 20), key='progressbar')],
                    [sg.Cancel()]
                ]
            popup = sg.Window('Notice', layout, modal=True)
            for i, image in enumerate(dir):
                if image.lower().endswith(('.jpg', '.jpeg', '.tiff', '.bmp')):
                    event = popup.read(timeout=10)[0]
                    if event == 'Cancel'  or event == sg.WIN_CLOSED:
                        break
                    convert_to_png(image)
                    popup['progressbar'].UpdateBar(i + 1)
            popup.close()
    popup.close()


class SlideShow():
    def __init__(self, dir, window):
        self.directory = dir
        self.images = self.parse_images()
        self.index = 0
        self.window = window
        self.time = 0

    def parse_images(self):
        try:
            files = os.listdir(self.directory)
        except Exception as e:
            print(e)
            files = []
        images = [os.path.join(self.directory, f) for f in files if os.path.isfile(
            os.path.join(self.directory, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]
        for image in images:
            if image.lower().endswith(('.jpg', '.jpeg', '.tiff', '.bmp')):
                convert_directory(images)
                images = [os.path.join(self.directory, f) for f in files if os.path.isfile(
                    os.path.join(self.directory, f)) and f.lower().endswith(('.png', '.gif'))]
                return images
        return images

    def show(self):
        image = Image.open(self.images[self.index])
        image = ImageOps.pad(image, (1300, 900))
        with BytesIO() as bio:
            image.save(bio, format="PNG")
            del image
            self.window['IMAGE'].update(data=bio.getvalue())

    def next(self):
        if OPTIONS['RANDOMIZE'] == True:
            self.index = randint(0, len(self.images))
        else:
            if self.index + 1 == len(self.images):
                self.index = 0
            else:
                self.index += 1
        self.show()

    def back(self):
        if OPTIONS['RANDOMIZE'] == True:
            self.index = randint(0, len(self.images))
        else:
            if self.index == 0:
                self.index = len(self.images) - 1
            else:
                self.index = self.index - 1
        self.show()

    def update(self, dt):
        if OPTIONS['DOMME_IMAGE_DIR'] != self.directory:
            self.directory = OPTIONS['DOMME_IMAGE_DIR']
            self.images = self.parse_images()
            self.show()
        self.time += dt
        if OPTIONS['ADV_METHOD'] == 'ADV_METHOD_INCREMENTAL' and OPTIONS['SLIDESHOW_INCREMENT'] < self.time:
            self.time = 0
            self.next()