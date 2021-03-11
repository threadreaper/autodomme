#!/usr/bin/env python3
"""Client class and associated methods"""
from __future__ import annotations

import os
import pickle
import sys
import time as t
from io import BytesIO
from socket import AF_INET, SOCK_STREAM, socket
from threading import Lock, Thread
from cv2 import cvtColor, COLOR_BGR2RGB, VideoCapture, CAP_PROP_POS_FRAMES #pylint: disable=no-name-in-module
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)
from PIL import Image
from PySide6.QtCore import Qt, QThread, QTimer # pylint: disable=no-name-in-module
from PySide6.QtGui import QImage, QPixmap # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow # pylint: disable=no-name-in-module

from crypto_functions import get_key_pair, open_package, send_package
from qt_windows import LoginBuilder, UIBuilder
from server import Server
from usersettings import UserSettings
from video_no_vlc import Player

def load_options() -> UserSettings:
    """
    Load the config file or load defaults

    :return: An instance of `UserSettings`
    :rtype: :class:`UserSettings`
    """
    defaults = {
        "USERNAME": None,
        "SAVE_CREDENTIALS": True,
        "CHAT_NAME": "Sub",
        "SERVER_PORT": 1337,
        "SERVER_ADDRESS": "127.0.0.1",
        "HOSTNAME": "0.0.0.0",
        "HOST_PORT": 1337,
        "DOMME_NAME": "Domme",
        "HOST_FOLDER": os.path.expanduser("~"),
        "BOOBS_FOLDER": os.path.expanduser("~"),
        "BUTTS_FOLDER": os.path.expanduser("~"),
        "UPDATES": False,
    }

    settings = UserSettings(os.getcwd() + "/config.json")
    for key, value in defaults.items():
        if key not in settings.read().keys():
            settings[key] = value
    return settings


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, myclient: Client) -> None:
        """
        Constructs the main window.

        :param client: An instance of the `Client` class.
        :type client: :class:`Client`
        """
        super(MainWindow, self).__init__()
        self.inter = UIBuilder()
        self.inter.setup(self)
        self.client = myclient
        self.server = Server()
        self.inter.start_server.triggered.connect(self.server.set_up_server)  # type: ignore
        self.inter.kill_server.triggered.connect(self.server.kill)  # type: ignore
        self.inter.connect_server.triggered.connect(self.client.connect)  # type: ignore
        self.inter.start_webcam.triggered.connect(self.client.play_media)  # type: ignore
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)  # type: ignore
        self.update_timer.start(15)

    def update(self) -> None:
        """Updates the GUI."""
        self.client_status()
        self.server_status()
        self.online_status()
        self.media_status()
        # self.window['SRV_FOLDER'].update(self.session.srv_folder)

    def media_status(self):
        """Checks the queue for a new image to display."""
        media_size = self.inter.media.contentsRect()
        self.client.media_size = media_size.width(), media_size.height()
        if self.client.media is not None:
            self.inter.media.setPixmap(QPixmap.fromImage(self.client.media))

    def online_status(self):
        """Updates the list of online users."""
        if self.client.connected:
            users = [
                user
                for user in self.inter.online.toPlainText().split("\n")
                if user != ""
            ]
            if users != self.client.session.online_users:
                self.inter.online.clear()
                for user in self.client.session.online_users:
                    self.inter.online.appendPlainText("%s\n" % user)

    def server_status(self):
        """Updates the local server status."""
        if not self.server.queue.empty():
            status = self.server.queue.get(False)
            self.inter.server_status.setText("Server status: " + status)

    def status_tip(self, message):
        """Slot for mouseover statusbar tips."""
        self.inter.tooltip.setText(message)

    def client_status(self):
        """Updates the client status."""
        self.client.status = (
            "Not Connected to any server.",
            "Connected to server @ %s" % self.client.address[0],
        )[self.client.connected]
        self.inter.client_status.setText("Client status: " + self.client.status)


class LoginWindow(QDialog):
    """Main application window"""

    def __init__(self, parent, myclient: Client) -> None:
        """
        Constructs the main window.

        :param client: An instance of the `Client` class.
        :type client: :class:`Client`
        """
        super(LoginWindow, self).__init__(parent)
        self.inter = LoginBuilder()
        self.inter.setup(self)
        self.client = myclient
        if self.client.settings["SAVE_CREDENTIALS"]:
            self.inter.username.setText(self.client.settings["USERNAME"])


