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
            [
                'git', '-C', '~/wwww/python/src',
                'config', '--get', 'remote.origin.url'
            ], stderr=DEVNULL)
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
        check_call(['git', 'clone', '--depth', '1', repo_url + ' ' + SRC])
    except CalledProcessError:  # SRC is not empty and git cannot clone
        rmtree(SRC)
        check_call(['git', 'clone', '--depth', '1', repo_url + ' ' + SRC])


def recreate_venv_and_restart_webservice():
    try:  # To prevent corrupt manifest file. See T164245.
        remove(HOME + '/service.manifest')
    except FileNotFoundError:
        pass
    try:
        rmtree(VENV)
    except FileNotFoundError:
        pass
    check_call(
        'webservice --backend=kubernetes python shell'
        '\npython3 -m venv ~/www/python/venv'
        '\npip install --upgrade pip'
        '\npip install -Ur ~/www/python/src/requirements.txt'
        '\nwebservice --backend=kubernetes python restart',
        shell=True)


def main():
    if KUBERNETES:
        raise RuntimeError(
            'You need to run ' + __file__ + ' from the bastion host'
            'so that it can control the webservice.')
    clone_repo()
    rm_old_logs()
    recreate_venv_and_restart_webservice()


if __name__ == '__main__':
    main()
