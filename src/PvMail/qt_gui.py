#!/usr/bin/env python

'''
===================================
pvMail: just the GUI
===================================

Build the Graphical User Interface for PvMail using PyQt4. 

Copyright (c) 2014, UChicago Argonne, LLC
'''


from PyQt4 import QtCore, QtGui
import sys

import PvMail


WINDOW_TITLE = 'pvMail'


class PvMail_GUI(QtGui.QMainWindow):
    '''
    GUI used for pvMail, based on PyQt4
    '''

    def __init__(self, *args, **kw):
        '''make this class callable from pvMail application'''
        super(PvMail_GUI, self).__init__(**kw)
        self.resize(600, 400)
        self.centralwidget = QtGui.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)

        self._create_statusbar()

        self.statusbar.showMessage('creating menubar') 
        self._create_menubar()

        self.statusbar.showMessage('creating widgets')
        self._create_widgets()
        
        self.statusbar.showMessage('assigning window title')
        self.setWindowTitle(WINDOW_TITLE)

        self.statusbar.showMessage('ready')

    def _create_statusbar(self):
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

    def _create_menubar(self):
        self.menubar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.menuFile = QtGui.QMenu('File', self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addSeparator()
        self.actionExit = QtGui.QAction('E&xit', None)
        self.actionExit.triggered.connect(self.doClose)
        self.menuFile.addAction(self.actionExit)

        self.menuEdit = QtGui.QMenu('Edit', self.menubar)
        self.menubar.addAction(self.menuEdit.menuAction())

        self.menuHelp = QtGui.QMenu('Help', self.menubar)
        self.menubar.addAction(self.menuHelp.menuAction())
        self.actionAbout = QtGui.QAction('About ...', None)
        self.actionAbout.triggered.connect(self.doAbout)
        self.menuHelp.addAction(self.actionAbout)

    def _create_widgets(self):
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)

        self.statusbar.showMessage('creating entry form')
        verticalLayoutWidget = QtGui.QWidget(self.splitter)
        verticalLayout = QtGui.QVBoxLayout(verticalLayoutWidget)
        verticalLayout.setMargin(0)

        formLayout = QtGui.QFormLayout()
        l_trigger_PV = QtGui.QLabel('trigger PV', verticalLayoutWidget)
        formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, l_trigger_PV)
        
        l_message_PV = QtGui.QLabel('message PV', verticalLayoutWidget)
        formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, l_message_PV)
        
        l_emails = QtGui.QLabel('email address(es)', verticalLayoutWidget)
        formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, l_emails)
        self.triggerPV = QtGui.QLineEdit(verticalLayoutWidget)
        formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.triggerPV)
        self.messagePV = QtGui.QLineEdit(verticalLayoutWidget)
        formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.messagePV)

        self.email_list = QtGui.QListWidget(verticalLayoutWidget)
        self.email_list.setAlternatingRowColors(True)
        formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.email_list)
        verticalLayout.addLayout(formLayout)

        self.statusbar.showMessage('creating controls')
        self.horizontalLayout = QtGui.QHBoxLayout()

        spacer_args = (40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        spacer = QtGui.QSpacerItem(*spacer_args)
        self.horizontalLayout.addItem(spacer)
        self.w_btn_run = QtGui.QPushButton('Run', verticalLayoutWidget)
        self.w_btn_run.released.connect(self.doRun)
        self.horizontalLayout.addWidget(self.w_btn_run)

        spacer = QtGui.QSpacerItem(*spacer_args)
        self.horizontalLayout.addItem(spacer)
        self.w_running_stopped = QtGui.QLabel(verticalLayoutWidget)
        self.horizontalLayout.addWidget(self.w_running_stopped)

        spacer = QtGui.QSpacerItem(*spacer_args)
        self.horizontalLayout.addItem(spacer)
        self.w_btn_stop = QtGui.QPushButton('Stop', verticalLayoutWidget)
        self.w_btn_stop.released.connect(self.doStop)
        self.horizontalLayout.addWidget(self.w_btn_stop)

        spacer = QtGui.QSpacerItem(*spacer_args)
        self.horizontalLayout.addItem(spacer)
        verticalLayout.addLayout(self.horizontalLayout)

        self.statusbar.showMessage('creating history')
        self.w_history = QtGui.QTextBrowser(self.splitter)

        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

    def doAbout(self, *args, **kw):
        msg = 'About: '
        msg += PvMail.__project_name__ 
        msg += ', v' + PvMail.__version__
        self.setStatus(msg)

    def doClose(self, *args, **kw):
        self.setStatus('application exit requested')
        self.close()
    
    def doRun(self, *args, **kw):
        self.setStatus('run requested')
    
    def doStop(self, *args, **kw):
        self.setStatus('stop requested')
    
    def appendEmailList(self, email_addr):
        self.email_list.insertItem(-1, email_addr)
    
    def getEmailList(self):
        return []
    
    def setEmailList(self, email_list):
        self.email_list.clear()
        self.email_list.addItems(email_list)
    
    def getMessagePV(self):
        return self.messagePV.text()
    
    def setMessagePV(self, messagePV):
        self.messagePV.setText(str(messagePV))
    
    def getTriggerPV(self):
        return self.triggerPV.text()
    
    def setTriggerPV(self, triggerPV):
        self.triggerPV.setText(str(triggerPV))

    def setStatus(self, message):
        self.statusbar.showMessage(str(message))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_window = PvMail_GUI()
    main_window.setMessagePV('epics:message:pv')
    main_window.setTriggerPV('epics:trigger:pv')
    main_window.setEmailList(['you', 'me', 'them', 'you', 'me', 'them', 'you', 'me', 'them', 'you', 'me', 'them', 'you', 'me', 'them', ])
    main_window.show()
    _r = app.exec_()
#     print 'message PV: ', main_window.getMessagePV()
#     print 'trigger PV: ', main_window.getTriggerPV()
#     print 'email list: ', main_window.getEmailList()
    sys.exit(_r)
