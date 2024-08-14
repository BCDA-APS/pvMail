#!/usr/bin/env python

'''PV controls to test the GUI: uses default database (test.db)'''

from PyQt4 import QtCore
from PyQt4 import QtGui

pyqtSignal = QtCore.pyqtSignal
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
