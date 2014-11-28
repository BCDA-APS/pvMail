
'''
Button Delegate For QTableViews

http://www.gulon.co.uk/2013/01/30/
'''

# The following tells SIP (the system that binds Qt's C++ to Python)
# to return Python native types rather than QString and QVariant
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
 
class TableModel(QAbstractTableModel):
    """
    A simple 10x10 table model to demonstrate the button delegate
    """
    def rowCount(self, parent=QModelIndex()): return 10
    def columnCount(self, parent=QModelIndex()): return 10
 
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        if not role==Qt.DisplayRole: return None
 
        # If the QModelIndex is valid and the data role is DisplayRole,
        # i.e. text, then return a string of the cells position in the
        # table in the form (row,col)
        return "({0:02d},{1:02d})".format(index.row(), index.column())
 
class ButtonDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QPushButton in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):
        # The parent is not an optional argument for the delegate as
        # we need to reference it in the paint method (see below)
        QItemDelegate.__init__(self, parent)
 
    def paint(self, painter, option, index):
        # This method will be called every time a particular cell is
        # in view and that view is changed in some way. We ask the
        # delegates parent (in this case a table view) if the index
        # in question (the table cell) already has a widget associated
        # with it. If not, create one with the text for this index and
        # connect its clicked signal to a slot in the parent view so
        # we are notified when its used and can do something.
        if not self.parent().indexWidget(index):
            self.parent().setIndexWidget(
                index,
                QPushButton(
                    index.data(),
                    self.parent(),
                    clicked=self.parent().cellButtonClicked
                )
            )
 
class TableView(QTableView):
    """
    A simple table to demonstrate the button delegate.
    """
    def __init__(self, *args, **kwargs):
        QTableView.__init__(self, *args, **kwargs)
 
        # Set the delegate for column 0 of our table
        self.setItemDelegateForColumn(0, ButtonDelegate(self))
 
    @pyqtSlot()
    def cellButtonClicked(self):
        # This slot will be called when our button is clicked.
        # self.sender() returns a reference to the QPushButton created
        # by the delegate, not the delegate itself.
        print "Cell Button Clicked", self.sender().text()
 
if __name__=="__main__":
    from sys import argv, exit
 
    class Widget(QWidget):
        """
        A simple test widget to contain and own the model and table.
        """
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
 
            l=QVBoxLayout(self)
            self._tm=TableModel(self)
            self._tv=TableView(self)
            self._tv.setModel(self._tm)
            l.addWidget(self._tv)
 
    a=QApplication(argv)
    w=Widget()
    w.show()
    w.raise_()
    exit(a.exec_())
