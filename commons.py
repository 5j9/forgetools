from os.path import expanduser
from subprocess import check_call, CalledProcessError, DEVNULL

HOME = expanduser('~')  # py34

try:
    check_call('kubectl get pods', shell=True)
except CalledProcessError:
    KUBERNETES = True
else:
    KUBERNETES = False
