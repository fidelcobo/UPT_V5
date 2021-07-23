import os
import openpyxl

from PyQt5 import QtWidgets
from PyQt5.QtCore import *

from clases_pantallas import Ui_Maintenance_Dialog
from clases_pantallas import Ui_not_found, Ui_consulta_csv
from procedimientos_auxiliares import csv_from_excel

from procedimientos_principales import calculo_backouts
from procedimientos_principales import generacion_csv
from version import VERSION


class SignalsProc(QObject):
    """
    En esta clase se definen las señales multithreading que se usarán para indicar eventos en el
    procesado de las ofertas
    """

    informacion = pyqtSignal(str)
    error_fichero = pyqtSignal(str)
    buscando = pyqtSignal()
    warning = pyqtSignal(str)
    # error_oferta = pyqtSignal()
    fin_OK_backouts = pyqtSignal(object, list, object)
    fin_OK_csv = pyqtSignal(object, object, object, object, bool)


class NotFound(QtWidgets.QDialog, Ui_not_found):  # Usada para presentar la pantalla de códigos no encontrados

    def __init__(self, lista):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.lista = lista

        for item in self.lista:
            self.not_found_list.addItem(item)

        self.ok_button.clicked.connect(self.close)


class CsvConsolidated(QtWidgets.QDialog, Ui_consulta_csv):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.consolidated = True

        self.boton_si.clicked.connect(self.close)
        self.boton_no.clicked.connect(self.no_consolidar)

    def no_consolidar(self):
        self.consolidated = False
        self.close()


class ProcesarBackout(QRunnable):
    """
    Clase usada para correr en multithreading el procedimiento principal calculo_backouts
    """

    def __init__(self, *args):
        super(ProcesarBackout, self).__init__()
        self.fich_a = args[0]
        self.light = args[3]
        self.signals = SignalsProc()

    @pyqtSlot()
    def run(self):
        calculo_backouts(self.fich_a, self.light, self)


class ProcesarCsv(QRunnable):
    """
    Esta clase se usa para poder correr en modo multithreading el procedimiento principal
    generacion_csv
    """

    def __init__(self, *args):
        super(ProcesarCsv, self).__init__()
        self.fich_a = args[0]
        self.consolidated = args[1]
        self.oferta_cliente = args[2]
        self.signals = SignalsProc()

    @pyqtSlot()
    def run(self):
        generacion_csv(self.fich_a, self.consolidated, self.oferta_cliente, self)


