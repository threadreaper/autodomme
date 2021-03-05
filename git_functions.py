import os
from sh import git


def auto_update():
    """Updates the application from a github repo."""
    add_remote = git.bake('remote', 'add', 'origin',
                          'https://github.com/threadreaper/autodomme.git')

    if '.git' not in os.listdir(os.getcwd()):
        git('init')
        add_remote()
    elif git('remote').exit_code != 0:
        add_remote()

    git('pull')
