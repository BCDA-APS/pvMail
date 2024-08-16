"""
Email list model for Qt's MVC QListView
"""

from PyQt5 import QtCore


class EmailListModel(QtCore.QAbstractListModel):
    def __init__(self, input_list, parent=None, *args):
        """
        data model for GUI: supports list of email addresses

        :param [str] input_list: list of email addresses
        :param QWidget parent: view widget for this data model
        """
        super(EmailListModel, self).__init__(parent, *args)
        self.listdata = input_list

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.listdata)

    def data(self, index, role):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.listdata[index.row()])
            elif role == QtCore.Qt.EditRole:
                return QtCore.QVariant(self.listdata[index.row()])
            else:
                return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            self.listdata[row] = str(value)
            if row + 1 == len(self.listdata):
                # always keep a blank item at end to grow the list
                self.listdata.append("")
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        defaultFlags = QtCore.QAbstractItemModel.flags(self, index)

        if index.isValid():
            return (
                defaultFlags
                | QtCore.Qt.ItemIsEditable
                | QtCore.Qt.ItemIsDragEnabled
                | QtCore.Qt.ItemIsDropEnabled
            )

        else:
            return defaultFlags | QtCore.Qt.ItemIsDropEnabled

    def reset(self):
        self.listdata = []
