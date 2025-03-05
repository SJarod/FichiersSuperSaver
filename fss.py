import sys

import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi

import subprocess

class Window(QtWidgets.QMainWindow) :
    def __init__(self) :
        super(Window, self).__init__()
        loadUi("main.ui", self)

        self.fssTokenBrowse.clicked.connect(self.fss_select_token)
        self.fssDestBrowse.clicked.connect(self.fss_select_dest)

        self.pfsDestBrowse.clicked.connect(self.pfs_select_dest)

        self.sdsSrcBrowse.clicked.connect(self.sds_select_source)
        self.sdsDestBrowse.clicked.connect(self.sds_select_dest)

    def browse_directory(self) :
        return QFileDialog.getExistingDirectory(self, "Select a directory")
    
    def open_explorer(self, dir) :
        # TODO : other platforms compatibility (/ vs \\)
        dir = dir.replace("/", "\\")
        dir = dir + "\\"
        subprocess.Popen(fr'explorer /select, "{dir}"')

    def fss_select_token(self) :
        filenames = QFileDialog.getOpenFileName(self, "Select token file", "", "Text files (*.txt)")
        if filenames[0] == '' :
            return
        
        f = open(filenames[0], "r")
        self.tokenField.setText(f.readlines()[0])

    def fss_select_dest(self) :
        dir = self.browse_directory()
        if dir == '' :
            return
        
        self.fssSaveDirField.setText(dir)

    def fss_execute(self) :
        if (self.tokenField.text() == "") :
            print("Please specify the Discord bot token")
            return
        os.system("backup_discord_servers_fss.py " + self.tokenField.text())

        if self.checkBox.isChecked() :
            self.open_explorer(self.saveDirField.text())


    def pfs_select_dest(self) :
        dir = self.browse_directory()
        if dir == '' :
            return
        
        self.saveDirField.setText(dir)

    def pfs_execute(self) :
        os.system("backup_pc_personal_files.py -v -y -d " + self.saveDirField.text())

        if self.checkBox_2.isChecked() :
            self.open_explorer(self.saveDirField.text())

    def sds_select_source(self) :
        dir = self.browse_directory()
        if dir == '' :
            return
        
        self.sourceDirField.setText(dir)

    def sds_select_dest(self) :
        dir = self.browse_directory()
        if dir == '' :
            return
        
        self.destDirField.setText(dir)

    def sds_execute(self) :
        os.system("backup+clean_directory.py")

        if self.checkBox_3.isChecked() :
            self.open_explorer(self.saveDirField.text())


app = QApplication(sys.argv)
window = Window()

widget = QtWidgets.QStackedWidget()
widget.addWidget(window)
widget.setWindowTitle("Fichiers Super Saver 0.2.1")
widget.setGeometry(100, 100, window.geometry().width(), window.geometry().height())
widget.show()

sys.exit(app.exec_())