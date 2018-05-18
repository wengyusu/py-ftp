import os

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt


class FileModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        self.fileData = []
        self.dataInit()

    def rowCount(self, parent=QModelIndex):
        return len(self.fileData)

    def columnCount(self, parent=QModelIndex):
        return 4

    def dataInit(self):
        for i in range(1, 10):
            itemData = {'name': '', 'type': '', 'size': '', 'time': ''}
            itemData['name'] = i
            itemData['type'] = i
            itemData['size'] = i
            itemData['time'] = i
            self.fileData.append(itemData)

    def data(self, QModelIndex, role):
        row = QModelIndex.row()
        col = QModelIndex.column()
        if QModelIndex.isValid() or (0 <= row < len(self.fileData)):
            if role == Qt.DisplayRole:
                if col == 0:
                    return QVariant(self.fileData[row]['name'])
                elif col == 1:
                    return QVariant(self.fileData[row]['type'])
                elif col == 2:
                    return QVariant(self.fileData[row]['size'])
                elif col == 3:
                    return QVariant(self.fileData[row]['time'])
            elif role==Qt.TextAlignmentRole:
                return QVariant(int(Qt.AlignVCenter))
        else:
            return QVariant()

    def index(self, p_int, p_int_1, parent=QModelIndex):
        if p_int < 0 or p_int_1 < 0 or p_int_1 >= self.columnCount(parent):
            return QModelIndex

        return self.createIndex(p_int, p_int_1)

    def parent(self, QModelIndex):
        return QModelIndex

    def headerData(self, p_int, Qt_Orientation, role):
        if role==Qt.DisplayRole:
            if p_int==0:
                return QVariant('name')
            elif p_int==1:
                return QVariant('type')
            elif p_int==2:
                return QVariant('size')
            elif p_int==3:
                return QVariant('time')
        else:
            return QVariant()