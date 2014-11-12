#!/usr/bin/env python

'''
===================================
pvMail: just the GUI
===================================

Build the Graphical User Interface for PvMail using PyQt4. 

Copyright (c) 2014, UChicago Argonne, LLC
'''


import traits.api
import traitsui.api
import pvMail


def run(traits_object):
    '''
    run the GUI
    
    This is an abstraction that allows to change the GUI backend from this file.
    '''
    raise NotImplementedYet


class PvMail_GUI(object):
    '''
    GUI used for pvMail,
    declared using Enthought's Traits module
    '''
    #triggerPV = traits.api.String(
    #		  desc="EPICS PV name on which to trigger an email",
    #		  label="trigger PV",)
    #messagePV = traits.api.String(
    #		  desc="EPICS string PV name with short message text",
    #		  label="message PV",)
    #recipients = traits.api.List(
    #		  trait=traits.api.String,
    #		  value=["", "",],
    #		  desc="email addresses of message recipients",
    #		  label="email address(es)",)
    #actionRun = traitsui.api.Action(name = "Run",
    #			desc = "start watching for trigger PV to go from 0 to 1",
    #			action = "do_run")
    #actionStop = traitsui.api.Action(name = "Stop",
    #			 desc = "stop watching trigger PV",
    #			 action = "do_stop")

    def __init__(self, 
                 triggerPV = "", 
                 messagePV = "", 
                 recipients = ["", ""], 
                 log_file = "",
                 **kw):
        '''make this class callable from pvMail application'''
        super(PvMail_GUI, self).__init__(**kw)
    raise NotImplementedYet


if __name__ == '__main__':
    print "Do not call this module directly.  Use pvMail.py instead"
