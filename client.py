#!/usr/bin/env python3
"""Client class and associated methods"""
from io import BytesIO
from socket import AF_INET, SOCK_STREAM, socket
from threading import Lock, Thread

import PySimpleGUI as sG
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization.base import \
    load_pem_public_key
from PIL import Image, ImageOps

from options import OPTIONS


class Client:
    """
    for communication with server
    """
    HOST = OPTIONS['SERVER_ADDRESS']
    PORT = OPTIONS['SERVER_PORT']
    ADDR = (HOST, PORT)
    BUFSIZ = 512

    def __init__(self, window):
        """
        Init object and send name to server
        :param name: str
        """
        self.window = window
        self.chat_name = OPTIONS['CHAT_NAME']
        self.username = OPTIONS['USERNAME']
        self.password = OPTIONS['PASSWORD']
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        pub = self.private_key.public_key()
        self.public_key = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.srv_key = None
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.messages = []
        self.lock = Lock()

    def connect(self):
        """Attempt to connect to a server"""
        self.client_socket.connect(self.ADDR)
        self.client_socket.send(self.public_key)
        self.srv_key = load_pem_public_key(self.client_socket.recv(833))
        if isinstance(self.srv_key, rsa.RSAPublicKey):
            authenticated = self.authenticate('')
            while authenticated != 'True':
                if not authenticated:
                    break
                else:
                    authenticated = self.authenticate(authenticated)
            if authenticated:
                receive_thread = Thread(target=self.receive_messages)
                receive_thread.start()
                self.send_message(self.chat_name)
        else:
            print('Key handshake failure - connection rejected')

    def update_window(self, user):
        """Add user to online users list"""
        txt = self.window['ONLINE_USERS'].get()
        if f"{user}\n" not in txt:
            self.window['ONLINE_USERS'].update(f'{user}\n', append=True)
        else:
            self.window['ONLINE_USERS'].update(txt.strip(user), append=False)

    def decrypt(self, msg):
        """Decrypt a transmission from the server"""
        plaintext = self.private_key.decrypt(
            msg,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()

    def decrypt_file(self, file, fern_key):
        """Decrypt a received image file"""
        fern = Fernet(fern_key)
        return fern.decrypt(file)

    def receive_messages(self):
        """
        receive messages from server
        :return: None
        """
        while True:
            try:
                msg = self.client_socket.recv(512)
                if len(msg) == 0:
                    break
                msg = self.decrypt(msg)
                if 'has joined the chat' in msg or 'has left the chat' in msg:
                    self.update_window(msg.split()[0])
                if msg.startswith('IMG'):
                    _, length, key = msg.split(':')

                    img = self.client_socket.recv(512)
                    while len(img) < int(length):
                        img += self.client_socket.recv(512)

                    with open('client.png', 'wb') as file:
                        file.write(img)

                    dec_img = BytesIO(self.decrypt_file(img, key))
                    image = Image.open(dec_img)
                    image = ImageOps.pad(image, (980, 780))
                    with BytesIO() as bio:
                        image.save(bio, format="PNG")
                        del image
                        self.window['IMAGE'].update(data=bio.getvalue())
                else:
                    sG.cprint(msg)
                # make sure memory is safe to access
                self.lock.acquire()
                self.messages.append(msg)
                self.lock.release()
            except OSError as error:
                print('[EXCPETION]', error)
                break

    def send_message(self, msg):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        try:
            text = msg.encode('utf8')
            text = self.srv_key.encrypt(
                text,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                ))
            self.client_socket.send(text)
            if msg == "quit":
                self.client_socket.close()
        except OSError as error:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.ADDR)
            print(error)

    def get_messages(self):
        """
        :returns a list of str messages
        :return: list[str]
        """
        messages_copy = self.messages[:]

        # make sure memory is safe to access
        self.lock.acquire()
        self.messages = []
        self.lock.release()

        return messages_copy

    def disconnect(self):
        """Disconnect from chat server."""
        self.send_message("/quit")

    def authenticate(self, last):
        """Authenticate on the server."""
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
                return False
            elif event == 'Submit':
                username = login['USERNAME'].get()
                password = login['PASSWORD'].get()
                if OPTIONS['SAVE_CREDENTIALS']:
                    OPTIONS['USERNAME'] = username
                self.send_message('%s %s' % (username, password))
                answer = self.decrypt(self.client_socket.recv(512))
                login.close()
                return answer