class Client:
    """Client object for communication with server."""

    class Session:
        """Holds session variables while connected to a server."""

        def __init__(self, key: rsa.RSAPublicKey) -> None:
            """Initialize the session."""
            self.srv_folder = "Not Connected."
            self.online_users = []
            self.browser_folders = ["None"]
            self.browser_files = ["None"]
            self.srv_key = key

    def __init__(self) -> None:
        """
        Initializes the client.
        """
        self.settings = load_options()
        self.session = None
        self.address = (
            self.settings["SERVER_ADDRESS"],
            self.settings["SERVER_PORT"],
        )
        self.buffer = 512
        self.private_key, self.public_key = get_key_pair()
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(5)
        self.connected = False
        self.recv_lock = Lock()
        self.status = "Not connected."
        self.media = None
        self.window = MainWindow(self)
        media_size = self.window.inter.media.contentsRect()
        self.media_size = media_size.width(), media_size.height()

    def play_media(self, checked: bool = None,
                   media: str | None = None) -> None:
        """
        Slot that responds to requests to play video.
        """
        if media is None:
            media = "/mnt/veracrypt1/video/softcore/belakazar.mp4"
        if not checked:
            player = Player(self.window.inter.media)
            # video_thread = Video(self.window, self, media)
            # video_thread.start()

    def connect(self) -> None:
        """Attempt to connect to a server"""
        if self.connected:
            self.status = "Error: already connected."
        else:
            self.socket.connect(self.address)
            self.socket.send(
                self.public_key.public_bytes(
                    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
                )
            )
            key = load_pem_public_key(self.socket.recv(833))
            if isinstance(key, rsa.RSAPublicKey):
                self.session = self.Session(key)
                response = self._authenticate()
                while response != "True":
                    if response is None:
                        break
                    response = self._authenticate()
                if response == "True":
                    recv_thread = Thread(
                        target=self._receive_messages, daemon=True
                    )
                    recv_thread.start()
                    settings = pickle.dumps(self.settings)
                    self.send_message(settings, "SES")
                    self.connected = True
            else:
                print("Key handshake failure - connection rejected")

    def _authenticate(self) -> bool | str | None:
        """
        Authenticate on the server. Returns the server's response.

        :param last: The server's response to previous attempt to
            authenticate.
        :type last: `str`
        :return: The server's response or None if window was closed.
        :rtype: `Any`
        """
        login = LoginWindow(self.window, self)
        if login.exec_() == 1:
            username = login.inter.username.text()
            password = login.inter.password.text()
            if self.settings["SAVE_CREDENTIALS"]:
                self.settings["USERNAME"] = username
            self.send_message("%s %s" % (username, password), "LOG")
            self.recv_lock.acquire()
            msg_type, answer = self.recv()
            self.recv_lock.release()
            if msg_type == "LOG":
                return answer.decode()

    def recv(self):
        """Receive a message from the server."""
        return open_package(self.session.srv_key, self.private_key,
                            self.socket)

    def send_message(self, msg: str | bytes, msg_type: str) -> None:
        """
        Send a message to the server.

        :param msg: Message to send.
        :type msg: string
        :param msg_type: The type of transmission, one of MSG, IMG, SES, FOL
            or LOG
        :type msg_type: `str`
        """
        send_package(
            self.session.srv_key, self.private_key, msg, msg_type, self.socket
        )

    def _receive_messages(self) -> None:
        """Receive messages from the server."""
        while True:
            try:
                self.recv_lock.acquire()
                msg_type, msg = open_package(
                    self.session.srv_key, self.private_key, self.socket
                )
                self.recv_lock.release()
                if len(msg) == 0:
                    break
                if msg_type == "MSG":
                    self.window.inter.chat.appendPlainText(msg.decode())
                elif msg_type == "SES":
                    self._set_session_vars(msg.decode())
                    continue
                elif msg_type == "FOL":
                    self._folders_and_files(msg.decode())
                    continue
                elif msg_type == "IMG":
                    img = Image.open(BytesIO(msg))
                    rgb = cvtColor(img, COLOR_BGR2RGB)
                    height, width, chars = rgb.shape
                    bytes_per_line = chars * width
                    qimg = QImage(rgb.data, width, height, bytes_per_line,  # type: ignore
                                  QImage.Format_RGB888)
                    image = qimg.scaled(
                        *self.media_size,
                        Qt.KeepAspectRatio,
                        Qt.FastTransformation,
                    )
                    self.media = image
                    continue
                elif msg_type == "ERR":
                    self.status = msg
            except OSError:
                self.recv_lock.release()
            finally:
                t.sleep(0.1)

    def _set_session_vars(self, msg: str) -> None:
        """
        Sets session variables sent by the server.

        :param msg: A message packet from the server containing session
        variables.
        :type msg: str
        """
        chunks = msg.split(":")
        self.session.srv_folder = chunks[1]
        for chunk in chunks[3:]:
            if chunk != "END":
                self.session.online_users.append(chunk)

    def _folders_and_files(self, msg: str) -> None:
        """
        Passes retrieved folder and file information to the server browser
            object.

        :param msg: A message packet from the server containing the folder and
            file information.
        :type msg: string
        """
        browse_data = msg.split(":")
        try:
            self.session.browser_folders = browse_data[1].split(",")
        except IndexError:
            pass
        try:
            self.session.browser_files = browse_data[3].split(",")
        except IndexError:
            pass


class Video(QThread):
    """Worker thread for playing webcam"""

    def __init__(
        self, window: MainWindow, myclient: Client, filename: str = None
    ) -> None:
        QThread.__init__(self, window)
        self.filename = 0 if filename is None else filename
        self.client = myclient

    def run(self):
        """Gets the next frame of video and signals the GUI that it's ready."""
        cur_frame = 0
        cap = VideoCapture(self.filename)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cap.set(CAP_PROP_POS_FRAMES, cur_frame)
                cur_frame += 1
                rgb = cvtColor(frame, COLOR_BGR2RGB)
                height, width, chars = rgb.shape
                bytes_per_line = chars * width
                qimg = QImage(rgb.data, width, height, bytes_per_line,  # type: ignore
                              QImage.Format_RGB888)
                image = qimg.scaled(
                    *self.client.media_size,
                    Qt.KeepAspectRatio,
                    Qt.FastTransformation,
                )
                self.client.media = image


if __name__ == "__main__":
    app = QApplication([])

    client = Client()
    with open('style.qss', "r") as fh:
        client.window.setStyleSheet(fh.read())
    client.window.show()

    sys.exit(app.exec_())
