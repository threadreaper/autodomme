import re
import sqlite3
import random


class Parser():
    """Script parser object"""

    def __init__(self, script: str) -> None:
        """
        Initializes the parser.

        :param script: The script file to parse.
        :type script: file
        """
        self.script = script
        self.conn = sqlite3.connect('teaseai.db')
        self.lines = self.read()
        self.index = 0
        self.rx_dict = {
            'verb': re.compile(r'^\S+\(.*\)'),
            'option': re.compile(r'^-\s\*\*.*\*\*\s.*\n'),
            'anchor': re.compile(r'^#\s.*\n')
        }

    def _get_synonym(self, vocab):
        """
        Retrieves a list of synonyms for the given vocab word from the
        database and returns a randomly selected synonym.

        :param vocab: The vocab string from the parser.
        :type vocab: string
        :return: A randomly selected synonym.
        :rtype: string
        """
        vocab = vocab.strip('_') if vocab.startswith('_') else vocab
        sql = 'WITH const as (SELECT SynID FROM vocab WHERE word = "%s"), \
               const2 as (SELECT SynID from synonyms where ParentSynID \
               in (SELECT * from const) UNION SELECT ParentSynID from \
               synonyms where SynID in (SELECT * from const)) SELECT word \
               from vocab WHERE SynID in const2' % vocab
        res = [line[0] for line in self.conn.execute(sql)]
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
                    line = line.replace(hit, self._get_synonym(hit))
                lines[i] = line
        return lines

    def next(self) -> None:
        """
        Parses the next line of the script.
        """
        line = self.lines[self.index]
        for key, rx in self.rx_dict.items():
            match = rx.findall(line)
            if match:
                if key == 'verb' and match[0] != '':
                    for item in match:
                        print('%s - got a command' % self.index)
                elif key == 'option' and match[0] != '':
                    for item in match:
                        print('%s - parsed an option' % self.index)
                elif key == 'anchor' and match[0] != '':
                    for item in match:
                        print('%s - parsed an anchor' % self.index)


if __name__ == '__main__':
    parser = Parser('Scripts/Start/HappyToSeeMe.md')
    parser.read()
    parser.next()
    while parser.index <= len(parser.lines) - 2:
        parser.index += 1
        parser.next()

    def syn(terms: list) -> None:
        conn = sqlite3.connect('teaseai.db')
        junk = []
        for term in terms:
            tuples = [(term, x) for x in terms if x != term]
            for x in tuples:
                junk.append(x) if (x[1], x[0]) not in junk else ...

        for x in junk:
            conn.execute('INSERT INTO synonyms(ParentSynID, SynID) \
                         VALUES(?, ?)', (x[0], x[1]))
        conn.commit()

