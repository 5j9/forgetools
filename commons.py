from pathlib import Path
from subprocess import check_call, CalledProcessError

HOME = str(Path.home())  # py34

try:
    check_call('webservice status', shell=True)
except CalledProcessError:  # webservice is not available in Kubernetes pod
    KUBERNETES = True
else:
    KUBERNETES = False
