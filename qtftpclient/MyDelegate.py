from PyQt5.QtWidgets import QItemDelegate
from PyQt5.QtCore import QSize

class MyDelegate(QItemDelegate):
    def sizeHint(self, QStyleOptionViewItem, QModelIndex):
        return QSize(50,20)