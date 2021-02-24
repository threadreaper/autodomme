#!/usr/bin/env python3
"""Client class and associated methods"""
from functools import lru_cache
from io import BytesIO
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

import PySimpleGUI as sG
from cryptography.hazmat.primitives.asymmetric import rsa
from PIL import Image, ImageOps

from crypto import decrypt, decrypt_file, encrypt, get_key_pair, load_pem
from options import OPTIONS


class Session:
    """Holds session variables while connected to a server."""

    def __init__(self) -> None:
        """Initialize the session."""
        self.srv_folder = ''
        self.online_users = []
        self.browser_folders = []
        self.browser_files = []


class Client:
    """Client object for communication with server."""

    def __init__(self, window: sG.Window = None) -> None:
        """
        Initializes the client.

        Public methods:
        - connect(): Connect to server.

        :param window: Instance of Window used for updating the GUI.
        :window type: sG.Window
        """

        self.address = (OPTIONS['SERVER_ADDRESS'], OPTIONS['SERVER_PORT'])
        self.buffer = 512
        self.window = window
        self.chat_name = OPTIONS['CHAT_NAME']
        self.username = OPTIONS['USERNAME']
        self.password = OPTIONS['PASSWORD']
        self.private_key, self.public_key = get_key_pair()
        self.srv_key = rsa.RSAPublicKey
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.messages = []
        self.connected = False
        self.session = Session()

    def connect(self) -> None:
        """Attempt to connect to a server"""
        if self.connected is False:
            self.client_socket.connect(self.address)
            self.client_socket.send(self.public_key)
            self.srv_key = load_pem(self.client_socket.recv(833))
            if isinstance(self.srv_key, rsa.RSAPublicKey):
                authenticated = self._authenticate()
                while authenticated != 'True':
                    if not authenticated:
                        break
                    authenticated = self._authenticate(authenticated)
                if authenticated:
                    if self.window is not None:
                        self.window['CLIENT_STATUS'].update(
                            'Connected to server: %s' %
                            OPTIONS['SERVER_ADDRESS'])
                    receive_thread = Thread(target=self._receive_messages)
                    receive_thread.start()
                    self.send_message(self.chat_name)
                    self.connected = True
            else:
                print('Key handshake failure - connection rejected')
        else:
            if self.window is not None:
                self.window['CLIENT_STATUS'].update('Error: already connected.')

    def _update_users(self) -> None:
        """Updates the online users list."""
        if self.window is not None:
            self.window['ONLINE_USERS'].update('', append=False)
            for user in self.session.online_users:
                self.window['ONLINE_USERS'].update('%s\n' % user, append=True)

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
        self._update_users()

    def _receive_messages(self) -> None:
        """Receive messages from the server."""
        while True:
            try:
                msg = self.client_socket.recv(self.buffer)
                if len(msg) == 0:
                    break
                msg = decrypt(self.private_key, msg)
                if msg.startswith('PATH'):
                    self._set_session_vars(msg)
                elif msg.startswith('FOLDERS:'):
                    stuff = msg.split(':')
                    try:
                        self.session.browser_folders = stuff[1].split(',')
                    except IndexError:
                        pass
                    try:
                        self.session.browser_files = stuff[3].split(',')
                    except IndexError:
                        pass
                elif msg.endswith('has joined the chat!'):
                    sG.cprint(msg)
                    if msg.split()[0] != OPTIONS['CHAT_NAME']:
                        self.session.online_users.append(msg.split()[0])
                        self._update_users()
                elif msg.endswith('has left the chat.'):
                    sG.cprint(msg)
                    self.session.online_users.remove(msg.split()[0])
                    self._update_users()
                elif msg.startswith('IMG'):
                    with BytesIO() as bio:
                        self._get_file(msg).save(bio, format="PNG")
                        if self.window is not None:
                            self.window['IMAGE'].update(data=bio.getvalue())

                else:
                    sG.cprint(msg)
            except OSError as error:
                print('[EXCEPTION]', error)
                break

    def _get_file(self, msg: str):
        """
        Retrieves a file from the server given a message packet containing \
            a header that indicates the server is preparing to send a file.

        :param msg: Message packet starting with the IMG header.
        :type msg: str
        :return: A PIL `Image` object.
        :rtype: :class:`Image`
        """
        _, length, key = msg.split(':')
        img = self.client_socket.recv(self.buffer)
        while len(img) < int(length):
            img += self.client_socket.recv(self.buffer)
        dec_img = BytesIO(decrypt_file(img, key))
        image = Image.open(dec_img)
        image = ImageOps.pad(image, (980, 780))
        return image

    @lru_cache
    def _request_file(self, filename: str):
        """
        Request a file from the server.  Takes a path to file on the server
        and returns the file.

        :param filename: /path/to/file
        :type filename: str
        :returns: The file requested from the server.
        :rtype: bytes
        """
        self.send_message('FILE:%s' % filename)
        msg = decrypt(self.private_key, self.client_socket.recv(self.buffer))
        return self._get_file(msg)

    def send_message(self, msg: str) -> None:
        """
        Send a message to the server.

        :param msg: Message to send.
        :type msg: string
        """
        try:
            txt = encrypt(self.srv_key, msg)
            self.client_socket.send(txt)
            if msg == "/quit":
                if self.window is not None:
                    self.window['CLIENT_STATUS'].update('Not connected.')
                self.client_socket.close()
        except OSError as error:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.address)
            print(error)

    def disconnect(self) -> None:
        """Disconnect from chat server."""
        self.send_message("/quit")
        self.connected = False

    def _authenticate(self, last: str = None) -> str:
        """
        Authenticate on the server. Returns the server's response.

        :param last: The server's response to previous attempt to \
            authenticate or None if this the first attempt.
        :type last: string
        :return: The server's response.
        :rtype: string
        """
        login_layout = [
            [sG.T(last, size=(30, 1), visible=(False, True)[last != ''])],
            [sG.T("Username:", size=(15, 1)),
             sG.Input(default_text=self.username, size=(20, 1), k='USERNAME')],
            [sG.T("Password:", size=(15, 1)),
             sG.Input(default_text=self.password, size=(20, 1), k='PASSWORD',
                      password_char='*')],
            [sG.Checkbox('Save credentials',
                         default=OPTIONS['SAVE_CREDENTIALS'],
                         k='CREDENTIALS')],
            [sG.Submit(), sG.Cancel()]
        ]

        login = sG.Window("Server Requesting Authentication", login_layout)

        while True:
            event = login.read()[0]
            if event in ['Cancel', sG.WIN_CLOSED]:
                login.close()
                return 'Previous login attempt suspended.'
            elif event == 'Submit':
                username = login['USERNAME'].get()
                password = login['PASSWORD'].get()
                if OPTIONS['SAVE_CREDENTIALS']:
                    OPTIONS['USERNAME'] = username
                self.send_message('%s %s' % (username, password))
                answer = decrypt(self.private_key,
                                 self.client_socket.recv(self.buffer))
                login.close()
                return answer
