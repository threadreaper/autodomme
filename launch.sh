 
#!/bin/bash
git config --global alias.up '!git remote update -p; git merge --ff-only @{u}'
git up
python3 __main__.py
