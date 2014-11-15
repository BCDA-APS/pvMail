#!/usr/bin/env python

'''Watch an EPICS PV. Send email when it changes from 0 to 1'''
# see file LICENSE included with this distribution. 
# docs: http://PvMail.readthedocs.org


import argparse
import datetime
import epics
import logging
import os
import socket
import sys
import threading
import time
import traceback

import ini_config
import mailer


LOG_FILE = "pvMail-%d.log" % os.getpid()
RETRY_INTERVAL_S = 0.2
CHECKPOINT_INTERVAL_S = 5 * 60.0

gui_object = None


class PvMail(threading.Thread):
    '''
    Watch an EPICS PV (using PyEpics interface) and send an email
    when the PV changes from 0 to 1.
    '''
    
    def __init__(self, config=None):
        self.trigger = False
        self.message = "default message"
        self.subject = "pvMail.py"
        self.triggerPV = ""
        self.messagePV = ""
        self.recipients = []
        self.old_value = None
        self.monitoredPVs = []
        self.ca_timestamp = None
        self.config = config
    
    def basicChecks(self):
        '''
        check for valid inputs, 
        raise exceptions as discovered, 
        otherwise no return result
        '''
        if len(self.recipients) == 0:
            msg = "need at least one email address for list of recipients"
            raise RuntimeWarning, msg
        fmt = "could not connect to %s PV: %s"
        parts = {'message': self.messagePV, 
                 'trigger': self.triggerPV}
        for name, pv in parts.items():
            if len(pv) == 0:
                raise RuntimeWarning, "no name for the %s PV" % name
            if pv not in self.monitoredPVs:
                if self.testConnect(pv, timeout=0.5) is False:
                    raise RuntimeWarning, fmt % (name, pv)
        
    def testConnect(self, pvname, timeout=5.0):
        '''
        create PV, 
        wait for connection, 
        return connection state (True | False)
        
        adapted from PyEpics __createPV() method
        '''
        logger("test connect with %s" % pvname)
        retry_interval_s = 0.0001
        start_time = time.time()
        thispv = epics.PV(pvname)
        thispv.connect()
        while not thispv.connected:
            time.sleep(retry_interval_s)
            epics.ca.poll()
            if time.time()-start_time > timeout:
                break
        return thispv.connected
    
    def do_start(self):
        '''start watching for triggers'''
        logger("do_start")
        if len(self.monitoredPVs) == 0:
            self.basicChecks()
            logger("passed basicChecks(), starting monitors")
            epics.camonitor(self.messagePV, callback=self.receiveMessageMonitor)
            epics.camonitor(self.triggerPV, callback=self.receiveTriggerMonitor)
            self.old_value = epics.caget(self.triggerPV)
            self.message = epics.caget(self.messagePV)
            # What happens if either self.messagePV or self.triggerPV
            # are changed after self.do_start() is called?
            # Keep a local list of what was initiated.
            self.monitoredPVs.append(self.messagePV)
            self.monitoredPVs.append(self.triggerPV)
    
    def do_stop(self):
        '''stop watching for triggers'''
        logger("do_stop")
        for pv in self.monitoredPVs:
            epics.camonitor_clear(pv)   # no problem if pv was not monitored
        self.monitoredPVs = []
    
    def do_restart(self):
        '''restart watching for triggers'''
        self.do_stop()
        self.do_start()
    
    def receiveMessageMonitor(self, value, **kw):
        '''respond to EPICS CA monitors on message PV'''
        logger("%s = %s" % (self.messagePV, value))
        self.message = value
    
    def receiveTriggerMonitor(self, value, **kw):
        '''respond to EPICS CA monitors on trigger PV'''
        logger("%s = %s" % (self.triggerPV, value))
        # print self.old_value, type(self.old_value), value, type(value)
        if self.old_value == 0:
            if value == 1:
                self.ca_timestamp = None
                # Cannot use this definition:
                #     self.trigger = (value == 1)
                # since the trigger PV just may transition back
                # to zero before SendMessage() runs.
                self.trigger = True
                pv = epics.ca._PVMonitors[self.triggerPV]
                self.ca_timestamp = pv.timestamp
                # self.ca_timestamp = epics.ca.get_timestamp(pv.chid)
                SendMessage(self, self.config)
        self.old_value = value


class SendMessage(threading.Thread):
    '''
    initiate sending the message in a separate thread
    
    :param obj pvm: instance of PvMail object on which to report
    '''

    def __init__(self, pvm, agent_db):
        logger("SendMessage")
        pvm.trigger = False        # triggered event received

        email_agent_dict = dict(sendmail=mailer.sendMail_sendmail, SMTP=mailer.sendMail_SMTP)
        email_agent = email_agent_dict[agent_db.mail_transfer_agent]

        try:
            pvm.basicChecks()
            
            pvm.subject = "pvMail.py: " + pvm.triggerPV
            
            msg = ''        # start with a new message
            msg += "\n\n"
            msg += pvm.message
            msg += "\n\n"
            msg += 'user: %s\n' % os.environ['LOGNAME']
            msg += 'host: %s\n' % socket.gethostname()
            msg += 'date: %s (UNIX, not PV)\n' % datetime.datetime.now()
            try:
                msg += 'CA_timestamp: %d\n' % pvm.ca_timestamp
            except:
                msg += 'CA_timestamp: not available\n'
            msg += 'program: %s\n' % sys.argv[0]
            msg += 'PID: %d\n' % os.getpid()
            msg += 'trigger PV: %s\n' % pvm.triggerPV
            msg += 'message PV: %s\n' % pvm.messagePV
            msg += 'recipients: %s\n' % ", ".join(pvm.recipients)
            pvm.message = msg

            email_agent(pvm.subject, msg, pvm.recipients, agent_db.get(), logger=logger)
            logger("message(s) sent")
        except:
            err_msg = traceback.format_exc()
            final_msg = "pvm.subject = %s\nmsg = %s\ntraceback: %s" % (pvm.subject, str(msg), err_msg)
            logger(final_msg)


