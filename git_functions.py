from git import Repo
import os

repo = Repo.init(os.getcwd())
# repo.create_remote('origin', 'https://github.com/threadreaper/autodomme')
# repo.git.checkout((repo.remote().refs))
print(repo.active_branch)
