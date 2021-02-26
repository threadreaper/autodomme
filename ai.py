import random
from parser import Parser


class AI(object):
    """Class for AI domme"""

    def __init__(self, server: object) -> None:
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
        self.parser = Parser('./Scripts/Start/HappyToSeeMe.md')
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
