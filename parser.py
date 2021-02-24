import re
import sqlite3
import random
from typing import Any
from options import OPTIONS

DB = 'teaseai.db'


class Parser():
    """Script parser object"""

    def __init__(self, script: str) -> None:
        """
        Initializes the parser.

        :param script: The script file to parse.
        :type script: file
        """
        self.script = script
        self.conn = sqlite3.connect(DB)
        self.lines = self.read()
        self.index = -1
        self.rx_dict = {
            'function': re.compile(r'\S+\(.*\)'),
            'option': re.compile(r'^-\s\*\*.*\*\*\s.*\n'),
            'anchor': re.compile(r'^#\s.*\n'),
            'question': re.compile(r'\".*\?\"\s'),
            'string': re.compile(r'\".*\"'),
        }
        self.stroking = False
        self.stack = []

    def _get_synonym(self, vocab: str) -> str:
        """
        Retrieves a list of synonyms for the given vocab word from the
        database and returns a randomly selected synonym.

        :param vocab: The vocab string from the parser.
        :type vocab: string
        :return: A randomly selected synonym.
        :rtype: string
        """
        con = sqlite3.connect(DB)
        vocab = vocab.strip('_') if vocab.startswith('_') else vocab
        sql = 'WITH const as (SELECT SynID FROM vocab WHERE word = "%s"), \
               const2 as (SELECT SynID from synonyms where ParentSynID \
               in (SELECT * from const) UNION SELECT ParentSynID from \
               synonyms where SynID in (SELECT * from const)) SELECT word \
               from vocab WHERE SynID in const2' % vocab
        res = [line[0] for line in con.execute(sql)]
        res.append(vocab)
        return res[random.randint(0, len(res) - 1)]

    def read(self) -> list[str]:
        """
        Reads the current script file into memory, strips blank lines and
        the @Info line and parses all the vocab strings.  Returns a list
        of lines.

        :return: A list of lines.
        :rtype: list of strings
        """
        with open(self.script, 'r') as file:
            lines = file.readlines()
            regex = re.compile(r'^@|^\s')
            lines = [line for line in lines if not regex.search(line)]
            regex = re.compile(r'\_[\w\*]*_')
            for i, line in enumerate(lines):
                for hit in regex.findall(line):
                    lines[i] = line.replace(hit, self._get_synonym(hit))
            regex = re.compile(r'var\(\w+_*\w*\)')
            for i, line in enumerate(lines):
                for hit in regex.findall(line):
                    args = self._parse_function(hit)[1]
                    lines[i] = line.replace(hit, OPTIONS[args[0].upper()])
        return lines

    def _parse_function(self, function: str):
        """
        Parses a string identified by the parser as a regex match for a
        function and returns a tuple containing the name of the function
        and a list of arguments.

        :param function: The string matching the regex for a function.
        :type function: string
        :return: A tuple containing the name of the function and a list of
        arguments to be passed to the function.
        :rtype: tuple
        """
        words = function.split('(', 1)
        args = words[1][:-1].split(',', 1)
        for i, arg in enumerate(args):
            args[i] = arg.strip()
        return (words[0], args)

    def get_answer(self):
        options = []
        # TODO: prompt user after timeout
        # TODO: get input from the chat
        # TODO: resolve options to vocab words
        if self.lines[self.index + 1].startswith('#'):
            self.index += 2
        if self.lines[self.index].startswith('#'):
            self.index += 1
        for i, line in enumerate(self.lines[self.index:]):
            match = re.match(self.rx_dict['option'], line)
            if match:
                match = match.group().split('**')
                options.append((match[1].split(', '),
                                match[2].strip(), i))
            match = re.match(self.rx_dict['anchor'], line)
            if match:
                break
        user_input = 'yeah'
        for option in options:
            if user_input in option[0]:
                self.index += option[2] - 1
                return option[1]

    def parse(self, line: str) -> Any:
        """
        Parses a line of a script.  Returns output if any is necessary.

        TODO: figure out when/how to send dialog lines to chat.
        :param line: The line to parse.
        :type line: string
        :return: String to output to chat.
        :rtype: str|None
        """
        for key, rx in self.rx_dict.items():
            match = rx.findall(line)
            if len(match) > 0:
                if key == 'question':
                    for item in match:
                        self.parse('\"%s\"' % item.strip())
                        self.parse('%s' % self.get_answer())
                if key == 'function':
                    for item in match:
                        func, args = self._parse_function(match[0])
                        if func == 'chance':
                            if random.randint(0, 100) <= int(args[0]):
                                self.parse(args[1])
                        elif func == 'goto':
                            for i, line in enumerate(self.lines):
                                if args[0] in line and line.startswith('#'):
                                    self.index = i
                        elif func == 'startStroking':
                            self.stroking = True
                            return '\"%s\"' % \
                                self._get_synonym('_Start stroking._')
                        elif func == 'stopStroking':
                            self.stroking = False
                            return '\"%s\"' % \
                                self._get_synonym('_Stop stroking._')
                        elif func == 'setFlag':
                            OPTIONS[args[0]] = True
                            return None
                        elif func == 'getFlag':
                            keys = OPTIONS.dict.keys()
                            if args[0] in keys and OPTIONS[args[0]]:
                                self.lines.insert(self.index + 1, 'goto(%s)' %
                                                  args[0])
                            return None
                        elif func == 'loopAnswer':
                            for i, line in enumerate(self.lines):
                                if args[0] in line and line.startswith('#'):
                                    self.index = i + 1
                            return self.get_answer()
                        elif func == 'edge':
                            # TODO: wait for edge confirmation from client
                            return '\"%s\"' % \
                                self._get_synonym('_Edge._')
                        elif func == 'end':
                            break
                            # TODO: pick up new script
                elif key == 'string':
                    for item in match:
                        return item.strip()


if __name__ == '__main__':
    parser = Parser('Scripts/Start/HappyToSeeMe.md')
    while parser.index <= len(parser.lines) - 2:
        parser.index += 1
        line = parser.parse(parser.lines[parser.index])
        if line and line.startswith('"'):
            print(line)

    def syn(terms: list) -> None:
        """
        Takes a list of indeces for vocab words and adds the synonym\
        crossreferences to the database.

        :param terms: The list of indeces of synonyms in the vocab table.
        :type terms: list
        """
        conn = sqlite3.connect(DB)
        junk = []
        for term in terms:
            tuples = [(term, x) for x in terms if x != term]
            for x in tuples:
                junk.append(x) if (x[1], x[0]) not in junk else ...

        for x in junk:
            conn.execute('INSERT INTO synonyms(ParentSynID, SynID) \
                         VALUES(?, ?)', (x[0], x[1]))
        conn.commit()
