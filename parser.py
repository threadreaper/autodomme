import re
import sqlite3
import random
from typing import Any
from options import OPTIONS

DB = 'teaseai.db'


class Parser(object):
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
            'option': re.compile(r'^\[.*\]'),
            'anchor': re.compile(r'^#\s.*\n'),
            'string': re.compile(r'\".*\"'),
        }
        self.stroking = False

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
        args = [arg.strip() for arg in args]
        return (words[0], args)

    def getanswer(self, args: list[str]) -> str:
        """
        Gets an answer to a question from the client and returns\
            the AI's response

        :param args: A list of arguments to be passed to the function.
        :type args: list[str]
        """
        options = []
        # TODO: prompt user after timeout
        # TODO: get input from the chat
        # TODO: resolve options to vocab words
        lines = self.lines[self.index:]
        for i, line in enumerate(lines):
            match = re.match(self.rx_dict['option'], line)
            if match:
                line = line.lstrip('[').rstrip(']  \n')
                options.append(line.split(', '))
                options.append(lines[i + 1].rstrip('  \n'))
                options.append(i + 1)
            match = re.match(self.rx_dict['anchor'], line)
            if match:
                break
        user_input = 'wtf'
        for i, option in enumerate(options):
            if type(option) == list and user_input in option:
                self.index += options[i+2]
                return options[i+1]
        self.index -= 2
        return '"Your response to my question seems meaningless."'

    def goto(self, args: list[str]) -> None:
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        anchor = args[0]
        for i, line in enumerate(self.lines):
            if anchor in line and line.startswith('#'):
                self.index = i

    def chance(self, args: list[str]) -> None:
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        chance = args[0]
        command = args[1]
        if random.randint(0, 100) <= int(chance):
            self.parse(command.strip('\''))

    def startstroking(self, args: list[str]) -> str:
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        self.stroking = True
        return '\"%s\"' % self._get_synonym('_Start stroking._')

    def stopstroking(self, args: list[str]) -> str:
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        self.stroking = False
        return '\"%s\"' % self._get_synonym('_Stop stroking._')

    def setflag(self, args: list[str]) -> None:
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        OPTIONS[args[0]] = True

    def getflag(self, args: list[str]) -> None:
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        keys = OPTIONS.dict.keys()
        if args[0] in keys and OPTIONS[args[0]]:
            self.goto([args[0]])

    def loopanswer(self, args: list[str]) -> str:
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        for i, line in enumerate(self.lines):
            if args[0] in line and line.startswith('#'):
                self.index = i + 1
        return self.getanswer([])

    def edge(self, args):
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        return '\"%s\"' % self._get_synonym('_Edge._')

    def end(self, args):
        """
        Jumps to a different position in the script.

        :param args: A list of arguments for the function.
        :type args: list[str]
        """
        # TODO: pick up the next script
        exit()

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
            for item in match:
                if key == 'function':
                    func, args = self._parse_function(match[0])
                    return eval('self.%s(%s)' % (func.lower(), args))
                elif key == 'string':
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
