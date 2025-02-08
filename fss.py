import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi

class Window(QDialog) :
    def __init__(self) :
        super(Window, self).__init__()
        loadUi("gui.ui", self)

app = QApplication(sys.argv)
window = Window()

widget = QtWidgets.QStackedWidget()
widget.addWidget(window)
widget.setWindowTitle("Fichiers Super Saver")
widget.setGeometry(100, 100, window.geometry().width(), window.geometry().height())
widget.show()

sys.exit(app.exec_())