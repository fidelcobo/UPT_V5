import csv
import locale
import os
from os.path import dirname
import openpyxl
from PyQt5 import QtWidgets
from typing import List

from aux_class import FullElementosOferta


def pass_to_excel(datos_clases: List[FullElementosOferta], moneda:str, instance):  # V4. Nuevo método compactado

    """
    Este procedimiento recibe los datos de la oferta como lista de elementos FullElementosOferta y compone un libro
    Excel que posteriormente se pasará a .csv, ya descargable en Direct
    :param datos_clases: Datos de la oferta en elementos FullElementosOferta
    :param moneda: Tipo de moneda del libro: EUR o USD
    :param instance:
    :return: Libro excel
    """
    project_dir = dirname(os.path.abspath(os.path.dirname(__file__)))

    # Ahora abrimos el fichero Excel auxiliar de plantilla de MS
    filen = os.path.join(project_dir, 'plantilla_ms.xlsx')  # Este fichero no se toca. Hace de plantilla
    sheet_name = 'ms'

    if os.path.exists(filen):
        libro = openpyxl.load_workbook(filen)
        hoja = libro.get_sheet_by_name(sheet_name)

    else:
        instance.signals.error_fichero.emit('Fichero de plantilla{} no existe'.format(filen))
        return None, False

    curr_row = 2
    num_fila = 10
    cont_items = 0

    for articulo in datos_clases:
        fila = str(curr_row)
        fila_sig = str(curr_row + 1)

        if articulo.currency == moneda:
            if (articulo.in_csv):  # Este ítem no está filtrado
                cont_items += 1
                hoja['A' + fila] = num_fila
                hoja['A' + fila_sig] = num_fila + 1
                hoja['B' + fila_sig] = num_fila
                hoja['H' + fila] = 2
                hoja['H' + fila_sig] = 20
                hoja['C' + fila] = 'Dimension Data'
                hoja['C' + fila_sig] = articulo.manufacturer
                hoja['E' + fila] = articulo.qty
                hoja['E' + fila_sig] = articulo.qty
                hoja['F' + fila] = articulo.uptime
                hoja['F' + fila_sig] = articulo.backout_name
                hoja['G' + fila] = articulo.uptime_descr
                hoja['G' + fila_sig] = articulo.code
                hoja['I' + fila] = articulo.code
                hoja['I' + fila_sig] = 0
                hoja['J' + fila] = articulo.manufacturer
                hoja['J' + fila_sig] = ''
                hoja['K' + fila] = 1
                hoja['K' + fila_sig] = 1
                hoja['L' + fila] = 'EA'
                hoja['L' + fila_sig] = 'EA'
                hoja['M' + fila] = articulo.currency
                hoja['M' + fila_sig] = articulo.currency
                hoja['N' + fila] = 'Fixed'
                hoja['N' + fila_sig] = 'Fixed'
                if not articulo.gpl:
                    wpl = '0'
                else:
                    wpl = str(locale.format_string('%.2f', articulo.gpl))

                hoja['O' + fila] = wpl
                hoja['O' + fila_sig] = wpl
                try:
                    unit_price = float(articulo.total_sell_price) # / int(articulo.qty)
                except ValueError:
                    instance.signals.error_fichero.emit('Fichero no procesable\n Los datos finales de coste'
                                                        ' y PVP no están definidos')
                    return None, False

                unit_cost = float(articulo.total_cost) # / int(articulo.qty)
                unit_cost_back = float(articulo.cost_backout) # / int(articulo.qty)
                unit_sell_back = float(articulo.venta_backout) # / int(articulo.qty)
                hoja['P' + fila_sig] = locale.format_string('%.2f', unit_sell_back)
                hoja['P' + fila] = locale.format_string('%.2f', unit_price)
                hoja['Q' + fila] = locale.format_string('%.2f', unit_cost)
                hoja['Q' + fila_sig] = locale.format_string('%.2f', unit_cost_back)
                try:
                    fecha_init = '{}/{}/{}'.format(articulo.init_date.day, articulo.init_date.month,
                                                   articulo.init_date.year)
                    fecha_init_limpia = '{}{}{}'.format(str(articulo.init_date.year), str(articulo.init_date.month).zfill(2),
                                                        str(articulo.init_date.day).zfill(2))
                except AttributeError:
                    instance.signals.error_fichero.emit('Fichero no procesable\n La fecha de inicio'
                                                        ' no tiene formato correcto')
                    return None, False

                try:
                    fecha_fin = '{}/{}/{}'.format(articulo.end_date.day, articulo.end_date.month,
                                                  articulo.end_date.year)
                except AttributeError:
                    instance.signals.error_fichero.emit('Fichero no procesable\n La fecha de final'
                                                        ' no tiene formato correcto')
                    return None, False

                hoja['X' + fila] = fecha_init
                hoja['X' + fila_sig] = fecha_init
                hoja['Y' + fila] = fecha_fin
                hoja['Y' + fila_sig] = fecha_fin
                hoja['AA' + fila] = 'StartDate=' + fecha_init_limpia + '#Duration=' + str(articulo.duration) + \
                                    '#InvoiceInterval=Yearly#InvoiceMode=anticipated'
                hoja['AA' + fila_sig] = 'StartDate=' + fecha_init_limpia + '#Duration=' + str(articulo.duration) + \
                                        '#InvoiceInterval=Yearly#InvoiceMode=anticipated'
                hoja['AF' + fila] = articulo.tech
                hoja['AF' + fila_sig] = articulo.tech
                hoja['AG' + fila] = articulo.serial_no
                hoja['AG' + fila_sig] = articulo.serial_no
                hoja['AI' + fila] = 226  # Nuevo campo 24/5/2019

                curr_row += 2
                num_fila += 3

    if cont_items == 0:
        return None, True
    else:
        return libro, True


def csv_from_excel(entrada, salida, instance):

    """
    Esta rutina convierte un libro Excel de oferta en .csv cargable por Direct
    :param entrada: Fichero Excel de entrada
    :param salida: Fichero .csv de salida
    :param instance: Proceso PyQt5 para enviar pantallas y señales
    :return: Nada
    """

    ok = False
    while not ok:
        try:
            wb = openpyxl.load_workbook(entrada)
            sh = wb.active  # or wb.sheet_by_name('name_of_the_sheet_here')

            with open(salida, 'w', newline='') as f:
                c = csv.writer(f, dialect='excel', delimiter=';')
                for r in sh.rows:
                    c.writerow([cell.value for cell in r])
            ok = True

        except PermissionError:
            text = 'Fichero {} ya abierto.\n Por favor, ciérrelo para seguir'.format(salida)
            QtWidgets.QMessageBox.warning(instance, "Error", text)
