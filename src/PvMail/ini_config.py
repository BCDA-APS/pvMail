#!/usr/bin/env python

'''
handle application configuration settings in a .ini file

Copyright (c) 2014, UChicago Argonne, LLC.  See LICENSE file.

To identify the configuration file (and create if it does not exist already)::

    [joeuser] $ pvMail_mail_config_file
    /home/joeuser/.pvMail/pvMail.ini

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

        u1 = os.environ.get('LOGNAME', None)
        u2 = os.environ.get('USERNAME', None)
        u3 = 'joeuser'
        username = u1 or u2 or u3

        self.agent_db = dict(sendmail=dict(user=username),
                             SMTP=dict(user=username,
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


def main():
    con = Config()
    print con.ini_file
    # print len(con.agent_db), ' configuration(s) described'


if __name__ == '__main__':
    main()
