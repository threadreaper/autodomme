import re

regex_dict = {
    '@_token': re.compile(r'@\w*\(?\w*\)?'),
    'vocab_token': re.compile(r'#\w*'),
    'opt_token': re.compile(r'\[.*\]'),
    'anchor_token': re.compile(r'^\(\w*\)'),
    'question': re.compile(r'\?\"\s'),
    }


def convert(script):
    with open(script, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        for key, rx in regex_dict.items():
            match = rx.findall(line)
            if len(match) > 0:
                for item in match:
                    if key == '@_token':
                        if item == '@StopStroking':
                            lines[i] = 'stopStroking()'
                        elif item.startswith('@CheckFlag'):
                            lines[i] = lines[i].replace('@CheckFlag',
                                                        'getFlag')
                        elif item.startswith('@Goto'):
                            lines[i] = lines[i].replace(item, 'goto')
                        elif item == '@LoopAnswer':
                            if lines[i].startswith('@LoopAnswer'):
                                lines[i] = lines[i].replace(item,
                                                            'loopAnswer()')
                            else:
                                lines[i] = lines[i].replace(item,
                                                            '\nloopAnswer()')
                        elif item == '@DifferentAnswer':
                            lines.remove(lines[i])
                    elif key == 'vocab_token':
                        if item == '#PetName':
                            lines[i] = lines[i].replace(item, 'var(chat_name)')
                    elif key == 'opt_token':
                        lines[i] = lines[i].replace('[', '- **')
                        lines[i] = lines[i].replace(']', '**')
                    elif key == 'anchor_token':
                        print('got anchor token', item)
    for line in lines:
        print(line.strip())


convert('/home/michael/projects/teaseme/Tease AI 0.54.9/Scripts/'
        'Wicked Tease/Modules/AssOrTitsMan_EDGING.txt')
