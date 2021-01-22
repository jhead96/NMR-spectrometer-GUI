# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'spectrometer_tabbed.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(900,700)
        mainWindow.setAnimated(True)
        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.mainTab = QtWidgets.QTabWidget(self.centralwidget)
        self.mainTab.setEnabled(True)
        self.mainTab.setTabPosition(QtWidgets.QTabWidget.North)
        self.mainTab.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.mainTab.setObjectName("mainTab")
        self.tab_sample = QtWidgets.QWidget()
        self.tab_sample.setObjectName("tab_sample")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_sample)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.dataFileNameLbl = QtWidgets.QLabel(self.tab_sample)
        self.dataFileNameLbl.setObjectName("dataFileNameLbl")
        self.gridLayout_2.addWidget(self.dataFileNameLbl, 3, 0, 1, 1)
        self.dataFileNameLineEdit = QtWidgets.QLineEdit(self.tab_sample)
        self.dataFileNameLineEdit.setObjectName("dataFileNameLineEdit")
        self.gridLayout_2.addWidget(self.dataFileNameLineEdit, 3, 1, 1, 1)
        self.sampleTitleLbl = QtWidgets.QLabel(self.tab_sample)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sampleTitleLbl.sizePolicy().hasHeightForWidth())
        self.sampleTitleLbl.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.sampleTitleLbl.setFont(font)
        self.sampleTitleLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.sampleTitleLbl.setObjectName("sampleTitleLbl")
        self.gridLayout_2.addWidget(self.sampleTitleLbl, 0, 0, 1, 2)
        self.sampleNameLineEdit = QtWidgets.QLineEdit(self.tab_sample)
        self.sampleNameLineEdit.setObjectName("sampleNameLineEdit")
        self.gridLayout_2.addWidget(self.sampleNameLineEdit, 1, 1, 1, 1)
        self.sampleNameLbl = QtWidgets.QLabel(self.tab_sample)
        self.sampleNameLbl.setObjectName("sampleNameLbl")
        self.gridLayout_2.addWidget(self.sampleNameLbl, 1, 0, 1, 1)
        self.sampleMassLbl = QtWidgets.QLabel(self.tab_sample)
        self.sampleMassLbl.setObjectName("sampleMassLbl")
        self.gridLayout_2.addWidget(self.sampleMassLbl, 2, 0, 1, 1)
        self.sampleMassLineEdit = QtWidgets.QLineEdit(self.tab_sample)
        self.sampleMassLineEdit.setObjectName("sampleMassLineEdit")
        self.gridLayout_2.addWidget(self.sampleMassLineEdit, 2, 1, 1, 1)
        self.sampleTabNextBtn = QtWidgets.QPushButton(self.tab_sample)
        self.sampleTabNextBtn.setObjectName("sampleTabNextBtn")
        self.gridLayout_2.addWidget(self.sampleTabNextBtn, 9, 1, 1, 1)
        self.dataFileLocLbl = QtWidgets.QLabel(self.tab_sample)
        self.dataFileLocLbl.setObjectName("dataFileLocLbl")
        self.gridLayout_2.addWidget(self.dataFileLocLbl, 4, 0, 1, 1)
        self.dataFileBrowseBtn = QtWidgets.QPushButton(self.tab_sample)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataFileBrowseBtn.sizePolicy().hasHeightForWidth())
        self.dataFileBrowseBtn.setSizePolicy(sizePolicy)
        self.dataFileBrowseBtn.setDefault(False)
        self.dataFileBrowseBtn.setObjectName("dataFileBrowseBtn")
        self.gridLayout_2.addWidget(self.dataFileBrowseBtn, 5, 1, 1, 1)
        self.dataFileGenerateLbl = QtWidgets.QLabel(self.tab_sample)
        self.dataFileGenerateLbl.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataFileGenerateLbl.sizePolicy().hasHeightForWidth())
        self.dataFileGenerateLbl.setSizePolicy(sizePolicy)
        self.dataFileGenerateLbl.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dataFileGenerateLbl.setFont(font)
        self.dataFileGenerateLbl.setScaledContents(False)
        self.dataFileGenerateLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.dataFileGenerateLbl.setObjectName("dataFileGenerateLbl")
        self.dataFileGenerateLbl.setHidden(True)
        self.gridLayout_2.addWidget(self.dataFileGenerateLbl, 8, 1, 1, 1)
        self.dataFileLineEdit = QtWidgets.QLineEdit(self.tab_sample)
        self.dataFileLineEdit.setEnabled(True)
        self.dataFileLineEdit.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.dataFileLineEdit.setAutoFillBackground(False)
        self.dataFileLineEdit.setText("")
        self.dataFileLineEdit.setReadOnly(True)
        self.dataFileLineEdit.setClearButtonEnabled(False)
        self.dataFileLineEdit.setObjectName("dataFileLineEdit")
        self.gridLayout_2.addWidget(self.dataFileLineEdit, 4, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.tab_sample)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 6, 1, 1, 1)
        self.mainTab.addTab(self.tab_sample, "")
        self.tab_seq = QtWidgets.QWidget()
        self.tab_seq.setObjectName("tab_seq")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_seq)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.savedSeqLbl = QtWidgets.QLabel(self.tab_seq)
        self.savedSeqLbl.setObjectName("savedSeqLbl")
        self.gridLayout_3.addWidget(self.savedSeqLbl, 6, 3, 1, 1)
        self.gapLenLbl = QtWidgets.QLabel(self.tab_seq)
        self.gapLenLbl.setObjectName("gapLenLbl")
        self.gridLayout_3.addWidget(self.gapLenLbl, 5, 0, 1, 1)
        self.phaseLbl = QtWidgets.QLabel(self.tab_seq)
        self.phaseLbl.setObjectName("phaseLbl")
        self.gridLayout_3.addWidget(self.phaseLbl, 2, 0, 1, 1)
        self.pulse2LenLbl = QtWidgets.QLabel(self.tab_seq)
        self.pulse2LenLbl.setObjectName("pulse2LenLbl")
        self.gridLayout_3.addWidget(self.pulse2LenLbl, 4, 0, 1, 1)
        self.frequencyLineEdit = QtWidgets.QLineEdit(self.tab_seq)
        self.frequencyLineEdit.setObjectName("frequencyLineEdit")
        self.gridLayout_3.addWidget(self.frequencyLineEdit, 1, 1, 1, 1)
        self.pulse1LenLineEdit = QtWidgets.QLineEdit(self.tab_seq)
        self.pulse1LenLineEdit.setObjectName("pulse1LenLineEdit")
        self.gridLayout_3.addWidget(self.pulse1LenLineEdit, 3, 1, 1, 1)
        self.pulse2LenLineEdit = QtWidgets.QLineEdit(self.tab_seq)
        self.pulse2LenLineEdit.setObjectName("pulse2LenLineEdit")
        self.gridLayout_3.addWidget(self.pulse2LenLineEdit, 4, 1, 1, 1)
        self.gapLenLineEdit = QtWidgets.QLineEdit(self.tab_seq)
        self.gapLenLineEdit.setObjectName("gapLenLineEdit")
        self.gridLayout_3.addWidget(self.gapLenLineEdit, 5, 1, 1, 1)
        self.loadedSeqLbl = QtWidgets.QLabel(self.tab_seq)
        self.loadedSeqLbl.setObjectName("loadedSeqLbl")
        self.gridLayout_3.addWidget(self.loadedSeqLbl, 1, 3, 1, 1)
        self.pulse1LenLbl = QtWidgets.QLabel(self.tab_seq)
        self.pulse1LenLbl.setObjectName("pulse1LenLbl")
        self.gridLayout_3.addWidget(self.pulse1LenLbl, 3, 0, 1, 1)
        self.clearAllBtn = QtWidgets.QPushButton(self.tab_seq)
        self.clearAllBtn.setObjectName("clearAllBtn")
        self.gridLayout_3.addWidget(self.clearAllBtn, 7, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 4, 2, 1, 1)
        self.recLenLineEdit = QtWidgets.QLineEdit(self.tab_seq)
        self.recLenLineEdit.setObjectName("recLenLineEdit")
        self.gridLayout_3.addWidget(self.recLenLineEdit, 6, 1, 1, 1)
        self.frequencyLbl = QtWidgets.QLabel(self.tab_seq)
        self.frequencyLbl.setObjectName("frequencyLbl")
        self.gridLayout_3.addWidget(self.frequencyLbl, 1, 0, 1, 1)
        self.phaseComboBox = QtWidgets.QComboBox(self.tab_seq)
        self.phaseComboBox.setObjectName("phaseComboBox")
        self.phaseComboBox.addItem("")
        self.phaseComboBox.addItem("")
        self.phaseComboBox.addItem("")
        self.phaseComboBox.addItem("")
        self.gridLayout_3.addWidget(self.phaseComboBox, 2, 1, 1, 1)
        self.recordLenLbl = QtWidgets.QLabel(self.tab_seq)
        self.recordLenLbl.setObjectName("recordLenLbl")
        self.gridLayout_3.addWidget(self.recordLenLbl, 6, 0, 1, 1)
        self.savedSeqLineEdit = QtWidgets.QLineEdit(self.tab_seq)
        self.savedSeqLineEdit.setObjectName("savedSeqLineEdit")
        self.gridLayout_3.addWidget(self.savedSeqLineEdit, 6, 4, 1, 1)
        self.loadedSeqLineEdit = QtWidgets.QLineEdit(self.tab_seq)
        self.loadedSeqLineEdit.setReadOnly(True)
        self.loadedSeqLineEdit.setObjectName("loadedSeqLineEdit")
        self.gridLayout_3.addWidget(self.loadedSeqLineEdit, 1, 4, 1, 1)
        self.loadSeqBtn = QtWidgets.QPushButton(self.tab_seq)
        self.loadSeqBtn.setObjectName("loadSeqBtn")
        self.gridLayout_3.addWidget(self.loadSeqBtn, 2, 4, 1, 1)
        self.saveSeqTitleLbl = QtWidgets.QLabel(self.tab_seq)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.saveSeqTitleLbl.setFont(font)
        self.saveSeqTitleLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.saveSeqTitleLbl.setObjectName("saveSeqTitleLbl")
        self.gridLayout_3.addWidget(self.saveSeqTitleLbl, 4, 3, 1, 2)
        self.seqTabReturnBtn = QtWidgets.QPushButton(self.tab_seq)
        self.seqTabReturnBtn.setObjectName("seqTabReturnBtn")
        self.gridLayout_3.addWidget(self.seqTabReturnBtn, 8, 0, 1, 2)
        self.loadSeqTitleLbl = QtWidgets.QLabel(self.tab_seq)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.loadSeqTitleLbl.setFont(font)
        self.loadSeqTitleLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.loadSeqTitleLbl.setObjectName("loadSeqTitleLbl")
        self.gridLayout_3.addWidget(self.loadSeqTitleLbl, 0, 3, 1, 2)
        self.createSeqLbl = QtWidgets.QLabel(self.tab_seq)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.createSeqLbl.sizePolicy().hasHeightForWidth())
        self.createSeqLbl.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.createSeqLbl.setFont(font)
        self.createSeqLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.createSeqLbl.setObjectName("createSeqLbl")
        self.gridLayout_3.addWidget(self.createSeqLbl, 0, 0, 1, 2)
        self.seqTabNextBtn = QtWidgets.QPushButton(self.tab_seq)
        self.seqTabNextBtn.setObjectName("seqTabNextBtn")
        self.gridLayout_3.addWidget(self.seqTabNextBtn, 8, 3, 1, 2)
        self.saveSeqBtn = QtWidgets.QPushButton(self.tab_seq)
        self.saveSeqBtn.setObjectName("saveSeqBtn")
        self.gridLayout_3.addWidget(self.saveSeqBtn, 5, 3, 1, 2)
        self.mainTab.addTab(self.tab_seq, "")
        self.tab_expt = QtWidgets.QWidget()
        self.tab_expt.setObjectName("tab_expt")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.tab_expt)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.selectSeqLbl = QtWidgets.QLabel(self.tab_expt)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.selectSeqLbl.setFont(font)
        self.selectSeqLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.selectSeqLbl.setObjectName("selectSeqLbl")
        self.gridLayout_8.addWidget(self.selectSeqLbl, 0, 0, 1, 1)
        self.selectedSeqLbl = QtWidgets.QLabel(self.tab_expt)
        self.selectedSeqLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.selectedSeqLbl.setObjectName("selectedSeqLbl")
        self.gridLayout_8.addWidget(self.selectedSeqLbl, 3, 0, 1, 1)
        self.browseSeqBtn = QtWidgets.QPushButton(self.tab_expt)
        self.browseSeqBtn.setObjectName("browseSeqBtn")
        self.gridLayout_8.addWidget(self.browseSeqBtn, 2, 0, 1, 1)
        self.selectSeqLineEdit = QtWidgets.QLineEdit(self.tab_expt)
        self.selectSeqLineEdit.setObjectName("selectSeqLineEdit")
        self.gridLayout_8.addWidget(self.selectSeqLineEdit, 1, 0, 1, 1)
        self.mainTab.addTab(self.tab_expt, "")
        self.tab_data = QtWidgets.QWidget()
        self.tab_data.setObjectName("tab_data")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_data)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.plotTab = QtWidgets.QTabWidget(self.tab_data)
        self.plotTab.setTabPosition(QtWidgets.QTabWidget.South)
        self.plotTab.setObjectName("plotTab")
        self.tab_time = QtWidgets.QWidget()
        self.tab_time.setObjectName("tab_time")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.tab_time)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 701, 451))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.timePlotWidget = MplWidget(self.verticalLayoutWidget)
        self.timePlotWidget.setObjectName("timePlotWidget")
        self.gridLayout_6.addWidget(self.timePlotWidget, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_6)
        self.plotTab.addTab(self.tab_time, "")
        self.tab_frq = QtWidgets.QWidget()
        self.tab_frq.setObjectName("tab_frq")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.tab_frq)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 701, 451))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.frqPlotWidget = MplWidget(self.gridLayoutWidget_2)
        self.frqPlotWidget.setObjectName("frqPlotWidget")
        self.gridLayout_7.addWidget(self.frqPlotWidget, 0, 0, 1, 1)
        self.plotTab.addTab(self.tab_frq, "")
        self.gridLayout_4.addWidget(self.plotTab, 0, 0, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.genDataBtn = QtWidgets.QPushButton(self.tab_data)
        self.genDataBtn.setObjectName("genDataBtn")
        self.gridLayout_5.addWidget(self.genDataBtn, 1, 0, 1, 1)
        self.chComboBox = QtWidgets.QComboBox(self.tab_data)
        self.chComboBox.setObjectName("chComboBox")
        self.chComboBox.addItem("")
        self.chComboBox.addItem("")
        self.gridLayout_5.addWidget(self.chComboBox, 0, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_5, 0, 1, 1, 1)
        self.mainTab.addTab(self.tab_data, "")
        self.tab_debug = QtWidgets.QWidget()
        self.tab_debug.setObjectName("tab_debug")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_debug)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.function1Btn = QtWidgets.QPushButton(self.tab_debug)
        self.function1Btn.setObjectName("function1Btn")
        self.verticalLayout_2.addWidget(self.function1Btn)
        self.function2Btn = QtWidgets.QPushButton(self.tab_debug)
        self.function2Btn.setObjectName("function2Btn")
        self.verticalLayout_2.addWidget(self.function2Btn)
        self.function3Btn = QtWidgets.QPushButton(self.tab_debug)
        self.function3Btn.setObjectName("function3Btn")
        self.verticalLayout_2.addWidget(self.function3Btn)
        self.mainTab.addTab(self.tab_debug, "")
        self.gridLayout.addWidget(self.mainTab, 0, 0, 1, 1)
        mainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)
        self.mainTab.setCurrentIndex(0)
        self.plotTab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "NMR Spectrometer"))
        self.dataFileNameLbl.setText(_translate("mainWindow", "Data File name"))
        self.sampleTitleLbl.setText(_translate("mainWindow", "Enter Sample Information"))
        self.sampleNameLbl.setText(_translate("mainWindow", "Sample Name"))
        self.sampleMassLbl.setText(_translate("mainWindow", "Sample Mass (mg)"))
        self.sampleTabNextBtn.setText(_translate("mainWindow", "Next"))
        self.dataFileLocLbl.setText(_translate("mainWindow", "Data File save location"))
        self.dataFileBrowseBtn.setText(_translate("mainWindow", "Browse"))
        self.dataFileGenerateLbl.setText(_translate("mainWindow", "Data file generated!"))
        self.dataFileLineEdit.setPlaceholderText(_translate("mainWindow", "No Data File location selected!"))
        self.pushButton.setText(_translate("mainWindow", "Confirm and generate file"))
        self.mainTab.setTabText(self.mainTab.indexOf(self.tab_sample), _translate("mainWindow", "Sample"))
        self.savedSeqLbl.setText(_translate("mainWindow", "Saved Sequence"))
        self.gapLenLbl.setText(_translate("mainWindow", "Gap Length (ns)"))
        self.phaseLbl.setText(_translate("mainWindow", "Phase"))
        self.pulse2LenLbl.setText(_translate("mainWindow", "Pulse 2 Length (ns)"))
        self.loadedSeqLbl.setText(_translate("mainWindow", "Loaded sequence"))
        self.pulse1LenLbl.setText(_translate("mainWindow", "Pulse 1 Length (ns)"))
        self.clearAllBtn.setText(_translate("mainWindow", "Clear all"))
        self.frequencyLbl.setText(_translate("mainWindow", "Frequency (MHz)"))
        self.phaseComboBox.setItemText(0, _translate("mainWindow", "0"))
        self.phaseComboBox.setItemText(1, _translate("mainWindow", "90"))
        self.phaseComboBox.setItemText(2, _translate("mainWindow", "180"))
        self.phaseComboBox.setItemText(3, _translate("mainWindow", "270"))
        self.recordLenLbl.setText(_translate("mainWindow", "Record Length (ns)"))
        self.savedSeqLineEdit.setPlaceholderText(_translate("mainWindow", "No Sequence Saved!"))
        self.loadedSeqLineEdit.setPlaceholderText(_translate("mainWindow", "No Sequence Loaded!"))
        self.loadSeqBtn.setText(_translate("mainWindow", "Load Sequence"))
        self.saveSeqTitleLbl.setText(_translate("mainWindow", "Save sequence"))
        self.seqTabReturnBtn.setText(_translate("mainWindow", "Return"))
        self.loadSeqTitleLbl.setText(_translate("mainWindow", "Load sequence"))
        self.createSeqLbl.setText(_translate("mainWindow", "Create sequence"))
        self.seqTabNextBtn.setText(_translate("mainWindow", "Next"))
        self.saveSeqBtn.setText(_translate("mainWindow", "Save Sequence"))
        self.mainTab.setTabText(self.mainTab.indexOf(self.tab_seq), _translate("mainWindow", "Sequence"))
        self.selectSeqLbl.setText(_translate("mainWindow", "Select Sequence"))
        self.selectedSeqLbl.setText(_translate("mainWindow", "No Sequence Loaded!"))
        self.browseSeqBtn.setText(_translate("mainWindow", "Browse"))
        self.mainTab.setTabText(self.mainTab.indexOf(self.tab_expt), _translate("mainWindow", "Experiment"))
        self.plotTab.setTabText(self.plotTab.indexOf(self.tab_time), _translate("mainWindow", "Time"))
        self.plotTab.setTabText(self.plotTab.indexOf(self.tab_frq), _translate("mainWindow", "Frequency"))
        self.genDataBtn.setText(_translate("mainWindow", "Generate Data"))
        self.chComboBox.setItemText(0, _translate("mainWindow", "Ch A"))
        self.chComboBox.setItemText(1, _translate("mainWindow", "Ch B"))
        self.mainTab.setTabText(self.mainTab.indexOf(self.tab_data), _translate("mainWindow", "Data"))
        self.function1Btn.setText(_translate("mainWindow", "Function 1"))
        self.function2Btn.setText(_translate("mainWindow", "Function 2"))
        self.function3Btn.setText(_translate("mainWindow", "Function 3"))
        self.mainTab.setTabText(self.mainTab.indexOf(self.tab_debug), _translate("mainWindow", "Debug"))
from mplwidget import MplWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_mainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
