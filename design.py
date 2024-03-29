# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DiskImageProcessor(object):
    def setupUi(self, DiskImageProcessor):
        DiskImageProcessor.setObjectName("DiskImageProcessor")
        DiskImageProcessor.resize(642, 448)
        self.centralwidget = QtWidgets.QWidget(DiskImageProcessor)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 621, 381))
        self.tabWidget.setObjectName("tabWidget")
        self.analysisTab = QtWidgets.QWidget()
        self.analysisTab.setObjectName("analysisTab")
        self.layoutWidget = QtWidgets.QWidget(self.analysisTab)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 22, 601, 262))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.analysisSource = QtWidgets.QLineEdit(self.layoutWidget)
        self.analysisSource.setObjectName("analysisSource")
        self.horizontalLayout.addWidget(self.analysisSource)
        self.analysisSourceBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.analysisSourceBtn.setObjectName("analysisSourceBtn")
        self.horizontalLayout.addWidget(self.analysisSourceBtn)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.verticalLayout_9.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_6.addWidget(self.label_5)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.analysisDest = QtWidgets.QLineEdit(self.layoutWidget)
        self.analysisDest.setObjectName("analysisDest")
        self.horizontalLayout_2.addWidget(self.analysisDest)
        self.analysisDestBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.analysisDestBtn.setObjectName("analysisDestBtn")
        self.horizontalLayout_2.addWidget(self.analysisDestBtn)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.verticalLayout_9.addLayout(self.verticalLayout_6)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_6 = QtWidgets.QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_7.addWidget(self.label_6)
        self.retainFilesBtn = QtWidgets.QCheckBox(self.layoutWidget)
        self.retainFilesBtn.setObjectName("retainFilesBtn")
        self.verticalLayout_7.addWidget(self.retainFilesBtn)
        self.verticalLayout_9.addLayout(self.verticalLayout_7)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_7 = QtWidgets.QLabel(self.layoutWidget)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_8.addWidget(self.label_7)
        self.analysisStatus = QtWidgets.QLineEdit(self.layoutWidget)
        self.analysisStatus.setObjectName("analysisStatus")
        self.verticalLayout_8.addWidget(self.analysisStatus)
        self.verticalLayout_9.addLayout(self.verticalLayout_8)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.analysisCancelBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.analysisCancelBtn.setObjectName("analysisCancelBtn")
        self.horizontalLayout_3.addWidget(self.analysisCancelBtn)
        self.analysisStartBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.analysisStartBtn.setDefault(True)
        self.analysisStartBtn.setFlat(False)
        self.analysisStartBtn.setObjectName("analysisStartBtn")
        self.horizontalLayout_3.addWidget(self.analysisStartBtn)
        self.verticalLayout_9.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.analysisTab, "")
        self.processingTab = QtWidgets.QWidget()
        self.processingTab.setObjectName("processingTab")
        self.layoutWidget1 = QtWidgets.QWidget(self.processingTab)
        self.layoutWidget1.setGeometry(QtCore.QRect(12, 22, 601, 56))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_10.addWidget(self.label_9)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.procSource = QtWidgets.QLineEdit(self.layoutWidget1)
        self.procSource.setObjectName("procSource")
        self.horizontalLayout_4.addWidget(self.procSource)
        self.procSourceBtn = QtWidgets.QPushButton(self.layoutWidget1)
        self.procSourceBtn.setObjectName("procSourceBtn")
        self.horizontalLayout_4.addWidget(self.procSourceBtn)
        self.verticalLayout_10.addLayout(self.horizontalLayout_4)
        self.verticalLayout_14.addLayout(self.verticalLayout_10)
        self.layoutWidget2 = QtWidgets.QWidget(self.processingTab)
        self.layoutWidget2.setGeometry(QtCore.QRect(12, 84, 601, 258))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_10 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_11.addWidget(self.label_10)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.procDest = QtWidgets.QLineEdit(self.layoutWidget2)
        self.procDest.setObjectName("procDest")
        self.horizontalLayout_5.addWidget(self.procDest)
        self.procDestBtn = QtWidgets.QPushButton(self.layoutWidget2)
        self.procDestBtn.setObjectName("procDestBtn")
        self.horizontalLayout_5.addWidget(self.procDestBtn)
        self.verticalLayout_11.addLayout(self.horizontalLayout_5)
        self.verticalLayout_3.addLayout(self.verticalLayout_11)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.bagBtn = QtWidgets.QCheckBox(self.layoutWidget2)
        self.bagBtn.setObjectName("bagBtn")
        self.verticalLayout_2.addWidget(self.bagBtn)
        self.logicalFilesOnlyBtn = QtWidgets.QCheckBox(self.layoutWidget2)
        self.logicalFilesOnlyBtn.setObjectName("logicalFilesOnlyBtn")
        self.verticalLayout_2.addWidget(self.logicalFilesOnlyBtn)
        self.bulkExtBtn = QtWidgets.QCheckBox(self.layoutWidget2)
        self.bulkExtBtn.setObjectName("bulkExtBtn")
        self.verticalLayout_2.addWidget(self.bulkExtBtn)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_12 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_12.setObjectName("label_12")
        self.verticalLayout_13.addWidget(self.label_12)
        self.procStatus = QtWidgets.QLineEdit(self.layoutWidget2)
        self.procStatus.setObjectName("procStatus")
        self.verticalLayout_13.addWidget(self.procStatus)
        self.verticalLayout_3.addLayout(self.verticalLayout_13)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.procCancelBtn = QtWidgets.QPushButton(self.layoutWidget2)
        self.procCancelBtn.setObjectName("procCancelBtn")
        self.horizontalLayout_6.addWidget(self.procCancelBtn)
        self.procStartBtn = QtWidgets.QPushButton(self.layoutWidget2)
        self.procStartBtn.setDefault(True)
        self.procStartBtn.setFlat(False)
        self.procStartBtn.setObjectName("procStartBtn")
        self.horizontalLayout_6.addWidget(self.procStartBtn)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.tabWidget.addTab(self.processingTab, "")
        self.optionsTab = QtWidgets.QWidget()
        self.optionsTab.setObjectName("optionsTab")
        self.layoutWidget3 = QtWidgets.QWidget(self.optionsTab)
        self.layoutWidget3.setGeometry(QtCore.QRect(20, 20, 479, 105))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget3)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget3)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.unallocBtn = QtWidgets.QCheckBox(self.layoutWidget3)
        self.unallocBtn.setObjectName("unallocBtn")
        self.verticalLayout.addWidget(self.unallocBtn)
        self.resForksBtn = QtWidgets.QCheckBox(self.layoutWidget3)
        self.resForksBtn.setObjectName("resForksBtn")
        self.verticalLayout.addWidget(self.resForksBtn)
        self.quietLogBtn = QtWidgets.QCheckBox(self.layoutWidget3)
        self.quietLogBtn.setObjectName("quietLogBtn")
        self.verticalLayout.addWidget(self.quietLogBtn)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.tabWidget.addTab(self.optionsTab, "")
        DiskImageProcessor.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(DiskImageProcessor)
        self.statusbar.setObjectName("statusbar")
        DiskImageProcessor.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(DiskImageProcessor)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 642, 25))
        self.menubar.setObjectName("menubar")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        DiskImageProcessor.setMenuBar(self.menubar)
        self.actionAbout = QtWidgets.QAction(DiskImageProcessor)
        self.actionAbout.setObjectName("actionAbout")
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(DiskImageProcessor)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(DiskImageProcessor)

    def retranslateUi(self, DiskImageProcessor):
        _translate = QtCore.QCoreApplication.translate
        DiskImageProcessor.setWindowTitle(
            _translate("DiskImageProcessor", "Disk Image Processor")
        )
        self.label.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">Source</span></p></body></html>',
            )
        )
        self.analysisSource.setPlaceholderText(
            _translate("DiskImageProcessor", "/path/to/source/directory")
        )
        self.analysisSourceBtn.setText(_translate("DiskImageProcessor", "Browse"))
        self.label_5.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">Destination</span></p></body></html>',
            )
        )
        self.analysisDest.setPlaceholderText(
            _translate("DiskImageProcessor", "/path/to/output/directory")
        )
        self.analysisDestBtn.setText(_translate("DiskImageProcessor", "Browse"))
        self.label_6.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">Options</span></p></body></html>',
            )
        )
        self.retainFilesBtn.setText(
            _translate("DiskImageProcessor", "Retain logical files at end of process")
        )
        self.label_7.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">Status</span></p></body></html>',
            )
        )
        self.analysisCancelBtn.setText(_translate("DiskImageProcessor", "Cancel"))
        self.analysisStartBtn.setText(
            _translate("DiskImageProcessor", "Start analysis")
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.analysisTab),
            _translate("DiskImageProcessor", "Analysis"),
        )
        self.label_9.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">Source</span></p></body></html>',
            )
        )
        self.procSource.setPlaceholderText(
            _translate("DiskImageProcessor", "/path/to/source/directory")
        )
        self.procSourceBtn.setText(_translate("DiskImageProcessor", "Browse"))
        self.label_10.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">Destination</span></p></body></html>',
            )
        )
        self.procDest.setPlaceholderText(
            _translate("DiskImageProcessor", "/path/to/output/directory")
        )
        self.procDestBtn.setText(_translate("DiskImageProcessor", "Browse"))
        self.label_2.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">Options</span></p></body></html>',
            )
        )
        self.bagBtn.setText(_translate("DiskImageProcessor", "Bag SIPs"))
        self.logicalFilesOnlyBtn.setText(
            _translate(
                "DiskImageProcessor", "Make SIPs from carved files only (no disk image)"
            )
        )
        self.bulkExtBtn.setText(_translate("DiskImageProcessor", "Run bulk_extractor"))
        self.label_12.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">Status</span></p></body></html>',
            )
        )
        self.procCancelBtn.setText(_translate("DiskImageProcessor", "Cancel"))
        self.procStartBtn.setText(_translate("DiskImageProcessor", "Start processing"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.processingTab),
            _translate("DiskImageProcessor", "Processing"),
        )
        self.label_3.setText(
            _translate(
                "DiskImageProcessor",
                '<html><head/><body><p><span style=" font-weight:600;">General options</span></p></body></html>',
            )
        )
        self.unallocBtn.setText(
            _translate(
                "DiskImageProcessor",
                "Include deleted/unallocated files (excluding HFS-formatted disks)",
            )
        )
        self.resForksBtn.setText(
            _translate(
                "DiskImageProcessor",
                "Include AppleDouble resource forks (HFS-formatted disks)",
            )
        )
        self.quietLogBtn.setText(
            _translate(
                "DiskImageProcessor", "Include only Error messages in log (--quiet)"
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.optionsTab),
            _translate("DiskImageProcessor", "Options"),
        )
        self.menuAbout.setTitle(_translate("DiskImageProcessor", "About"))
        self.actionAbout.setText(_translate("DiskImageProcessor", "About"))
        self.actionAbout.setToolTip(_translate("DiskImageProcessor", "About"))
