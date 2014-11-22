#!/usr/bin/env python

'''PV controls to test the GUI: uses default database (test.db)'''

try:
    from PyQt4 import QtCore, QtGui
    pyqtSignal = QtCore.pyqtSignal
except:
    from PySide import QtCore, QtGui
    pyqtSignal = QtCore.Signal
import sys
import bcdaqwidgets


class DemoView(QtGui.QWidget):
    '''Controls for the default pvMail test database.'''

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QFormLayout()
        self.setLayout(layout)

        lbl = QtGui.QLabel('trigger')
        pb = bcdaqwidgets.BcdaQToggleButton('pvMail:trigger')
        layout.addRow(lbl, pb)

        lbl = QtGui.QLabel('message')
        msg = bcdaqwidgets.BcdaQLineEdit('pvMail:message')
        layout.addRow(lbl, msg)


app = QtGui.QApplication(sys.argv)
view = DemoView()
view.show()
sys.exit(app.exec_())
