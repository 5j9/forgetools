#!/usr/bin/env python3
"""Add .profile, .bashrc, and other commons settings."""

from glob import glob
from logging import info
from pathlib import Path
from shutil import copyfile

from commons import DATAFILES, HOME


def write_profile():
    if glob(HOME + 'pythons/ve*'):
        activate_venv = Path(DATAFILES + '.profile.venv').read_bytes()
    else:
        info(
            'No ve* was found in ~/pythons. '
            'No venv activation will be added to profile.'
        )
        activate_venv = b''

    ezprompt = Path(DATAFILES + '.profile.ezprompt').read_bytes()

    Path(HOME + '.profile').write_bytes(
        Path('/etc/skel/.profile', 'rb').read_bytes()
        + ezprompt
        + activate_venv
    )


def write_bashrc():
    Path(HOME + '.bashrc').write_bytes(
        Path('/etc/skel/.bashrc')  # T131561
        .read_bytes()
        .replace(
            b'HISTCONTROL=ignoredups:ignorespace',
            b'HISTCONTROL=ignoreboth:erasedups',
            1,
        )
    )


def write_gitconfig():
    from configparser import RawConfigParser

    updates = RawConfigParser()
    with open(DATAFILES + '.gitconfig', encoding='utf8') as f:
        updates.read_file(f)

    home_config = RawConfigParser()
    with open(HOME + '.gitconfig', 'a+', encoding='utf8') as f:
        f.seek(0)
        home_config.read_file(f)
        f.seek(0)
        home_config.update(updates)
        f.truncate()
        home_config.write(f)


def main():
    write_bashrc()
    write_profile()
    copyfile(DATAFILES + '.vimrc', HOME + '.vimrc')
    copyfile(DATAFILES + '.selected_editor', HOME + '.selected_editor')
    copyfile(DATAFILES + '.gitignore_global', HOME + '.gitignore_global')
    write_gitconfig()


if __name__ == '__main__':
    main()
