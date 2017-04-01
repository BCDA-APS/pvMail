import os


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
__author__ = "Pete Jemian"
__full_author_list__ = ["Pete Jemian", "Kurt Goetze"]
__institution__ = "Advanced Photon Source, Argonne National Laboratory"
__author_email__= "jemian@anl.gov"
__url__ = "http://PvMail.readthedocs.org"
__license__ = "(c) 2009-2017, UChicago Argonne, LLC"
__license__ += " (see LICENSE file for details)"

# create & install console_scripts in <python>/bin
__console_scripts__ = [
                       'pvMail = PvMail.cli:main', 
                       'pvMail_mail_test = PvMail.mailer:main', 
                       'pvMail_mail_config_file = PvMail.ini_config:main', 
                       ]


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
