#!/usr/bin/env python3
"""Install the tool on toolforge."""

from os import remove
from shutil import rmtree
from subprocess import check_call, check_output, CalledProcessError, DEVNULL

from commons import HOME, assert_webservice_control
from update_python_webservice import pull_updates, rm_old_logs


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
    src = HOME + '/www/python/src'
    try:
        check_call(['git', 'clone', '--depth', '1', repo_url + ' ' + src])
    except CalledProcessError:  # SRC is not empty and git cannot clone
        rmtree(src)
        check_call(['git', 'clone', '--depth', '1', repo_url + ' ' + src])


def recreate_venv_and_restart_webservice():
    try:  # To prevent corrupt manifest file. See T164245.
        remove(HOME + '/service.manifest')
    except FileNotFoundError:
        pass
    try:
        rmtree(HOME + '/www/python/venv')
    except FileNotFoundError:
        pass
    check_call(
        'webservice --backend=kubernetes python shell\n'
        'python3 -m venv ~/www/python/venv'
        ' && pip install --upgrade pip'
        ' && pip install -Ur ~/www/python/src/requirements.txt'
        ' && webservice --backend=kubernetes python restart',
        shell=True)


def main():
    assert_webservice_control(__file__)
    clone_repo()
    rm_old_logs()
    recreate_venv_and_restart_webservice()


if __name__ == '__main__':
    main()
