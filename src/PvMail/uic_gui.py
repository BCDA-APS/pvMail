#!/usr/bin/env python

'''
===================================
pvMail: just the GUI
===================================

Run the Graphical User Interface for PvMail using PyQt4 from a .ui file with the uic subpackage. 

Copyright (c) 2014, UChicago Argonne, LLC
'''

# TODO: Connect status updates from :class:`pvMail.PvMail()` with status in the GUI
# TODO: GUI: display the tail end of the LOG_FILE.


# http://pyqt.sourceforge.net/Docs/PyQt4/designer.html


from PyQt4 import QtCore, QtGui, uic

import datetime
import os
import sys

import PvMail
import pvMail
import ini_config
import bcdaqwidgets


WINDOW_TITLE = 'pvMail'
RESOURCE_PATH = 'resources'
MAIN_UI_FILE = os.path.join(RESOURCE_PATH, 'gui.ui')
ABOUT_UI_FILE = os.path.join(RESOURCE_PATH, 'about.ui')


class PvMail_GUI(object):
    '''
    GUI used for pvMail, based on PyQt4
    '''
    
    def __init__(self, ui_file=None, logger=None, logfile=None, config=None, *args, **kw):
        '''make this class callable from pvMail application'''
        self.ui = uic.loadUi(PvMail.get_pkg_file_path(ui_file or MAIN_UI_FILE))
        # PySide way: 
        # http://stackoverflow.com/questions/7144313/loading-qtdesigners-ui-files-in-pyside/18293756#18293756

        self.ui.history.clear()
        self.logger = logger
        
        self.setStatus('starting')

        self.email_address_model = EmailListModel([], self.ui)
        self.logfile = logfile
        self.config = config or ini_config.Config()
        self.pvmail = None
        self.watching = False
        
        # menu item handlers
        self.ui.actionSend_test_email.triggered.connect(self.doSendTestMessage)
        self.ui.actionE_xit.triggered.connect(self.doClose)
        self.ui.actionAbout_pvMail.triggered.connect(self.doAbout)
        
        # button handlers
        self.ui.w_btn_run.released.connect(self.doRun)
        self.ui.w_btn_stop.released.connect(self.doStop)

        # the list of email recipients
        self.ui.emails.setModel(self.email_address_model)
        
        # adjust dynamic labels
        self.ui.config_file_name.setText(config.ini_file)
        self.ui.log_file_name.setText(str(logfile))
        self.ui.w_running_stopped.setText('stopped')
        
        # replace standard widget with EPICS-aware widget
        # FIXME: need to replace widget in layout also
        # self.ui.messagePV_text = bcdaqwidgets.BcdaQLineEdit()
#         self.ui.l_pv_message = QtGui.QLabel('message')
#         self.ui.pv_message = bcdaqwidgets.BcdaQLineEdit()
#         self.ui.pv_message.setToolTip('PV not connected, no text available')
#         self.ui.formLayout.addRow(self.ui.l_pv_message, self.ui.pv_message)

        self.setStatus('ready')
    
    def show(self):
        self.ui.show()

    def doAbout(self, *args, **kw):
        about = uic.loadUi(PvMail.get_pkg_file_path(ABOUT_UI_FILE))
        about.title.setText(PvMail.__project_name__ + '  ' + PvMail.__version__)
        about.description.setText(PvMail.__description__)
        about.authors.setText(', '.join(PvMail.__full_author_list__))
        about.copyright.setText(PvMail.__license__)
        # TODO: can this URL be an active link?
        about.url.setText(PvMail.__url__)
        # TODO: provide control to show the license

        # feed the status message
        msg = 'About: '
        msg += PvMail.__project_name__ 
        msg += ', v' + PvMail.__version__
        msg += ', PID=' + str(os.getpid())
        self.setStatus(msg)
        about.show()
        about.exec_()

    def doClose(self, *args, **kw):
        self.setStatus('application exit requested')
        self.ui.close()
    
    def doRun(self, *args, **kw):
        self.setStatus('<Run> button pressed')
        if self.watching:
            self.setStatus('already watching')
        else:
            self.pvmail = pvMail.PvMail(self.config)
            msg_pv = str(self.getMessagePV())
            trig_pv = str(self.getTriggerPV())

            # report connection failure and abort
            for key, pv in dict(message=msg_pv, trigger=trig_pv).items():
                if self.pvmail.testConnect(pv, timeout=pvMail.CONNECTION_TEST_TIMEOUT) is False:
                    msg = "could not connect to %s PV: %s" % (key, pv)
                    self.setStatus(msg)
                    self.pvmail = None
                    return
            
            self.pvmail.triggerPV = trig_pv
            self.pvmail.messagePV = msg_pv
            
            # TODO: when running, show triggerPV value
#             self.ui.pv_message.ca_connect(msg_pv)
#             self.ui.pv_message.setText('<connecting...>')
            # TODO: onConnect: self.ui.pv_message needs to pull info from PV and set widget text
            addresses = self.getEmailList_Stripped()
            self.pvmail.recipients = addresses
            self.setStatus('trigger PV: ' + self.pvmail.triggerPV)
            self.setStatus('message PV: ' + self.pvmail.messagePV)
            self.setStatus('recipients: ' + '  '.join(addresses))
            # TODO: need to set status when email is sent
            # TODO: when running, show/edit messagePV content
            try:
                self.pvmail.do_start()
            except Exception, exc:
                self.setStatus(str(exc))
                return
            self.ui.w_running_stopped.setText('running')
            sty = bcdaqwidgets.StyleSheet(self.ui.w_running_stopped)
            sty.updateStyleSheet({
                'background-color': 'lightgreen',
                'qproperty-alignment': 'AlignCenter',
            })
            self.setStatus('CA monitors started')
            self.watching = True
    
    def doStop(self, *args, **kw):
        if not self.watching:
            self.setStatus('not watching now')
        else:
            self.setStatus('<Stop> button pressed')
            self.pvmail.do_stop()
            self.ui.w_running_stopped.setText('stopped')
            sty = bcdaqwidgets.StyleSheet(self.ui.w_running_stopped)
            sty.updateStyleSheet({
                'background-color': '#eee',
            })
