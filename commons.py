from os.path import expanduser
from subprocess import check_output, CalledProcessError

HOME = expanduser('~')  # py34

try:
    POD_NAME = check_output('kubectl get pod -o name', shell=True)
except CalledProcessError:
    KUBERNETES = True
    POD_NAME = None
else:
    KUBERNETES = False
    POD_NAME = POD_NAME[4:].rstrip().decode()
