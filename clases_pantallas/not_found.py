# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'not_found.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_not_found(object):
    def setupUi(self, not_found):
        not_found.setObjectName("not_found")
        not_found.resize(400, 433)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Alien.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        not_found.setWindowIcon(icon)
        not_found.setStyleSheet("QDialog{background-color: rgb(213, 213, 213);}")
        self.label = QtWidgets.QLabel(not_found)
        self.label.setGeometry(QtCore.QRect(70, 40, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.not_found_list = QtWidgets.QListWidget(not_found)
        self.not_found_list.setGeometry(QtCore.QRect(70, 90, 256, 221))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.not_found_list.setFont(font)
        self.not_found_list.setObjectName("not_found_list")
        self.ok_button = QtWidgets.QPushButton(not_found)
        self.ok_button.setGeometry(QtCore.QRect(164, 340, 81, 51))
        self.ok_button.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.994, y1:0.869318, x2:1, y2:0, stop:0 rgba(134, 150, 255, 255), stop:1 rgba(227, 227, 227, 255));")
        self.ok_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Apply.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ok_button.setIcon(icon1)
        self.ok_button.setIconSize(QtCore.QSize(32, 32))
        self.ok_button.setObjectName("ok_button")

        self.retranslateUi(not_found)
        QtCore.QMetaObject.connectSlotsByName(not_found)

    def retranslateUi(self, not_found):
        _translate = QtCore.QCoreApplication.translate
        not_found.setWindowTitle(_translate("not_found", "No encontrados"))
        self.label.setText(_translate("not_found", "Códigos Cisco no encontrados"))

from clases_pantallas import icons_rc
