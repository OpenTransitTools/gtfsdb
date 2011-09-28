import argparse
import os
import pkg_resources
import subprocess
import sys
from urllib import urlretrieve


def init_parser():
    parser = argparse.ArgumentParser(
        prog='gtfsdb-validate',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'file',
        help='URL or local directory path to GTFS zip FILE'
    )
    args = parser.parse_args()
    return args


def main():
    args = init_parser()
    (filename, headers) = urlretrieve(args.file)

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
    sys.stdout.write(stdout)
