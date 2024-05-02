from functools import lru_cache
from operator import itemgetter
from os.path import dirname, expanduser
from platform import node
from subprocess import CalledProcessError, CompletedProcess, run
from sys import stderr, stdout

HOME = expanduser('~') + '/'
KUBERNETES = node() == 'interactive'
FORGETOOLS = dirname(__file__) + '/'
DATAFILES = FORGETOOLS + 'datafiles/'


def verbose_run(*args: str) -> CompletedProcess:
    """Print args, capture stdout and stderr, then print them back.

    Note: This function does not print stdout and stderr in real-time. It
    first waits for the process to finish.
    """
    print(args)
    cp = run(args, capture_output=True, check=True)
    stdout.write(cp.stdout.decode())
    stderr.write(cp.stderr.decode())
    return cp


@lru_cache(None)
def cached_check_output(*args) -> str:
    return verbose_run(*args).stdout.decode()


def max_version(str_version_pairs) -> str:
    type_version_pairs = [
        (t, tuple(map(int, (v.split('.'))))) for (t, v) in str_version_pairs
    ]
    return max(type_version_pairs, key=itemgetter(1))[0]


def assert_webservice_control(script_name):
    if KUBERNETES:
        raise RuntimeError(
            'You need to run ' + script_name + ' from the bastion host'
            ' so that it can control the webservice.'
        )


def get_pod_name():
    try:
        pod_name = verbose_run(('kubectl', 'get', 'pod', '-o', 'name')).stdout
    except CalledProcessError:
        return None
    return pod_name[4:].splitlines()[-1].decode()
