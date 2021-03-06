#!/usr/bin/env python3
"""Client class and associated methods"""
from __future__ import annotations

import os
import pickle
import time as t
from io import BytesIO
from queue import SimpleQueue
from socket import AF_INET, SOCK_STREAM, socket
from threading import Lock, Thread

import PySimpleGUI as sG
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (Encoding,
                                                          PublicFormat,
                                                          load_pem_public_key)
from PIL import Image, ImageOps

import windows
from crypto_functions import get_key_pair, open_package, send_package
from filebrowser import FileBrowser
from server import Server, SlideShow
from server_browser import ServerBrowser
from solitaire import MyGame, arcade
from git_functions import auto_update


def load_options() -> sG.UserSettings:
    """
    Load the config file or load defaults

    :return: An instance of `PySimpleGUI.UserSettings`
    :rtype: :class:`PySimpleGUI.UserSettings`
    """
    defaults = {
        'THEME': '15. DarkBlue12',
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
    settings = os.getcwd() + '/config.json'
    sG.user_settings_filename(settings)
    if sG.user_settings_file_exists(settings):
        for k, v in defaults.items():
            if k not in sG.user_settings().keys():
                sG.user_settings_set_entry(k, v)
    else:
        for k, v in defaults.items():
            sG.user_settings_set_entry(k, v)
    return sG.UserSettings(settings)


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
        self.options = load_options()
        self.session = None
        self.address = (self.options['SERVER_ADDRESS'],
                        self.options['SERVER_PORT'])
        self.buffer = 512
        self.private_key, self.public_key = get_key_pair()
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(5)
        self.messages = list
        self.connected = False
        self.recv_lock = Lock()
        self.queue = SimpleQueue()
        self.status = 'Not connected to any server.'
        self.media = None
        self.server_status = 'No server running.'
        self.window = windows.main_window(self)
        self.media_size = self.window['IMAGE'].get_size()

    def update(self) -> None:
        """Updates the GUI."""
        self.status = (
            'Not Connected to any server.',
            'Connected to server @ %s' % self.address[0]
            )[self.connected]
        self.window['CLIENT_STATUS'].update(self.status)
        self.window['SERVER_STATUS'].update(self.server_status)
        if client.connected:
            users = [user for user in
                     self.window['ONLINE_USERS'].get().split('\n')
                     if user != '']
            if users != self.session.online_users:
                self.window['ONLINE_USERS'].update('', append=False)
                for user in self.session.online_users:
                    self.window['ONLINE_USERS'].update('%s\n' % user,
                                                       append=True)
            if self.media is not None:
                self.window['IMAGE'].update(self.media)
            self.window['SRV_FOLDER'].update(self.session.srv_folder)

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
                    options = pickle.dumps(self.options)
                    self.send_message(options, 'SES')
                    self.connected = True
            else:
                print('Key handshake failure - connection rejected')

    def _authenticate(self, last: str | bool | None = None) -> \
            bool | str | None:
        """
        Authenticate on the server. Returns the server's response.

        :param last: The server's response to previous attempt to \
            authenticate.
        :type last: `str`
        :return: The server's response or None if window was closed.
        :rtype: `Any`
        """
        login = windows.login_window(self, last)

        while True:
            event = login.read()[0]
            if event in ['Cancel', sG.WIN_CLOSED]:
                break
            elif event == 'Submit':
                username = login['USERNAME'].get()
                password = login['PASSWORD'].get()
                if self.options['SAVE_CREDENTIALS']:
                    self.options['USERNAME'] = username
                self.send_message('%s %s' % (username, password), 'LOG')
                self.recv_lock.acquire()
                msg_type, answer = self.recv()
                self.recv_lock.release()
                login.close()
                if msg_type == 'LOG':
                    return answer.decode()

    def recv(self):
        """Receive a message from the server."""
        return open_package(self.session.srv_key, self.private_key,
                            self.socket)

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
                    sG.cprint(msg.decode())
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
                    sG.PopupError(msg.decode())
            except OSError:
                self.recv_lock.release()
            finally:
                t.sleep(0.1)

    def _request_file(self, filename: str, size: tuple[int, int]):
        """
        Request a file from the server.  Takes a path to file on the server
        and returns the file.

        :param filename: /path/to/file
        :type filename: str
        :returns: The file requested from the server.
        :rtype: bytes
        """
        # TODO: change this and associated serverside funcs to new method
        self.send_message(filename, 'IMG')
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

    def disconnect(self) -> None:
        """Disconnect from chat server."""
        self.send_message("/quit", 'MSG')
        self.connected = False


if __name__ == '__main__':
    client = Client()
    server = Server()
    slideshow = server.slideshow
    time = t.time()

    if client.options['UPDATES'] and auto_update():
        client.queue.put('Automatic update in progress.')

    while True:
        client.update()
        delta = t.time() - time
        time = t.time()
        event, values = client.window.read(timeout=50)
        if slideshow is not None:
            slideshow.update(delta)
        if event in ["Exit", sG.WIN_CLOSED]:
            break
        elif event == 'Start Server':
            server.set_up_server()
        elif event == 'Kill Server':
            server.kill()
        elif event == 'Connect to Server':
            client.connect()
            srv_folder = ''
            while srv_folder == '':
                srv_folder = client.session.srv_folder
        elif event == 'SRV_PLAY':
            for person in server.clients:
                if person.name.lstrip('@') == client.options['CHAT_NAME']\
                        and person.ops:
                    server.slideshow = SlideShow(
                        client.window['SRV_FOLDER'].get(), server)
                    slideshow = server.slideshow
                    slideshow.start()
                else:
                    sG.cprint('Error: Must have server ops \
                        for this operation.')
        elif event == 'SRV_PAUSE':
            slideshow.stop()
        elif event == 'SRV_BACK':
            slideshow.back()
        elif event == 'SRV_FORWARD':
            slideshow.next()
        elif event == 'Submit':
            if client.connected is True:
                client.send_message(client.window['INPUT'].get(), 'MSG')
            else:
                sG.cprint('Error: Not connected to server')
        elif event == 'HIDE':
            x, y = client.window.current_location()
            client.window.hide()
            solitaire = MyGame(client.window)
            solitaire.setup()
            solitaire.set_location(x, y)
            arcade.run()
        elif 'SRV_BROWSE' in event:
            browser = ServerBrowser(client, client.window['SRV_FOLDER'].get())
            srv_folder = browser.show()
            client.session.srv_folder = srv_folder
            browser.window.close()
        elif event == "Options Menu":
            opts = windows.options_window(client)
            while True:
                opt_event, opt_vals = opts.read()
                if opt_event in ["Exit", sG.WIN_CLOSED]:
                    break
                if opt_event.startswith('BROWSE_'):
                    prefix = opt_event.split('_')[1]
                    browser = FileBrowser(opts[prefix + '_FOLDER'].get())
                    folder = browser.show()
                    opts[prefix + '_FOLDER'].update(value=folder)
                    browser.window.close()
                if opt_event in client.options.dict.keys():
                    client.options[opt_event] = opt_vals[opt_event]
                if 'SRV' in opt_event:
                    server.opt_set(opt_event.split('_')[1],
                                   opt_vals[opt_event])
                if opt_event == 'SERV_BROWSE':
                    filetype = opts[opt_event].metadata
                    browser = FileBrowser(client.options['HOST_FOLDER'])
                    srv_folder = browser.show()
                    opts['SRV_folder'].update(value=srv_folder)
                    server.opt_set('folder', srv_folder)
                    browser.window.close()
                if 'ADV_METHOD' in opt_event:
                    client.options['ADV_METHOD'] = opt_event
                if opt_event == 'THEME':
                    client.options['THEME'] = opt_vals[opt_event][0]
                    old = [opts, client.window]
                    window = windows.main_window(client)
                    client.window = window
                    opts = windows.options_window(client)
                    for expired in old:
                        expired.close()
            opts.close()
        if not client.queue.empty():
            msg = client.queue.get(False)
            sG.cprint(msg)
        if not server.queue.empty():
            status = server.queue.get(False)
            client.server_status = status

    if server.started is True:
        server.kill()
    if client.connected is True:
        client.socket.close()
    client.window.close()
