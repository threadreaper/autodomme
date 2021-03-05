import os
import sh


if '.git' not in os.listdir(os.getcwd()):
    sh.git('init')
    sh.git('remote', 'add', 'origin', 'https://github.com/threadreaper/autod,omme.git')
    sh.git.checkout('new_client')
else:
    remote = sh.git('remote')
    if remote.exit_code != 0:
        sh.git('remote', 'add', 'origin', 'https://github.com/threadreaper/autodomme.git')
