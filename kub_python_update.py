#!/usr/bin/env python3
"""Update the source and restart `webservice --backend=kubernetes python`"""

from subprocess import check_call, check_output
from os import chdir, remove
from commons import HOME, POD_NAME


def pull_updates():
    chdir(HOME + '/www/python/src')
    check_call('git reset --hard && git pull', shell=True)


def install_requirements():
    upgrade_commands = (
        '. ~/www/python/venv/bin/activate '
        '&& pip install --upgrade pip '
        '&& pip install -Ur ~/www/python/src/requirements.txt'
    )
    if POD_NAME:
        check_output(
            'kubectl exec '
            + POD_NAME
            + ' -- bash -c "' + upgrade_commands + '"',
            shell=True
        )
        return
    # already in pod's shell
    check_call(upgrade_commands, shell=True)


def rm_old_files():
    try:
        remove(HOME + '/uwsgi.log')
    except FileNotFoundError:
        pass
    try:
        remove(HOME + '/error.log')
    except FileNotFoundError:
        pass


def main():
    rm_old_files()
    pull_updates()
    install_requirements()
    check_output(
        'webservice --backend=kubernetes python restart', shell=True)


if __name__ == '__main__':
    main()
