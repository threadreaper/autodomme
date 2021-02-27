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