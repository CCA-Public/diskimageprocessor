#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
import subprocess
import sys

import design

class StartScanThread(QThread):

    def __init__(self, process_list):
        QThread.__init__(self)
        self.process_list = process_list

    def start_scan(self):
        print(self.process_list) # for debugging
        subprocess.check_output(self.process_list)

    def run(self):
        self.start_scan()

class DiskImageProcessorApp(QMainWindow, design.Ui_DiskImageProcessor):

    def __init__(self, parent=None):
        super(DiskImageProcessorApp, self).__init__(parent)
        self.setupUi(self)

        # build browse functionality buttons
        self.analysisSourceBtn.clicked.connect(self.browse_analysis_source)
        self.procSourceBtn.clicked.connect(self.browse_processing_source)
        self.analysisDestBtn.clicked.connect(self.browse_analysis_dest)
        self.procDestBtn.clicked.connect(self.browse_processing_dest)

        # build start functionality
        self.analysisStartBtn.clicked.connect(self.start_analysis)
        self.procStartBtn.clicked.connect(self.start_processing)

        # about dialog
        self.actionAbout.triggered.connect(self.about_dialog)

    def about_dialog(self):
        QMessageBox.information(self, "About", 
            "Disk Image Processor v1.0.0\nCanadian Centre for Architecture\nDeveloper: Tim Walsh\n2018\nMIT License\nhttps://github.com/CCA-Public/cca-diskimageprocessor")

    def browse_analysis_source(self):
        self.analysisSource.clear() # clear directory source text
        directory = QFileDialog.getExistingDirectory(self, "Select folder")

        if directory: # if user didn't pick directory don't continue
            self.analysisSource.setText(directory)

    def browse_processing_source(self):
        self.procSource.clear() # clear directory source text
        directory = QFileDialog.getExistingDirectory(self, "Select folder")

        if directory: # if user didn't pick directory don't continue
            self.procSource.setText(directory)

    def browse_analysis_dest(self):
        self.analysisDest.clear() # clear directory source text
        directory = QFileDialog.getExistingDirectory(self, "Select folder")

        if directory: # if user didn't pick directory don't continue
            self.analysisDest.setText(directory)

    def browse_processing_dest(self):
        self.procDest.clear() # clear directory source text
        directory = QFileDialog.getExistingDirectory(self, "Select folder")

        if directory: # if user didn't pick directory don't continue
            self.procDest.setText(directory)

    def done_analysis(self):
        self.analysisCancelBtn.setEnabled(False)
        self.analysisStartBtn.setEnabled(True)
        QMessageBox.information(self, "Finished", "Analysis complete.")
        self.analysisStatus.setText("Completed")

    def done_processing(self):
        self.procCancelBtn.setEnabled(False)
        self.procStartBtn.setEnabled(True)
        QMessageBox.information(self, "Finished", "Processing complete.")
        self.procStatus.setText("Completed")

    def start_analysis(self):
        # clear status
        self.analysisStatus.clear()

        # create list for process
        self.process_list = list()
        self.process_list.append("python3")
        self.process_list.append("/usr/share/ccatools/diskimageprocessor/diskimageanalyzer.py")

        # give indication process has started
        self.analysisStatus.setText("Processing. Please be patient.")

        # option handling
        if self.quietLogBtn.isChecked():
            self.process_list.append("--quiet")
        if self.retainFilesBtn.isChecked():
            self.process_list.append("-k")
        if self.unallocBtn.isChecked():
            self.process_list.append("-e")
        if self.resForksBtn.isChecked():
            self.process_list.append("-r")

        # add source and dest
        self.process_list.append(self.analysisSource.text())
        self.process_list.append(self.analysisDest.text())

        # process
        self.get_thread = StartScanThread(self.process_list)
        self.get_thread.finished.connect(self.done_analysis)
        self.get_thread.start()
        self.analysisCancelBtn.setEnabled(True)
        self.analysisCancelBtn.clicked.connect(self.get_thread.terminate)
        self.analysisStartBtn.setEnabled(False)

    def start_processing(self):
        # clear status
        self.procStatus.clear()

        # create list for process
        self.process_list = list()
        self.process_list.append("python3")
        self.process_list.append("/usr/share/ccatools/diskimageprocessor/diskimageprocessor.py")

        # give indication process has started
        self.procStatus.setText("Processing. Please be patient.")

        # option handling
        if self.quietLogBtn.isChecked():
            self.process_list.append("--quiet")
        if self.unallocBtn.isChecked():
            self.process_list.append("-e")
        if self.resForksBtn.isChecked():
            self.process_list.append("-r")
        if self.bagBtn.isChecked():
            self.process_list.append("-b")
        if self.logicalFilesOnlyBtn.isChecked():
            self.process_list.append("-f")
        if self.bulkExtBtn.isChecked():
            self.process_list.append("-p")

        # add source and dest
        self.process_list.append(self.procSource.text())
        self.process_list.append(self.procDest.text())

        # process
        self.get_thread = StartScanThread(self.process_list)
        self.get_thread.finished.connect(self.done_processing)
        self.get_thread.start()
        self.procCancelBtn.setEnabled(True)
        self.procCancelBtn.clicked.connect(self.get_thread.terminate)
        self.procStartBtn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    form = DiskImageProcessorApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
