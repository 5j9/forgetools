#!/usr/bin/env python3
"""Add .profile, .bashrc, and other commons settings."""

from glob import glob
from logging import info

from commons import HOME


EZPROMPT = rb"""
# http://ezprompt.net/ START
function nonzero_return() {
    RETVAL=$?
    [ $RETVAL -ne 0 ] && echo "$RETVAL"
}

# get current branch in git repo
function parse_git_branch() {
    BRANCH=`git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'`
    if [ ! "${BRANCH}" == "" ]
    then
        STAT=`parse_git_dirty`
        echo "[${BRANCH}${STAT}]"
    else
        echo ""
    fi
}

# get current status of git repo
function parse_git_dirty {
    status=`git status 2>&1 | tee`
    dirty=`echo -n "${status}" 2> /dev/null \
    | grep "modified:" &> /dev/null; echo "$?"`
    untracked=`echo -n "${status}" 2> /dev/null \
    | grep "Untracked files" &> /dev/null; echo "$?"`
    ahead=`echo -n "${status}" 2> /dev/null \
    | grep "Your branch is ahead of" &> /dev/null; echo "$?"`
    newfile=`echo -n "${status}" 2> /dev/null \
    | grep "new file:" &> /dev/null; echo "$?"`
    renamed=`echo -n "${status}" 2> /dev/null \
    | grep "renamed:" &> /dev/null; echo "$?"`
    deleted=`echo -n "${status}" 2> /dev/null \
    | grep "deleted:" &> /dev/null; echo "$?"`
    bits=''
    if [ "${renamed}" == "0" ]; then
        bits=">${bits}"
    fi
    if [ "${ahead}" == "0" ]; then
        bits="*${bits}"
    fi
    if [ "${newfile}" == "0" ]; then
        bits="+${bits}"
    fi
    if [ "${untracked}" == "0" ]; then
        bits="?${bits}"
    fi
    if [ "${deleted}" == "0" ]; then
        bits="x${bits}"
    fi
    if [ "${dirty}" == "0" ]; then
        bits="!${bits}"
    fi
    if [ ! "${bits}" == "" ]; then
        echo " ${bits}"
    else
        echo ""
    fi
}

export PS1="\[\e[33m\]\t\[\e[m\]\[\e[37m\]:\
\[\e[m\]\[\e[36m\]\u\[\e[m\]\[\e[37m\]@\[\e[m\]\[\e[36m\]\H\[\e[m\]\[\e[37m\]:\
\[\e[m\]\[\e[32m\]\w\[\e[m\]\[\e[33m\]\`parse_git_branch\
\`\[\e[m\]\[\e[31m\]\`nonzero_return\`\[\e[m\]\[\e[37;40m\]\n\\$\[\e[m\] "
# http://ezprompt.net/ END
"""


def write_profile():
    if glob(HOME + '/pythons/ve*'):
        activate_venv = (
            b'\n# activate venv START'
            b'\n. $(ls -d ~/pythons/ve* | tail -1)/bin/activate'
            b'\n# activate venv END'
            b'\n')
    else:
        info('No ve* was found in ~/pythons. '
             'No venv activation will be added to profile.')
        activate_venv = b''

    with open('/etc/skel/.profile', 'rb') as profile_skel:
        with open(HOME + '/.profile', 'wb') as profile:
            profile.write(
                profile_skel.read()
                + EZPROMPT
                + activate_venv)


def write_bashrc():
    with open('/etc/skel/.bashrc', 'rb') as bashrc_skel:  # T131561
        with open(HOME + '/.bashrc', 'wb') as bashrc:
            bashrc.write(bashrc_skel.read().replace(
                b'HISTCONTROL=ignoredups:ignorespace',
                b'HISTCONTROL=ignoreboth:erasedups', 1))


VIMRC = b'''\
color elflord
syntax on
set wildmenu
set shiftwidth=4
set tabstop=4
'''


def main():
    write_bashrc()
    write_profile()
    with open(HOME + '/.vimrc', 'wb') as f:
        f.write(VIMRC)
    with open(HOME + '/.selected_editor', 'wb') as f:
        f.write(b'# Generated by /usr/bin/select-editor'
                b'\nSELECTED_EDITOR="/usr/bin/vim.basic"')


if __name__ == '__main__':
    main()