class Mantenimiento(QtWidgets.QDialog, Ui_Maintenance_Dialog):
    """
    Esta es la clase principal del programa.
    Contiene todos los procedimientos necesarios para procesar la oferta
    Se comunica mediante señales multithreading Qt5 con los procedimientos principales
    calculo_backouts y generate_csv. Maneja los diversos elementos de las pantallas GUI.
    """

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # Bloque de inicialización de parámetros de la clase
        # lista_precios = self.buscar_ficheros_precios()
        self.version.setText(VERSION)
        self.fich_oferta.setText('')
        # self.fich_precios_normal.setText(lista_precios[0][:-1])
        # self.fich_precios_UCS.setText(lista_precios[1][:-1])
        self.backout_button.setChecked(True)
        self.activar_precios()
        self.progreso.hide()
        self.plantillaLight.hide()  # Versión 4. Este elemento deja de valer
        self.oferta_cliente.hide()

        self.threadpool = QThreadPool()

        # Bloque de comprobación de eventos
        self.cancel_button.clicked.connect(self.close)
        self.ok_button.clicked.connect(self.procesar_oferta)
        self.browse_offer.clicked.connect(self.buscar_oferta)
        # self.browse_Cisco.clicked.connect(self.buscar_cisco_file)
        # self.browse_UCS.clicked.connect(self.buscar_ucs_file)
        self.csv_button.clicked.connect(self.desactivar_precios)
        self.backout_button.clicked.connect(self.activar_precios)

    def desactivar_precios(self):
        self.operacion.setText('Generación de csv')
        self.oferta_cliente.show()
        # self.fich_precios_normal.setEnabled(False)
        # self.fich_precios_UCS.setEnabled(False)
        # self.fich_precios_normal.hide()
        # self.fich_precios_UCS.hide()
        # self.browse_Cisco.setEnabled(False)
        # self.browse_UCS.setEnabled(False)
        # self.browse_Cisco.hide()
        # self.browse_UCS.hide()

    def activar_precios(self):
        self.operacion.setText('Búsqueda de backouts')
        self.oferta_cliente.hide()
        # self.fich_precios_normal.setEnabled(True)
        # self.fich_precios_UCS.setEnabled(True)
        # self.fich_precios_normal.show()
        # self.fich_precios_UCS.show()
        # self.browse_Cisco.setEnabled(True)
        # self.browse_UCS.setEnabled(True)
        # self.browse_Cisco.show()
        # self.browse_UCS.show()

    def procesar_oferta(self):

        if self.backout_button.isChecked():  # Se buscarán los backouts y sus GPLs

            if self.fich_oferta.text():

                self.cancel_button.setEnabled(True)
                self.ok_button.setEnabled(False)
                # if self.plantillaLight.isChecked():
                #     light = True
                # else:
                #     light = False
                light = False  # Versión 4. Parámetro sin uso. El bloque if-else anterior se suprime
                trabajo = ProcesarBackout(self.fich_oferta.text(), None,
                                          None, light)
                trabajo.signals.informacion.connect(self.reportar)
                trabajo.signals.fin_OK_backouts.connect(self.finalizar_backouts)
                trabajo.signals.buscando.connect(self.buscando)
                # trabajo.signals.error_oferta.connect(self.fallo_oferta)
                trabajo.signals.error_fichero.connect(self.notif_error)
                trabajo.signals.warning.connect(self.notif_warning)

                self.threadpool.start(trabajo)

            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Por favor, rellene todos los datos")

        elif self.csv_button.isChecked():  # Ahora se trata de generar el csv

            if self.fich_oferta.text():
                self.cancel_button.setEnabled(True)
                self.ok_button.setEnabled(False)

                #
                # light = False  # Versión 4. Parámetro sin uso. El bloque if-else anterior se suprime
                # En su lugar usamos consolidated, que define si hay que consolidar o no las entradas del csv
                # En este bloque lo preguntamos
                mess = CsvConsolidated()
                mess.show()
                mess.exec()

                consolidated = mess.consolidated

                oferta_final = False  # Indica si hay que hacer oferta de cliente. V4

                if self.oferta_cliente.isChecked():  # V4
                    oferta_final = True

                get_csv = ProcesarCsv(self.fich_oferta.text(), consolidated, oferta_final)
                get_csv.signals.fin_OK_backouts.connect(self.finalizar_backouts)
                get_csv.signals.error_fichero.connect(self.notif_error)
                get_csv.signals.fin_OK_csv.connect(self.finalizar_csv)
                get_csv.signals.informacion.connect(self.reportar)
                get_csv.signals.warning.connect(self.notif_warning)
                # get_csv.signals.error_oferta.connect(self.fallo_oferta)

                self.threadpool.start(get_csv)

            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Por favor, introduzca el nombre del fichero de oferta")

    def notif_error(self, text):
        QtWidgets.QMessageBox.critical(self, "Error", text)
        self.cancel_button.setEnabled(False)
        self.ok_button.setEnabled(True)

    def notif_warning(self, text):
        QtWidgets.QMessageBox.information(self, "Aviso", text)

    def reportar(self, text):
        self.progreso.show()
        self.progreso.setText(text)

    def buscando(self):
        self.progreso.setText('Buscando códigos de producto')

    def finalizar_backouts(self, libro, not_found_list, aux_book):
        self.progreso.setText('')
        self.progreso.hide()
        self.cancel_button.setEnabled(False)
        self.ok_button.setEnabled(True)
        carpeta, nombre_file = os.path.split(self.fich_oferta.text())
        file_not_found = os.path.join(carpeta, 'no_encontrados.csv')

        if not_found_list:  # Algunos códigos no se han encontrado. Presentarlos en ventana nueva
            aviso = NotFound(not_found_list)
            aviso.show()
            aviso.exec()

            # Además, guardamos los códigos no encontrados en el fichero no_encontrados.csv
            # carpeta, nombre_file = os.path.split(self.fich_oferta.text())
            with open(file_not_found, 'w') as k:
                for item in not_found_list:
                    k.writelines(item + '\n')

        else:  # Se han encontrado todos los códigos Cisco. Borramos el fichero file_not_found
            if os.path.exists(file_not_found):
                os.remove(file_not_found)

        todo_ok = False
        while not todo_ok:
            if libro:
                carpeta, nombre_file = os.path.split(self.fich_oferta.text())
                try:
                    nom_fich, ext = nombre_file.split('.')
                except ValueError:  # El nombre del fichero tiene algún punto intermedio
                    nom_fich = 'oferta_intermedia.xlsx'
                    QtWidgets.QMessageBox.information(self, "Aviso", "El nombre de oferta tiene un '.' intermedio \n"
                                                                     "El fichero de salida se llamará "
                                                                     "oferta_intermedia")
                aux_file = os.path.join(carpeta, 'result_data Cisco PSS.xlsx')

                try:
                    aux_book.save(aux_file)
                except PermissionError:
                    text = 'Fichero {} abierto.\Ciérrelo para poder continuar'.format(aux_file)
                    QtWidgets.QMessageBox.critical(self, 'Error', text)

                nom_fich = nom_fich + '_proc.xlsx'
                output_file = os.path.join(carpeta, nom_fich)
                print(output_file)

                try:
                    libro.save(output_file)
                    todo_ok = True
                    QtWidgets.QMessageBox.information(self, "Proceso correcto", "No ha habido problemas. \nTodo OK")
                    self.fich_oferta.setText(output_file)
                    os.startfile(output_file)

                except PermissionError:
                    text = 'Fichero {} abierto.\Ciérrelo para poder continuar'.format(self.fich_oferta.text())
                    QtWidgets.QMessageBox.critical(self, 'Error', text)
                    todo_ok = False

            else:
                todo_ok = True
                QtWidgets.QMessageBox.information(self, "Proceso correcto", "No ha habido problemas. \nTodo OK")

    def buscar_oferta(self):

        direct = QtWidgets.QFileDialog.getOpenFileName(self, "Elegir archivo de oferta")
        print(direct[0])
        self.fich_oferta.setText(direct[0])

    # def buscar_cisco_file(self):
    #
    #     direct = QtWidgets.QFileDialog.getOpenFileName(self, "Elegir archivo de precios Cisco")
    #     self.fich_precios_normal.setText(direct[0])
    #
    # def buscar_ucs_file(self):
    #
    #     direct = QtWidgets.QFileDialog.getOpenFileName(self, "Elegir archivo de precios UCS")
    #     self.fich_precios_UCS.setText(direct[0])

    # def buscar_video_file(self): ELIMINADO
    #
    #     direct = QtWidgets.QFileDialog.getOpenFileName(self, "Elegir archivo de precios de vídeo")
    #     self.fich_precios_video.setText(direct[0])

    def finalizar_csv(self, libro1, libro2, libro3, carpeta, ok):

        if not ok:
            self.cancel_button.setEnabled(False)
            self.ok_button.setEnabled(True)
            return

        self.progreso.setText('')
        self.progreso.hide()  # Cerramos la caja informativa, ya no hace falta

        # No ha habido problemas en la generación de los libros de oferta
        fichero_auxiliar_excel = os.path.join(carpeta, 'auxiliar_' + 'USD' + '.xlsx')
        fichero_csv = os.path.join(carpeta, 'upload_direct_' + 'USD' + '.csv')
        fichero_cliente = os.path.join(carpeta, 'oferta_cliente' + '.xlsx')

        if libro1:
            try:
                libro1.save(fichero_auxiliar_excel)
                csv_from_excel(fichero_auxiliar_excel, fichero_csv, self)
                os.remove(fichero_auxiliar_excel)

            except PermissionError:
                text = 'Fichero {} ya abierto.\n Por favor, ciérrelo para seguir'.format(fichero_auxiliar_excel)
                QtWidgets.QMessageBox.critical(self, "Error", text)

        fichero_auxiliar_excel = os.path.join(carpeta, 'auxiliar_' + 'EUR' + '.xlsx')
        fichero_csv = os.path.join(carpeta, 'upload_direct_' + 'EUR' + '.csv')

        if libro2:
            try:
                libro2.save(fichero_auxiliar_excel)
                csv_from_excel(fichero_auxiliar_excel, fichero_csv, self)
                os.remove(fichero_auxiliar_excel)

            except PermissionError:
                text = 'Fichero {} ya abierto.\n Por favor, ciérrelo para seguir'
                QtWidgets.QMessageBox.critical(self, "Error", text)

        if libro3:
            try:
                libro3.save(fichero_cliente)

            except PermissionError:
                text = 'Fichero {} ya abierto.\n Por favor, ciérrelo para seguir'.format(fichero_cliente)
                QtWidgets.QMessageBox.critical(self, "Error", text)

        QtWidgets.QMessageBox.information(self, "Proceso correcto", "No ha habido problemas. \nTodo OK")
        self.cancel_button.setEnabled(False)
        self.ok_button.setEnabled(True)
        self.fich_oferta.setText('')
