
import os


def _get_version():
    vpath = os.path.abspath(os.path.dirname(__file__))
    vfile = os.path.join(vpath, 'VERSION')
    version = open(vfile).read().strip()
    return version


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
__install_requires__ = ['pyepics', 'traits', 'traitsui', ]

__project_name__ = "PvMail"
__description__ = "Watch an EPICS PV. Send email when it changes from 0 to 1."
__version__ = _get_version()
__author__ = "Pete Jemian"
__institution__ = "Advanced Photon Source, Argonne National Laboratory"
__author_email__= "jemian@anl.gov"
__url__ = "http://subversion.xray.aps.anl.gov/admin_bcdaext/pvMail"
__license__ = "(c) 2009-2014, UChicago Argonne, LLC"
__license__ += " (see LICENSE file for details)"

# create & install console_scripts in <python>/bin
__console_scripts__ = ['pvMail = PvMail.pvMail:main', ]
