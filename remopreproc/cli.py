"""Console script for remopreproc."""
import argparse
import sys
import os

import logging

import fire

from . import remopreproc


logger = logging.getLogger(__name__)


def main_bak():
    """Console script for remopreproc."""
    init()
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "remopreproc.cli.main")
    return 0


def run():
    pass



class Preprocessor():

    @staticmethod
    def init(root=None):
        """Initialize working directory.

        Parameters
        ----------
        root: str
            Root directory.
        """
        logger.info('running init')
        remopreproc.init_workspace(root)

    def input():
        """search for input data
        """

def main():
    fire.Fire(Preprocessor(), name='intorg')

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
