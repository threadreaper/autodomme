#!/usr/bin/env python3
"""Classes related to the TeaseAI server"""
import io
import os
import random
import socket
import sqlite3
from script_parser import Parser
from queue import SimpleQueue
from threading import Lock, Thread
from typing import Any

from cryptography.hazmat.primitives.asymmetric import rsa

from crypto import (decrypt, encrypt, encrypt_file, encrypt_message,
                    get_key_pair, hash_password, load_pem)

DB = 'teaseai.db'

conn = sqlite3.connect(DB)

BUFFER = 512


class Person:
    """Class to hold data about connected clients"""

    def __init__(self, addr: str, client: socket.socket,
                 key: rsa.RSAPublicKey) -> None:
        """
        Initializes client information

        :param addr: Client's IP address.
        :type addr: string
        :param client: Client's socket.
        :type client: socket
        :param key: Client's public RSA key.
        :type key: rsa.RSAPublicKey
        """
        self.addr = addr
        self.client = client
        self.name = None
        self.key = key
        self.ops = False

    def set_name(self, name: str) -> None:
        """
        Sets the chat name for a connected client.

        :param name: Client's chat name.
        :type name: str
        """

        self.name = name


class Server(object):
    """TeaseAI server object"""

    def __init__(self) -> None:
        """
        Initialize the server and create a key pair for encrypted
        communication and a message queue for server status updates.

        Public methods:
        - set_up_server(): Starts the server.
        - kill(): Shuts down the server.
        - opt_get(): Retrieves the value of a server option.
        - opt_set(): Sets the value of a server option.
        - broadcast(): Sends a chat message to all connected clients.
        - new_user(): Creates a new user in the database.
        - broadcast_image(): Displays an image to all connected clients.
        - queue.empty(): Returns True if the queue is empty, False
        otherwise.
        - queue.get(): Returns the oldest server status message.
        """

        self.host = self.opt_get('hostname')
        self.port = int(self.opt_get('port'))
        self.address = (self.host, self.port)
        self.path = self.opt_get('folder')
        self.started = False
        self.clients: list[Person] = []
        self.socket = None
        self.private_key, self.public_key = get_key_pair()
        self.client_lock = Lock()
        self.queue = SimpleQueue()
        self.slideshow = SlideShow(self.path, self)
        self.ai = AI(self)

    def set_up_server(self) -> None:
        """
        Starts the server and launches a daemon that listens for incoming
        clients.
        """
        try:
            if self.started is True:
                self.queue.put('Error: Server is already running')
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR, 1)
                self.socket.bind(self.address)
                self.socket.listen(5)
                self.queue.put("Server Set-Up Successful")
                self.started = True
                accept_thread = Thread(target=self._start_server, daemon=True)
                accept_thread.start()
        except socket.error as error:
            self.queue.put("Error....Unable to Set Up Sockets with"
                           "{0}".format(error.strerror))
            print("Error....Unable to Set Up Sockets with\
                {0}".format(error.strerror))
            self.socket.close()

    def kill(self) -> None:
        """Shuts down a running server."""
        if self.started is True:
            self.queue.put("Server shut down")
            self.started = False
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        else:
            self.queue.put("Error: No Server is running.")

    def opt_get(self, opt: str) -> Any:
        """
        Retrieve an option setting from the server and return it.

        :param opt: Option to retrieve
        :type opt: string
        :returns: Option setting
        :rtype: string
        """
        con = sqlite3.connect(DB)
        for row in con.execute("SELECT setting FROM options WHERE name = ?",
                               (opt, )):
            con.close()
            return row[0]

    def opt_set(self, opt: str, setting: Any) -> None:
        """
        Set an option setting on the server.

        :param opt: Option to set
        :type opt: string
        :param setting: Value to set the option to
        :type setting: Any
        """
        conn.execute("UPDATE options SET setting = ? WHERE name = ?",
                     (setting, opt))
        conn.commit()

    def broadcast(self, msg: str, name: str) -> None:
        """
        Encrypts and broadcasts a chat message to all connected clients.

        :param msg: The message to broadcast
        :type msg: str
        :param name: The name of the sender of the message
        :type name: str
        """
        for person in self.clients:
            txt = '%s %s' % (name, msg)
            try:
                self.send_message(person, txt)
            except socket.error as error:
                self.queue.put("Failed to BroadCast message - %s" % error)

    def _validate_auth_packet(self, auth_packet: bytes,
                              person: Person) -> tuple[str, str]:
        """
        Verifies that username and password are both populated and if not,
        prompts the user to re-enter them. Returns the username and password
        on success.

        :param auth_packet: BUFFER bytes of encrypted data read from a socket
        containing a client's username and password
        :type auth_packet: bytes
        :param person: An instance of the `Person` class
        :type person: :class:`Person`
        :returns: Username and password
        :rtype: tuple
        """
        try:
            username, password = decrypt(self.private_key, auth_packet).split()
        except ValueError:
            self.send_message(person, 'User/Pass must not be empty.')
            auth_packet = person.client.recv(BUFFER)
            username, password = self._validate_auth_packet(auth_packet,
                                                            person)
        return username, password

    def _login(self, person: Person) -> bool:
        """
        Log a user in to the server, returns True on success, False otherwise.

        :param person: The person object of the client attempting to
        authenticate.
        :type person: :class:`Person`
        :returns: True on success, False otherwise
        :rtype: bool
        """
        if not self._authenticate(person):
            return False
        self.send_message(person, 'True')
        name = person.client.recv(BUFFER)
        name = decrypt(self.private_key, name)
        if len(self.clients) == 0:
            person.set_name('@%s' % name)
            person.ops = True
        else:
            person.set_name(name)
        message = (f"{person.name} has joined the chat!")
        self.client_lock.acquire()
        self.clients.append(person)
        self.client_lock.release()
        self.broadcast(message, "")
        if person.ops:
            msg = ('Server sets mode +o %s' % name)
            self.broadcast(msg, "")
        for person in self.clients:
            self._send_session_vars(person)
        return True

    def _send_session_vars(self, person: Person) -> None:
        """
        Sends a message containing necessary session information for an
        authenticated user.

        :param person: The authenticated user's `Person` object.
        :type person: :class:`Person`
        """
        msg = 'PATH:%s:ONLINE:' % self.path
        for client in self.clients:
            msg += '%s:' % client.name
        msg += 'END'
        self.send_message(person, msg)

    def send_message(self, person: Person, message: str) -> None:
        """
        Encrypts and sends a message to a connected client.

        :param person: The `Person` object for the client to send the message\
            to.
        :type person: :class:`Person`
        :param message: The message to send.
        :type message: string.
        """
        enc_msg = encrypt(person.key, message)
        person.client.send(enc_msg)

    def _authenticate(self, person):
        """
        Authenticates a user. Returns True on success

        :param person: The client's `Person` object.
        :type person: :class:`Person`
        :return: True on success
        :rtype: bool
        """
        con = sqlite3.connect(DB)
        auth_packet = person.client.recv(BUFFER)
        username, password = self._validate_auth_packet(auth_packet, person)
        salt = False
        while not salt:
            for row in con.execute("SELECT salt FROM users WHERE username = ?",
                                   (username,)):
                salt = row[0]
            if salt == '':
                self.send_message(person, 'Invalid user.')
                auth_packet = person.client.recv(BUFFER)
                username, password = self._validate_auth_packet(auth_packet,
                                                                person)
        user = False
        while not user:
            key = hash_password(password, salt)
            for row in con.execute(
                    "SELECT username FROM users WHERE username = ? AND \
                    password = ?", (username, key)):
                user = row[0]
            if not user:
                self.send_message(person, 'Invalid password.')
                auth_packet = person.client.recv(BUFFER)
                username, password = self._validate_auth_packet(auth_packet,
                                                                person)
        con.close()
        return True

    def _client_handler(self, person: Person) -> None:
        """
        Handles communication with the client

        :param person: The person object for the client
        :type person: :class:`Person`
        """
        client = person.client
        if self._login(person):
            while True:
                msg = decrypt(self.private_key, client.recv(BUFFER))
                if msg.startswith('FILE:'):
                    path = msg.split(':')
                    self._serve_file(person, path[1])
                elif msg.startswith('PATH:'):
                    path = msg.split(':')[1]
                    self._add_folder(path, person)
                elif msg == "/quit":
                    message = ('%s has left the chat.' % person.name)
                    self.broadcast(message, "")
                    client.close()
                    self.clients.remove(person)
                    self.queue.put("Disconnected %s from server" % person.name)
                    break
                else:
                    self.broadcast(msg, person.name + ": ")
        else:
            self.send_message(person, 'Something went wrong.')

    def _start_server(self) -> None:
        """Starts the server and handles incoming client connections."""
        while True:
            try:
                self.queue.put("Server running...")
                (request_socket, client_addr) = self.socket.accept()
                client_key = request_socket.recv(833)
                client_key = load_pem(client_key)
                if isinstance(client_key, rsa.RSAPublicKey):
                    person = Person(client_addr, request_socket, client_key)
                    self.queue.put(
                        "Got a connection request from...{0}".format(
                            client_addr))
                    handler = Thread(target=self._client_handler,
                                     args=(person,), daemon=True)
                    handler.start()
                    request_socket.send(self.public_key)
                else:
                    request_socket.close()
                    self.queue.put("Connection rejected - bad key")
                    break
            except socket.error as error:
                self.queue.put(
                    "Error... Failed to send a request"
                    "to the client {0}".format(error.strerror))

    def new_user(self, user: str, password: str) -> None:
        """
        Creates a new user in the local database

        :param user: The username to create
        :type user: str
        :param password: The user's password
        :type password: str
        """
        salt = os.urandom(32)
        key = hash_password(password, salt)
        conn.execute("INSERT INTO users VALUES (?, ?, ?)", (user, key, salt))

    def _send_file(self, person, enc_file, length, key):
        """
        Sends a file to a connected client.

        :param person: The client's `Person` object.
        :type person: :class:`Person`
        :param enc_file: The encrypted file to send.
        :type file: bytes
        :param length: The length of the file to send.
        :type length: str
        :param key: The Fernet key used to encrypt the file.
        :type key: str
        """
        self.send_message(person, 'IMG:%s:%s' % (length, key))

        with io.BytesIO(enc_file) as file:
            chunk = file.read(BUFFER)
            while chunk:
                person.client.send(chunk)
                chunk = file.read(BUFFER)

    def _broadcast_image(self, image: str) -> None:
        """
        Encrypts and broadcasts an image to all connected clients.

        :param image: /path/to/image
        :type image: str
        """
        enc_file, length, key = encrypt_file(image)

        self.client_lock.acquire()
        for person in self.clients:
            self._send_file(person, enc_file, length, key)
        self.client_lock.release()

    def _serve_file(self, person: Person, file: str) -> None:
        """
        Answer a client's request to retrieve a file from the server

        :param person: An instance of the client's `Person` object.
        :type person: :class:`Person`
        :param file: /path/to/file
        :type file: str
        """
        enc_file, length, key = encrypt_file(file)
        self._send_file(person, enc_file, length, key)

    def _add_folder(self, path, person: Person):
        """
        Answer a client's request to populate the server browser window
        """
        files = []
        folders = []
        try:
            for item in os.listdir(path):
                if not item.startswith('.'):
                    fqp = os.path.join(path, item)
                    if os.path.isdir(fqp):
                        folders.append(item)
                    elif item.endswith(('jpg', 'jpeg', 'gif', 'png', 'bmp')):
                        files.append(item)
        except PermissionError:
            pass
        folders = 'FOLDERS:' + ((',').join(folders)
                                if folders else 'NULL') + ':'
        files = 'FILES:' + ((',').join(files) if files else 'NULL')
        if len(folders + files) > 446:
            enc_msg, length, key = encrypt_message(folders + files)
            self.send_message(person, 'MSG:%s:%s' % (length, key))
            with io.BytesIO(enc_msg) as file:
                chunk = file.read(BUFFER)
                while chunk:
                    person.client.send(chunk)
                    chunk = file.read(BUFFER)
        else:
            self.send_message(person, folders + files)


