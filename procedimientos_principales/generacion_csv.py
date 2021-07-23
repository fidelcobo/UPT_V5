import locale
import os
from os.path import dirname

import openpyxl

from procedimientos_auxiliares import busca_columnas, get_ultima_fila
from procedimientos_auxiliares import pass_to_excel, generar_oferta_cliente, obtener_datos_generales
from procedimientos_auxiliares import compactar_datos_oferta, consolidar_datos

locale.setlocale(locale.LC_ALL, 'FR')
base_dir = dirname(os.path.abspath(os.path.dirname(__file__)))
db_file = os.path.join(base_dir + '/cisco.db')
CELDA_DESCUENTO = 'K3'
FIRST_ROW = str(11)
HEADERS_ROW = str(10)


def generacion_csv(oferta, consolidated, oferta_cliente, instance):

    """
    Esta rutina genera los ficheros .csv (uno para euros y otro para dólares) que pueden cargarse directamente en
    la aplicación Direct. Puede, además, a voluntad del usuario, generar un fichero Excel de cliente.
    :param oferta: Fichero Excel de partida
    :param consolidated: Parámetro que indica si se quieren consolidar las entradas repetidas de la oferta
    :param oferta_cliente: Parámetro que define si se quiere generar un fichero Excel de cliente
    :param instance: Para poder usar la posibilidad de enviar señales y presentar pantallas de PyQt5
    :return: En condiciones normales se envía la señal fin_OK_csv a la clase principal conteniendo un libro Excel para
    los datos en euros, otro para dólares y en su caso, la oferta de cliente

    """
    # V4: Lo primero, consultamos si se quiere un csv consolidado o no. Con una pantalla ad hoc

    file_ramon = oferta
    carpeta, file_name = os.path.split(file_ramon)

    instance.signals.informacion.emit('Abriendo fichero de oferta')

    try:
        libro_oferta = openpyxl.load_workbook(file_ramon, data_only=True)
        sheet = libro_oferta.get_sheet_by_name('Quote_Detail')

    except Exception as e:
        print(e)
        text = 'Fichero de oferta {} \nno procesable \n Elija otro.'.format(file_ramon)
        instance.signals.error_fichero.emit(text)
        return

    # Buscamos ahora en qué columnas está la información relevante. Lo haremos en varias tandas

    instance.signals.informacion.emit('Procesando oferta')

    # Eliminaremos toda referencia al parámetro light, que no se usa ya en V4

    lista_busqueda = ['Part Number to quote', 'End Date', 'SKU - Entitlement Uptime/Smartnet Services',
                      'SKU Backout', 'Unit Backout Price List (EUR) - ANNUAL']
    ok, lista_columnas = busca_columnas(sheet, lista_busqueda, HEADERS_ROW)
    if ok:
        code_col, end_date_col, upt_col, back_col, price_col = lista_columnas
    else:
        text = 'El formato de la oferta no es correcto\n El nombre de algún campo clave es incorrecto o no existe'
        instance.signals.error_fichero.emit(text)
        return

    lista_busqueda = ['Description Entitlement Uptime/Smartnet Services', 'LoB', 'Vendor',
                      'Start Date', 'Period (days)']
    ok, lista_columnas = busca_columnas(sheet, lista_busqueda, HEADERS_ROW)
    if ok:
        uptime_descr_col, tech_col, manuf_col, init_date_col, durac_col = lista_columnas
    else:
        text = 'El formato de la oferta no es correcto\n El nombre de algún campo clave es incorrecto o no existe'
        instance.signals.error_fichero.emit(text)
        return

    lista_busqueda = ['TOTAL Backout Cost (EUR) - PRO_RATED', 'Total Cost (EUR)', 'Total Sell Price (EUR)',
                      'Qty', 'Serial Number', 'Currency', 'TOTAL Backout Sell Price (EUR) - PRO_RATED']
    ok, lista_columnas = busca_columnas(sheet, lista_busqueda, HEADERS_ROW)
    if ok:
        cost_back_col, coste_tot_col, venta_col, qty_col, serial_col, currency_col, venta_back_col = lista_columnas
    else:
        text = 'El formato de la oferta no es correcto\n El nombre de algún campo clave es incorrecto o no existe'
        instance.signals.error_fichero.emit(text)
        return

    lista_busqueda = ['csv line (Yes/No)?']  # Si no está esta columna se trata de una plantilla <= v1.6 o Light
    #  --> All to csv
    ok, lista_columnas = busca_columnas(sheet, lista_busqueda, HEADERS_ROW)
    if ok:
        insert_in_csv_col = lista_columnas[0]  # Apunta la letra de la columna en la que está este campo
    else:
        insert_in_csv_col = ''

    last_row = str(get_ultima_fila(sheet, code_col))  # Buscamos cuál es la última fila rellena con algún código

    codes = [r[0].value
             for r in sheet[code_col + FIRST_ROW: code_col + last_row]]
    uptime_code = [r[0].value
                   for r in sheet[upt_col + FIRST_ROW:upt_col + str(last_row)]]
    uptime_descr = [r[0].value
                    for r in sheet[uptime_descr_col + FIRST_ROW:uptime_descr_col + str(last_row)]]
    tech = [r[0].value
            for r in sheet[tech_col + FIRST_ROW:tech_col + str(last_row)]]
    manufacturer = [r[0].value
                    for r in sheet[manuf_col + FIRST_ROW:manuf_col + str(last_row)]]
    init_date = [r[0].value
                 for r in sheet[init_date_col + FIRST_ROW:init_date_col + str(last_row)]]
    end_date = [r[0].value
                for r in sheet[end_date_col + FIRST_ROW:end_date_col + str(last_row)]]
    try:
        duration = [int(12 * int(r[0].value) / 365)
                    for r in sheet[durac_col + FIRST_ROW:durac_col + str(last_row)]]

    except TypeError:  # El fichero de oferta intermedia tiene valores no consolidados
        instance.signals.error_fichero.emit('Fichero con valores no definidos')
        return

    gpl = [r[0].value
           for r in sheet[price_col + FIRST_ROW:price_col + str(last_row)]]
    cost_backout = [r[0].value
                    for r in sheet[cost_back_col + FIRST_ROW:cost_back_col + str(last_row)]]
    venta_backout = [r[0].value
                     for r in sheet[venta_back_col + FIRST_ROW:venta_back_col + str(last_row)]]
    total_cost = [r[0].value
                       for r in sheet[coste_tot_col + FIRST_ROW:coste_tot_col + str(last_row)]]
    total_sell_price = [r[0].value
                        for r in sheet[venta_col + FIRST_ROW:venta_col + str(last_row)]]
    backout_name = [r[0].value
                    for r in sheet[back_col + FIRST_ROW:back_col + str(last_row)]]
    qty = [r[0].value
           for r in sheet[qty_col + FIRST_ROW:qty_col + str(last_row)]]
    serial_no = [r[0].value
                 for r in sheet[serial_col + FIRST_ROW:serial_col + str(last_row)]]
    currency = [r[0].value
                for r in sheet[currency_col + FIRST_ROW:currency_col + str(last_row)]]
    if insert_in_csv_col:
        insert_in_csv = [r[0].value
                         for r in sheet[insert_in_csv_col + FIRST_ROW:insert_in_csv_col + str(last_row)]]
    else:
        insert_in_csv = []

    # Vamos ahora a ver si tenemos que consolidar los datos. Si es así, invocamos el procedimiento
    # correspondiente
    datos_clases = compactar_datos_oferta(codes, uptime_code, uptime_descr, tech, manufacturer, init_date, end_date,
                                          duration,  gpl, cost_backout, venta_backout, total_cost, total_sell_price,
                                          backout_name, qty, serial_no, currency, insert_in_csv, 0, 0)

    if consolidated:  # Se precisa consolidar la lista de ítems
        datos_clases = consolidar_datos(datos_clases)


    # book1, ok1 = pass_to_excel(codes, uptime_code, uptime_descr, tech, manufacturer, init_date, end_date, duration,
    #                            gpl, cost_backout, venta_backout, total_unit_cost, total_unit_price, backout_name, qty,
    #                            serial_no, currency, 'USD', insert_in_csv, instance)
    book1, ok1 = pass_to_excel(datos_clases, 'USD', instance)

    # book2, ok2 = pass_to_excel(codes, uptime_code, uptime_descr, tech, manufacturer, init_date, end_date, duration,
    #                            gpl, cost_backout, venta_backout, total_unit_cost, total_unit_price, backout_name,
    #                            qty, serial_no, currency, 'EUR', insert_in_csv, instance)
    book2, ok2 = pass_to_excel(datos_clases, 'EUR', instance)

    print('Hasta aquí hemos llegado.\n Ni tan mal')
    ok_total = False

    if ok1 and ok2:
        ok_total = True

    if oferta_cliente:  # V4
        instance.signals.informacion.emit('Generando fichero de oferta de cliente')

        if not consolidated:  # Si los datos no están consolidados, los consolidamos para hacer la oferta
            datos_clases = consolidar_datos(datos_clases)

        hoja_oferta = libro_oferta.get_sheet_by_name('SUMMARY_QUOTE')
        datos_generales = obtener_datos_generales(hoja_oferta)
        book3 = generar_oferta_cliente(datos_clases, datos_generales, instance)
    else:
        book3 = None

    instance.signals.fin_OK_csv.emit(book1, book2, book3, carpeta, ok_total)
