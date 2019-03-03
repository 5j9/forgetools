#!/usr/bin/env python3
"""Install the tool on toolforge."""

from os import remove
from shutil import rmtree
from subprocess import check_call, check_output, CalledProcessError, DEVNULL

from commons import HOME, KUBERNETES
from update_kube_python import pull_updates, rm_old_logs


SRC = HOME + '/www/python/src'
VENV = HOME + '/www/python/venv'


def get_repo_url() -> (str, bool):
    try:
        repo_url = check_output(
            'git -C ~/wwww/python/src config --get remote.origin.url',
            shell=True, stderr=DEVNULL)
    except CalledProcessError:
        return input('Enter the URL of the git repository:'), False
    else:
        return repo_url.rstrip().decode(), True


def clone_repo():
    repo_url, repo_exists = get_repo_url()
    if repo_exists:
        pull_updates()
        return
    try:
        check_call('git clone --depth 1 ' + repo_url + ' ' + SRC, shell=True)
    except CalledProcessError:  # SRC is not empty and git cannot clone
        rmtree(SRC)
        check_call('git clone --depth 1 ' + repo_url + ' ' + SRC, shell=True)


def recreate_venv_and_start_webservice():
    try:  # To prevent corrupt manifest file. See T164245.
        remove(HOME + '/service.manifest')
    except FileNotFoundError:
        pass
    ve_commands = (
        'python3 -m venv ~/www/python/venv'
        '\npip install --upgrade pip'
        '\npip install -Ur ~/www/python/src/requirements.txt'
        '\nwebservice --backend=kubernetes python restart')
    try:
        rmtree(VENV)
    except FileNotFoundError:
        pass
    if KUBERNETES:
        check_call(ve_commands, shell=True)
        return

    check_call(
        'webservice --backend=kubernetes python shell\n' + ve_commands,
        shell=True)


if __name__ == '__main__':
    clone_repo()
    rm_old_logs()
    recreate_venv_and_start_webservice()
    print('All Done!')
