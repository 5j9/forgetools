#!/usr/bin/env python3
"""Install the tool on toolforge."""

from shutil import rmtree
from subprocess import CalledProcessError

from commons import HOME, assert_webservice_control, verbose_run
from update_python_webservice import (
    pull_updates,
    restart_webservice,
    rm_old_logs,
    run_install_script,
    sync_up_venv,
)


def get_repo_url() -> tuple[str, bool]:
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


def main():
    assert_webservice_control(__file__)
    clone_repo()
    rm_old_logs()
    sync_up_venv()
    run_install_script()
    restart_webservice()


if __name__ == '__main__':
    main()
