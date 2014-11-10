
'''
handle application configuration settings in a .ini file

Application defaults are stored in a file compatible with
:class:`ConfigParser.Config`.  This file is to be stored in
a *secure* location such that it is accessible and readable 
only to the account user (to the extent possible on the
operating system).

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

The main reason why an application configuration settings file
is needed is to supply the configuration to send email
through an SMTP server.

example ``pvMail.ini`` file::

    [header]
    application = pvMail
    written = 2014-11-09 11:47:47.709000
    
    [mailer]
    mail_transfer_agent = SMTP
    
    [SMTP]
    password = keep_this_private
    user = joeuser
    server = smtp.server.org
    
    [sendmail]
    user = joeuser


OVERVIEW

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
to be set inside a section, or possible an entire section.  Such as::
    
    [SMTP]
    server = smtp.mycompany.com
    user = j.o.e.user@mycompany.com
    password = keep_this_private
    hint = comment: use your email as "user" name

or::
    
    [comment]
    comment_2 = this is also a comment

It is possible to define other sections, such as to preserve the content
of two different SMTP configurations.  For example::

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
is configured for Joe's work email SMTP server.

KEYWORDS

These keywords (exact spelling) are recognized (others are ignored):

:server:      IP name or address of email server
:user:        username accepted by *server* to send an email
:password:    (optional) if required by SMTP server
:port:        port number to be used
:authentication: ``Normal password``
:connection_security: ``STARTTLS`` (SSL/TLS is not available via smtplib)

WRITING THE CONFIGURATION FILE

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
   One way to do this on a linux system::
   
       [joeuser] $ /path/to/PvMail/ini_config.py
       /home/joeuser/.pvMail/pvMail.ini
       [joeuser] $ chmod 600 /home/joeuser/.pvMail/pvMail.ini
   
   It is also advisable to restrict access to the parent
   directory of this file (owner: read+write+executable)::

       [joeuser] $ chmod 700 /home/joeuser/.pvMail

On Windows, the default file might be:
``C:\\Users\\JoeUser\\AppData\\Roaming\\pvMail\\pvMail.ini``.

It is possible to provide a custom editor (command-line or GUI)
for the application configuration settings file.  For now,
a text editor will suffice.

ALTERNATE CONFIGURATION FILE

An alternate application configuration settings file may be
used by setting the **PVMAIL_INI_FILE** environment variable
with the absolute file path to the desired file.

'''


import ConfigParser
import datetime
import os
import sys


APPLICATION = 'pvMail'
INI_FILE = 'pvMail.ini'


class Unknown_MTA(Exception): pass
class NoConfigFile(Exception): pass


class Config(object):
    
    def __init__(self):
        if 'PVMAIL_INI_FILE' in os.environ:
            self.ini_file = os.path.abspath(os.environ['PVMAIL_INI_FILE'])
            self.ini_dir = os.path.dirname(self.ini_file)
        else:
            op_sys_config_dir_env = dict(posix='HOME',nt='APPDATA')[os.name]
            dir_prefix = dict(posix='.',nt='')[os.name]
            base_dir = os.environ.get(op_sys_config_dir_env, None) or '.'
            
            self.ini_dir = os.path.join(base_dir, dir_prefix + APPLICATION)
            self.ini_file = os.path.join(self.ini_dir, INI_FILE)

        self.mail_transfer_agent = 'sendmail'
        if sys.platform not in ('linux2'):
            # only use sendmail on linux systems
            self.mail_transfer_agent = 'SMTP'

        self.agent_db = dict(sendmail=dict(user='joeuser'),
                             SMTP=dict(user='joeuser',
                                       password='keep_this_private',
                                       server='smtp.server.org',
                                       port='465',
                                       connection_security='STARTTLS',),)

        try:
            self.read()
        except NoConfigFile:
            self.write()
            self.read()

    def setAgent(self, agent):
        '''choose the mail transfer agent'''
        if agent in self.agent_db:
            self.mail_transfer_agent = agent
        else:
            raise Unknown_MTA(str(agent))
    
    def read(self):
        '''read the configuration file'''
        if not os.path.exists(self.ini_file):
            raise NoConfigFile(str(self.ini_file))

        config = ConfigParser.ConfigParser()
        config.read(self.ini_file)
        
        self.mail_transfer_agent = config.get('mailer', 'mail_transfer_agent')
        
        # https://docs.python.org/2/library/configparser.html#ConfigParser.RawConfigParser
        for section in config.sections():
            if section not in ('header', 'mailer'):
                for option in config.options(section):
                    if section not in self.agent_db:
                        self.agent_db[section] = {}
                    self.agent_db[section][option] = config.get(section, option)
    
    def write(self):
        '''
        (re)write the configuration file
        '''
        config = ConfigParser.ConfigParser()
        config.add_section('header')
        config.set('header', 'application', 'pvMail')
        config.set('header', 'written', str(datetime.datetime.now()))
        
        config.add_section('mailer')
        config.set('mailer', 'mail_transfer_agent', self.mail_transfer_agent)
        
        for section in self.agent_db:
            config.add_section(section)
            for k, v in self.agent_db[section].items():
                config.set(section, k, v)
        
        if not os.path.exists(self.ini_dir):
            os.mkdir(self.ini_dir)
        config.write(open(self.ini_file, 'w'))
    
    def get(self):
        '''
        return the chosen configuration dictionary
        '''
        return self.agent_db[self.mail_transfer_agent]


if __name__ == '__main__':
    con = Config()
    print con.ini_file
    # print len(con.agent_db), ' configuration(s) described'
