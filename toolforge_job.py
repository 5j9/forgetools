from subprocess import check_call
from path import Path


def prepare(job_path: Path):
    from commons import FORGETOOLS

    # create venv
    check_call([
        'toolforge-jobs',
        'run',
        'bootstrap',  # name
        '--command',
        f'cd {job_path.parent} && {FORGETOOLS}/toolforge_job_boostrap.sh',
        '--image', 'tf-python39',
        '--wait',
    ])


def schedule(job_path: Path, daily=False):
    from time import localtime

    t = localtime()

    args = [
        'toolforge-jobs',
        'run', job_path.name[:-3].replace('_', '-'),
        '--command', f'python3 {job_path}',
        '--image', 'tf-python39',
    ]
    if daily:
        args += ['--schedule', f'{t.tm_min + 1} {t.tm_hour} * * *']

    check_call(args)
