#!/usr/bin/env python3
"""Update the source and restart `webservice --backend=kubernetes python`"""

from commons import HOME, assert_webservice_control, POD_NAME
from os import chdir, remove
from subprocess import check_call
from logging import info


def pull_updates():
    chdir(HOME + '/www/python/src')
    check_call('git reset --hard && git pull', shell=True)


def install_requirements_and_restart_webservice():
    common_upgrade_commands = (
        '. ~/www/python/venv/bin/activate '
        ' && pip install --upgrade pip '
        ' && pip install -Ur ~/www/python/src/requirements.txt')
    if POD_NAME:
        info('Using the existing pod for upgrading requirements.')
        check_call([
            'kubectl', 'exec', POD_NAME, '--', 'bash', '-c',
            "'" + common_upgrade_commands + '"'])
        check_call(['webservice', '--backend=kubernetes', 'python', 'restart'])
        return
    check_call(
        'webservice --backend=kubernetes python shell\n'
        + common_upgrade_commands +
        ' && webservice --backend=kubernetes python restart',
        shell=True)


def rm_old_logs():
    try:
        remove(HOME + '/uwsgi.log')
    except FileNotFoundError:
        pass
    try:
        remove(HOME + '/error.log')
    except FileNotFoundError:
        pass


def main():
    assert_webservice_control(__file__)
    rm_old_logs()
    pull_updates()
    install_requirements_and_restart_webservice()


if __name__ == '__main__':
    main()
