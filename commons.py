from os.path import expanduser
from subprocess import check_call, CalledProcessError, DEVNULL

HOME = expanduser('~')  # py34

try:
    check_call('webservice status', shell=True, stderr=DEVNULL)
except CalledProcessError:
    print('Working in a Kubernetes container.')
    KUBERNETES = True
else:
    KUBERNETES = False
