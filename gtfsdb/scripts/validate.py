import argparse
import sys

from gtfsdb import GTFS


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
    feed = GTFS(args.file)
    is_valid, stdout = feed.validate()
    sys.stdout.write(stdout)
