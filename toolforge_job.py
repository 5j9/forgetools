from subprocess import check_call
from pathlib import Path


def prepare(job_path: Path):
    from commons import FORGETOOLS

    bootstrap = Path(FORGETOOLS + 'toolforge_job_bootstrap.sh')
    bootstrap.chmod(0o770)

    # create venv
    check_call([
        'toolforge-jobs',
        'run',
        'bootstrap',  # name
        '--command',
        f'cd {job_path.parent} && {bootstrap}',
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
