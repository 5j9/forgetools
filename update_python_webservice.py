#!/usr/bin/env python3
"""Update the source and restart `webservice --backend=kubernetes python`"""

from commons import HOME, assert_webservice_control
from os import chdir, remove
from subprocess import check_call


def pull_updates():
    chdir(HOME + '/www/python/src')
    check_call(('git', 'reset', '--hard'))
    check_call(('git', 'pull'))


def install_requirements(shell_script_prepend: str = None):
    shell_script = (
        '. ~/www/python/venv/bin/activate '
        ' && pip install --upgrade pip setuptools'
        ' && pip install -Ur ~/www/python/src/requirements.txt')
    if shell_script_prepend:
        shell_script = shell_script_prepend + ' && ' + shell_script
    # Todo: `kubectl run` creates a deployment, use `create` for a pod without
    # a deployment, see the link below for more info:
    # http://jamesdefabia.github.io/docs/user-guide/pods/single-container/
    check_call([
        'kubectl', 'run', '--image',
        'docker-registry.tools.wmflabs.org/toollabs-python-web:latest',
        'requirements-installer'])
    check_call([
        'kubectl', 'exec', 'requirements-installer', '--',
        'sh', '-c', shell_script])
    check_call(['kubectl', 'delete', 'deployment', 'requirements-installer'])


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
    check_call(['webservice', '--backend=kubernetes', 'python', 'restart'])


def main():
    assert_webservice_control(__file__)
    rm_old_logs()
    pull_updates()
    install_requirements()
    restart_webservice()


if __name__ == '__main__':
    main()
