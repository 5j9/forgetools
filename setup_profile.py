"""Install Python."""


from shutil import copyfile

from commons import HOME, KUBERNETES


EZPROMPT = r"""\
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


def ezprompt_profile():
    """Add ezprompt to .profile."""
    with open(str(HOME + '/.profile'), 'a') as f:  # py34 compatibility
        f.write(EZPROMPT)


def activate_python_in_profile():
    if KUBERNETES:
        with open(HOME + '/.profile', 'a') as f:
            f.write(
                '\n'
                '# activate venv START\n'
                'webservice --backend=kubernetes python shell'
                '. {HOME}/www/python/venv/bin/activate\n'
                '# activate venv END\n'.format(HOME=HOME)
            )
        return
    with open(HOME + '/.profile', 'a') as f:
        f.write(
            '\n'
            '# activate venv START\n'
            '. $(ls -d ~/pythons/ve* | tail -1)/bin/activate\n'
            '# activate venv END\n'
        )


def main():
    # convert path to str for py34 compatibility
    copyfile('/etc/skel/.bashrc', HOME + '/.bashrc')  # T131561
    copyfile('/etc/skel/.profile', HOME + '/.profile')
    ezprompt_profile()


if __name__ == '__main__':
    main()
