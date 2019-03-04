from os.path import expanduser
from subprocess import check_output, CalledProcessError

HOME = expanduser('~')  # py34

try:
    POD_NAME = check_output(['kubectl', 'get', 'pod', '-o', 'name'])
except CalledProcessError:
    KUBERNETES = True
    POD_NAME = None
else:
    KUBERNETES = False
    POD_NAME = POD_NAME[4:].rstrip().decode()


def assert_webservice_control(script_name):
    if KUBERNETES:
        raise RuntimeError(
            'You need to run ' + script_name + ' from the bastion host'
            ' so that it can control the webservice.'
        )
