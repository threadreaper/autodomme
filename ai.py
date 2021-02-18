from server import Server
import os


class AI():
    """Class for AI domme"""

    def __init__(self, server: Server = None) -> None:
        """
        Initializes the AI

        :param server: An instance of a server object
        :type server: :class: `Server`
        """
        self.server = server
        self.name = server.opt_get('domme-name')
        self.folder = server.opt_get('folder')
        self.time = 0
        self.delta = 0
        self.lines = []
        self.index = 0
        self.send('%s has joined the chat!' % self.name, '')

    def send(self, msg, name):
        self.server.broadcast(msg, name)

    def start_script(self):
        """
        Initializes an AI-guided teasing session.
        """
        starts = os.listdir('./Scripts')
        print(starts)
        #with open(script, 'r') as file:
        #    self.lines = file.readlines()

    def update(self, delta):
        """
        Runs the next line of a script.
        """
        self.delta += delta
        if self.delta >= self.time:
            self.send(self.lines[self.index], self.name)


if __name__ == '__main__':
    ai = AI()
    ai.start_script()