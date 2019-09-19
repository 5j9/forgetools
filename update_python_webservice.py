#!/usr/bin/env python3
"""Update the source and restart `webservice --backend=kubernetes python3.5`"""

from commons import HOME, assert_webservice_control
from logging import debug
from os import chdir, remove, write, close
from pty import openpty
from runpy import run_path
from subprocess import check_call, Popen


def pull_updates():
    chdir(HOME + '/www/python/src')
    check_call(('git', 'reset', '--hard'))
    check_call(('git', 'pull'))


def install_requirements(shell_script_prepend: bytes = None):
    # ~ is / in the kubectl's shell
    shell_script = (
        b'. ~/www/python/venv/bin/activate '
        b' && pip install --upgrade pip setuptools'
        b' && pip install -Ur ~/www/python/src/requirements.txt'
        b' && exit\n')
    if shell_script_prepend:
        shell_script = shell_script_prepend + b' && ' + shell_script
    # Kubernetes terminates immediately on a non-tty process. Use pty instead.
    master, slave = openpty()
    try:
        p = Popen(
            ['webservice', '--backend=kubernetes', 'python3.5', 'shell'],
            stdin=slave, bufsize=1)
        write(master, shell_script)
        p.wait()
    finally:
        close(master)
        close(slave)


def rm_old_logs():
    try:
        remove(HOME + '/uwsgi.log')
    except FileNotFoundError:
        pass
    try:
        remove(HOME + '/error.log')
    except FileNotFoundError:
        pass


def restart_webservice():
    try:  # To prevent corrupt manifest file. See T164245.
        remove(HOME + '/service.manifest')
    except FileNotFoundError:
        pass
    check_call(['webservice', '--backend=kubernetes', 'python3.5', 'restart'])


def run_install_script():
    try:
        run_path(HOME + '/www/python/src/install.py', run_name='__main__')
    except FileNotFoundError:
        debug('no install.py')


def main():
    assert_webservice_control(__file__)
    rm_old_logs()
    pull_updates()
    install_requirements()
    run_install_script()
    restart_webservice()


if __name__ == '__main__':
    main()
