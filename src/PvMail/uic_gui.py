#!/usr/bin/env python

'''
===================================
pvMail: just the GUI
===================================

Run the Graphical User Interface for PvMail using PyQt4 from a .ui file. 

Copyright (c) 2014, UChicago Argonne, LLC
'''

# TODO: Connect status updates from :class:`pvMail.PvMail()` with status in the GUI
# TODO: Report PV connection problems in an obvious way
# TODO: GUI: display the tail end of the LOG_FILE.


# http://pyqt.sourceforge.net/Docs/PyQt4/designer.html


from PyQt4 import QtCore
import datetime
import os
import sys

import pvMail


WINDOW_TITLE = 'pvMail'
MAIN_UI_FILE = 'gui.ui'


class Customizer(object):
    
    def __init__(self, ui, logger=None, logfile=None, config=None, *args, **kw):
        self.ui = ui
        self.email_address_model = EmailListModel([], ui)
        self.logfile = logfile
        self.logger = logger
        self.config = config
        self.pvmail = None
        self.watching = False
        
        # menu item handlers
        self.ui.actionSend_test_email.triggered.connect(self.doSendTestMessage)
        self.ui.actionE_xit.triggered.connect(self.doClose)
        self.ui.actionAbout_pvMail.triggered.connect(self.doAbout)
        
        # button handlers
        self.ui.w_btn_run.released.connect(self.doRun)
        self.ui.w_btn_stop.released.connect(self.doStop)

    def doAbout(self, *args, **kw):
        import PvMail
        msg = 'About: '
        msg += PvMail.__project_name__ 
        msg += ', v' + PvMail.__version__
        msg += ', PID=' + str(os.getpid())
        self.setStatus(msg)

    def doClose(self, *args, **kw):
        self.setStatus('application exit requested')
        self.ui.close()
        sys.exit()      # FIXME: does not exit cleanly
    
    def doRun(self, *args, **kw):
        self.setStatus('<Run> button pressed')
        if self.watching:
            self.setStatus('already watching')
        else:
            self.pvmail = pvMail.PvMail(self.config)
            self.pvmail.triggerPV = str(self.getTriggerPV())
            self.pvmail.messagePV = str(self.getMessagePV())
            addresses = self.getEmailList_Stripped()
            self.pvmail.recipients = addresses
            self.setStatus('trigger PV: ' + self.pvmail.triggerPV)
            self.setStatus('message PV: ' + self.pvmail.messagePV)
            self.setStatus('recipients: ' + '  '.join(addresses))
            # TODO: need to set status when email is sent
            # TODO: show/edit messagePV content
            self.pvmail.do_start()
            self.setStatus('CA monitors started')
            self.watching = True
    
    def doStop(self, *args, **kw):
        if not self.watching:
            self.setStatus('not watching now')
        else:
            self.setStatus('<Stop> button pressed')
            self.pvmail.do_stop()
            self.setStatus('CA monitors stopped')
            self.pvmail = None
            self.watching = False
    
    def doSendTestMessage(self):
        import mailer
        import PvMail
        self.setStatus('requested a test email')
        subject = 'PvMail mailer test message: ' + self.config.mail_transfer_agent
        message = 'This is a test of the PvMail mailer, v' + PvMail.__version__
        message += '\n\n triggerPV = ' + str(self.getTriggerPV())
        message += '\n messagePV = ' + str(self.getMessagePV())
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
        if index.isValid() and role == QtCore.Qt.DisplayRole:
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
        
        # FIXME: item selection for editing removes item text
        # TODO: support undo
       
        if index.isValid():
            return QtCore.Qt.ItemIsEditable \
                    | QtCore.Qt.ItemIsDragEnabled \
                    | QtCore.Qt.ItemIsDropEnabled \
                    | defaultFlags
           
        else:
            return QtCore.Qt.ItemIsDropEnabled | defaultFlags


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    from PyQt4 import uic
    app = QApplication(sys.argv)
    ui = uic.loadUi(MAIN_UI_FILE)
    custom = Customizer(ui)
    
    ui.show()
    _r = app.exec_()
    print 'ui done'
    sys.exit(_r)
