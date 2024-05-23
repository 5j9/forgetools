from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os import execv
from pathlib import Path
from sys import argv, executable

from commons import FORGETOOLS, verbose_run


def update():
    verbose_run('git', '-C', FORGETOOLS, 'reset', '--hard')
    out = verbose_run('git', '-C', FORGETOOLS, 'pull').stdout
    if b'files changed,' in out:
        print('restarting the current process')
        # about the second executable: stackoverflow.com/questions/61728339
        argv.insert(1, '--no-git-pull')
        execv(executable, [executable] + argv)
        # raise RuntimeError('This line should never be run!')


def get_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '--no-git-pull',
        action='store_true',
        help='do not perform git pull for forgetools',
    )

    sub_parsers = parser.add_subparsers(dest='sub_command')

    python = sub_parsers.add_parser('python', help='install Python')
    python.add_argument(
        '--pyver', help='The desired Python version, e.g. `3.12.0`.'
    )

    sub_parsers.add_parser(
        'dotfiles',
        help='Create ~/.profile, .gitconfig and other user settings.',
    )

    webservice = sub_parsers.add_parser(
        'webservice',
        help='webservice-related functions',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    # webservice.add_argument(
    #   '-t', '--type', help='Set webservice type. Only python is supported.')
    # webservice.add_argument(
    #   '-b', '--backend', help='webservice backend', default='kubernetes')
    webservice.add_argument(
        'install_or_update',
        help='install or update webservice.',
        choices=['update', 'u', 'install', 'i'],
    )

    job = sub_parsers.add_parser(
        'job', help='prepare and/or run a python toolforge-job'
    )
    job.add_argument(
        'file',
        help=(
            'python file path '
            '(its directory should also contain requirements.txt)'
        ),
    )
    job.add_argument('--prepare', help='create venv', action='store_true')
    job.add_argument(
        '--daily', help='schedule the job for daily run', action='store_true'
    )
    job.add_argument(
        '--once',
        help='schedule the job for immediate one-time run',
        action='store_true',
    )

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
    elif sub_command == 'dotfiles':
        import dotfiles

        dotfiles.main()
    elif sub_command == 'webservice':
        if args.install_or_update in {'i', 'install'}:
            from install_python_webservice import main as install_webservice

            install_webservice()
        else:  # install_or_update is 'u' or 'update'.
            from update_python_webservice import main as update_webservice

            update_webservice()
    elif sub_command == 'job':
        from toolforge_job import prepare, schedule

        job_path = Path(args.file)

        if args.prepare:
            prepare(job_path)

        if args.daily:
            schedule(job_path, daily=True)
        elif args.once:
            schedule(job_path, daily=False)
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == '__main__':
    main()
