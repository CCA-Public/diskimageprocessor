# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(602, 689)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.source1 = QtGui.QLineEdit(self.centralwidget)
        self.source1.setObjectName(_fromUtf8("source1"))
        self.verticalLayout.addWidget(self.source1)
        self.source1btn = QtGui.QPushButton(self.centralwidget)
        self.source1btn.setObjectName(_fromUtf8("source1btn"))
        self.verticalLayout.addWidget(self.source1btn)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.destination1 = QtGui.QLineEdit(self.centralwidget)
        self.destination1.setObjectName(_fromUtf8("destination1"))
        self.verticalLayout.addWidget(self.destination1)
        self.destination1btn = QtGui.QPushButton(self.centralwidget)
        self.destination1btn.setObjectName(_fromUtf8("destination1btn"))
        self.verticalLayout.addWidget(self.destination1btn)
        self.label_6 = QtGui.QLabel(self.centralwidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.analysisBtn = QtGui.QRadioButton(self.centralwidget)
        self.analysisBtn.setChecked(False)
        self.analysisBtn.setObjectName(_fromUtf8("analysisBtn"))
        self.verticalLayout.addWidget(self.analysisBtn)
        self.processingBtn = QtGui.QRadioButton(self.centralwidget)
        self.processingBtn.setChecked(True)
        self.processingBtn.setObjectName(_fromUtf8("processingBtn"))
        self.verticalLayout.addWidget(self.processingBtn)
        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.sleuthkit = QtGui.QRadioButton(self.centralwidget)
        self.sleuthkit.setChecked(True)
        self.sleuthkit.setAutoRepeat(False)
        self.sleuthkit.setObjectName(_fromUtf8("sleuthkit"))
        self.buttonGroup_2 = QtGui.QButtonGroup(MainWindow)
        self.buttonGroup_2.setObjectName(_fromUtf8("buttonGroup_2"))
        self.buttonGroup_2.addButton(self.sleuthkit)
        self.verticalLayout.addWidget(self.sleuthkit)
        self.mountcopy = QtGui.QRadioButton(self.centralwidget)
        self.mountcopy.setObjectName(_fromUtf8("mountcopy"))
        self.buttonGroup_2.addButton(self.mountcopy)
        self.verticalLayout.addWidget(self.mountcopy)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.checkBox = QtGui.QCheckBox(self.centralwidget)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout.addWidget(self.checkBox)
        self.filesonlyBtn = QtGui.QCheckBox(self.centralwidget)
        self.filesonlyBtn.setObjectName(_fromUtf8("filesonlyBtn"))
        self.verticalLayout.addWidget(self.filesonlyBtn)
        self.checkBox_3 = QtGui.QCheckBox(self.centralwidget)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.verticalLayout.addWidget(self.checkBox_3)
        self.resforksBtn = QtGui.QCheckBox(self.centralwidget)
        self.resforksBtn.setObjectName(_fromUtf8("resforksBtn"))
        self.verticalLayout.addWidget(self.resforksBtn)
        self.label_7 = QtGui.QLabel(self.centralwidget)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout.addWidget(self.label_7)
        self.textEdit = QtGui.QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.verticalLayout.addWidget(self.textEdit)
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.verticalLayout.addWidget(self.lineEdit)
        self.process = QtGui.QPushButton(self.centralwidget)
        self.process.setObjectName(_fromUtf8("process"))
        self.verticalLayout.addWidget(self.process)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Disk Image Processor", None))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Source</span></p></body></html>", None))
        self.source1.setPlaceholderText(_translate("MainWindow", "/path/to/source", None))
        self.source1btn.setText(_translate("MainWindow", "Browse", None))
        self.label_3.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Destination</span></p></body></html>", None))
        self.destination1.setPlaceholderText(_translate("MainWindow", "/path/to/destination", None))
        self.destination1btn.setText(_translate("MainWindow", "Browse", None))
        self.label_6.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Mode</span></p></body></html>", None))
        self.analysisBtn.setText(_translate("MainWindow", "Analysis", None))
        self.processingBtn.setText(_translate("MainWindow", "Processing", None))
        self.label_5.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Processing toolset (for non-HFS, non-UDF disks)</span></p></body></html>", None))
        self.sleuthkit.setText(_translate("MainWindow", "tsk_recover and fiwalk", None))
        self.mountcopy.setText(_translate("MainWindow", "mount-copy and walk_to_dfxml.py", None))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Processing options</span></p></body></html>", None))
        self.checkBox.setText(_translate("MainWindow", "Bag SIPs", None))
        self.filesonlyBtn.setText(_translate("MainWindow", "Make SIPs from logical files only (do not include disk image)", None))
        self.checkBox_3.setText(_translate("MainWindow", "Run bulk_extractor", None))
        self.resforksBtn.setText(_translate("MainWindow", "unhfs: Export AppleDouble resource forks", None))
        self.label_7.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Detailed output</span></p></body></html>", None))
        self.label_4.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Status</span></p></body></html>", None))
        self.process.setText(_translate("MainWindow", "Process disk images", None))

