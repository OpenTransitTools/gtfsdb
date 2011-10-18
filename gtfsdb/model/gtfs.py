import os
import pkg_resources
import subprocess
import sys
import tempfile
from urllib import urlretrieve
import zipfile


class GTFS(object):

    def __init__(self, file):
        self.file = file
        (self.local_file, headers) = urlretrieve(file)

    def validate(self):
        """Run transitfeed.feedvalidator"""
        path = os.path.join(
            pkg_resources.get_distribution('transitfeed').egg_info,
            'scripts/feedvalidator.py'
        )

        stdout, stderr = subprocess.Popen(
            [sys.executable, path, '--output=CONSOLE', self.local_file],
            stdout=subprocess.PIPE
        ).communicate()

        is_valid = True
        for line in str(stdout).splitlines():
            if line.startswith('ERROR'):
                is_valid = 'errors' not in line.lower()
                continue
        return is_valid, stdout

    def unzip(self, path=None):
        """Unzip GTFS files from URL/directory to path."""
        path = path if path else tempfile.mkdtemp()
        with zipfile.ZipFile(self.local_file) as zip:
            zip.extractall(path)
        return path
