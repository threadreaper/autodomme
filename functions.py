# functions to be exposed to userspace scripts
from options import OPTIONS

class ChatServer():
    def __init__(self):
        self.que = []
        self.responses = []
    def push(self, message):
        self.que.append(message)
    def respond(self, message):
        self.responses.append(message)
    def update(self):
        if len(self.que) > 0:
            return self.que.pop(0)

chat = ChatServer()

def hotkey(key):
    chat.push(f'{OPTIONS["SUB_NAME"]}: {OPTIONS[key]}')
    chat.respond(OPTIONS[key])

