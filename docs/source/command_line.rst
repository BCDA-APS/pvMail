.. _cli:

pvMail: command-line interface
==============================

Basically, you use it either as a background daemon or as a GUI. Call
it with a ``-g`` or ``--gui`` command line option to force the GUI to run,
otherwise you get the background daemon.  Either way, it makes a log
file (based on PID number) with any program output.

.. index:: example

background daemon::

	pvMail triggerPV messagePV user1@email.domain,user2@host.server &

GUI::

	pvMail triggerPV messagePV user1@email.domain,user2@host.server -g &

.. tip::
   Since *PvMail* creates a log file (by default in the current working directory),
   be sure you start the program from a directory to which you have write
   access or specify the absolute path to the log file as a command line
   argument::

     pvMail -l /path/to/log_file.txt triggerPV messagePV user1@email.domain &


Starting PvMail
+++++++++++++++


Starting PvMail from the command-line
-------------------------------------

.. index:: example

PvMail is started from the command line::

	$ pvMail pvMail:trigger pvMail:message jemian

.. index:: log file

No program output is printed to the screen.  Instead, the output is directed
to a log file.  Here is an example::

	INFO:root:(pvMail.py,2011-11-27 19:03:23.072392) ############################################################
	INFO:root:(pvMail.py,2011-11-27 19:03:23.072826) startup
	INFO:root:(pvMail.py,2011-11-27 19:03:23.072897) trigger PV       = pvMail:trigger
	INFO:root:(pvMail.py,2011-11-27 19:03:23.073323) message PV       = pvMail:message
	INFO:root:(pvMail.py,2011-11-27 19:03:23.073401) email list       = ['jemian']
	INFO:root:(pvMail.py,2011-11-27 19:03:23.073463) log file         = logfile.log
	INFO:root:(pvMail.py,2011-11-27 19:03:23.073667) logging interval = 5.0
	INFO:root:(pvMail.py,2011-11-27 19:03:23.073735) sleep duration   = 0.2
	INFO:root:(pvMail.py,2011-11-27 19:03:23.073795) interface        = command-line
	INFO:root:(pvMail.py,2011-11-27 19:03:23.073855) user             = jemian
	INFO:root:(pvMail.py,2011-11-27 19:03:23.073952) host             = como-ubuntu64
	INFO:root:(pvMail.py,2011-11-27 19:03:23.074053) program          = ./pvMail.py
	INFO:root:(pvMail.py,2011-11-27 19:03:23.074124) PID              = 8903
	INFO:root:(pvMail.py,2011-11-27 19:03:23.074196) do_start
	INFO:root:(pvMail.py,2011-11-27 19:03:23.074280) test connect with pvMail:message
	INFO:root:(pvMail.py,2011-11-27 19:03:23.445334) test connect with pvMail:trigger
	INFO:root:(pvMail.py,2011-11-27 19:03:23.468540) passed basicChecks(), starting monitors
	INFO:root:(pvMail.py,2011-11-27 19:03:23.477917) checkpoint
	INFO:root:(pvMail.py,2011-11-27 19:03:27.373142) pvMail:trigger = 1
	INFO:root:(pvMail.py,2011-11-27 19:03:27.373908) SendMessage
	INFO:root:(pvMail.py,2011-11-27 19:03:27.374199) sending email to: jemian
	INFO:root:(pvMail.py,2011-11-27 19:03:27.374716) mail -s "pvMail.py: pvMail:trigger" jemian < /tmp/pvmail_message.txt
	INFO:root:(pvMail.py,2011-11-27 19:03:27.538022) message(s) sent
	INFO:root:(pvMail.py,2011-11-27 19:03:28.092551) checkpoint
	INFO:root:(pvMail.py,2011-11-27 19:03:29.440516) pvMail:trigger = 0

The program starts, reports its configurations, and connects with the
EPICS PVs, and then goes into a background mode.  A checkpoint (command-line
option ``-i``) is reported periodically.  The default is 5 seconds.  This may
be changed to 10 minutes or longer for production use, but is always
specified in seconds.

Observe that, in the above example, the trigger PV changed from 0 to 1 at
19:03:27.373142 (and back to 0 at 19:03:29.440516).
The change at ~19:03:27 triggered PvMail to send an email as configured.
For now, the code writes the text of the email to a temporary file
(command-line option ``-m``, default is "/tmp/pvmail_message.txt").
In this example, the message reads::

	pvMail default message

	user: jemian
	host: como-ubuntu64
	date: 2011-11-27 19:03:27.374135
	program: ./pvMail.py
	PID: 8903
	trigger PV: pvMail:trigger
	message PV: pvMail:message
	recipients: jemian

The message shows up in the mail browser (here my Linux ``mail`` program)::

	jemian@como-ubuntu64$ mail
	Mail version 8.1.2 01/15/2001.  Type ? for help.
	"/var/mail/jemian": 3 messages 3 new
	>N  1 jemian@como-ubunt  Sun Nov 27 18:27   25/730   pvMail.py: pvMail:trigger
	 N  2 jemian@como-ubunt  Sun Nov 27 18:58   25/730   pvMail.py: pvMail:trigger
	 N  3 jemian@como-ubunt  Sun Nov 27 19:03   25/730   pvMail.py: pvMail:trigger

.. index:: email

