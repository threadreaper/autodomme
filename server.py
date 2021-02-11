#!/usr/bin/env python3
"""Server class and methods related to crypto"""
import binascii
import hashlib
import os
import socket
import sqlite3
from threading import Event, Thread

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from options import OPTIONS


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
    """Class for Server object"""
    def __init__(self):
        self.host = OPTIONS['HOSTNAME']
        self.port = OPTIONS['HOST_PORT']
        self.address = (self.host, self.port)
        self.clients = []
        self.server = None
        self.exit_event = Event()
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        pub = self.private_key.public_key()
        self.public_key = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

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

    def encrypt(self, person, msg):
        """Encrypt a message"""
        text = msg.encode('utf8')
        text = person.key.encrypt(
            text,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        return text

    def start_broadcasting(self, msg, name):
        """
        This method broadcasts  new messages to all clients
        :param msg:
        :param name: the name of the client
        :type name: str
        :return:
        """
        for person in self.clients:
            client = person.client
            try:
                msg = self.encrypt(person, '%s %s' % (name, msg))
                client.send(msg)
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
        conn = sqlite3.connect('teaseai.db')
        cursor = conn.cursor()
        auth_packet = person.client.recv(512)
        username, password = self.decrypt(auth_packet).split()
        cursor.execute("SELECT salt FROM users WHERE username = ?",
                        (username,))
        salt, = cursor.fetchone()
        key = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt, 100000)
        key = binascii.hexlify(key).decode()
        cursor.execute("SELECT username FROM users WHERE username = ?"
                       "AND password = ?", (username, key))
        user, = cursor.fetchone()
        if user:
            msg = self.encrypt(person, 'true')
            person.client.send(msg)
            name = person.client.recv(512)
            name = self.decrypt(name)
            person.set_name(name)
            message = (f"{name} has joined the chat!")
            self.clients.append(person)
            self.start_broadcasting(message, "")
            return True
        else:
            cursor.close()
            conn.close()
            return False

    def client_handler(self, person):
        """Handle communication with the client"""
        client = person.client
        if self.login(person):
            while True:
                try:
                    message = client.recv(512)
                    result = self.decrypt(message)
                    print("Received Message....{0}".format(result))
                    if result == "/quit":
                        message = (f"{person.name} has left the chat.")
                        self.start_broadcasting(message, "")
                        client.close()
                        self.clients.remove(person)
                        print("Disconnected {0} from server".format(
                            person.name))
                        break
                    else:
                        self.start_broadcasting(result, person.name + ": ")
                        print("{0}: ".format(person.name), result)
                except socket.error as error:
                    print("Error...Failed to Broadcast Message", error)
        else:
            msg = self.encrypt(person, 'False')
            client.send(msg)
            client.close()

    def start_server(self):
        """Start the server"""
        while True:
            if self.exit_event.is_set():
                print('server exit signal received')
                break
            try:
                print("Waiting For a Client...")
                (request_socket, client_addr) = self.server.accept()
                client_key = request_socket.recv(833)
                client_key = serialization.load_pem_public_key(client_key)
                person = Person(client_addr, request_socket, client_key)
                if isinstance(client_key, rsa.RSAPublicKey):
                    print(
                        "Got a connection request from...{0}".format(
                            client_addr))
                    handler = Thread(target=self.client_handler,
                                     args=(person,), daemon=True)
                    handler.start()
                    request_socket.send(self.public_key)
                else:
                    person.client.close()
                    print("Connection rejected - malformed public key")
                    break
            except socket.error as error:
                print(
                    "Error... Failed to send a request"
                    "to the client {0}".format(error.strerror))

    def new_user(self, user: str, password: str):
        """Create a new user in the local database"""
        conn = sqlite3.connect('teaseai.db')
        cursor = conn.cursor()
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(),
                                  salt, 100000)
        key = binascii.hexlify(key).decode()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user, key, salt))
        conn.commit()
        cursor.close()
        conn.close()


if __name__ == '__main__':
    server = Server()
    server.set_up_server()
