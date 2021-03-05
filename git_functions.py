from git import Repo
import os


if '.git' not in os.listdir(os.getcwd()):
    repo = Repo.init(os.getcwd())
    repo.create_remote('origin', 'https://github.com/threadreaper/autodomme')
    repo.git.checkout('new_client')
else:
    repo = Repo.init(os.getcwd())

origin = repo.remote('origin')
if origin.exists():
    repo.git.checkout('new_client')
    if repo.is_dirty():
        repo.git.add('--all')
        repo.git.commit('-m', 'commit from python')
        origin.push()
    else:
        origin.pull()
