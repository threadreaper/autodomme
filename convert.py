import re
import os

scripts_dir = 'Scripts/Module'

tokens = re.compile(r'@\w*|#\w*|^\(\w*\)')

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
    '#LetTheEdgeFade': '\nstopStroking()',
    '] ': ']\n',
    'tits': '_boobs_',
    'an ass': '_an ass_'
}


def swap(line_list, i, item, new_item):
    line_list[i] = line_list[i].replace(item, new_item)


def convert(lines: list[str]) -> list[str]:
    for i, line in enumerate(lines):
        if '@StopStroking' in line:
            lines[i] = 'stopStroking()\n'
        elif re.match(r'^\(.*\)', line):
            lines[i] = '# %s\n' % lines[i][1:-2]
        for x, y in swap_dict.items():
            if x in line:
                swap(lines, i, x, y)
    return lines


def convert_step_2(lines: list[str]) -> list[str]:
    for i, line in enumerate(lines):
        if '@DifferentAnswer' in line:
            lines.remove(line)
        elif line.startswith('\n'):
            swap(lines, i, '\n', "")
        elif lines[-1].startswith('@Info'):
            lines.insert(0, lines.pop(-1))
    return lines


script = '/home/michael/projects/teaseme/Tease AI 0.54.9/\
Scripts/Wicked Tease/Modules/AssOrTitsMan_EDGING.txt'
with open(script, 'r') as file:
    lines = file.readlines()
    filename = os.path.basename(script)

lines: list[str] = convert(lines)

with open('%s/%s' % (scripts_dir, filename), 'w') as file:
    file.writelines(lines)

with open('%s/%s' % (scripts_dir, filename), 'r') as file:
    lines: list[str] = file.readlines()

lines: list[str] = convert_step_2(lines)

with open('%s/%s' % (scripts_dir, filename), 'w') as file:
    file.writelines(lines)

with open('%s/%s' % (scripts_dir, filename), 'r') as file:
    lines: list[str] = file.readlines()

for i, line in enumerate(lines):
    if line[0].isupper():
        swap(lines, i, line, '\"%s\"\n' % line.strip())

with open('%s/%s' % (scripts_dir, filename), 'w') as file:
    file.writelines(lines)
