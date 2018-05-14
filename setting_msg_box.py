from PyQt5.QtWidgets import QMessageBox


class SettingMessage(QMessageBox):

    def __init__(self):
        super(SettingMessage, self).__init__(QMessageBox.NoIcon, 'Setting saved', 'You have successfully saved your settings.\n It will take effect after restarting the Server. ')
        self.setModal(True)