def logger(message):
    '''
    log a message or report from PvMail

    :param str message: words to be logged
    '''
    now = datetime.datetime.now()
    name = os.path.basename(sys.argv[0])
    text = "(%s,%s) %s" % (name, now, message)
    logging.info(text)


def cli(results, config=None):
    '''
    command-line interface to the PvMail class
    
    :param obj results: default parameters from argparse, see main()
    :param obj config: email configuration from ini_config.Config()
    '''
    logging_interval = min(60*60, max(5.0, results.logging_interval))
    sleep_duration = min(5.0, max(0.0001, results.sleep_duration))

    pvm = PvMail(config)
    pvm.triggerPV = results.trigger_PV
    pvm.messagePV = results.message_PV
    pvm.recipients = results.email_addresses.strip().split(",")
    checkpoint_time = time.time()
    pvm.do_start()
    while True:     # endless loop, kill with ^C or equal
        if time.time() > checkpoint_time:
            checkpoint_time += logging_interval
            logger("checkpoint")
        if pvm.trigger:
            SendMessage(pvm, config)
            logger('triggered received, sending email')
        time.sleep(sleep_duration)
    pvm.do_stop()        # this will never be called


def gui(results, config=None):
    '''
    graphical user interface to the PvMail class
    
    :param obj results: default parameters from argparse, see main()
    :param obj config: email configuration from ini_config.Config()
    '''
    
    import qt_gui
    qt_gui.main(
        results.trigger_PV, 
        results.message_PV, 
        results.email_addresses.strip().split(","),
        logger=logger,
        logfile=results.log_file,
        config=config,
    )


def main():
    '''parse command-line arguments and choose which interface to use'''
    vpath = os.path.abspath(os.path.dirname(__file__))
    vfile = os.path.join(vpath, 'VERSION')
    version = open(vfile).read().strip()

    doc = 'v' + version + ', ' + __doc__.strip()
    parser = argparse.ArgumentParser(description=doc)

    # positional arguments
    # not required if GUI option is selected
    parser.add_argument('trigger_PV', action='store', nargs='?',
                        help="EPICS trigger PV name", default="")

    parser.add_argument('message_PV', action='store', nargs='?',
                        help="EPICS message PV name", default="")

    parser.add_argument('email_addresses', action='store', nargs='?',
                        help="email address(es), comma-separated if more than one", 
                        default="")

    # optional arguments
    parser.add_argument('-l', action='store', dest='log_file',
                        help="for logging program progress and comments", 
                        default=LOG_FILE)

    parser.add_argument('-i', action='store', dest='logging_interval', 
                        type=float,
                        help="checkpoint reporting interval (s) in log file", 
                        default=CHECKPOINT_INTERVAL_S)

    parser.add_argument('-r', action='store', dest='sleep_duration', 
                        type=float,
                        help="sleep duration (s) in main event loop", 
                        default=RETRY_INTERVAL_S)

    parser.add_argument('-g', '--gui', action='store_true', default=False,
                        dest='interface',
                        help='Use the graphical rather than command-line interface')

    parser.add_argument('-v', '--version', action='version', version=version)

    results = parser.parse_args()

    addresses = results.email_addresses.strip().split(",")
    interface = {False: 'command-line', True: 'GUI'}[results.interface]
    
    agent_db = ini_config.Config()

    logging.basicConfig(filename=results.log_file, level=logging.INFO)
    logger("#"*60)
    logger("startup")
    logger("trigger PV       = " + results.trigger_PV)
    logger("message PV       = " + results.message_PV)
    logger("email list       = " + str(addresses) )
    logger("log file         = " + results.log_file)
    logger("logging interval = " + str( results.logging_interval ) )
    logger("sleep duration   = " + str( results.sleep_duration ) )
    logger("interface        = " + interface)
    user = os.environ.get('LOGNAME', None) or os.environ.get('USERNAME', None)
    logger("user             = " + user)
    logger("host             = " + socket.gethostname() )
    logger("program          = " + sys.argv[0] )
    logger("PID              = " + str(os.getpid()) )
    logger("PyEpics version  = " + str(epics.__version__) )
    logger("config file      = " + agent_db.ini_file )
    
    if results.interface is False:
        # When the GUI is not selected, 
        # ensure the positional arguments are given
        tests = [
                     len(results.trigger_PV),
                     len(results.message_PV),
                     len(" ".join(addresses)),
                ]
        if 0 in tests:
            parser.print_usage()
            sys.exit()
    
    # call the interface
    {False: cli, True: gui}[results.interface](results)     


if __name__ == '__main__':
    main()
