.. $Id: index.rst 1574 2014-07-10 17:28:14Z jemian $

PvMail: combined CLI and GUI
############################

http://PvMail.readthedocs.org

.. note:: While *PvMail* is the name of the Python package, 
   the executable installed in <python>/bin is called 
   ``pvMail`` using a command line such as::
   
   [user@host,518,~]$ pvMail

PvMail was built to watch (monitor) an EPICS PV and send an email
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
	Email is sent using a call to the ``sendmail`` program on the native OS.
	This almost certainly precludes its use on Windows systems.
	The GUI or command-line versions will operate but likely no email
	is sent.  Also, the host computer must allow and be configured for
	sending email to the intended recipients.

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


*This documentation was built:* |today| 
