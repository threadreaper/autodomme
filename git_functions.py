import os
from sh import git

add_remote = git.bake('remote', 'add', 'origin',
                      'https://github.com/threadreaper/autodomme.git')
if '.git' not in os.listdir(os.getcwd()):
    git('init')
    add_remote()
    git.checkout('new_client')
else:
    remote = git('remote')
    if remote.exit_code != 0:
        add_remote()

git('pull')
