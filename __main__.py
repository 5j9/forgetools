from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os import execv
from sys import executable, argv
from subprocess import check_output

from commons import FORGETOOLS


def update():
    stdout = check_output(('git', '-C', FORGETOOLS, 'pull'))
    if b'files changed,' in stdout:
        print('restarting the current process')
        # about the second executable: stackoverflow.com/questions/61728339
        execv(executable, [executable] + argv + ['--no-git-pull'])
        raise RuntimeError('This line should never be run!')


def get_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '--no-git-pull', action='store_true',
        help='do not perform git pull for forgetools')
    sub_parsers = parser.add_subparsers(dest='sub_command')
    python = sub_parsers.add_parser(
        'python', help='install Python')
    python.add_argument(
        '--pyver', help='The desired Python version, e.g. 372.')
    sub_parsers.add_parser(
        'profile', help='Create ~/.profile and other user settings.')
    webservice = sub_parsers.add_parser(
        'webservice', help='webservice-related functions',
        formatter_class=ArgumentDefaultsHelpFormatter)
    # webservice.add_argument(
    #   '-t', '--type', help='Set webservice type. Only python is supported.')
    # webservice.add_argument(
    #   '-b', '--backend', help='webservice backend', default='kubernetes')
    webservice.add_argument(
        'install_or_update',
        help='install or update webservice.',
        choices=['update', 'u', 'install', 'i'])
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    if not args.no_git_pull:
        update()
    sub_command = args.sub_command
    if sub_command == 'python':
        from install_python import main as install_python
        install_python(args.pyver)
    elif sub_command == 'profile':
        from setup_profile import main as setup_profile
        setup_profile()
    elif sub_command == 'webservice':
        if args.install_or_update in {'i', 'install'}:
            from install_python_webservice import main as install_webservice
            install_webservice()
        else:  # install_or_update is 'u' or 'update'.
            from update_python_webservice import main as update_webservice
            update_webservice()
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == '__main__':
    main()
