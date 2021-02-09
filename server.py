#!usr/bin/python
import socket
from threading import Thread, Event
from PySimpleGUI.PySimpleGUI import obj_to_string
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
import server
import sqlite3
import hashlib
import binascii
import os

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)
public_key = private_key.public_key()
public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


socket.setdefaulttimeout(60)


class Person:

    def __init__(self, addr, client, key):
        self.addr = addr
        self.client = client
        self.name = None
        self.key = key

    def set_name(self, name, username):
        self.name = name
        conn = sqlite3.connect('teaseai.db')
        c = conn.cursor()
        c.execute("UPDATE users SET chat_name=?, online=1 WHERE username = ?", (name, username,))
        conn.commit()
        c.close()
        conn.close()
    
    def __repr__(self):
        result = "The client: {0} with IP addr: {1}".format(
            self.name, self.addr)
        return result


HOST = "0.0.0.0"
PORT = 1337
address = (HOST, PORT)


class Server(object):

    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.address = (self.host, self.port)
        self.clients = []
        self.server = None
        self.exit_event = Event()

    def encrypt(self, person, msg):
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
            except Exception as e:
                print("Failed to BroadCast message", e)

    def set_up_server(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(address)
            self.server.listen(5)
            print("Server Set-Up Successful")
            accept_thread = Thread(target=self.start_server, daemon=True)
            accept_thread.start()
        except socket.error as e:
            print(
                "Error....Unable to Set Up Sockets with {0}".format(e.strerror))
            self.server.close()

    def decrypt(self, msg):
        plaintext = private_key.decrypt(
            msg,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()

    def login(self, person):
        conn = sqlite3.connect('teaseai.db')
        c = conn.cursor()
        auth_packet = person.client.recv(512)
        username, password = self.decrypt(auth_packet).split()
        hash = (False, True)[len(password) > 15]
        if hash == False:
            c.execute("SELECT salt FROM users WHERE username = ?", (username,))
            salt, = c.fetchone()
            key = hashlib.pbkdf2_hmac(
                'sha256', password.encode(), salt, 100000)
            key = binascii.hexlify(key).decode()
        else:
            key = password
        c.execute(
            "SELECT username FROM users WHERE username = ? AND password = ?", (username, key))
        user, = c.fetchone()
        if user:
            msg = self.encrypt(person, 'true')
            person.client.send(msg)
            name = person.client.recv(512)
            name = self.decrypt(name)
            person.set_name(name, username)
            message = (f"{name} has joined the chat!")
            self.clients.append(person)
            self.start_broadcasting(message, "")            
            return True
        else:
            c.close()
            conn.close()
            return False

    def client_handler(self, person):
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
                        print("Disconnected {0} from server".format(person.name))
                        break
                    else:
                        self.start_broadcasting(result, person.name + ": ")
                        print("{0}: ".format(person.name), result)
                except Exception as e:
                    print("Error...Failed to Broadcast Message", e)
        else:
            msg = self.encrypt(person, 'False')
            client.send(msg)
            client.close()

    def start_server(self):
        while True:
            if self.exit_event.is_set():
                print('server exit signal received')
                break
            try:
                print("Waiting For a Client...")
                (requestSocket, clientAddr) = self.server.accept()
                client_key = requestSocket.recv(833)
                client_key = serialization.load_pem_public_key(client_key)
                person = Person(clientAddr, requestSocket, client_key)
                if isinstance(client_key, rsa.RSAPublicKey):
                    print(
                        "Got a connection request from...{0}".format(clientAddr))
                    handler = Thread(target=self.client_handler,
                                     args=(person,), daemon=True)
                    handler.start()
                    requestSocket.send(public_key)
                else:
                    person.client.close()
                    print("Connection rejected - malformed public key")
                    break
            except socket.error as e:
                print(
                    "Error... Failed to send a request to the client {0}".format(e.strerror))

            """     def new_user(self, user: str, password: str):
        conn = sqlite3.connect('teaseai.db')
        c = conn.cursor()
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        key = binascii.hexlify(key).decode()
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (user, key, salt))
        conn.commit()
        c.close()
        conn.close() """


if __name__ == '__main__':
    server = Server()
    server.set_up_server()
