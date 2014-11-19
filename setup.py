#!/usr/bin/env python

'''packaging for PvMail'''

from setuptools import setup, find_packages
import os
import sys

# make sure our development source is found FIRST!
sys.path.insert(0, os.path.abspath('./src'))
import PvMail

setup(
    name             = 'PvMail',
    version          = PvMail.__version__,
    author           = PvMail.__author__,
    author_email     = PvMail.__author_email__,
    url              = PvMail.__url__,
    license          = PvMail.__license__,
    description      = PvMail.__description__,
    long_description = PvMail.__description__,
    keywords         = PvMail.__keywords__,
    classifiers      = PvMail.__classifiers__,
    platforms        = 'any',
    install_requires = PvMail.__install_requires__,
    packages         = ['PvMail',],
    package_dir      = {'PvMail': 'src/PvMail',},
    package_data     = {'PvMail': ['test.db', 'LICENSE', 'VERSION', 'resources/*'],},
    entry_points     = {
        # create & install console_scripts in <python>/bin
        'console_scripts': PvMail.__console_scripts__,
    },
    zip_safe = False,
)

########### SVN repository information ###################
# $Date: 2014-07-10 13:47:46 -0500 (Thu, 10 Jul 2014) $
# $Author: jemian $
# $Revision: 1580 $
# $URL: https://subversion.xray.aps.anl.gov/bcdaext/pvMail/trunk/setup.py $
# $Id: setup.py 1580 2014-07-10 18:47:46Z jemian $
########### SVN repository information ###################
