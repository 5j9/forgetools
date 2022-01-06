from os.path import expanduser, dirname
from platform import node
from subprocess import check_output, CalledProcessError

HOME = expanduser('~')  # py34
KUBERNETES = node() == 'interactive'
DATAFILES = dirname(__file__) + 'datafiles/'


def assert_webservice_control(script_name):
    if KUBERNETES:
        raise RuntimeError(
            'You need to run ' + script_name + ' from the bastion host'
            ' so that it can control the webservice.'
        )


def get_pod_name():
    try:
        pod_name = check_output(['kubectl', 'get', 'pod', '-o', 'name'])
    except CalledProcessError:
        return None
    return pod_name[4:].splitlines()[-1].decode()
