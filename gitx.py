import argparse
import sys
from pathlib import Path

from lib import repo


def parse_args(argv):
    argparser = argparse.ArgumentParser(description="VCS experiment.")
    argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
    argsubparsers.required = True

    argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
    argsp.add_argument("path", metavar="directory", nargs="?", default=".", help="Where to create the repository.")
    return argparser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])

    if args.command == "init":
        repo.repo_create(Path(args.path))
