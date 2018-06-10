from PyQt5.QtWidgets import QDirModel
from PyQt5.QtCore import Qt,QVariant

class ChangedQDirModel(QDirModel):
    def __init__(self):
        super().__init__()

    def headerData(self, p_int, Qt_Orientation, role):
        if role==Qt.DisplayRole:
            if p_int==0:
                return QVariant('文件名')
            elif p_int==1:
                return QVariant('文件大小')
            elif p_int==2:
                return QVariant('文件类型')
            elif p_int==3:
                return QVariant('最近修改')
        else:
            return QVariant()