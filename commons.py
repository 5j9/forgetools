from os.path import expanduser
from subprocess import check_call, CalledProcessError

HOME = expanduser('~')  # py34

try:
    check_call('webservice status', shell=True)
except CalledProcessError:  # webservice is not available in Kubernetes pod
    KUBERNETES = True
else:
    KUBERNETES = False
