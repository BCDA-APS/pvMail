PvMail
######

Watches an EPICS PV and sends email when value changes from 0 to 1.  

:author:    Pete R. Jemian
:email:     jemian@anl.gov
:copyright: 2009-2024, UChicago Argonne, LLC
:license:   ANL OPEN SOURCE LICENSE (see *LICENSE*)
:docs:      http://PvMail.readthedocs.io
:git:       https://github.com/prjemian/pvMail
:PyPI:      https://pypi.python.org/pypi/PvMail
:version:   |version|
:release:   |release|
:published: |today|

.. note:: While *PvMail* is the name of the Python package, 
   the executable installed in <python>/bin is called 
   ``pvMail`` using a command line such as::
   
   [user@host,518,~]$ pvMail

PvMail watches (monitor) an EPICS PV and send an email
when the value of that PV changes from 0 to 1.  

..	sidebar:: IMPORTANT:

	PvMail *only* triggers when the trigger_PV makes a transition from 0 to 1.
	
	* It will ignore transitions (in floating-point PVs) to
	  1.0000... that do not come directly from 0.0000...
	  If you wish to watch a PV that presents values other than 0 and 1,
	  then use a calculation PV as the trigger which results in a 
	  transition from 0 to 1.
	* Reset the value of the trigger_PV to 0 to resume watching 
	  for the next triggered event.

The PV being watched (that *triggers* the sending of the email)
can be any EPICS record type or field
that results in a value of 0 (zero) that changes to 1 (one).  This 
includes these EPICS records (and possibly more):
*ai*, *ao*,  *bi*, *bo*, *calcout*, *scalcout*, *swait*, ...

When an event causes an email to be triggered, PvMail will retrieve
the value of another PV that is the first part of the message to be 
sent.  Additional metadata will be appended to the message.

.. note::
	Email is sent using either a call to a configured SMTP server or
	the ``sendmail`` program on the native OS.
	The sendmail protocol is only supported on Linux systems
	that provide a ``sendmail`` program.
	The SMTP protocol is more general but requires valid credentials
	on the SMTP server and the credentials must be stored
	in a local configuration file.

PvMail provides either a command-line interface or a graphical user
interface.  Both are accessed from the same command, using different
command-line options.  The command-line version is intended to run 
as a background program, it has no user interaction but logs all its
output into a log file.  The GUI version provides a screen to edit
each of the parameters before the background process is started.  
It also provides buttons to start and stop the background process.

Overview of Contents
####################

.. toctree::
   :maxdepth: 2
   
   contents
   glossary
   dependencies