class SlideShow(object):
    """Class for an Image slideshow"""

    def __init__(self, folder: str, server: Server) -> None:
        """
        Initializes the slideshow.

        Public methods:
        - start(): Start the slideshow.
        - stop(): Stop the slideshow.
        - next(): Display the next slide.
        - back(): Display the previous slide.
        - update(): Update the slideshow.

        :param folder: /path/to/folder containing slideshow images.
        :type folder: string
        :param server: An instance of the `Server` object.
        :type server: :class: `Server`
        """
        self.directory = folder
        self.index = 0
        self.time = 0
        self.server = server
        self.randomize = self.server.opt_get('randomize')
        self.started = False
        self.images = []

    def _add_folder(self, folder: str) -> None:
        """
        Grabs all images from the given folder and adds them to the slideshow.
        Runs recursively if "Include subfolders" option is checked.

        :param folder: The folder to add images from.
        :type folder: string
        """
        images = []
        folders = []
        try:
            images = [os.path.join(folder, f) for f in sorted(os.listdir(
                folder)) if os.path.isfile(os.path.join(folder, f)) and
                f.lower().endswith(('png', 'jpg', 'jpeg', 'tiff', 'bmp'))]
            folders = [os.path.join(folder, f) for f in sorted(os.listdir(
                folder)) if os.path.isdir(os.path.join(folder, f))]
        except PermissionError:
            ...
        self.images += images
        if self.server.opt_get('subfolders') == '1':
            for folder in folders:
                self._add_folder(folder)

    def start(self) -> None:
        """Start the slideshow."""
        self._add_folder(self.directory)
        self.started = True
        self._show()

    def stop(self) -> None:
        """Stop the slideshow."""
        self.started = False

    def _show(self) -> None:
        """Display the current slideshow image."""
        image = self.images[self.index]
        self.server._broadcast_image(image)

    def next(self) -> None:
        """Advance the slideshow to the next slide."""
        if self.server.opt_get('randomize') == '1':
            self.index = random.randint(0, len(self.images) - 1)
        else:
            if self.index + 1 == len(self.images):
                self.index = 0
            else:
                self.index += 1
        self._show()

    def back(self) -> None:
        """Display the previous slide."""
        self.index -= 1
        self._show()

    def update(self, delta: float) -> None:
        """
        Update the slideshow.

        :param delta: The amount of time since the last update.
        :type delta: float
        """
        if self.started is True:
            self.time += delta
            if self.time > 3:
                self.time = 0
                self.next()


class AI(object):
    """Class for AI domme"""

    def __init__(self, server: Server) -> None:
        """
        Initializes the AI

        :param server: An instance of a server object
        :type server: :class: `Server`
        """
        self.server = server
        self.name = server.opt_get('domme-name')
        self.folder = server.opt_get('folder')
        self.time = random.uniform(0.0, 3.0)
        self.delta = 0
        self.lines = []
        self.index = 0
        self.send('%s has joined the chat!' % self.name, '')
        self.parser = Parser('./Scripts/Start/HappyToSeeMe.md', self.server)
        self.flags = {}

    def send(self, msg, name):
        self.server.broadcast(msg, name)

    def update(self, delta):
        """
        Runs the next line of a script.
        """
        self.delta += delta
        if self.parser.index >= len(self.parser.lines):
            return None
        if self.delta >= self.time:
            self.delta = 0
            self.time = random.uniform(0.0, 3.0)
            line = self.parser.parse(self.parser.lines[self.parser.index])
            if line and line.startswith('"'):
                self.send(line.strip(), self.name)
            self.parser.index += 1


if __name__ == '__main__':
    server = Server()
    server.set_up_server()
