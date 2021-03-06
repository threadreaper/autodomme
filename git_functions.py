import os
import string

import PySimpleGUI as sG
from sh import git
from urllib3 import PoolManager


def download(filename: str) -> None:
    """
    Downloads a file from the git repo and saves it to the local directory.

    :param filename: The filename to download from the repo.
    :type filename: `str`
    """
    url = 'https://raw.githubusercontent.com/threadreaper/autodomme/master/'

    r = PoolManager().request('GET', url + filename, preload_content=False)

    with open(filename, 'wb') as out:
        while True:
            data = r.read(512)
            if not data:
                break
            out.write(data)

    r.release_conn()


def filter_filename(filename: str) -> str:
    """
    Filters the filenames returned from the stdout of the auto_update function.
    This list represents all characters considered valid in "POSIX fully
    portable" filenames. Returns the filtered string.

    :param filename: A string containing a line of output from auto_update().
    :type filename: `str`
    :return: The filtered string.
    :rtype: `str`
    """
    return ''.join(x for x in filename if x in string.ascii_letters +
                   string.digits + '_.-/').rstrip('m').lstrip('1h')


def update_popup(filenames: list[str]) -> None:
    """
    Constructs the popup window for the auto_update function.

    :param filenames: A list of filenames to update.
    :type filenames: `list[str]`
    """
    layout = [
        [sG.Text('Updating application...')],
        [sG.ProgressBar(len(filenames), orientation='h', size=(20, 20),
                        k='progressbar')],
        [sG.Cancel()]
    ]

    popup = sG.Window('Notice', layout, modal=True)
    for i, filename in enumerate(filenames):
        if '/' in filename and not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        event = popup.read(timeout=10)[0]
        if event in ['Cancel', sG.WIN_CLOSED]:
            break
        download(filename)
        popup['progressbar'].UpdateBar(i + 1)
    popup.close()


def auto_update() -> bool:
    """Updates the application from a github repo."""
    add_remote = git.bake('remote', 'add', '-f', '--tags', '-m', 'master',
                          '-t', 'master', 'origin',
                          'https://github.com/threadreaper/autodomme.git')

    if '.git' not in os.listdir(os.getcwd()):
        git('init')
        add_remote()
        git.branch('--set-upstream-to', 'origin/master')
    elif git('remote').exit_code != 0:
        add_remote()
        git.branch('--set-upstream-to', 'origin/master')

    files = [line for line in git('--no-pager', 'diff', '--name-only',
                                  _iter=True)]
    if files:
        filenames = [filter_filename(file) for file in files[:-1]]
        update_popup(filenames)
        return True
    else:
        return False


if __name__ == '__main__':
    auto_update()
