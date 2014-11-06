.. $Id: info.rst 1593 2014-11-06 05:44:30Z jemian $

More Information
################

Functionally based on pvMail UNIX shell script written in 1999.

Summary
*******

Watches an EPICS PV and sends email when it changes from 0 to 1.
PV value can be either integer or float.

.. note::
   When "running", wait for trigger PV to go from 0 to 1.  When that
   happens, fetch mail message from message PV.  Then, send that
   message out to each of the email addresses.  The message 
   content is prioritized for view on a small-screen device such 
   as a pager or a PDA or smartphone.


.. _svn.repo:

subversion repository
*********************

The PvMail project is hosted on the APS XSD subversion server.
You may check out the entire project source code 
:index:`subversion repository`
and development subdirectory::

	svn co  https://subversion.xray.aps.anl.gov/bcdaext/pvMail ./pvMail


project management site
***********************

You may find it easier to view the various code revisions and other aspects
of the project from the project management site.  Links there will direct
you to the resources (documentation, source code) for the PvMail project.

https://subversion.xray.aps.anl.gov/trac/bcdaext/wiki/PvMail


Documentation
*************

.. index:: 
    PvMail project

Documentation for the PvMail project, 
maintained using Sphinx (http://sphinx.pocoo.org),
is available from:

* http://subversion.xray.aps.anl.gov/admin_bcdaext/pvMail


.. index:: TODO items

.. _TODO:

TODO items for a future release
###############################

#. Connect status updates from :class:`pvMail.PvMail()` with status in the GUI
#. Report PV connection problems in an obvious way
#. GUI: display the tail end of the LOG_FILE.
#. GUI: save/restore settings from a named file
#. GUI: manage multiple pvMail.PvMail() objects (starting, stopping, detaching, ...)


Authors
#######

:author: Kurt Goetze (original version)
:author: Pete Jemian (this version)
:organization: AES/BCDA, Advanced Photon Source, Argonne National Laboratory



Requirements
############

:requires: EPICS system (http://www.aps.anl.gov/epics) 
    with at least two process variables (PVs)
    where the "Trigger PV" toggles between values of 0 and 1
    and the "SendMessage PV" contains a string to send as part of 
    the email message.
:requires: PyEpics (http://cars9.uchicago.edu/software/python/pyepics3/)
:requires: Traits (http://code.enthought.com/projects/traits/)
