#!/usr/bin/env python

"""
MVC demo
"""


from PyQt4 import QtCore
from PyQt4 import QtGui

pyqtSignal = QtCore.pyqtSignal
import datetime

LABEL_COLUMN = 0
Q_COLUMN = 1
AR_COLUMN = 2
AY_COLUMN = 3
DY_COLUMN = 4


class TableModel(QtCore.QAbstractTableModel):
    """
    Model (data) of our table of motor positions for each Q
    """

    def __init__(self, datain, parent=None, *args):
        super(TableModel, self).__init__(parent, *args)
        self.model = []
        self.newRow(datain)
        self.headers = [
            "description",
            "Q, 1/A",
            "AR, degrees",
            "AY, mm",
            "DY, mm",
        ]

    def newRow(self, data=None):
        if data is None:
            now = str(datetime.datetime.now())
            self.model.append(
                [
                    now,
                    0,
                    0.3,
                    0.4,
                    0.5,
                ]
            )
        else:
            if not isinstance(data, list):
                raise RuntimeError("data must be a list of rows")
            if not isinstance(data[0], list):
                raise RuntimeError(
                    "each row must contain values for: label, Q, AR, AY, DY"
                )
            for _ in data:
                self.model.append(_)

    def rowCount(self, parent):
        return len(self.model)

    def columnCount(self, parent):
        return len(self.model[0])

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headers[col])
        return QtCore.QVariant()

    def data(self, index, role):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.model[index.row()][index.column()])
            elif role == QtCore.Qt.EditRole:
                return QtCore.QVariant(self.model[index.row()][index.column()])
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        """update the model from the control"""
        if index.isValid():
            row = index.row()
            column = index.column()
            if column == 0:
                self.model[row][column] = value
                return True
            elif column == 1:
                val, ok = value.toDouble()
                if ok:
                    self.model[row][column] = val
                    # TODO: update AR, AY, DY model data now from actual computations
                    # example floating point calculation
                    arr = [r[Q_COLUMN] for r in self.model]
                    self.model[row][AR_COLUMN] = sum(arr) / len(arr)
                    self.model[row][AY_COLUMN] = max(arr)
                    self.model[row][DY_COLUMN] = min(arr)
                    return True
        return False

    def flags(self, index):
        defaultFlags = QtCore.QAbstractItemModel.flags(self, index)
        if index.isValid():
            return (
                defaultFlags
                | QtCore.Qt.ItemIsEnabled
                | QtCore.Qt.ItemIsEditable
                | QtCore.Qt.ItemIsDragEnabled
                | QtCore.Qt.ItemIsDropEnabled
            )

        else:
            return defaultFlags | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled


class TableView(QtGui.QTableView):
    """
    A table to demonstrate the button delegate.
    """

    def __init__(self, *args, **kwargs):
        super(TableView, self).__init__(*args, **kwargs)

        # self.q_control = FloatControl(self, self.AR_ButtonClicked, '%.6f')
        self.q_control = FloatControl()
        self.setItemDelegate(self.q_control)

        self.ar_control = ButtonControl(self, self.AR_ButtonClicked, "%.6f")
        self.ay_control = ButtonControl(self, self.AY_ButtonClicked, "%.3f")
        self.dy_control = ButtonControl(self, self.DY_ButtonClicked, "%.3f")

        self.setItemDelegateForColumn(AR_COLUMN, self.ar_control)
        self.setItemDelegateForColumn(AY_COLUMN, self.ay_control)
        self.setItemDelegateForColumn(DY_COLUMN, self.dy_control)

    def _buttonClicked(self, buttonname="", *args, **kw):
        statusbar = self.parent().parent().statusBar()
        msg = buttonname + " button: " + self.sender().text()
        statusbar.showMessage(msg)

    def AR_ButtonClicked(self):
        self._buttonClicked("AR")

    def AY_ButtonClicked(self):
        self._buttonClicked("AY")

    def DY_ButtonClicked(self):
        self._buttonClicked("DY")


class FloatControl(QtGui.QStyledItemDelegate):
    """Constrained floating-point input on Q column"""

    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0
        if index.column() == Q_COLUMN:  # only on the cells in the Q column
            editor = QtGui.QLineEdit(widget)
            validator = QtGui.QDoubleValidator()
            editor.setValidator(validator)
            return editor
        return super(FloatControl, self).createEditor(widget, option, index)


class ButtonControl(QtGui.QItemDelegate):
    """A QPushButton in every cell of the column to which it's applied"""

    def __init__(self, parent, action, display_format="%f"):
        QtGui.QItemDelegate.__init__(self, parent)
        self.action = action
        self.format = display_format

    def paint(self, painter, option, index):
        widget = self.parent().indexWidget(index)
        if widget is None:
            # create the PushButton widget
            value, ok = index.data().toDouble()  # *MUST* be a double
            if ok:
                text = self.format % value
                owner = self.parent()
                pb = QtGui.QPushButton(text, owner, clicked=self.action)
                owner.setIndexWidget(index, pb)
        else:
            if isinstance(widget, QtGui.QPushButton):
                # update the PushButton text if the model's value changed
                value, ok = index.data().toDouble()
                if ok:
                    text = self.format % value
                    if text != widget.text():
                        widget.setText(text)  # update only if non-trivial


def main(*args, **kw):
    """
    A simple test widget to contain and own the model and table.
    """
    import sys

    app = QtGui.QApplication(sys.argv)

    mw = QtGui.QMainWindow(None)
    mw.resize(600, 400)

    # data_array = [['row ' + str(_+1), _+.2, _+.3, _+.4, _+.5] for _ in range(3)]
    data_array = None

    w = QtGui.QWidget(mw)
    mw.setCentralWidget(w)
    mw.statusBar().showMessage("edit Q in a row, then press one of the three buttons")

    l = QtGui.QVBoxLayout(w)
    mw.model = TableModel(data_array, parent=mw)
    for __ in range(3):
        mw.model.newRow()
    mw.view = TableView(w)
    mw.view.setModel(mw.model)
    l.addWidget(mw.view)

    mw.show()

    _r = app.exec_()
    sys.exit(_r)


if __name__ == "__main__":
    main()
