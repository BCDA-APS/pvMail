
'''
http://www.saltycrane.com/blog/2008/01/pyqt-how-to-pass-arguments-while/
'''

import sys
import time
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 

#################################################################### 
class MyWindow(QWidget): 
    def __init__(self, *args): 
        QWidget.__init__(self, *args)

        self.label = QLabel(" ")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.connect(self, SIGNAL("didSomething"),
                     self.update_label)
        # revised: demo this after a short delay
        QTimer.singleShot(1000, self.do_first)
        QTimer.singleShot(3000, self.do_something)

    def do_first(self):
        self.emit(SIGNAL("didSomething"), "wait", 'for', "something", '...')

    def do_something(self):
        self.emit(SIGNAL("didSomething"), "important", "information")

    def update_label(self, *args):
        self.label.setText(str(len(args)) + ': ' + ' '.join(args))

####################################################################
if __name__ == "__main__": 
    app = QApplication(sys.argv) 
    w = MyWindow() 
    w.show() 
    sys.exit(app.exec_())
