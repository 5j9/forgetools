from subprocess import check_call
from pathlib import Path


def prepare(job_path: Path):
    job_dir = job_path.parent

    # remove previous logs
    (job_dir / 'bootstrap.err').unlink(missing_ok=True)
    (job_dir / 'bootstrap.out').unlink(missing_ok=True)

    # create venv
    check_call([
        'toolforge-jobs',
        'run',
        'bootstrap',  # name
        '--command',
        f'cd {job_dir} '
        '&& python3 -m venv pyvenv'
        '&& . pyvenv/bin/activate'
        '&& pip install -U pip'
        '&& pip install -Ur requirements.txt',
        '--image', 'tf-python39',
        '--wait',
    ])


def schedule(job_path: Path, daily=False):
    from time import localtime

    t = localtime()

    job_name = job_path.name[:-3].replace('_', '-')

    # remove previous logs
    job_dir = job_path.parent
    (job_dir / f'{job_name}.err').unlink(missing_ok=True)
    (job_dir / f'{job_name}.out').unlink(missing_ok=True)
    # delete any job with this name
    check_call(['toolforge-jobs', 'delete', job_name])

    command = f'cd {job_path.parent} '
    if (job_dir / 'pyvenv').exists():
        command += '&& . pyvenv/bin/activate '
    command += f'&& python3 {job_path} '

    args = [
        'toolforge-jobs',
        'run', job_name,
        '--command', command,
        '--image', 'tf-python39',
    ]
    if daily:
        args += ['--schedule', f'{t.tm_min + 1} {t.tm_hour} * * *']

    check_call(args)
