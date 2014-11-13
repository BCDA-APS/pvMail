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


def run(obj):
    '''
    run the GUI
    
    This is an abstraction that allows to change the GUI backend from this file.
    '''
    raise NotImplementedError


    #triggerPV = traits.api.String(
    #          desc="EPICS PV name on which to trigger an email",
    #          label="trigger PV",)
    #messagePV = traits.api.String(
    #          desc="EPICS string PV name with short message text",
    #          label="message PV",)
    #recipients = traits.api.List(
    #          trait=traits.api.String,
    #          value=["", "",],
    #          desc="email addresses of message recipients",
    #          label="email address(es)",)
    #actionRun = traitsui.api.Action(name = "Run",
    #            desc = "start watching for trigger PV to go from 0 to 1",
    #            action = "do_run")
    #actionStop = traitsui.api.Action(name = "Stop",
    #             desc = "stop watching trigger PV",
    #             action = "do_stop")


class PvMail_GUI(QtGui.QMainWindow):
    '''
    GUI used for pvMail, based on PyQt4
    '''

    def __init__(self, *args, **kw):
        '''make this class callable from pvMail application'''
        super(PvMail_GUI, self).__init__(**kw)
        self.resize(600, 400)
        self.centralwidget = QtGui.QWidget(self)
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)

        self._create_menubar()
        self._create_statusbar()
        self.statusbar.showMessage('starting') 

        self.statusbar.showMessage('creating splitter')
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)

        self.statusbar.showMessage('creating entry form')
        self.verticalLayoutWidget = QtGui.QWidget(self.splitter)
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setMargin(0)

        self.formLayout_2 = QtGui.QFormLayout()
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        
        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        
        self.label_3 = QtGui.QLabel(self.verticalLayoutWidget)
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.triggerPV = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.triggerPV)
        self.messagePV = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.messagePV)

        self.email_list = QtGui.QListWidget(self.verticalLayoutWidget)
        self.email_list.setAlternatingRowColors(True)
        #self.email_list.setObjectName(_fromUtf8("email_list"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.email_list)
        self.verticalLayout_2.addLayout(self.formLayout_2)

        self.statusbar.showMessage('creating controls')
        self.horizontalLayout = QtGui.QHBoxLayout()

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.w_btn_run = QtGui.QPushButton(self.verticalLayoutWidget)
        self.w_btn_run.setObjectName('w_btn_run')
        self.horizontalLayout.addWidget(self.w_btn_run)

        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.w_running_stopped = QtGui.QLabel(self.verticalLayoutWidget)
        self.w_running_stopped.setObjectName('w_running_stopped')
        self.horizontalLayout.addWidget(self.w_running_stopped)

        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.w_btn_stop = QtGui.QPushButton(self.verticalLayoutWidget)
        self.w_btn_stop.setObjectName('w_btn_stop')
        self.horizontalLayout.addWidget(self.w_btn_stop)

        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.statusbar.showMessage('creating history')
        self.w_history = QtGui.QTextBrowser(self.splitter)
        self.w_history.setObjectName('w_history')

        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        
        self.statusbar.showMessage('assigning labels')
        self._assign_labels()
        self.statusbar.showMessage('ready')

    def _create_statusbar(self):
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

    def _create_menubar(self):
        self.menubar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addSeparator()
        self.actionExit = QtGui.QAction('E&xit', None)
        self.actionExit.triggered.connect(self.doClose)
        self.menuFile.addAction(self.actionExit)

        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menubar.addAction(self.menuEdit.menuAction())

        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menubar.addAction(self.menuHelp.menuAction())
        self.actionAbout = QtGui.QAction('About ...', None)
        self.actionAbout.triggered.connect(self.doAbout)
        self.menuHelp.addAction(self.actionAbout)

    def _assign_labels(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.label.setText("trigger PV")
        self.label_2.setText("message PV")
        self.label_3.setText("email address(es)")
        self.w_btn_run.setText("Run")
        self.w_running_stopped.setText("running | stopped")
        self.w_btn_stop.setText("Stop")
        self.menuFile.setTitle("File")
        self.menuEdit.setTitle("Edit")
        self.menuHelp.setTitle("Help")
        self.actionExit.setText("Exit")

    def _init_actions_(self):
        self.actionExit.triggered.connect(self.doClose)
        #self.actionAbout.triggered.connect(self.doAbout)
    
    def doClose(self, *args, **kw):
        self.statusbar.showMessage('application exit requested')
        self.close()
    
    def doAbout(self, *args, **kw):
        print 'doAbout'
        msg = PvMail.__project_name__ + ', v' + PvMail.__version__
        self.statusbar.showMessage(msg)
    
    def getMessagePV(self):
        return self.messagePV.text()
    
    def setMessagePV(self, messagePV):
        self.messagePV.setText(str(messagePV))
    
    def getTriggerPV(self):
        return self.triggerPV.text()
    
    def setTriggerPV(self, triggerPV):
        self.triggerPV.setText(str(triggerPV))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_window = PvMail_GUI()
    main_window.setMessagePV('epics:message:pv')
    main_window.setTriggerPV('epics:trigger:pv')
    main_window.show()
    sys.exit(app.exec_())
