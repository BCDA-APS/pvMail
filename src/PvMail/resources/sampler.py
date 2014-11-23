#!/usr/bin/env python

'''PV controls to test the GUI: uses default database (test.db)'''

import sys
from PyQt4 import QtGui, uic


class DemoView(object):
    '''show the UI file'''

    def __init__(self, uifile):
        self.ui = uic.loadUi(uifile)
        self.ui.pop.released.connect(self.doPop)
        self.counter = 0
    
    def show(self):
        self.ui.show()
    
    def doPop(self, *args, **kw):
        # pop the top item from the vertical layout
        layout = self.ui.vlayout
        if layout is not None:
            # layout.count()
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                self.counter += 1
                btn = QtGui.QPushButton('Pop ' + str(self.counter), parent=self.ui)
                btn.released.connect(self.doPop)
                layout.addWidget(btn)


app = QtGui.QApplication(sys.argv)
view = DemoView('sampler.ui')
view.show()
sys.exit(app.exec_())
