#!/usr/bin/env python3
"""Update the source and restart `webservice --backend=kubernetes <type>`"""

from logging import debug, info, warning
from os import chdir, close, remove, rename, write
from os.path import exists
from pathlib import Path
from pty import openpty
from re import findall
from runpy import run_path
from subprocess import CalledProcessError, Popen

from commons import (
    HOME,
    assert_webservice_control,
    cached_check_output,
    max_version,
    verbose_run,
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


def handle_master_renamed_to_main(e: CalledProcessError) -> None:
    if b'ref refs/heads/master' not in e.stderr:
        raise
    # Assuming the error is caused by master being renamed to main.
    verbose_run('git', 'branch', '-m', 'master', 'main')
    verbose_run('git', 'fetch', 'origin')
    verbose_run('git', 'branch', '-u', 'origin/main', 'main')
    verbose_run('git', 'remote', 'set-head', 'origin', '-a')


def pull_updates() -> None:
    chdir(HOME + 'www/python/src')
    verbose_run('git', 'reset', '--hard')
    try:
        verbose_run('git', 'pull')
    except CalledProcessError as e:
        handle_master_renamed_to_main(e)
        verbose_run('git', 'pull')


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


def rm_manifest():
    try:  # To prevent corrupt manifest file. See T164245.
        rename(HOME + 'service.manifest', HOME + 'service.manifest.backup')
    except FileNotFoundError:
        info('service.manifest not found')
    except FileExistsError:
        remove(HOME + 'service.manifest.backup')
        rename(HOME + 'service.manifest', HOME + 'service.manifest.backup')
        warning('replaced service.manifest.backup with service.manifest')
    else:
        warning('service.manifest was moved to service.manifest.backup')


def restart_webservice():
    rm_manifest()
    try:
        args = (Path.home() / '.webservice-args').read_bytes().decode().split()
    except FileNotFoundError:
        args = ()
    verbose_run(
        'webservice',
        '--backend=kubernetes',
        *args,
        newest_container_type(),
        'restart',
    )


def run_install_script():
    install = HOME + 'www/python/src/install.py'
    try:
        run_path(install, run_name='__main__')
    except FileNotFoundError:
        if exists(install):  # the error is from inside install.py
            raise
        debug('no install.py')


def assert_webservice_type():
    o = verbose_run('webservice', 'status').stdout
    webservice_type = (
        o.partition(b'Your webservice of type ')[2]
        .partition(b' is running on backend kubernetes')[0]
        .decode()
    )
    if webservice_type != newest_container_type():
        raise SystemExit(
            f'current webservice is of type {webservice_type}, '
            f'newest container type is {newest_container_type()}, '
            f'try `python3 forgetools webservice install`'
        )


def main():
    assert_webservice_control(__file__)
    assert_webservice_type()
    rm_old_logs()
    pull_updates()
    install_requirements()
    run_install_script()
    restart_webservice()


if __name__ == '__main__':
    main()