The full message, as seen in the mail browser is::

	Message 3:
	From jemian@como-ubuntu64 Sun Nov 27 19:03:27 2011
	Envelope-to: jemian@como-ubuntu64
	Delivery-date: Sun, 27 Nov 2011 19:03:27 -0600
	To: jemian@como-ubuntu64
	Subject: pvMail.py: pvMail:trigger
	From: Pete R Jemian <jemian@como-ubuntu64>
	Date: Sun, 27 Nov 2011 19:03:27 -0600

	pvMail default message

	user: jemian
	host: como-ubuntu64
	date: 2011-11-27 19:03:27.374135
	program: ./pvMail.py
	PID: 8903
	trigger PV: pvMail:trigger
	message PV: pvMail:message
	recipients: jemian

Starting PvMail from the command-line at the APS
------------------------------------------------

At the APS, Enthought Python Distribution is installed on the /APSshare partition
available to all beam lines.

.. index:: example

Here is a command to run PvMail and get the help message::

	/APSshare/epd/rh5-x86_64/bin/pvMail -h

or the 32-bit version::

	/APSshare/epd/rh5-x86/bin/pvMail -h

..	note::
	Support at APS for both RHEL5 and RHEL6 use the same Enthought Python Distribution.



command-line parameters
+++++++++++++++++++++++

.. index:: command-line

.. index:: usage

usage
-----

.. index:: example

When PvMail is started from the command line with no additional parameters::

	$ pvMail

	usage: pvMail [-h] [-l LOG_FILE] [-i LOGGING_INTERVAL]
	                 [-r SLEEP_DURATION] [-g] [-v]
	                 trigger_PV message_PV email_addresses
	pvMail: error: too few arguments

This is the *usage* message.
It tells us we must supply three :index:`positional arguments`:
``trigger_PV message_PV email_addresses``.

positional argument: ``trigger_PV``
-------------------------------------

EPICS process variable name to watch using a CA monitor.
When ``trigger_PV`` makes a transition from 0 (zero) to 1 (one),
then get the string from the ``message_PV`` and send an email
to all of the ``email_addresses`` on the list.

positional argument: ``message_PV``
-------------------------------------

EPICS process variable name pointing to a (short) message that will
be used as the first part of the email message to be sent.

.. Can this be a waveform of char acting as a string?  Probably but test it.

positional argument: ``email_addresses``
----------------------------------------

List of email addresses, separated by commas if more than one.  For example,
``user1@email.domain,user2@host.server`` will send one email to
``user1@email.domain`` and another email to ``user2@host.server``.

.. index:: email to a pager at APS

..	note::
	At Argonne, it is possible to send email to a pager using
	the email address ``####@pager.anl.gov`` and the pager number.
	Be sure not to use a preceding ``4-`` or the email will not be
	deliverable.

.. index:: optional arguments

option: ``--version``  or  ``-v``
-----------------------------------

The current version of the program can always be printed using the
``-v`` or ``--version``.  With this option, the program prints
the version number and then quits.

::

	$ pvMail --version
	3.0-663

option: ``--help``  or  ``-h``
-----------------------------------

It may be easier to review the short help instructions for command-line options::

	$ ./pvMail --help
	usage: pvMail [-h] [-l LOG_FILE] [-i LOGGING_INTERVAL]
	                 [-r SLEEP_DURATION] [-g] [-v]
	                 trigger_PV message_PV email_addresses

	Watch an EPICS PV. Send email when it changes from 0 to 1.

	positional arguments:
	  trigger_PV           EPICS trigger PV name
	  message_PV           EPICS message PV name
	  email_addresses      email address(es), comma-separated if more than one

	optional arguments:
	  -h, --help           show this help message and exit
	  -l LOG_FILE          for logging program progress and comments
	  -i LOGGING_INTERVAL  checkpoint reporting interval (s) in log file
	  -r SLEEP_DURATION    sleep duration (s) in main event loop
	  -g, --gui            Use the graphical rather than command-line interface
	  -v, --version        show program's version number and exit

option: ``--gui``  or ``-g``
-----------------------------------

This command line option is used to start the GUI (see :ref:`GUI`).
If either GUI option is used, then the positional arguments
(``triggerPV messagePV email@address``) are optional.

option: ``-l LOG_FILE``
-----------------------------------

Both the command-line and GUI versions of PvMail log all
program output to a log file.  If a LOG_FILE is not specified on the command
line, the default file will be ``pvMail-PID.log`` in the current directory
where *PID* is the process identifier of the running ``pvMail`` program.

..	note::
	If the LOG_FILE already exists, new information will be appended.
	It is up to the account owner to delete a LOG_FILE when it is no
	longer useful.

The PID number is useful when you wish to end a program that is running
as a background daemon.  The UNIX/Linux command is::

	kill PID

option: ``-i LOGGING_INTERVAL``
-----------------------------------

:units: seconds

When a program runs in the background, waiting for occasional activity,
there is often some concern that the program is actually prepared to act
when needed.  To offset this concern, PvMail will report a
*checkpoint* message periodically (every LOGGING_INTERVAL seconds,
default is every 5 minutes) to the LOG_FILE.  The program ensures that
LOGGING_INTERVAL is no shorter than 5 seconds or longer than 1 hour.

option: ``-r SLEEP_DURATION``
-----------------------------------

:units: seconds

For operation as a background daemon process, the command-line version
must check periodically for new EPICS CA events, using a call to
:meth:`epics.ca.poll()`.  In between calls, the application is told to sleep
for SLEEP_DURATION seconds.  The default SLEEP_DURATION is 0.2 seconds and
is limited to values between 0.1 ms and 5 s.


