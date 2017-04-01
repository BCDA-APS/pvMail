
.. _overview:

Overview
========

There are now several parts to the PvMail support package.

.. index::
   single: executables
   single: pvMail (executable)
   single: pvMail_mail_config_file (executable)
   single: pvMail_mail_test (executable)

==========================  ==========================  =============================================
command                     section                     description
==========================  ==========================  =============================================
`pvMail -g`                 :ref:`GUI`                  runs the graphical user interface
`pvMail`                    :ref:`cli`                  runs the command line interface
`pvMail_mail_config_file`   :ref:`ini_config`           prints the name of the configuration file
`pvMail_mail_test`          :ref:`mailer`               tests the emailer and configuration file
==========================  ==========================  =============================================

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
