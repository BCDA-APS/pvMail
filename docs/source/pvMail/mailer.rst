
.. _mailer:


:mod:`mailer` Module
####################

.. index:: mail agents

========  ================================================================
agent     description
========  ================================================================
sendmail  (linux-only) uses either */usr/lib/sendmail* or */usr/bin/mail*
SMTP      uses smtplib [#]_
========  ================================================================

.. [#] *smtplib*: https://docs.python.org/2/library/smtplib.html


TESTING THE CONFIGURATION
*************************

.. index:: email; testing the configuration
.. index:: configuration file; testing

It is possible to test the email sending using the configuration file.
(Alternatively, the GUI has a *File* menu item to send a test email.)
First, the help message for the command::

    $ pvMail_mail_test --help
    
    usage: pvMail_mail_test [-h] recipient [recipient ...]
    
    test the email sender from PvMail 3.1.0
    
    positional arguments:
      recipient   email address(es), whitespace-separated if more than one
    
    optional arguments:
      -h, --help  show this help message and exit


To test the email sending using the configuration file::

    $ python ./mailer.py joeuser@example.com

An email message is sent from *joeuser* to  joeuser@example.com:

.. code-block:: text
   :linenos:

   To: joeuser@example.com
   Subject: PvMail mailer test message: sendmail
   Date: Tue, 16 Aug 2024 13:17:31 -0600 (CDT)
   From: joeuser@example.com

   This is a test of the PvMail mailer, v4.0.0
   For more help, see: https://prjemian.github.io/pvMail


Source Code Documentation
*************************

.. automodule:: PvMail.mailer
   :members:
   :undoc-members:
   :show-inheritance:
