"""
http://www.saltycrane.com/blog/2008/01/pyqt-how-to-pass-arguments-while/
"""

import sys

from PyQt4 import QtCore
from PyQt4 import QtGui


####################################################################
class MyWindow(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)

        self.label = QtGui.QLabel(" ")
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.connect(self, QtCore.SIGNAL("didSomething"), self.update_label)
        # revised: demo this after a short delay
        QtCore.QTimer.singleShot(1000, self.do_first)
        QtCore.QTimer.singleShot(3000, self.do_something)

    def do_first(self):
        self.emit(QtCore.SIGNAL("didSomething"), "wait", "for", "something", "...")

    def do_something(self):
        self.emit(QtCore.SIGNAL("didSomething"), "important", "information")

    def update_label(self, *args):
        self.label.setText(str(len(args)) + ": " + " ".join(args))


####################################################################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
