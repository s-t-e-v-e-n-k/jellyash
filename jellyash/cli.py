import argparse

from . import __version__


def argparse_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"jellyash {__version__}")
    return parser
