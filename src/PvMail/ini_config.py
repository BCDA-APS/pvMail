
'''
handle application configuration settings in a .ini file
'''


import ConfigParser
import datetime
import os
import sys


APPLICATION = 'pvMail'
INI_FILE = 'pvMail.rc'
MTA_STRUCTURE = dict(sendmail=['from',], SMTP=['from','password','server'])


class Unknown_MTA(Exception): pass
class NoConfigFile(Exception): pass


class Config(object):
    
    def __init__(self):
        op_sys_config_dir_env = dict(posix='HOME',nt='APPDATA')[os.name]
        dir_prefix = dict(posix='.',nt='')[os.name]
        self.ini_dir = os.path.join(os.environ.get(op_sys_config_dir_env, None) or '.', dir_prefix + APPLICATION)
        self.ini_file = os.path.join(self.ini_dir, dir_prefix + INI_FILE)

        self.mail_transfer_agent = 'sendmail'
        if sys.platform not in ('linux2'):
            self.mail_transfer_agent = 'SMTP'

        self.sendmail = {'from': 'joeuser'}
        self.SMTP = {'from': 'joeuser', 'password': 'keep_this_private', 'server': 'smtp.server.org'}

    def setMTA(self, agent):
        '''choose the mail transfer agent'''
        if agent in MTA_STRUCTURE:
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
        
        for section, fields in MTA_STRUCTURE.items():
            if config.has_section(section):
                node = self.__getattribute__(section)
                for option in fields:
                    if config.has_option(section, option):
                        node[option] = config.get(section, option)
    
    def write(self):
        '''
        (re)write the configuration file
        
        example ``pvMail.rc`` file::

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
        config = ConfigParser.ConfigParser()
        config.add_section('header')
        config.set('header', 'application', 'pvMail')
        config.set('header', 'written', str(datetime.datetime.now()))
        
        config.add_section('mailer')
        config.set('mailer', 'mail_transfer_agent', self.mail_transfer_agent)
        
        for section in MTA_STRUCTURE:
            config.add_section(section)
            for k, v in self.__getattribute__(section).items():
                config.set(section, k, v)
        
        if not os.path.exists(self.ini_dir):
            os.mkdir(self.ini_dir)
        config.write(open(self.ini_file, 'w'))


if __name__ == '__main__':
    con = Config()
    print con.ini_file
    try:
        con.read()
    except NoConfigFile, exc:
        con.write()
        con.read()

    print con
