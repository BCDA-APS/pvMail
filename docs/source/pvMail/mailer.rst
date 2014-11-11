
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

To test the email sending using the configuration file, use either of the first two lines::

    [joeuser] $ pvMail_mail_test
    [joeuser] $ python ./mailer.py
    
    usage: mailer.py [-h] recipient [recipient ...]
    
    test the email sender from PvMail 3.1.0
    
    positional arguments:
      recipient   email address(es), whitespace-separated if more than one
    
    optional arguments:
      -h, --help  show this help message and exit


    [joeuser] $ python ./mailer.py joeuser@example.com



Source Code Documentation
*************************

.. automodule:: PvMail.mailer
   :members:
   :undoc-members:
   :show-inheritance:
