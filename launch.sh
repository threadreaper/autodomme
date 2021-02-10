 
#!/bin/bash
git config --global alias.up '!git remote update -p; git merge --ff-only @{u}'
git up
pip3 install -r requirements.txt
python3 __main__.py
