
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

version control repository
**************************

The PvMail project is hosted on GitHub (https://github.com/BCDA-APS/pvMail).
You may check out the entire project source code 
:index:`github repository`::

	git clone  https://github.com/BCDA-APS/pvMail

GitHub has additional advice for alternative methods.


Documentation
*************

.. index:: 
    PvMail project

Documentation for the PvMail project, 
maintained using Sphinx (http://www.sphinx-doc.org),
is available from:

* https://prjemian.github.io/pvMail


.. index:: TODO items

.. _TODO:

Items for future releases
##############################

:see: https://github.com/BCDA-APS/pvMail/issues


Authors
#######

:author: Kurt Goetze (original version)
:author: Pete Jemian (this version)
:organization: BCDA, Advanced Photon Source, Argonne National Laboratory



Requirements
############

Requires these Python :ref:`packages <install.dependencies>` and an `EPICS
<https://www.aps.anl.gov/epics>`_ system with at least two process variables
(PVs) where the "Trigger PV" toggles between values of 0 and 1 and the
"SendMessage PV" contains a string to send as part of the email message.