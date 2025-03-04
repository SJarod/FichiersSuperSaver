import sys

import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi

import subprocess

class Window(QDialog) :
    def __init__(self) :
        super(Window, self).__init__()
        loadUi("gui.ui", self)

        # fss
        self.tokenBrowse.clicked.connect(self.select_token)
        self.fssSaveDirBrowse.clicked.connect(self.select_fss_dir)
        self.backupDiscord.clicked.connect(self.backup_discord)

        # personal files
        self.saveDirBrowse.clicked.connect(self.select_pf_dir)
        self.backupPCPersonal.clicked.connect(self.backup_personal_files)

        # save+clean+er
        self.sourceDirBrowse.clicked.connect(self.select_source_sc_dir)
        self.destDirBrowse.clicked.connect(self.select_dest_sc_dir)
        self.backupDirectory.clicked.connect(self.backup_directory)

    def select_destination_directory(self) :
        return QFileDialog.getExistingDirectory(self, "Select a destination directory")
    
    def open_explorer(self, dir) :
        dir = dir.replace("/", "\\")
        dir = dir + "\\"
        subprocess.Popen(fr'explorer /select, "{dir}"')

    # fss
    def select_token(self) :
        filenames = QFileDialog.getOpenFileName(self, "Select token file", "", "Text files (*.txt)")
        if filenames == None :
            return
        
        f = open(filenames[0], "r")
        self.tokenField.setText(f.readlines()[0])

        self.backupDiscord.setEnabled(self.fssSaveDirField.text() != None)

    def select_fss_dir(self) :
        dir = self.select_destination_directory()
        if dir == None :
            return
        
        self.fssSaveDirField.setText(dir)

        self.backupDiscord.setEnabled(self.tokenField.text() != None)

    def backup_discord(self) :
        if (self.tokenField.text() == "") :
            print("Please specify the Discord bot token")
            return
        os.system("backup_discord_servers_fss.py " + self.tokenField.text())

        if self.checkBox.isChecked() :
            self.open_explorer(self.saveDirField.text())


    # personal files
    def select_pf_dir(self) :
        dir = self.select_destination_directory()
        if dir == None :
            return
        
        self.saveDirField.setText(dir)
        self.backupPCPersonal.setEnabled(True)

    def backup_personal_files(self) :
        os.system("backup_pc_personal_files.py -v -y -d " + self.saveDirField.text())

        if self.checkBox_2.isChecked() :
            self.open_explorer(self.saveDirField.text())

    # save+clean+er
    def select_source_sc_dir(self) :
        dir = self.select_destination_directory()
        if dir == None :
            return
        
        self.sourceDirField.setText(dir)
        self.backupDirectory.setEnabled(self.destDirField.text() != None)

    def select_dest_sc_dir(self) :
        dir = self.select_destination_directory()
        if dir == None :
            return
        
        self.destDirField.setText(dir)
        self.backupDirectory.setEnabled(self.sourceDirField.text() != None)

    def backup_directory(self) :
        os.system("backup+clean_directory.py")

        if self.checkBox_3.isChecked() :
            self.open_explorer(self.saveDirField.text())


app = QApplication(sys.argv)
window = Window()

widget = QtWidgets.QStackedWidget()
widget.addWidget(window)
widget.setWindowTitle("Fichiers Super Saver 0.1.0")
widget.setGeometry(100, 100, window.geometry().width(), window.geometry().height())
widget.show()

sys.exit(app.exec_())