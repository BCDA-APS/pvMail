
'''
handle application configuration settings in a .ini file

Application defaults are stored in a file compatible with
:class:`ConfigParser.Config`.  This file is to be stored in
a *secure* location such that it is accessible and readable 
only to the account user (to the extent possible on the
operating system).

The application configuration settings file *pvMail.ini*
is stored in a directory that depends on the operating system,
as selected by the :attr:`os.name` value::

===============  =================================
:attr:`os.name`  path
===============  =================================
*posix*          *$HOST/.pvMail/pvMail.ini*
*nt*             *%APPDATA%\\pvMail\\pvMail.ini*
===============  =================================

The user can override this path by defining the 
**PVMAIL_INI_FILE** environment variable to point
to the desired application configuration settings file.
This definition must be made before the call to 
:class:`ini_config.Config`.

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
    from = joeuser
    server = smtp.server.org
    
    [sendmail]
    from = joeuser

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

        self.mta = {
            'sendmail': {
                            'from': 'joeuser'
                         },
            'SMTP': {
                        'from': 'joeuser', 
                        'password': 'keep_this_private', 
                        'server': 'smtp.server.org'
                     },
        }

        try:
            self.read()
        except NoConfigFile:
            self.write()
            self.read()

    def setMTA(self, agent):
        '''choose the mail transfer agent'''
        if agent in self.mta:
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
        
        for section, fields in self.mta.items():
            if config.has_section(section):
                for option in fields.keys():
                    if config.has_option(section, option):
                        fields[option] = config.get(section, option)
    
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
        
        for section in self.mta:
            config.add_section(section)
            for k, v in self.mta['section'].items():
                config.set(section, k, v)
        
        if not os.path.exists(self.ini_dir):
            os.mkdir(self.ini_dir)
        config.write(open(self.ini_file, 'w'))
    
    def get(self):
        '''
        return the chosen configuration dictionary
        '''
        return self.mta[self.mail_transfer_agent]


if __name__ == '__main__':
    con = Config()
    print con.ini_file
    print con
