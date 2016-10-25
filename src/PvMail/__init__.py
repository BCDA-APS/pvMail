import os
from ._version import git_release


VERSION_FILE = 'VERSION'


def get_pkg_file_path(fname):
    '''return the absolute path to the named file in the package directory'''
    vpath = os.path.abspath(os.path.dirname(__file__))
    vfile = os.path.join(vpath, fname)
    if os.path.exists(vfile):
        RuntimeError('file does not exist: ' + vfile)
    return vfile


def read_resource_file(fname):
    '''return contents of the named file in the package directory'''
    return open(get_pkg_file_path(fname)).read()


__classifiers__ = [
     'Development Status :: 5 - Production/Stable',
     'Environment :: Console',
     'Intended Audience :: Science/Research',
     'License :: Freely Distributable',
     'License :: Public Domain',
     'Programming Language :: Python',
     'Programming Language :: Python :: 2',
     'Programming Language :: Python :: 2.7',
     'Topic :: Scientific/Engineering',
     'Topic :: Utilities',
   ]
__keywords__ = ['EPICS', 'PV', 'email', 'monitor']
#__install_requires__ = ['pyepics>=3.2.3', 'PyQt4>=4.8.5', ]
__install_requires__ = ['pyepics>=3.2.3', ]

__project_name__ = "PvMail"
__description__ = "Watch an EPICS PV. Send email when it changes from 0 to 1."
__version__ = read_resource_file(VERSION_FILE).strip()
__release__ = git_release(__project_name__, __version__)
__author__ = "Pete Jemian"
__full_author_list__ = ["Pete Jemian", "Kurt Goetze"]
__institution__ = "Advanced Photon Source, Argonne National Laboratory"
__author_email__= "jemian@anl.gov"
__url__ = "http://PvMail.readthedocs.org"
__license__ = "(c) 2009-2014, UChicago Argonne, LLC"
__license__ += " (see LICENSE file for details)"

# create & install console_scripts in <python>/bin
__console_scripts__ = [
                       'pvMail = PvMail.pvMail:main', 
                       'pvMail_mail_test = PvMail.mailer:main', 
                       'pvMail_mail_config_file = PvMail.ini_config:main', 
                       ]
