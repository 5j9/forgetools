from pathlib import Path
from re import findall

from commons import cached_check_output, max_version, verbose_run


def newest_image(lang='python') -> str:
    """Use `toolforge-jobs images` to return newest image for the given lang.

    The output of `toolforge-jobs images` is a table:

    ```
    Short name    Container image URL
    ------------  ----------------------------------------------------------------------
    [...]
    python3.11    docker-registry.tools.wmflabs.org/toolforge-python311-sssd-base:latest
    python3.9     docker-registry.tools.wmflabs.org/toolforge-python39-sssd-base:latest
    [...]
    ```
    """
    images = cached_check_output('toolforge-jobs', 'images')
    iamge_version_pairs = findall(rf'\b({lang}([\d.]+))\b', images)
    return max_version(iamge_version_pairs)


def prepare(job_path: Path):
    job_dir = job_path.parent

    # remove previous logs
    (job_dir / 'bootstrap.err').unlink(missing_ok=True)
    (job_dir / 'bootstrap.out').unlink(missing_ok=True)

    # create venv
    verbose_run(
        'toolforge-jobs',
        'run',
        'bootstrap',  # name
        '--command',
        f'cd {job_dir} '
        '&& python3 -m venv pyvenv'
        '&& . pyvenv/bin/activate'
        '&& pip install -U pip'
        '&& pip install -Ur requirements.txt',
        '--image',
        newest_image(),
        '--wait',
    )


def schedule(job_path: Path, daily=False):
    from time import localtime

    t = localtime()

    job_name = job_path.name[:-3].replace('_', '-')

    # remove previous logs
    job_dir = job_path.parent
    (job_dir / f'{job_name}.err').unlink(missing_ok=True)
    (job_dir / f'{job_name}.out').unlink(missing_ok=True)
    # delete any job with this name
    verbose_run('toolforge-jobs', 'delete', job_name)

    command = f'cd {job_path.parent} '
    if (job_dir / 'pyvenv').exists():
        command += '&& . pyvenv/bin/activate '
    command += f'&& python {job_path} '

    args = [
        'toolforge-jobs',
        'run',
        job_name,
        '--command',
        command,
        '--image',
        newest_image(),
    ]
    if daily:
        args += ['--schedule', f'{t.tm_min + 1} {t.tm_hour} * * *']

    verbose_run(*args)
