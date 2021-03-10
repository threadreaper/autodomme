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

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (Encoding,
                                                          PublicFormat,
                                                          load_pem_public_key)
from PIL import Image, ImageOps
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow

from crypto_functions import get_key_pair, open_package, send_package
from qt_windows import LoginBuilder, UIBuilder
from server import Server
from usersettings import UserSettings


def load_options() -> UserSettings:
    """
    Load the config file or load defaults

    :return: An instance of `UserSettings`
    :rtype: :class:`UserSettings`
    """
    defaults = {
        'USERNAME': None,
        'SAVE_CREDENTIALS': True,
        'CHAT_NAME': 'Sub',
        'SERVER_PORT': 1337,
        'SERVER_ADDRESS': '127.0.0.1',
        'HOSTNAME': '0.0.0.0',
        'HOST_PORT': 1337,
        'DOMME_NAME': 'Domme',
        'HOST_FOLDER': os.path.expanduser('~'),
        'BOOBS_FOLDER': os.path.expanduser('~'),
        'BUTTS_FOLDER': os.path.expanduser('~'),
        'UPDATES': False
    }

    settings = UserSettings(os.getcwd() + '/config.json')
    for k, v in defaults.items():
        if k not in settings.read().keys():
           settings[k] = v
    return settings


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, client: Client) -> None:
        """
        Constructs the main window.

        :param client: An instance of the `Client` class.
        :type client: :class:`Client`
        """
        super(MainWindow, self).__init__()
        self.ui = UIBuilder()
        self.ui.setup(self)
        self.client = client
        self.server = Server()
        self.ui.start_server.triggered.connect(self.server.set_up_server)
        self.ui.kill_server.triggered.connect(self.server.kill)
        self.ui.connect_server.triggered.connect(self.client.connect)
        self.client_queue = self.status_queue(self.client_status)
        self.server_queue = self.status_queue(self.server_status)

    def status_queue(self, slot) -> QTimer:
        """
        Initializes a QTimer object, connects its timeout to the provided slot,
        starts the queue and returns a reference to it.

        :param slot: The slot to connect the timeout signal to.
        :type slot: `Slot`
        """
        queue = QTimer(self)
        queue.timeout.connect(slot)
        queue.start(15)
        return queue

    def server_status(self):
        if not self.server.queue.empty():
            status = self.server.queue.get(False)
            self.ui.server_status.setText("Server status: " + status)

    def status_tip(self, message):
        self.ui.tooltip.setText(message)

    def client_status(self):
        self.ui.client_status.setText("Client status: " + self.client.status)


class LoginWindow(QDialog):
    """Main application window"""

    def __init__(self, parent, client: Client) -> None:
        """
        Constructs the main window.

        :param client: An instance of the `Client` class.
        :type client: :class:`Client`
        """
        super(LoginWindow, self).__init__(parent)
        self.ui = LoginBuilder()
        self.ui.setup(self)
        self.client = client
        if self.client.settings['SAVE_CREDENTIALS']:
            self.ui.username.setText(self.client.settings['USERNAME'])

    def accept(self):
        username = self.ui.username.text()
        password = self.ui.password.text()
        if self.client.settings['SAVE_CREDENTIALS']:
            self.client.settings['USERNAME'] = username
        self.client.send_message('%s %s' % (username, password), 'LOG')
        self.close()


class Client:
    """Client object for communication with server."""

    class Session:
        """Holds session variables while connected to a server."""

        def __init__(self, key: rsa.RSAPublicKey) -> None:
            """Initialize the session."""
            self.srv_folder = 'Not Connected.'
            self.online_users = []
            self.browser_folders = ['None']
            self.browser_files = ['None']
            self.srv_key = key

    def __init__(self) -> None:
        """
        Initializes the client.
        """
        self.settings = load_options()
        self.session = None
        self.address = (self.settings['SERVER_ADDRESS'],
                        self.settings['SERVER_PORT'])
        self.buffer = 512
        self.private_key, self.public_key = get_key_pair()
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(5)
        self.connected = False
        self.recv_lock = Lock()
        self.status = 'Not connected.'
        self.media = None
        self.window = MainWindow(self)
        media_size = self.window.ui.media.size()
        self.media_size = media_size.width(), media_size.height()

    def connect(self) -> None:
        """Attempt to connect to a server"""
        if self.connected:
            self.status = 'Error: already connected.'
        else:
            self.socket.connect(self.address)
            self.socket.send(self.public_key.public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
            key = load_pem_public_key(self.socket.recv(833))
            if isinstance(key, rsa.RSAPublicKey):
                self.session = self.Session(key)
                response = self._authenticate()
                while response != 'True':
                    if response is None:
                        break
                    response = self._authenticate(response)
                if response == 'True':
                    recv_thread = Thread(target=self._receive_messages,
                                            daemon=True)
                    recv_thread.start()
                    settings = pickle.dumps(self.settings)
                    self.send_message(settings, 'SES')
                    self.connected = True
            else:
                print('Key handshake failure - connection rejected')

    def _authenticate(self, last: str | bool | None = None) -> \
        bool | str | None:
        """
        Authenticate on the server. Returns the server's response.

        :param last: The server's response to previous attempt to
            authenticate.
        :type last: `str`
        :return: The server's response or None if window was closed.
        :rtype: `Any`
        """
        login = LoginWindow(self.window, self)
        res = login.exec_()
        if login.exec_() == QDialog.Accepted:
            print(res, print('weird'))
        print(res)
        if res == 1:
            self.recv_lock.acquire()
            msg_type, answer = self.recv()
            print(answer)
            self.recv_lock.release()
            if msg_type == 'LOG':
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
        :param msg_type: The type of transmission, one of MSG, IMG, SES, FOL\
            or LOG
        :type msg_type: `str`
        """
        send_package(self.session.srv_key, self.private_key, msg, msg_type,
                     self.socket)

    def _receive_messages(self) -> None:
        """Receive messages from the server."""
        while True:
            try:
                self.recv_lock.acquire()
                msg_type, msg = open_package(self.session.srv_key,
                                             self.private_key,
                                             self.socket)
                self.recv_lock.release()
                if len(msg) == 0:
                    break
                if msg_type == 'MSG':
                    # connect to chat window
                    ...
                elif msg_type == 'SES':
                    self._set_session_vars(msg.decode())
                    continue
                elif msg_type == 'FOL':
                    self._folders_and_files(msg.decode())
                    continue
                elif msg_type == 'IMG':
                    img = Image.open(BytesIO(msg))
                    img = ImageOps.pad(img, self.media_size)
                    with BytesIO() as bio:
                        img.save(bio, format="PNG")
                        del img
                    self.media = bio.getvalue()
                    continue
                elif msg_type == 'ERR':
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
        chunks = msg.split(':')
        self.session.srv_folder = chunks[1]
        for chunk in chunks[3:]:
            if chunk != 'END':
                self.session.online_users.append(chunk)

    def _folders_and_files(self, msg: str) -> None:
        """
        Passes retrieved folder and file information to the server browser\
            object.

        :param msg: A message packet from the server containing the folder and\
            file information.
        :type msg: string
        """
        browse_data = msg.split(':')
        try:
            self.session.browser_folders = browse_data[1].split(',')
        except IndexError:
            pass
        try:
            self.session.browser_files = browse_data[3].split(',')
        except IndexError:
            pass




if __name__ == "__main__":
    app = QApplication([])
    client = Client()
    client.window.show()

    sys.exit(app.exec_())
