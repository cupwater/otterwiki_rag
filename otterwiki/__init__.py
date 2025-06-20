#!/usr/bin/env python
# vim: set et ts=8 sts=4 sw=4 ai:

import sys
from typing import Union

from .version import __version__

__all__ = ["fatal_error"]


def fatal_error(msg: Union[str, Exception]):
    print("\nError: {}\n".format(msg), file=sys.stderr)
    sys.exit(1)
