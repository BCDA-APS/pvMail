
.. _overview:

Overview
========

PvMail watches (monitor) an EPICS PV and send an email
when the value of that PV changes from 0 to 1.  

..	sidebar:: IMPORTANT:

	PvMail *only* triggers when the trigger_PV makes a transition from 0 to 1.
	
	* It ignores transitions (in floating-point PVs) to
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

Details
-------

There are now several parts to the PvMail support package.

.. index::
   single: executables
   single: pvMail (executable)
   single: pvMail_mail_config_file (executable)
   single: pvMail_mail_test (executable)

============================  ==========================  =============================================
command                       section                     description
============================  ==========================  =============================================
``pvMail -g``                 :ref:`GUI`                  runs the graphical user interface
``pvMail``                    :ref:`cli`                  runs the command line interface
``pvMail_mail_config_file``   :ref:`ini_config`           prints the name of the configuration file
``pvMail_mail_test``          :ref:`mailer`               tests the emailer and configuration file
============================  ==========================  =============================================

One-time steps
**************

Before you can run **pvMail**, you need to configure it.

**First**,  run::

   pvMail_mail_config_file

if you have not
already created a configuration file.  This command will create the file (if it
does not exist) and then print its name to the console.

Edit this file for the particulars of how you want to send your email.
Refer to the :ref:`ini_config` section for additional details about
the configuration file.

**Next**,  run::

   pvMail_mail_test joeuser@example.com
 
(use your own email address, not Joe's) 
to test that an email can be sent using your configuration.
Refer to the :ref:`mailer` section for additional details about
sending email.  Run this tool any time you suspect that you cannot
send email.

Routine usage
*************

You can run **pvMail** either in command-line mode (foreground or background)
or in GUI mode.  Follow the links above for more details about each.
