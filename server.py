#!/usr/bin/env python3
"""Server class and methods related to crypto"""
import binascii
import hashlib
import io
import os
import socket
import sqlite3
from threading import Event, Thread, Lock

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.fernet import Fernet

from options import OPTIONS

conn = sqlite3.connect('teaseai.db')


class Person:
    """Class to hold data about connected clients"""

    def __init__(self, addr, client, key):
        self.addr = addr
        self.client = client
        self.name = None
        self.key = key

    def set_name(self, name):
        """Setter for the name prop on Person"""
        self.name = name


class Server(object):
    """Class for Server object - accepts an instance of a status
    bar as an argument, and directs any output there"""

    def __init__(self, status_bar):
        self.host = OPTIONS['HOSTNAME']
        self.port = OPTIONS['HOST_PORT']
        self.address = (self.host, self.port)
        self.images = OPTIONS['HOST_FOLDER']
        self.status_bar = status_bar
        self.clients = []
        self.server = None
        self.exit_event = Event()
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        self.pub = self.private_key.public_key()
        self.public_key = self.pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.lock = Lock()

    def set_up_server(self):
        """Initialize the server."""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.address)
            self.server.listen(5)
            print("Server Set-Up Successful")
            accept_thread = Thread(target=self.start_server, daemon=True)
            accept_thread.start()
        except socket.error as error:
            print("Error....Unable to Set Up Sockets with"
                  "{0}".format(error.strerror))
            self.server.close()

    def opt_get(self, opt):
        """Retrieve an option setting from the server"""
        for row in conn.execute("SELECT setting FROM options WHERE name = ?",
                                (opt, )):
            return row[0]

    def opt_set(self, opt, setting):
        """Set an option setting on the server"""
        conn.execute("UPDATE options SET setting = ? WHERE name = ?",
                     (setting, opt))

    def encrypt(self, enc_key, msg):
        """Encrypt a message"""
        text = msg.encode('utf8')
        return enc_key.encrypt(
            text,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))

    def encrypt_file(self, filename):
        """Encrypt a file for sending"""
        with open(filename, 'rb') as file:
            file_data = file.read()
        f_key = Fernet.generate_key()
        print(f_key)
        fern = Fernet(f_key)
        out_file = fern.encrypt(file_data)
        return out_file, len(out_file), f_key

    def broadcast(self, msg, name):
        """
        This method broadcasts  new messages to all clients
        :param msg:
        :param name: the name of the client
        :type name: str
        :return:
        """
        for person in self.clients:
            client = person.client
            txt = self.encrypt(person.key, '%s %s' % (name, msg))
            try:
                client.send(txt)
            except socket.error as error:
                print("Failed to BroadCast message", error)

    def decrypt(self, msg):
        """Decrypt a message"""
        plaintext = self.private_key.decrypt(
            msg,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()

    def login(self, person):
        """Log a user in to the server"""
        con = sqlite3.connect('teaseai.db')
        auth_packet = person.client.recv(512)
        username, password = self.decrypt(auth_packet).split()
        for row in con.execute("SELECT salt FROM users WHERE username = ?",
                               (username,)):
            salt, = row
        key = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt, 100000)
        key = binascii.hexlify(key).decode()
        for row in con.execute("SELECT username FROM users WHERE username = ?"
                               "AND password = ?", (username, key)):
            user, = row
        if user:
            msg = self.encrypt(person.key, 'true')
            person.client.send(msg)
            name = person.client.recv(512)
            name = self.decrypt(name)
            person.set_name(name)
            message = (f"{name} has joined the chat!")
            self.lock.acquire()
            self.clients.append(person)
            self.lock.release()
            self.broadcast(message, "")
            return True
        else:
            con.close()
            return False

    def client_handler(self, person):
        """Handle communication with the client"""
        client = person.client
        if self.login(person):
            while True:
                if self.exit_event.is_set():
                    print('server thread exiting')
                    break
                try:
                    message = client.recv(512)
                    result = self.decrypt(message)
                    print(
                        "Received Message....{0}".format(result))
                    if result == "/quit":
                        message = (f"{person.name} has left the chat.")
                        self.broadcast(message, "")
                        client.close()
                        self.clients.remove(person)
                        print(
                            "Disconnected {0} from server".format(person.name))
                        break
                    self.broadcast(result, person.name + ": ")
                    print("{0}: ".format(person.name), result)
                except socket.error as error:
                    print(
                        "Error...Failed to Broadcast Message", error)
        else:
            msg = self.encrypt(person.key, 'False')
            client.send(msg)
            client.close()

    def start_server(self):
        """Start the server"""
        while True:
            if self.exit_event.is_set():
                print('server exit signal received')
                conn.close()
                break
            try:
                print("Waiting For a Client...")
                (request_socket, client_addr) = self.server.accept()
                client_key = request_socket.recv(833)
                client_key = serialization.load_pem_public_key(client_key)
                if isinstance(client_key, rsa.RSAPublicKey):
                    person = Person(client_addr, request_socket, client_key)
                    print(
                        "Got a connection request from...{0}".format(
                            client_addr))
                    handler = Thread(target=self.client_handler,
                                     args=(person,), daemon=True)
                    handler.start()
                    request_socket.send(self.public_key)
                else:
                    request_socket.close()
                    print("Connection rejected - bad key")
                    break
            except socket.error as error:
                print(
                    "Error... Failed to send a request"
                    "to the client {0}".format(error.strerror))

    def new_user(self, user: str, password: str):
        """Create a new user in the local database"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(),
                                  salt, 100000)
        key = binascii.hexlify(key).decode()
        conn.execute("INSERT INTO users VALUES (?, ?, ?)", (user, key, salt))

    def broadcast_image(self, image):
        """Broadcasts an encrypted image to connected clients"""
        with open(image, 'rb') as file:
            file_data = file.read()
        f_key = Fernet.generate_key()
        fern = Fernet(f_key)
        enc_file = fern.encrypt(file_data)

        self.lock.acquire()
        for person in self.clients:
            client = person.client
            msg = self.encrypt(person.key, 'IMG:%s:%s' %
                               (str(len(enc_file)), f_key.decode()))
            try:
                client.send(msg)
            except socket.error as error:
                print("Failed to BroadCast message", error)

        with io.BytesIO(enc_file) as file:
            for person in self.clients:
                client = person.client
                chunk = file.read(512)
                while chunk:
                    client.send(chunk)
                    chunk = file.read(512)
        self.lock.release()


if __name__ == '__main__':
    server = Server(None)
    server.set_up_server()
