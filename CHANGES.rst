..
  This file describes user-visible changes between the versions.


.. index:: change history

.. _changes:

Change History
##############

:v3.2.0 (2014-11-?): refactor GUI to PyQt4 framework
:v3.1.0 (2014-11-11): add optional SMTP email support and configuration file
:v3.0.5 (2014-11-06): move project to https://github.com/prjemian/pvMail
:v3.0.4 (2014-11-05): make docs build at http://pvmail.readthedocs.org
:v3.0.3 (2014-07-10):
    * Resolve CA monitor problems
    * update packaging to contemporary practice
    * handle change in PyEpics internal cache of monitored PVs

:v3.0.2 (2013-10-18): Simplify startup of ``pvMail`` by installing 
   launcher as ``<python>/bin/pvMail`` as part of ``setup.py`` tasks

:v3.0.1 (2012-09-07):
    * new home for documentation
    * check for existence of sendmail program before trying

:v3.0 (2012-06-19): release of new code

:2011-11-23 prj: complete rewrite using PyEpics and combined GUI (Traits) and CLI
:2009-12-02 prj: converted to use wxPython (no Tkinter or Pmw)
:2005.09.07 kag:   Initial alpha version.  Needs testing.
    