#!/usr/bin/env python

'''
===================================
pvMail: just the GUI
===================================

Build the Graphical User Interface for PvMail
using the Traits library from the
Enthought Python Distribution. 

Copyright (c) 2011, UChicago Argonne, LLC
'''


import traits.api
import traitsui.api
import pvMail

__svnid__ = "$Id: traits_gui.py 1594 2014-11-06 06:05:39Z jemian $"


class ActionHandler(traitsui.api.Handler):
    '''implements controls for PvMail GUI application'''
    
    _gui = None
    
    def _findGui(self, uinfo):
        '''return the PvMail_GUI object'''
        if self._gui is None:
            self._gui = uinfo.object
    
    def do_run(self, uinfo):
        '''
        start watching the EPICS triggerPV
        
        :param obj uinfo: UIInfo object passed from the Action()
        
        Traits Handler method that responds to a Traits Action()
        '''
        self._findGui(uinfo)
        if not self._gui.running:
            self._gui.SetStatus('<Run> button pressed')
            self._gui.running = True
            self._gui.pvm = pvMail.PvMail()
            self._gui.pvm.triggerPV = self._gui.triggerPV
            self._gui.pvm.messagePV = self._gui.messagePV
            addresses = list(self._gui.recipients)
            self._gui.pvm.recipients = addresses
            self._gui.pvm.do_start()
        else:
            self._gui.SetStatus('Already running')
    
    def do_stop(self, uinfo):
        '''
        stop watching the EPICS triggerPV
        
        :param obj uinfo: UIInfo object passed from the Action()
        
        Traits Handler method that responds to a Traits Action()
        '''
        self._findGui(uinfo)
        if self._gui.running:
            self._gui.SetStatus('<Stop> button pressed')
            self._gui.running = False
            self._gui.pvm.do_stop()
            self._gui.pvm = None
        else:
            self._gui.SetStatus('Not running')


def run_GUI(traits_object):
    '''run the traits GUI'''
    traits_object.configure_traits()


class PvMail_GUI(traits.api.HasTraits):
    '''
    GUI used for pvMail,
    declared using Enthought's Traits module
    '''
    triggerPV = traits.api.String(
                 desc="EPICS PV name on which to trigger an email",
                 label="trigger PV",)
    messagePV = traits.api.String(
                 desc="EPICS string PV name with short message text",
                 label="message PV",)
    recipients = traits.api.List(
                 trait=traits.api.String,
                 value=["", "",],
                 desc="email addresses of message recipients",
                 label="email address(es)",)
    actionRun = traitsui.api.Action(name = "Run",
                       desc = "start watching for trigger PV to go from 0 to 1",
                       action = "do_run")
    actionStop = traitsui.api.Action(name = "Stop",
                        desc = "stop watching trigger PV",
                        action = "do_stop")

    status_label = traits.api.String('status:')
    status_msg = traits.api.String
    running = traits.api.Bool(False)
    pvm = traits.api.Generic(None)
    
    view = traitsui.api.View('triggerPV', 
                'messagePV', 
                'recipients', 
                traitsui.api.Item('running', style = 'readonly', label = 'Running?', ),
                title="PvMail GUI",
                width=500,
                height=300,
                buttons = [actionRun, actionStop],
                handler = ActionHandler(),
                statusbar = [
                   traitsui.api.StatusItem(name = 'status_label', width = 80),
                   traitsui.api.StatusItem(name = 'status_msg', width = 0.5),
                ],
                resizable=True)

    def __init__(self, 
                 triggerPV = "", 
                 messagePV = "", 
                 recipients = ["", ""], 
                 log_file = "",
                 **kwtraits):
        '''make this class callable from pvMail application'''
        super(PvMail_GUI, self).__init__(**kwtraits)
        self.triggerPV = triggerPV
        self.messagePV = messagePV
        self.recipients = recipients
        self.SetStatus('log file = ' + log_file)

    def SetStatus(self, msg):
        '''put text in the status box'''
        self.status_msg = msg


if __name__ == '__main__':
    print "Do not call this module directly.  Use pvMail.py instead"
