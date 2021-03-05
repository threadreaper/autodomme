import os
from sh import git


def process_output(line):
    print(line)

    
def auto_update():
    """Updates the application from a github repo."""
    print('UPDATING')
    add_remote = git.bake('remote', 'add', 'origin',
                          'https://github.com/threadreaper/autodomme.git')

    if '.git' not in os.listdir(os.getcwd()):
        git('init')
        add_remote()
    elif git('remote').exit_code != 0:
        add_remote()

    git('pull', _out=process_output)

if __name__ == '__main__':
    auto_update()