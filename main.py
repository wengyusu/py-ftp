from PyQt5.QtWidgets import QApplication
import main_window
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwin = main_window.ServerMainWindow()
    sys.exit(app.exec_())
