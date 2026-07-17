import sys

import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.uic import loadUi

import subprocess

# TODO : bug save discord nom de fichier trop long

class Window(QtWidgets.QMainWindow) :
    id = -1

    def __init__(self) :
        super(Window, self).__init__()
        loadUi("main.ui", self)

        self.fssTokenBrowse.clicked.connect(self.fss_select_token)
        self.fssDestBrowse.clicked.connect(self.fss_select_dest)

        self.pfsDestBrowse.clicked.connect(self.pfs_select_dest)

        self.sdsSrcBrowse.clicked.connect(self.sds_select_source)
        self.sdsDestBrowse.clicked.connect(self.sds_select_dest)

        self.executeButton.clicked.connect(self.run)


    def ready(self, bReady: bool) :
        self.id = self.tabWidget.currentIndex()

        self.executeButton.setEnabled(bReady)
        self.openExplorer.setEnabled(bReady)

    def browse_directory(self) :
        return QFileDialog.getExistingDirectory(self, "Select a directory")
    
    def open_explorer(self, dir) :
        # TODO : other platforms compatibility (/ vs \\)
        dir = dir.replace("/", "\\")
        dir = dir + "\\"
        subprocess.Popen(fr'explorer /select, "{dir}"')

    def run(self) :
        if (self.id == 0) :
            self.fss_execute()
        elif (self.id == 1) :
            self.pfs_execute()
        elif (self.id == 2) :
            self.sds_execute()




    def fss_select_token(self) :
        filenames = QFileDialog.getOpenFileName(self, "Select token file", "", "Text files (*.txt)")
        if filenames[0] == '' :
            return
        
        f = open(filenames[0], "r")
        self.fssTokenField.setText(f.readlines()[0])
        self.ready(self.fss_condition())

    def fss_select_dest(self) :
        dir = self.browse_directory()
        if dir == '' :
            return
        
        self.fssDestField.setText(dir)
        self.ready(self.fss_condition())

    def fss_condition(self) :
        t1 = self.fssTokenField.text()
        t2 = self.fssDestField.text()
        return t1 != "" and t2 != ""
    
    def fss_execute(self) :
        if (self.fssTokenField.text() == "") :
            print("Please specify the Discord bot token")
            return
        # TODO : show a dialog window with a progress bar (gui.ui)
        os.system("backup_discord_servers_fss.py -t " + self.fssTokenField.text() + " -d " + self.fssDestField.text())

        if self.openExplorer.isChecked() :
            self.open_explorer(self.fssDestField.text())



    def pfs_select_dest(self) :
        dir = self.browse_directory()
        if dir == '' :
            return
        
        self.pfsDestField.setText(dir)
        self.ready(self.pfs_condition())

    def pfs_condition(self) :
        t = self.pfsDestField.text()
        return t != ""

    def pfs_execute(self) :
        os.system("backup_pc_personal_files.py -v -y -d " + self.pfsDestField.text())

        if self.openExplorer.isChecked() :
            self.open_explorer(self.pfsDestField.text())



    def sds_select_source(self) :
        dir = self.browse_directory()
        if dir == '' :
            return
        
        self.sdsSrcField.setText(dir)

    def sds_select_dest(self) :
        dir = self.browse_directory()
        if dir == '' :
            return
        
        self.sdsDestField.setText(dir)

    def sds_condition(self) :
        return False

    def sds_execute(self) :
        os.system("backup+clean_directory.py")

        if self.openExplorer.isChecked() :
            self.open_explorer(self.sdsDestField.text())


app = QApplication(sys.argv)
window = Window()

widget = QtWidgets.QStackedWidget()
widget.addWidget(window)
widget.setWindowTitle("Fichiers Super Saver 0.2.1")
widget.setGeometry(100, 100, window.geometry().width(), window.geometry().height())
widget.show()

sys.exit(app.exec_())