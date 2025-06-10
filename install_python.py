#!/usr/bin/env python3
"""Install Python, create virtual environment, and add ve to .profile.

If run from a kubernetes pod, install the venv in ~/www/python/venv,
otherwise it'll be in ~/pythons/ve{num_ver}.
"""

import gzip
from argparse import ArgumentParser
from io import BytesIO
from os import chdir, getcwd, mkdir
from re import search
from shutil import rmtree
from subprocess import check_call
from tarfile import open as tarfile_open

# wget and requests are not available in containers; use curl or urlopen
from urllib.request import urlopen

from commons import HOME, KUBERNETES

PYTHONS = HOME + 'pythons'


def download_info(version: str | None = None) -> tuple[str, str]:
    """Return the url of the latest version if `ver` is None."""
    if version:
        return version, (
            f'https://www.python.org/ftp/python/{version}/'
            f'Python-{version}.tar.xz'
        )
    response = urlopen('https://www.python.org/downloads/')
    downloads = response.read()
    if response.info().get('Content-Encoding') == 'gzip':
        downloads = gzip.decompress(downloads)

    g = search(
        rb'href="(?P<url>https://www\.python\.org/ftp/python/'
        rb'(?P<version>\d+\.\d+\.\d+)/Python-(?P=version)\.tar\.xz)"',
        downloads,
    ).group  # type: ignore
    return g('version').decode(), g('url').decode()


def download_python(version: str | None) -> tuple[str, str]:
    """Download installer, extract it, return the installer dir."""
    version, url = download_info(version)
    source_path = PYTHONS + '/Python-' + version
    print(f'{url=}')
    tar_file = tarfile_open(fileobj=BytesIO(urlopen(url).read()))
    tar_file.extractall(PYTHONS)
    return version, source_path


def install_python(source_path: str, version: str) -> None:
    """Install the requested python version."""
    owd = getcwd()
    chdir(source_path)
    check_call('./configure --prefix=' + PYTHONS + '/' + version, shell=True)
    check_call('make  --directory=' + source_path, shell=True)
    check_call('make install --directory=' + source_path, shell=True)
    chdir(owd)


def setup_virtual_env(version, requirements=None):
    """Create a virtual env using {num_ver}/bin/python3 in ve{num_ver} dir."""
    python3 = PYTHONS + '/' + version + '/bin/python3'
    if KUBERNETES:
        venv = HOME + 'www/python/venv'
        try:
            # `webservice` must be stopped before deleting the old venv?
            # Note however that we are in webservice already.
            rmtree(venv)
        except FileNotFoundError:
            pass
        check_call(python3 + ' -m venv ' + venv, shell=True)
        return
    ve_path = PYTHONS + '/ve' + version
    check_call(python3 + ' -m venv ' + ve_path, shell=True)
    if requirements:
        # Activate the newly created environment and install packages
        script = f"""
            . {ve_path}/bin/activate
            pip install -rU {requirements}
        """
        check_call(script, shell=True)


def main(version: str | None = None):
    try:
        mkdir(PYTHONS)
    except FileExistsError:
        pass
    version, source_path = download_python(version)
    install_python(source_path, version)
    setup_virtual_env(version)
    import dotfiles

    dotfiles.main()


if __name__ == '__main__':
    arg_parser = ArgumentParser(
        description='Install Python in `pythons` directory. '
        'By default install the latest Python version. '
        'Can be overridden by giving a specific Python version.'
    )
    arg_parser.add_argument(
        'pyver',
        nargs='?',
        help='The desired Python version, e.g. 3.7.2 or 3.9.0b3.',
    )
    args = arg_parser.parse_args()
    main(args.pyver)
