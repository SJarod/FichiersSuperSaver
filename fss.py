import sys

import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi

class Window(QDialog) :
    def __init__(self) :
        super(Window, self).__init__()
        loadUi("gui.ui", self)
        self.tokenBrowse.clicked.connect(self.select_token)
        self.backupDiscord.clicked.connect(self.backup_discord)

    def select_token(self) :
        filenames = QFileDialog.getOpenFileName(self, "Select token file", "", "Text files (*.txt)")
        f = open(filenames[0], "r")
        self.tokenField.setText(f.readlines()[0])

    def backup_discord(self) :
        if (self.tokenField.text() == "") :
            print("Please specify the Discord bot token")
            return
        os.system("backup_discord_servers_fss.py " + self.tokenField.text())

    def backup_personal_files(self) :
        pass

    def backup_directory(self) :
        pass

app = QApplication(sys.argv)
window = Window()

widget = QtWidgets.QStackedWidget()
widget.addWidget(window)
widget.setWindowTitle("Fichiers Super Saver 0.1.0")
widget.setGeometry(100, 100, window.geometry().width(), window.geometry().height())
widget.show()

sys.exit(app.exec_())