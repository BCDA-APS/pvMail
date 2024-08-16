"""Configuration of PvMail package."""

PROJECT = "PvMail"
DESCRIPTION = "Watch an EPICS PV. Send email when it changes from 0 to 1."
DOCS_URL = "https://BCDA-APS.github.io/pvMail"
AUTHORS = [
    "Pete Jemian",
    "Kurt Goetze",
]
COPYRIGHT = "Copyright (c) 2009-2024, UChicago Argonne, LLC."
LICENSE = "LICENSE"

try:
    from setuptools_scm import get_version

    __version__ = get_version(root="../..", relative_to=__file__)
    del get_version
except (LookupError, ModuleNotFoundError):
    from importlib.metadata import version

    __version__ = version(PROJECT)
