import platform
import os

from PySide6 import QtWidgets
import vlc


class Player:
    """A simple Media Player using VLC and Qt"""

    def __init__(self, widget):
        self.instance = vlc.Instance()
        self.media = widget
        self.video = None
        self.mediaplayer = self.instance.media_player_new()
        self.is_paused = False

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.is_paused = True
        else:
            if self.mediaplayer.play() == -1:
                self.open()
                return
            self.mediaplayer.play()
            self.is_paused = False

    def stop(self):
        self.mediaplayer.stop()

    def open(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self.media.parentWidget(), "Select a file", os.path.expanduser("~")
        )

        self.video = self.instance.media_new(filename[0])

        self.mediaplayer.set_media(self.video)

        self.video.parse()

        if platform.system() == "Linux":  # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.media.winId()))
        elif platform.system() == "Windows":  # for Windows
            self.mediaplayer.set_hwnd(int(self.media.winId()))
        elif platform.system() == "Darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.media.winId()))

        self.play_pause()
