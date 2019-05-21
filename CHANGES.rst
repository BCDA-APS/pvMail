..
  This file describes user-visible changes between the versions.


.. index:: change history

.. _changes:

Change History
##############

:3.3.0: *planned: 2019-09-01*

	* milestone: https://github.com/prjemian/pvMail/milestone/1

:3.2.9: *-tba-*

    * `#20 <https://github.com/prjemian/pvMail/issues/20>`_
      apply recommendations from LGTM.com automated code review

:3.2.8: *2017-04-01*

    * `#15 <https://github.com/prjemian/pvMail/issues/14>`_
      [bcdaqwidgets](https://pypi.python.org/pypi/PvMail) now on PyPI
    * `#14 <https://github.com/prjemian/pvMail/issues/14>`_
      pick up GitHub tag versions with [versioneer](https://github.com/warner/python-versioneer)
    * `#12 <https://github.com/prjemian/pvMail/issues/12>`_
      build for RTD in a conda environment

:v3.2.6 (2015.04.13): bcdaqwidgets has replaced PySide with PyQt4, do that here
:v3.2.5 (2014.12.05): make URL be an active (QPushButton) link in About box
:v3.2.4 (2014-11-24): Log status updates from :class:`pvMail.PvMail()` in the GUI
:v3.2.3 (2014-11-19): email sent in separate thread, PV content shown in GUI when connected
:v3.2.0 (2014-11-18): refactor GUI to Qt4 framework
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
:2005.09.07 kag: Initial alpha version.  Needs testing.
    