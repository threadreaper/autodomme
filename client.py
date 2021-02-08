from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Lock
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization.base import load_pem_public_key
import PySimpleGUI as sg
from options import OPTIONS

class Client:
    """
    for communication with server
    """
    HOST = "localhost"
    PORT = 1337
    ADDR = (HOST, PORT)
    BUFSIZ = 512
    
    def __init__(self, name):
        """
        Init object and send name to server
        :param name: str
        """
        self.username = OPTIONS['USERNAME']
        self.password = OPTIONS['PASSWORD']
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        self.public_key = self.private_key.public_key()
        self.public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)
        self.client_socket.send(self.public_key)
        self.srv_key = load_pem_public_key(self.client_socket.recv(833))
        if isinstance(self.srv_key, rsa.RSAPublicKey):
            if not self.authenticate():
                print('Authentication failur - conneciton rejected')
            else:
                self.messages = []
                receive_thread = Thread(target=self.receive_messages)
                receive_thread.start()
                self.send_message(name)
                self.lock = Lock()
        else:
            print('Key handshake failure - connection rejected')
        

    def decrypt(self, msg):
        plaintext = self.private_key.decrypt(
            msg,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()

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
                else:
                    msg = self.decrypt(msg)
                    sg.cprint(msg)
                # make sure memory is safe to access
                self.lock.acquire()
                self.messages.append(msg)
                self.lock.release()
            except Exception as e:
                print("[EXCPETION]", e)
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
        except Exception as e:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.ADDR)
            print(e)

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
        self.send_message("/quit")


    def authenticate(self):
        
        login_layout = [
            [sg.T('', size=(20,1), k='oops', visible=False)],
            [sg.T("Username:"), sg.Input(default_text=self.username, size=(20,1), k='USERNAME')],
            [sg.T("Password:"), sg.Input(default_text=self.password, size=(20,1), password_char='*', k='PASSWORD')],
            [sg.Checkbox('Save credentials', default=OPTIONS['SAVE_CREDENTIALS'], k='CREDENTIALS')],
            [sg.Submit(), sg.Cancel()]
        ]

        login = sg.Window("Server Requesting Authentication", login_layout)

        while True:
            event = login.read()[0]
            if event == 'Cancel' or event == sg.WIN_CLOSED:
                login.close()
                return 1            
            elif event == 'Submit':
                username = login['USERNAME'].get()
                password = login['PASSWORD'].get()
                self.send_message('%s %s' % (username, password))
                answer = self.client_socket.recv(512)
                login.close()
                return [True if answer == 'True' else False]