#             self.ui.pv_message.ca_disconnect()
#             self.ui.pv_message.setToolTip('PV not connected, no text available')
#             self.ui.pv_message.setText('<not connected>')
            self.setStatus('CA monitors stopped')
            self.pvmail = None
            self.watching = False
    
    def doSendTestMessage(self):
        import mailer
        self.setStatus('requested a test email')
        subject = 'PvMail mailer test message: ' + self.config.mail_transfer_agent
        message = 'This is a test of the PvMail mailer, v' + PvMail.__version__
        msg_pv = str(self.getMessagePV())
        if self.watching:
            message += '\n\n' + self.pvmail.message
        message += '\n\n triggerPV = ' + str(self.getTriggerPV())
        message += '\n messagePV = ' + msg_pv
        message += '\n\n For more help, see: ' + PvMail.__url__
        recipients = self.getEmailList_Stripped()
        mailer.send_message(subject, message, recipients, self.config)
        self.setStatus('sent a test email')
    
    def appendEmailList(self, email_addr):
        self.email_address_model.listdata.append(email_addr)
        self.setStatus('added email: ' + email_addr)
    
    def getEmailList(self):
        '''the complete list of email addresses'''
        return self.email_address_model.listdata
    
    def getEmailList_Stripped(self):
        '''the list of email addresses with empty items removed'''
        return [v for v in self.email_address_model.listdata if len(v)>0]
    
    def setEmailList(self, email_list):
        self.email_address_model.reset()
        for v in email_list:
            self.appendEmailList(v)
        # always keep a blank item at end to grow the list
        self.appendEmailList('')
    
    def getMessagePV(self):
        return self.ui.messagePV.text()
    
    def setMessagePV(self, messagePV):
        self.ui.messagePV.setText(str(messagePV))
        self.setStatus('set message PV: ' + messagePV)
    
    def getTriggerPV(self):
        return self.ui.triggerPV.text()
    
    def setTriggerPV(self, triggerPV):
        self.ui.triggerPV.setText(str(triggerPV))
        self.setStatus('set trigger PV: ' + triggerPV)

    def setStatus(self, message):
        ts = str(datetime.datetime.now())
        self.ui.statusbar.showMessage(str(message))
        if hasattr(self.ui, 'history'):
            self.ui.history.append(ts + '  ' + message)
        if self.logger is not None:
            self.logger(message)


class EmailListModel(QtCore.QAbstractListModel): 
    def __init__(self, input_list, parent=None, *args): 
        '''
        data model for GUI: supports list of email addresses
        
        :param [str] input_list: list of email addresses
        :param QWidget parent: view widget for this data model
        '''
        # see: http://www.saltycrane.com/blog/2008/01/pyqt-43-simple-qabstractlistmodel/
        super(EmailListModel, self).__init__(parent, *args) 
        self.listdata = input_list
        # see "Subclassing" on this URL:
        # http://qt-project.org/doc/qt-4.8/qabstractlistmodel.html
 
    def rowCount(self, parent=QtCore.QModelIndex()): 
        return len(self.listdata) 
 
    def data(self, index, role): 
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.listdata[index.row()])
            elif role == QtCore.Qt.EditRole:
                return QtCore.QVariant(self.listdata[index.row()])
            else: 
                return QtCore.QVariant()

    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            self.listdata[row] = str(value.toString())
            if row+1 == len(self.listdata):
                # always keep a blank item at end to grow the list
                self.listdata.append('')
            self.dataChanged.emit(index, index)
            return True
        return False
    
    def flags(self, index):
        # http://www.riverbankcomputing.com/pipermail/pyqt/2009-April/022729.html
        # http://qt-project.org/doc/qt-4.8/qabstractitemmodel.html#flags
        defaultFlags = QtCore.QAbstractItemModel.flags(self, index)
        
        # TODO: support undo
       
        if index.isValid():
            return defaultFlags \
                    | QtCore.Qt.ItemIsEditable \
                    | QtCore.Qt.ItemIsDragEnabled \
                    | QtCore.Qt.ItemIsDropEnabled
           
        else:
            return defaultFlags \
                    | QtCore.Qt.ItemIsDropEnabled


def main(triggerPV, messagePV, recipients, logger=None, logfile=None, config=None):
    app = QtGui.QApplication(sys.argv)
    config = config or ini_config.Config()
    gui = PvMail_GUI(logger = logger, config=config)
    
    gui.setStatus('PID: ' + str(os.getpid()))
    if logfile is not None and os.path.exists(logfile):
        gui.ui.history.append(open(logfile, 'r').read())
        gui.setStatus('log file: ' + logfile)
    gui.setStatus('email configuration file: ' + config.ini_file)
    gui.setStatus('email agent: ' + config.mail_transfer_agent)
    gui.setMessagePV(messagePV)
    gui.setTriggerPV(triggerPV)
    gui.setEmailList(recipients)

    gui.show()
    _r = app.exec_()
    sys.exit(_r)


if __name__ == '__main__':
    main('pvMail:trigger', 'pvMail:message', ['prjemian@gmail.com',])
