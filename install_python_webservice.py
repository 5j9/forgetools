#!/usr/bin/env python3
"""Install the tool on toolforge."""

from logging import debug
from shutil import rmtree
from subprocess import CalledProcessError

from commons import HOME, assert_webservice_control, verbose_run
from update_python_webservice import (
    install_requirements,
    pull_updates,
    restart_webservice,
    rm_old_logs,
    run_install_script,
)


def get_repo_url() -> (str, bool):
    try:
        repo_url = verbose_run(
            'git',
            '-C',
            HOME + 'www/python/src',
            'config',
            '--get',
            'remote.origin.url',
        ).stdout
    except CalledProcessError:
        return input('Enter the URL of the git repository:'), False
    else:
        return repo_url.rstrip().decode(), True


def clone_repo():
    repo_url, repo_exists = get_repo_url()
    if repo_exists:
        pull_updates()
        return
    src = HOME + 'www/python/src'
    try:
        verbose_run('git', 'clone', '--depth', '1', repo_url, src)
    except CalledProcessError:  # SRC is not empty and git cannot clone
        rmtree(src)
        verbose_run('git', 'clone', '--depth', '1', repo_url, src)


def recreate_venv_and_install_requirements():
    try:
        rmtree(HOME + 'www/python/venv')
    except FileNotFoundError:
        debug('/www/python/venv does not exist')
    install_requirements(b'python3 -m venv ~/www/python/venv')


def main():
    assert_webservice_control(__file__)
    clone_repo()
    rm_old_logs()
    recreate_venv_and_install_requirements()
    run_install_script()
    restart_webservice()


if __name__ == '__main__':
    main()
