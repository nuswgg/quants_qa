from translate import Ui_MainWindow
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())