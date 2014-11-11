
:mod:`ini_config` Module
########################

Application defaults are stored in a file compatible with
:class:`ConfigParser.Config`.  This file is to be stored in
a *secure* location such that it is accessible and readable 
only to the account user (to the extent possible on the
operating system).

.. index:: configuration file; default path

The application configuration settings file *pvMail.ini*
is stored in a directory that depends on the operating system,
as selected by the :attr:`os.name` value, as shown in this table:

===============  =======================================
:attr:`os.name`  path
===============  =======================================
*posix*          *$HOST/.pvMail/pvMail.ini*
*nt*             *%APPDATA%\\\\pvMail\\\\pvMail.ini*
===============  =======================================

The user can override this path by defining the 
**PVMAIL_INI_FILE** environment variable to point
to the desired application configuration settings file.
This definition must be made before the call to 
:class:`PvMail.ini_config.Config`.

.. index:: configuration file; create new file as template

If the application configuration settings file does not exist,
a default one will be created on the first call to 
:class:`PvMail.ini_config.Config`.  This default configuration file 
is only a template and **must be modified** with the user's settings
before email can be sent successfully.

OBJECTIVE
*********

The main reason why an application configuration settings file
is needed is to supply the configuration to send email from 
:mod:`PvMail.pvMail` through an SMTP server.

.. index:: configuration file; default

example application configuration settings (``pvMail.ini``) file:

.. literalinclude:: ../../../src/PvMail/pvMail.ini
    :tab-width: 4
    :linenos:
    :language: guess


OVERVIEW
********

.. index:: configuration file; overview

The :class:`PvMail.ini_config.Config` class reads the entire contents
of the application configuration settings file and copies that to
a dictionary in the class:  *self.agent_db*.  Each of the sections in the file
(such as *SMTP*, *sendmail*) comprise subdictionaries with *key = value* content.
The *header* section contains metadata about the file and is not read.  
The *mailer* section has a key *mail_transfer_agent* that indicates
which mail transport agent [#]_ will be used to send the email.
Current choices available are: *SMTP* or *sendmail* (supported on Linux only).

.. [#] MTA: https://en.wikipedia.org/wiki/Message_transfer_agent

Comments in the application configuration settings file will be ignored
and will not be written back to the file if the file is rewritten
from :meth:`PvMail.ini_config.Config.write`.  A tricky way to preserve
*comment* information is to write the comment as if it were a variable 
to be set inside a section, or possible an entire section.  Such as:

.. index:: SMTP

.. code-block:: guess
    :linenos:
    
    [SMTP]
    server = smtp.mycompany.com
    user = j.o.e.user@mycompany.com
    password = keep_this_private
    hint = comment: use your email as "user" name

or:

.. code-block:: guess
    :linenos:
    
    [comment]
    comment_2 = this is also a comment

It is possible to define other sections, such as to preserve the content
of two different SMTP configurations.  For example:

.. index:: configuration file; example

.. code-block:: guess
    :linenos:

    [header]
    application = pvMail
    written = 2014-11-09 11:47:47.709000
    
    [mailer]
    mail_transfer_agent = SMTP
    
    [SMTP]
    server = smtp.mycompany.com
    user = j.o.e.user
    password = keep_this_private
    port = 465
    connection_security = STARTTLS
    
    [work-SMTP]
    server = smtp.mycompany.com
    user = j.o.e.user
    password = keep_this_private
    port = 465
    connection_security = STARTTLS
    
    [gmail-SMTP]
    server = smtp.googlemail.com
    user = joeuser@gmail.com
    hint = use your gmail account as "user" name
    password = keep_this_private
    port = 587
    authentication = Normal password
    connection_security = STARTTLS
    
    [sendmail]
    user = joeuser

To manage between multiple *SMTP* configurations,
copy the settings from the desired section and replace
the content of the *SMTP* section.  The above example
is configured for the work email SMTP server.

KEYWORDS
********

.. index:: configuration file; keywords

These keywords (exact spelling) are recognized (others are ignored):

:server:      IP name or address of email server
:user:        username accepted by *server* to send an email
:password:    (optional) if required by SMTP server
:port:        port number to be used
:authentication: ``Normal password``
:connection_security: ``STARTTLS`` (SSL/TLS is not available via smtplib)

WRITING THE CONFIGURATION FILE
******************************

Under normal use, the application configuration settings file
is only read.  It is possible to create a new configuration
file (in the default location) by running the 
:mod:`PvMail.ini_config` program directly from the command line.
A new file will be created if none existed.
If the file already exists, it will not be modified.
The only output from this program will be the absolute path name
to the application configuration settings file.

It is possible to edit this file with any text editor.

.. tip::  It is advised to set the permissions on the
    application configuration settings file so that only the
    owner can read the file (owner: read+write).  
    One way to do this on a linux system:

    .. code-block:: guess
        :linenos:
   
        [joeuser] $ /path/to/PvMail/ini_config.py
        /home/joeuser/.pvMail/pvMail.ini
        [joeuser] $ chmod 600 /home/joeuser/.pvMail/pvMail.ini
   
    It is also advisable to restrict access to the parent
    directory of this file (owner: read+write+executable),
    such as this linux command:

    .. code-block:: guess
        :linenos:

        [joeuser] $ chmod 700 /home/joeuser/.pvMail

On Windows, the default file might be:
``C:\\Users\\JoeUser\\AppData\\Roaming\\pvMail\\pvMail.ini``.

It is possible to provide a custom editor (command-line or GUI)
for the application configuration settings file.  For now,
a text editor will suffice.


ALTERNATE CONFIGURATION FILE
****************************

.. index:: PVMAIL_INI_FILE
.. index:: configuration file; environment variable

An alternate application configuration settings file may be
used by setting the **PVMAIL_INI_FILE** environment variable
with the absolute file path to the desired file.

Source Code Documentation
*************************

.. automodule:: PvMail.ini_config
   :members:
   :undoc-members:
   :show-inheritance:
