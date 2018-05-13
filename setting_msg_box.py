from PyQt5.QtWidgets import QMessageBox


class SettingMessage(QMessageBox):

    def __init__(self):
        super(SettingMessage, self).__init__(QMessageBox.NoIcon, 'Setting saved', 'You have successfully saved your settings.\nYou have to restart the Server in order to reset it. ')
        self.setModal(True)