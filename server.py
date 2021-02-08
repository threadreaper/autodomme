#!usr/bin/python
import socket
from threading import Thread
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)
public_key = private_key.public_key()
public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


class Person:

    def __init__(self, addr, client, key):
        self.addr = addr
        self.client = client
        self.name = None
        self.key = key
        
    def set_name(self, name):
        self.name = name

    def __repr__(self):
        result = "The client: {0} with IP addr: {1}".format(self.name, self.addr)
        return result

HOST = "0.0.0.0"
PORT = 80
address = (HOST, PORT)

class Server(object):

    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.address = (self.host, self.port)
        self.clients = []
        self.server = None

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
                msg = '%s %s' % (name, msg)
                text = msg.encode('utf8')
                text = person.key.encrypt(
                    text,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    ))
                client.send(text)
            except Exception as e:
                print("Failed to BroadCast message", e)

    def set_up_server(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(address)
            self.server.listen(5)
            print("Server Set-Up Successful")
            accept_thread = Thread(target=self.start_server)
            accept_thread.start()
            accept_thread.join()
        except socket.error as e:
            print("Error....Unable to Set Up Sockets with {0}".format(e.strerror))
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

    def client_handler(self, person):
        client = person.client
        # get client's name
        name = client.recv(512)
        name = self.decrypt(name)
        person.set_name(name)
        message = (f"{name} has joined the chat!")
        self.start_broadcasting(message, "")
        while True:
            try:
                message = client.recv(512)                
                result = self.decrypt(message)
                print("Received Message....{0}".format(result))
                if result == "/quit":
                    client.close()
                    self.clients.remove(person)
                    message = (f"{name} has left the chat.")
                    self.start_broadcasting(message, "")
                    print("Disconnected {0} from server".format(name))
                    break
                else:
                    self.start_broadcasting(result, name + ": ")
                    print("{0}: ".format(name), result)
            except Exception as e:
                print("Error...Failed to Broadcast Message", e)

    def start_server(self):
        while True:
            try:
                print("Waiting For a Request from server...")
                (requestSocket, clientAddr) = self.server.accept()                
                client_key = requestSocket.recv(833)
                client_key = serialization.load_pem_public_key(client_key)
                person = Person(clientAddr, requestSocket, client_key)
                if isinstance(client_key, rsa.RSAPublicKey):
                    self.clients.append(person)
                    print("Got a connection request from...{0}".format(clientAddr))
                    Thread(target=self.client_handler, args=(person,)).start()
                    requestSocket.send(public_key)
                else:
                    person.client.close()
                    print("Connection rejected - malformed public key")
            except socket.error as e:
                print("Error... Failed to send a request to the client {0}".format(e.strerror))
                break


if __name__ == '__main__':
    server = Server()
    server.set_up_server()