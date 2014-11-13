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
        
        self.email_address_model = EmailListModel([], self)

        self._create_statusbar()
        self._create_menubar()
        self._create_widgets()
        self.setWindowTitle(WINDOW_TITLE)

        self.setStatus('ready')

    def _create_statusbar(self):
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

    def _create_menubar(self):
        mbar = QtGui.QMenuBar(self)
        self.setMenuBar(mbar)

        menuFile = QtGui.QMenu('File', mbar)
        mbar.addAction(menuFile.menuAction())
        menuFile.addSeparator()
        self.actionExit = QtGui.QAction('E&xit', None)
        self.actionExit.triggered.connect(self.doClose)
        menuFile.addAction(self.actionExit)

        menuEdit = QtGui.QMenu('Edit', mbar)
        mbar.addAction(menuEdit.menuAction())

        menuHelp = QtGui.QMenu('Help', mbar)
        mbar.addAction(menuHelp.menuAction())
        self.actionAbout = QtGui.QAction('About ...', None)
        self.actionAbout.triggered.connect(self.doAbout)
        menuHelp.addAction(self.actionAbout)

    def _create_widgets(self):
        splitter = QtGui.QSplitter(self.centralwidget)
        splitter.setOrientation(QtCore.Qt.Vertical)

        verticalLayoutWidget = QtGui.QWidget(splitter)
        vLayout = QtGui.QVBoxLayout(verticalLayoutWidget)
        vLayout.setMargin(0)

        formLayout = QtGui.QFormLayout()
        vLayout.addLayout(formLayout)

        labels = ['trigger PV', 'message PV', 'email address(es)']
        for r, txt in enumerate(labels):
            lbl = QtGui.QLabel(txt, verticalLayoutWidget)
            formLayout.setWidget(r, QtGui.QFormLayout.LabelRole, lbl)

        self.triggerPV = QtGui.QLineEdit(verticalLayoutWidget)
        formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.triggerPV)
        
        self.messagePV = QtGui.QLineEdit(verticalLayoutWidget)
        formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.messagePV)

        self.email_list = QtGui.QListView(verticalLayoutWidget)
        self.email_list.setAlternatingRowColors(True)
        formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.email_list)
        self.email_list.setModel(self.email_address_model)

        hLayout = QtGui.QHBoxLayout()

        spacer_args = (40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        spacer = QtGui.QSpacerItem(*spacer_args)
        hLayout.addItem(spacer)
        self.w_btn_run = QtGui.QPushButton('Run', verticalLayoutWidget)
        self.w_btn_run.released.connect(self.doRun)
        hLayout.addWidget(self.w_btn_run)

        spacer = QtGui.QSpacerItem(*spacer_args)
        hLayout.addItem(spacer)
        self.w_running_stopped = QtGui.QLabel(verticalLayoutWidget)
        hLayout.addWidget(self.w_running_stopped)

        spacer = QtGui.QSpacerItem(*spacer_args)
        hLayout.addItem(spacer)
        self.w_btn_stop = QtGui.QPushButton('Stop', verticalLayoutWidget)
        self.w_btn_stop.released.connect(self.doStop)
        hLayout.addWidget(self.w_btn_stop)

        spacer = QtGui.QSpacerItem(*spacer_args)
        hLayout.addItem(spacer)
        vLayout.addLayout(hLayout)

        groupBox = QtGui.QGroupBox('History', splitter)
        boxLayout = QtGui.QHBoxLayout(groupBox)
        self.history = QtGui.QTextBrowser(groupBox)
        boxLayout.addWidget(self.history)

        self.gridLayout.addWidget(splitter, 0, 0, 1, 1)

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
#         self.setStatus('inspector: ' + str(self.email_list.gridSize()))
    
    def appendEmailList(self, email_addr):
        self.email_address_model.listdata.append(email_addr)
        self.setStatus('added email: ' + email_addr)
    
    def getEmailList(self):
        return []
    
    def setEmailList(self, email_list):
        self.email_address_model.reset()
        for v in email_list:
            self.appendEmailList(v)
    
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
        self.history.append(message)


class EmailListModel(QtCore.QAbstractListModel): 
    def __init__(self, input_list, parent=None, *args): 
        """ datain: a list where each item is a row"""
        # see: http://www.saltycrane.com/blog/2008/01/pyqt-43-simple-qabstractlistmodel/
        super(EmailListModel, self).__init__(parent, *args) 
        self.listdata = input_list
 
    def rowCount(self, parent=QtCore.QModelIndex()): 
        return len(self.listdata) 
 
    def data(self, index, role): 
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.listdata[index.row()])
        else: 
            return QtCore.QVariant()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_window = PvMail_GUI()
    
    # TODO: remove these lines before release
    main_window.history.clear()
    main_window.setMessagePV('epics:message:pv')
    main_window.setTriggerPV('epics:trigger:pv')
    liszt = ['meg', 'yergoo', 'yerek',]
    main_window.setEmailList(liszt)

    main_window.show()
    _r = app.exec_()
    
    # TODO: remove these lines before release
    print 'message PV: ', main_window.getMessagePV()
    print 'trigger PV: ', main_window.getTriggerPV()
    print 'email list: ', main_window.getEmailList()

    sys.exit(_r)
