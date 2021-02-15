#!/usr/bin/env python3
"""TeaseAI server class"""
import io
import os
import socket
import sqlite3
from queue import SimpleQueue
from threading import Lock, Thread
from typing import Any
from cryptography.hazmat.primitives.asymmetric import rsa

from options import OPTIONS
from crypto import get_key_pair, load_pem, encrypt, decrypt, hash_password,\
    encrypt_file

conn = sqlite3.connect('teaseai.db')


class SlideShow():
    """Class for an Image slideshow"""
    def __init__(self, folder, server):
        self.directory = folder
        files = os.listdir(folder)
        self.images = [os.path.join(folder, f) for f in files
                       if os.path.isfile(os.path.join(folder, f)) and
                       f.lower().endswith(('png', 'jpg', 'jpeg', 'tiff',
                                           'bmp'))]

        self.index = 0
        self.time = 0
        self.server = server
        self.started = False

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def show(self):
        """Start the slideshow"""
        image = os.path.join(self.directory, self.images[self.index])
        self.server.broadcast_image(image)

    def next(self):
        """Advance the slideshow to the next slide"""
        if self.index + 1 == len(self.images):
            self.index = 0
        else:
            self.index += 1
        self.show()

    def back(self):
        """Display the slide before the current slide"""
        self.index -= 1
        self.show()

    def update(self, delta):
        """Update the slideshow"""
        if self.started is True:
            if OPTIONS['HOST_FOLDER'] != self.directory:
                self.directory = OPTIONS['HOST_FOLDER']
                self.images = os.listdir(self.directory)
                self.show()
            self.time += delta
            if self.time > 5000:
                self.time = 0
                self.next()


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
        - opt_get(): Retrieves the value of a server option.
        - opt_set(): Sets the value of a server option.
        - broadcast(): Sends a chat message to all connected clients.
        - new_user(): Creates a new user in the database.
        - broadcast_image(): Displays an image to all connected clients.
        - queue.empty(): Returns True if the queue is empty, False
        otherwise.
        - queue.get(): Returns the oldest server status message.
        - exit_event.set(): Signal server to shut down.
        """

        self.host = OPTIONS['HOSTNAME']
        self.port = OPTIONS['HOST_PORT']
        self.address = (self.host, self.port)
        self.path = OPTIONS['HOST_FOLDER']
        conn.execute('UPDATE options SET folder = ?', (self.path, ))
        self.started = False
        self.clients = []
        self.server = None
        self.private_key, self.public_key = get_key_pair()
        self.client_lock = Lock()
        self.queue = SimpleQueue()
        self.slideshow = SlideShow(self.path, self)

    def set_up_server(self) -> None:
        """
        Starts the server and launches a daemon that listens for incoming
        clients.
        """
        try:
            if self.started is True:
                self.queue.put('Error: Server is already running')
            else:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.bind(self.address)
                self.server.listen(5)
                self.queue.put("Server Set-Up Successful")
                self.started = True
                accept_thread = Thread(target=self._start_server, daemon=True)
                accept_thread.start()
        except socket.error as error:
            self.queue.put("Error....Unable to Set Up Sockets with"
                           "{0}".format(error.strerror))
            self.server.close()

    def kill(self) -> None:
        """Shuts down a running server."""
        if self.started is True:
            self.queue.put("Server shut down")
            if self.slideshow.started is True:
                self.slideshow.started = False
            self.started = False
            self.server.close()
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
        for row in conn.execute("SELECT setting FROM options WHERE name = ?",
                                (opt, )):
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

    def broadcast(self, msg: str, name: str) -> None:
        """
        Encrypts and broadcasts a chat message to all connected clients.

        :param msg: The message to broadcast
        :type msg: str
        :param name: The name of the sender of the message
        :type name: str
        """
        for person in self.clients:
            client = person.client
            txt = encrypt(person.key, '%s %s' % (name, msg))
            try:
                client.send(txt)
            except socket.error as error:
                self.queue.put("Failed to BroadCast message - %s" % error)

    def _validate_auth_packet(self, auth_packet: bytes,
                              person: Person) -> tuple[str, str]:
        """
        Verifies that username and password are both populated and if not,
        prompts the user to re-enter them. Returns the username and password
        on success.

        :param auth_packet: 512 bytes of encrypted data read from a socket
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
            msg = encrypt(person.key, 'User/Pass must not be empty.')
            person.client.send(msg)
            auth_packet = person.client.recv(512)
            username, password = self._validate_auth_packet(auth_packet,
                                                            person)
        return username, password

    def _login(self, person: Person) -> bool:
        """
        Log a user in to the server, returns True on success, False otherwise.

        :param person: The person object of the client attempting to
        authenticate
        :type person: :class:`Person`
        :returns: True on success, False otherwise
        :rtype: bool
        """
        if self._authenticate(person):
            msg = encrypt(person.key, 'True')
            person.client.send(msg)
            name = person.client.recv(512)
            name = decrypt(self.private_key, name)
            person.set_name(name)
            message = (f"{name} has joined the chat!")
            self.client_lock.acquire()
            self.clients.append(person)
            self.client_lock.release()
            self.broadcast(message, "")
            self._send_session_vars(person)
            return True
        else:
            return False

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
        msg = encrypt(person.key, msg)
        person.client.send(msg)

    def _authenticate(self, person):
        """
        Authenticates a user. Returns True on success

        :param person: The client's `Person` object.
        :type person: :class:`Person`
        :return: True on success
        :rtype: bool
        """
        con = sqlite3.connect('teaseai.db')
        auth_packet = person.client.recv(512)
        username, password = self._validate_auth_packet(auth_packet, person)
        salt = False
        while not salt:
            for row in con.execute("SELECT salt FROM users WHERE username = ?",
                                   (username,)):
                salt = row[0]
            if salt == '':
                msg = encrypt(person.key, 'Invalid User')
                person.client.send(msg)
                auth_packet = person.client.recv(512)
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
                msg = encrypt(person.key, 'Invalid Password')
                person.client.send(msg)
                auth_packet = person.client.recv(512)
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
                msg = decrypt(self.private_key, client.recv(512))
                self.queue.put("Received Message: {0}".format(msg))
                if msg.startswith('FILE:'):
                    path = msg.split(':')
                    self._serve_file(person, path[1])
                elif msg == "/quit":
                    message = (f"{person.name} has left the chat.")
                    self.broadcast(message, "")
                    client.close()
                    self.clients.remove(person)
                    self.queue.put(
                        "Disconnected {0} from server".format(person.name))
                    break
                else:
                    self.broadcast(msg, person.name + ": ")
        else:
            msg = encrypt(person.key, 'Something went wrong')
            client.send(msg)

    def _start_server(self) -> None:
        """Starts the server and handles incoming client connections."""
        while True:
            try:
                self.queue.put("Server running...")
                (request_socket, client_addr) = self.server.accept()
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
        msg = encrypt(person.key, 'IMG:%s:%s' % (length, key))
        try:
            person.client.send(msg)
        except socket.error as error:
            self.queue.put("Failed to BroadCast message %s" % error)

        with io.BytesIO(enc_file) as file:
            chunk = file.read(512)
            while chunk:
                person.client.send(chunk)
                chunk = file.read(512)

    def broadcast_image(self, image: str) -> None:
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


if __name__ == '__main__':
    server = Server()
    server.set_up_server()
