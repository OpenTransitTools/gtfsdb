import os
import pkg_resources
import subprocess
import sys
from urllib import urlretrieve


class GTFS(object):

    def __init__(self, file):
        self.file = file

    def validate(self):
        (filename, headers) = urlretrieve(self.file)

        path = os.path.join(
            pkg_resources.get_distribution('transitfeed').egg_info,
            'scripts/feedvalidator.py'
        )

        stdout, stderr = subprocess.Popen(
            [sys.executable, path, '--output=CONSOLE', filename],
            stdout=subprocess.PIPE
        ).communicate()

        is_valid = True
        for line in str(stdout).splitlines():
            if line.startswith('ERROR'):
                is_valid = 'errors' not in line.lower()
                continue
        return is_valid, stdout
