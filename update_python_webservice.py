#!/usr/bin/env python3
"""Update the source and restart `webservice --backend=kubernetes <type>`"""
from logging import debug
from os import chdir, close, remove, write
from pty import openpty
from re import findall
from runpy import run_path
from subprocess import Popen, check_call

from commons import (
    HOME,
    assert_webservice_control,
    cached_check_output,
    max_version,
)


def newest_container_type(lang='python') -> str:
    """Use `webservice -h` to return newest container type for the given lang.

    The output of `webservice -h` contains a list like this:
    ```
    Supported webservice types:
      Kubernetes backend:
        [...]
        * python3.11
        * python3.9
        [...]
    ```
    """
    webservice_help = cached_check_output('webservice', '-h')
    type_version_pairs = findall(rf'\* \b({lang}([\d.]+))\b', webservice_help)
    return max_version(type_version_pairs)


def pull_updates():
    chdir(HOME + 'www/python/src')
    check_call(('git', 'reset', '--hard'))
    check_call(('git', 'pull'))


def install_requirements(shell_script_prepend: bytes = None):
    # ~ is / in the kubectl's shell
    shell_script = (
        b'. ~/www/python/venv/bin/activate '
        b' && pip install --upgrade pip setuptools'
        b' && pip install -Ur ~/www/python/src/requirements.txt'
        b' && exit\n'
    )
    if shell_script_prepend:
        shell_script = shell_script_prepend + b' && ' + shell_script
    # Kubernetes terminates immediately on a non-tty process. Use pty instead.
    master, slave = openpty()
    try:
        p = Popen(
            [
                'webservice',
                '--backend=kubernetes',
                newest_container_type(),
                'shell',
            ],
            stdin=slave,
            bufsize=1,
        )
        write(master, shell_script)
        p.wait()
    finally:
        close(master)
        close(slave)


def rm_old_logs():
    try:
        remove(HOME + 'uwsgi.log')
    except FileNotFoundError:
        pass
    try:
        remove(HOME + 'error.log')
    except FileNotFoundError:
        pass


def restart_webservice():
    try:  # To prevent corrupt manifest file. See T164245.
        remove(HOME + 'service.manifest')
    except FileNotFoundError:
        pass
    check_call(
        [
            'webservice',
            '--backend=kubernetes',
            newest_container_type(),
            'restart',
        ]
    )


def run_install_script():
    try:
        run_path(HOME + 'www/python/src/install.py', run_name='__main__')
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
