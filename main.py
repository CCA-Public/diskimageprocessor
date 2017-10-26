#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import * 
import sys

import design

class ProcessorApp(QMainWindow, design.Ui_MainWindow):

    def __init__(self, parent=None):
        super(ProcessorApp, self).__init__(parent)
        self.setupUi(self)

        # build browse functionality buttons
        self.source1btn.clicked.connect(self.browse_source)
        self.destination1btn.clicked.connect(self.browse_dest)

        # build start functionality
        self.process.clicked.connect(self.start_processing)

        self.actionAbout.triggered.connect(self.about_dialog)

    def about_dialog(self):
        QMessageBox.information(self, "About", 
            "Disk Image Processor v0.7.1\nTim Walsh, 2017\nMIT License\nhttps://github.com/timothyryanwalsh/cca-diskimageprocessor")

    @pyqtSlot()
    def readStdOutput(self):
        self.textEdit.append(QString(self.proc.readAllStandardOutput()))

    @pyqtSlot()
    def readStdError(self):
        self.textEdit.append(QString(self.proc.readAllStandardError()))

    def browse_source(self):
        self.source1.clear() # clear directory source text
        directory = QFileDialog.getExistingDirectory(self, "Select folder")

        if directory: # if user didn't pick directory don't continue
            self.source1.setText(directory)

    def browse_dest(self):
        self.destination1.clear() # clear directory source text
        directory = QFileDialog.getExistingDirectory(self, "Select folder")

        if directory: # if user didn't pick directory don't continue
            self.destination1.setText(directory)

    def on_finished(self):
        self.lineEdit.setText('Finished')
        QMessageBox.information(self, "Done!", "Process complete.")
        self.process.setEnabled(True)

    def start_processing(self):
        # clear reports
        self.textEdit.clear()
        
        # path to script
        if self.processingBtn.isChecked():
            self.processing_script = "/usr/share/ccatools/diskimageprocessor/diskimageprocessor.py"
        else:
            self.processing_script = "/usr/share/ccatools/diskimageprocessor/diskimageanalyzer.py"

        # start QProcess
        self.proc = QProcess()

        # acknowledge process has started
        self.lineEdit.setText('In progress')
        self.process.setEnabled(False)

        # build QStringList
        call = QStringList()
        call.append(self.processing_script)
        if self.processingBtn.isChecked():
            if self.checkBox.isChecked():
                call.append("-b")
            if self.exportAllBtn.isChecked():
                call.append("-e")
            if self.checkBox_3.isChecked():
                call.append("-p")
            if self.filesonlyBtn.isChecked():
                call.append("-f")
            if self.resforksBtn.isChecked():
                call.append("-r")
        else:
            if self.checkBox_2.isChecked():
                call.append("-k")
            if self.exportAllBtn.isChecked():
                call.append("-e")
            if self.resforksBtn.isChecked():
                call.append("-r")
        call.append(self.source1.text())
        call.append(self.destination1.text())

        # call program and redirect stdout to GUI
        self.proc.start("python3", call)
        self.proc.setProcessChannelMode(QProcess.MergedChannels);
        QObject.connect(self.proc, SIGNAL("readyReadStandardOutput()"), self, SLOT("readStdOutput()"));
        QObject.connect(self.proc, SIGNAL("readyReadStandardError()"), self, SLOT("readStdError()"));

        # update status and display pop-up message when finished
        self.proc.finished.connect(self.on_finished)

def main():
    app = QApplication(sys.argv)
    form = ProcessorApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
