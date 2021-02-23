import re
import os

scripts_dir = 'Scripts/Module'

regex_dict = {
    '@_token': re.compile(r'@\w*'),
    'vocab_token': re.compile(r'#\w*'),
    'opt_token': re.compile(r'\[.*\]'),
    'anchor_token': re.compile(r'^\(\w*\)'),
    }

tokens = re.compile(r'@\w*|@\w*\({1}.*\){1}|#\w*')

swap_dict = {
    '@End': '\nend()',
    '@SetFlag': '\nsetFlag',
    '@CheckFlag': '\ngetFlag',
    '@Goto': '\ngoto',
    '@LoopAnswer': '\nloopAnswer()',
    '@Edge': '\nedge()',
    '@ShowBoobsImage': '\nshowBoobsImage()',
    '@ShowButtImage': '\nshowButtImage()',
    '@LockImages': '',
    '@UnlockImages': '',
    '#Gonna': 'gonna',
    '#PetName': 'var(chat_name)',
    '#SubName': 'var(chat_name)',
    '#Boobs': '_boobs_',
    '#Grin': '_*grins*_',
    '#LetTheEdgeFade': '\nstopStroking()'
}


def swap(line_list, i, item, new_item):
    line_list[i] = line_list[i].replace(item, new_item, 1)


def convert(script):
    with open(script, 'r') as file:
        lines = file.readlines()
    filename = os.path.basename(script)
    for i, line in enumerate(lines):
        for key, rx in regex_dict.items():
            for match in rx.finditer(line):
                if len(match.group(0)) > 0:
                    if match.group(0) == '@StopStroking':
                        lines[i] = 'stopStroking()\n'
                    if key == 'anchor_token':
                        lines[i] = '# %s\n' % lines[i][1:-2]
                    elif key == 'opt_token':
                        swap(lines, i, '[', '- **')
                        swap(lines, i, ']', '**')
                    else:
                        for x, y in swap_dict.items():
                            if x in match.group(0):
                                swap(lines, i, x, y)
    if lines[-1].startswith('@Info'):
        lines.insert(0, lines.pop(-1))
    for i, line in enumerate(lines):
        if '@DifferentAnswer' in line:
            lines.remove(line)
        if line.startswith('\n'):
            swap(lines, i, '\n', "")
        if 'tits' in line:
            swap(lines, i, 'tits', '_boobs_')
        if 'an ass' in line:
            swap(lines, i, 'an ass', '_an ass_')
    return lines, filename


lines, filename = convert('/home/michael/projects/teaseme/Tease AI 0.54.9/Scripts/Wicked Tease/Modules/AssOrTitsMan_EDGING.txt')

with open('%s/%s' % (scripts_dir, filename), 'w') as file:
    file.writelines(lines)