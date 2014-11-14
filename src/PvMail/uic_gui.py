#!/usr/bin/env python

'''run a .ui file directly'''

# http://pyqt.sourceforge.net/Docs/PyQt4/designer.html


import sys
from PyQt4.QtGui import QApplication, QDialog
from PyQt4 import uic
from gui_ui import Ui_MainWindow


class Customizer(object):
    
    def __init__(self, ui):
        self.ui = ui
        self.ui.actionE_xit.triggered.connect(self.doClose)
    
    def doClose(self, *args, **kw):
        print 'close requested'
        sys.exit()

app = QApplication(sys.argv)
ui = uic.loadUi('gui.ui')
custom = Customizer(ui)

ui.show()
sys.exit(app.exec_())