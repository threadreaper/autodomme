from git import Repo
import os


if '.git' not in os.listdir(os.getcwd()):
    repo = Repo.init(os.getcwd())
    repo.create_remote('origin', 'https://github.com/threadreaper/autodomme')
    repo.git.checkout('v0.0.2')
else:
    repo = Repo.init(os.getcwd())

if repo.remotes[0].exists():
    repo.remotes[0].fetch()
