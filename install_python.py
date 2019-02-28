"""Install Python, craete virtual environment, and add ve to .profile.

If run from a kubernetes pod, install the venv in ~/www/python/venv,
otherwise it'll be in ~/pythons/ve{num_ver}.
"""

from argparse import ArgumentParser
from os import mkdir
from shutil import rmtree
from re import search
# Use `check_call` instead of `run` to make the code py34 compatible.
from subprocess import check_call
# wget and requests are not available in containers; use curl or urlopen
from urllib.request import urlopen

from setup_profile import main as create_profle, activate_python_in_profile
from commons import HOME, KUBERNETES


PYTHONS = HOME + '/pythons'


def download_info(num_ver=None) -> tuple:
    """Return (url, dot_ver). Return the latest version info if not num_ver."""
    if num_ver:
        dot_ver = '.'.join(num_ver)
        return (
            'https://www.python.org/ftp/python/{dot_ver}/'
            'Python-{dot_ver}.tar.xz'.format(dot_ver=dot_ver),
            dot_ver,
            num_ver,
        )
    downloads = urlopen('https://www.python.org/downloads/').read()
    m = search(
        rb'href="(?P<url>https://www\.python\.org/ftp/python/'
        rb'(?P<dot_ver>\d+\.\d+\.\d+)/Python-(?P=dot_ver)\.tar\.xz)"',
        downloads,
    )
    return m.group('url').decode(), m.group('dot_ver').decode()


def download_python(num_ver) -> tuple:
    """Download installer, extract it, return the installer dir and num_ver."""
    url, dot_ver = download_info(num_ver)
    python_source_path = PYTHONS + '/Python-' + dot_ver
    zip_path = python_source_path + '.tar.xz'
    with open(zip_path, 'wb') as f:
        f.write(urlopen(url).read())
    check_call('tar xf ' + zip_path, shell=True)
    return python_source_path


def install_python(python_source_path, num_ver) -> None:
    """Install the requested python version."""
    check_call(
        python_source_path + '/configure --prefix=' + PYTHONS + '/' + num_ver,
        shell=True)
    check_call('make', shell=True)
    check_call('make install', shell=True)


def setup_vitual_env(num_ver, requirements=None):
    """Create a virtual env using {num_ver}/bin/python3 in ve{num_ver} dir."""
    python3 = PYTHONS + '/' + num_ver + '/bin/python3'
    if KUBERNETES:
        venv = HOME + '/www/python/venv'
        try:
            # `webservice` must be stopped before deleting the old venv?
            # Note however that we are in webservice already.
            rmtree(venv)
        except FileNotFoundError:
            pass
        check_call(python3 + ' -m venv ' + venv, shell=True)
        return
    ve_path = PYTHONS + '/ve' + num_ver
    check_call(python3 + ' -m venv ' + ve_path, shell=True)
    if requirements:
        # Activate the newly created environment and install packages
        script = """
            . {ve_path}/bin/activate
            pip install -rU {requirements}
        """.format(ve_path=ve_path, requirements=requirements)
        check_call(script, shell=True)


def main(num_ver):
    try:
        mkdir(PYTHONS)
    except FileExistsError:
        pass
    python_source_path = download_python(num_ver)
    install_python(python_source_path, num_ver)
    setup_vitual_env(num_ver)
    create_profle()
    activate_python_in_profile()


if __name__ == '__main__':
    arg_parser = ArgumentParser(
        description='Install Python in `pythons` directory. '
                    'By default install the latest Python version. '
                    'Can be overridden by giving a specific Python version as '
                    'a 3-digit number.')
    arg_parser.add_argument(
        'pyver', nargs='?', help='The desired Python version, e.g. 372.')
    args = arg_parser.parse_args()
    main(args.pyver)
