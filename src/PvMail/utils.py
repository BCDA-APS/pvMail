"""
utility routines for PvMail

Copyright (c) 2009-2024, UChicago Argonne, LLC.  See LICENSE file.
"""

import pathlib

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def get_pkg_file_path(fname):
    """return the absolute path to the named file in the package directory"""
    vpath = pathlib.Path(__file__).parent
    vfile = vpath / fname
    if not vfile.exists():
        raise FileNotFoundError(f"file does not exist: {vfile}")
    return vfile


def read_resource_file(fname):
    """return contents of the named file in the package directory"""
    return open(get_pkg_file_path(fname)).read()
