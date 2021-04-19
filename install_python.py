#!/usr/bin/env python3
"""Install Python, create virtual environment, and add ve to .profile.

If run from a kubernetes pod, install the venv in ~/www/python/venv,
otherwise it'll be in ~/pythons/ve{num_ver}.
"""

from argparse import ArgumentParser
from distutils.version import StrictVersion
from io import BytesIO
from os import mkdir, chdir, getcwd
from shutil import rmtree
from re import search
# Use `check_call` instead of `run` to make the code py34 compatible.
from subprocess import check_call
from tarfile import open as tarfile_open
# wget and requests are not available in containers; use curl or urlopen
from urllib.request import urlopen

from setup_profile import main as create_profile
from commons import HOME, KUBERNETES


PYTHONS = HOME + '/pythons'


def download_info(ver=None) -> tuple:
    """Return the url of the latest version if num_ver is None."""
    if ver:
        main_ver = '.'.join(str(v) for v in StrictVersion(ver).version)
        return ver, (
            'https://www.python.org/ftp/python/{main_ver}/'
            'Python-{full_ver}.tar.xz'.format(main_ver=main_ver, full_ver=ver))
    downloads = urlopen('https://www.python.org/downloads/').read()
    g = search(
        rb'href="(?P<url>https://www\.python\.org/ftp/python/'
        rb'(?P<dot_ver>\d+\.\d+\.\d+)/Python-(?P=dot_ver)\.tar\.xz)"',
        downloads).group
    return g('dot_ver').decode(), g('url').decode()


def download_python(ver) -> (str, str):
    """Download installer, extract it, return the installer dir."""
    ver, url = download_info(ver)
    source_path = PYTHONS + '/Python-' + ver
    print(url)
    tar_file = tarfile_open(fileobj=BytesIO(urlopen(url).read()))
    tar_file.extractall(PYTHONS)
    return ver, source_path


def install_python(source_path: str, ver: str) -> None:
    """Install the requested python version."""
    owd = getcwd()
    chdir(source_path)
    check_call('./configure --prefix=' + PYTHONS + '/' + ver, shell=True)
    check_call('make  --directory=' + source_path, shell=True)
    check_call('make install --directory=' + source_path, shell=True)
    chdir(owd)


def setup_virtual_env(ver, requirements=None):
    """Create a virtual env using {num_ver}/bin/python3 in ve{num_ver} dir."""
    python3 = PYTHONS + '/' + ver + '/bin/python3'
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
    ve_path = PYTHONS + '/ve' + ver
    check_call(python3 + ' -m venv ' + ve_path, shell=True)
    if requirements:
        # Activate the newly created environment and install packages
        script = """
            . {ve_path}/bin/activate
            pip install -rU {requirements}
        """.format(ve_path=ve_path, requirements=requirements)
        check_call(script, shell=True)


def main(ver=None):
    try:
        mkdir(PYTHONS)
    except FileExistsError:
        pass
    ver, source_path = download_python(ver)
    install_python(source_path, ver)
    setup_virtual_env(ver)
    create_profile()


if __name__ == '__main__':
    arg_parser = ArgumentParser(
        description='Install Python in `pythons` directory. '
                    'By default install the latest Python version. '
                    'Can be overridden by giving a specific Python version as '
                    'a 3-digit number.')
    arg_parser.add_argument(
        'pyver', nargs='?',
        help='The desired Python version, e.g. 3.7.2 or 3.9.0b3.')
    args = arg_parser.parse_args()
    main(args.pyver)
