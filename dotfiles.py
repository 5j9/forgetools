#!/usr/bin/env python3
"""Add .profile, .bashrc, and other commons settings."""

from glob import glob
from logging import info
from shutil import copyfile

from commons import HOME, DATAFILES


def write_profile():
    if glob(HOME + 'pythons/ve*'):
        with open(DATAFILES + '.profile.venv', 'rb') as f:
            activate_venv = f.read()
    else:
        info('No ve* was found in ~/pythons. '
             'No venv activation will be added to profile.')
        activate_venv = b''

    with open(DATAFILES + '.profile.ezprompt', 'rb') as f:
        ezprompt = f.read()

    with open('/etc/skel/.profile', 'rb') as profile_skel:
        with open(HOME + '.profile', 'wb') as profile:
            profile.write(
                profile_skel.read()
                + ezprompt
                + activate_venv)


def write_bashrc():
    with open('/etc/skel/.bashrc', 'rb') as bashrc_skel:  # T131561
        with open(HOME + '.bashrc', 'wb') as bashrc:
            bashrc.write(bashrc_skel.read().replace(
                b'HISTCONTROL=ignoredups:ignorespace',
                b'HISTCONTROL=ignoreboth:erasedups', 1))


def main():
    write_bashrc()
    write_profile()
    copyfile(DATAFILES + '.vimrc', HOME + '.vimrc')
    copyfile(DATAFILES + '.selected_editor', HOME + '.selected_editor')
    import git_config
    git_config.main()


if __name__ == '__main__':
    main()