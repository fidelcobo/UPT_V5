# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './Fich_Designer/csv_consolidated.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_consulta_csv(object):
    def setupUi(self, consulta_csv):
        consulta_csv.setObjectName("consulta_csv")
        consulta_csv.setWindowModality(QtCore.Qt.WindowModal)
        consulta_csv.resize(313, 218)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/capture.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        consulta_csv.setWindowIcon(icon)
        self.boton_si = QtWidgets.QPushButton(consulta_csv)
        self.boton_si.setGeometry(QtCore.QRect(50, 150, 93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.boton_si.setFont(font)
        self.boton_si.setObjectName("boton_si")
        self.boton_no = QtWidgets.QPushButton(consulta_csv)
        self.boton_no.setGeometry(QtCore.QRect(170, 150, 93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.boton_no.setFont(font)
        self.boton_no.setObjectName("boton_no")
        self.mensaje = QtWidgets.QLabel(consulta_csv)
        self.mensaje.setGeometry(QtCore.QRect(40, 50, 231, 71))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.mensaje.setFont(font)
        self.mensaje.setStyleSheet("color: rgb(170, 0, 0);")
        self.mensaje.setAlignment(QtCore.Qt.AlignCenter)
        self.mensaje.setObjectName("mensaje")

        self.retranslateUi(consulta_csv)
        QtCore.QMetaObject.connectSlotsByName(consulta_csv)

    def retranslateUi(self, consulta_csv):
        _translate = QtCore.QCoreApplication.translate
        consulta_csv.setWindowTitle(_translate("consulta_csv", "Consolidación csv"))
        self.boton_si.setText(_translate("consulta_csv", "SÍ"))
        self.boton_no.setText(_translate("consulta_csv", "NO"))
        self.mensaje.setText(_translate("consulta_csv", "¿Desea consolidar las \n"
" entradas del fichero .csv"))
import icons_rc