import datetime
import locale
import os
from os.path import dirname
from PyQt5 import QtWidgets

import openpyxl
from openpyxl import Workbook

from aux_class import CiscoItem
from database import look_for_cisco_list
from procedimientos_auxiliares import busca_columnas, get_ultima_fila, busca_codigos_cisco
from procedimientos_auxiliares import buscar_en_tabla_cisco, fill_aux, request_gdc_cost_list
from procedimientos_auxiliares import formar_diccionarios

locale.setlocale(locale.LC_ALL, 'FR')
base_dir = dirname(os.path.abspath(os.path.dirname(__file__)))
db_file = os.path.join(base_dir + '/cisco.db')
CELDA_DESCUENTO = 'K3'
FIRST_ROW = str(11)
HEADERS_ROW = str(10)


def calculo_backouts(fich_a, light, instance):
    """
    Este es uno de los procedimientos principales. Calcula los datos de los backouts Cisco
    del fichero de oferta. Es imprescindible que figuren el SKU del artículo y el servicio Uptime
    solicitado
    :param fich_a: Fichero de oferte
    :param light (bool): Indica si el fichero de oferta es de tipo light o no
    :param instance: La instancia Qt5 que maneja este proceso (para envío de pantallas)
    :return: Una señal multithreading Qt5 para indicar que ha terminado la tarea. Incluye los
    :diversos ficheros Excel necesarios para completar el tratamiento.
    """

    file_ramon = fich_a  # El fichero Excel de la oferta

    padre = instance  # Es la instancia de la clase principal que invocó este procedimiento. Lo usamos para presentar
    # pantallas de mensajes y enviar mensajes con información relevante (signals)

    # Confeccionamos ahora unos diccionarios que nos van a ayudar a relacionar los servicios con los códigos de PSS,
    # smartnet y los coeficientes aplicables para calcular los costes

    upt_pss_codes, upt_smartnet_codes, coef_servicio, coef_coste_interno = formar_diccionarios()

    # Abrimos el libro de la oferta
    padre.signals.informacion.emit('Abriendo fichero de oferta')

    try:
        libro_oferta = openpyxl.load_workbook(file_ramon)
        if light:  # Se está usando una oferta con plantilla light
            sheet = libro_oferta.get_sheet_by_name('Quote_Detail')
            lista_busqueda = ['Part Number real (*)', 'Fecha fin de soporte', 'Cisco Service Level',
                              'Nombre de Backout', 'Precio de lista Backout Unitario  - ANUAL', 'Manufacturer']

        else:  # Se usa la plantilla completa
            sheet = libro_oferta.get_sheet_by_name('Quote_Detail')
            lista_busqueda = ['Part Number to quote', 'Last Date of Support',
                              'SKU - Entitlement Uptime/Smartnet Services', 'SKU Backout',
                              'Unit Backout Price List (USD) - ANNUAL', 'Vendor', 'GDC Cost Price V4 $ - ANNUAL',
                              'DD Spain Cost Price V4 $ - ANNUAL']
    except:
        # Por lo que sea, no podemos abrir el fichero de oferta
        padre.signals.error_fichero.emit('El fichero de oferta no puede abrirse')
        return

    # Buscamos dónde están los campos clave. Esto nos permitirá leer y escribir los datos en sus ubicaciones correctas
    # Además, nos permite comprobar si el formato del fichero es el correcto. Para ello, comprobamos en qué columnas
    # se encuentran una serie de columnas clave, buscando la rotulación de sus cabeceras (lista_busqueda)

    ok, lista_columnas = busca_columnas(sheet, lista_busqueda, HEADERS_ROW)

    if light:  # En la plantilla Light hay que buscar también el campo de coste neto de backout
        lista_busqueda = ['Coste Backout Unitario - ANUAL']
        ok, back_cost_col = busca_columnas(sheet, lista_busqueda, HEADERS_ROW)
        back_net_col = back_cost_col[0]

    if ok:  # El formato del fichero de oferta parece bueno. Extraemos la ubicación de las columnas clave.
        # Estas columnas figuran en lista_columnas

        code_col, end_date_col, sla_col, back_col, price_col, manufact_col, \
        gdc_cost_col, internal_spain_cost_col = lista_columnas

        last_row = str(get_ultima_fila(sheet, code_col))  # Vemos cuál es la última fila significativa

        # A continuación colocamos en listas los datos fundamentales de la oferta

        codes_excel = sheet[code_col + FIRST_ROW: code_col + last_row]
        end_date_excel = sheet[end_date_col + FIRST_ROW: end_date_col + last_row]
        sla_excel = sheet[sla_col + FIRST_ROW: sla_col + last_row]
        backout_excel = sheet[back_col + FIRST_ROW: back_col + last_row]
        price_excel = sheet[price_col + FIRST_ROW: price_col + last_row]
        internal_spain_cost = sheet[internal_spain_cost_col + FIRST_ROW: internal_spain_cost_col + last_row]
        gdc_cost = sheet[gdc_cost_col + FIRST_ROW: gdc_cost_col + last_row]

        if light:
            net_cost = sheet[str(back_net_col) + '11': back_net_col + last_row]

        manufacturer = sheet[manufact_col + FIRST_ROW: manufact_col + last_row]
        print(datetime.datetime.now(), 'ok')
        descuento = sheet[CELDA_DESCUENTO].value

        # Comenzamos ahora una serie de búsquedas para componer una tabla (tabla_datos_cisco) donde se contengan
        # todos los datos significativos de las diversas combinaciones SKU-SLA (servicio Uptime) que aparecen en la
        # oferta. Las búsquedas individuales de cada línea de al oferta se harán contra esta tabla, una especie de
        # minicatálogo, lo que hará mucho más rápidas dichas búsquedas.

        set_codigos_cisco = busca_codigos_cisco(codes_excel, sla_excel, manufacturer)
        # Este set contiene los diferentes sku/sla (uptime) Cisco que hay en la oferta.
        # Pasamos los datos de este set auxiliar a la lista que usaremos para consultar precios y demás

        tabla_datos_cisco = []  # Usaremos luego esta tabla para consultar datos de backout de los artículos

        for item in set_codigos_cisco:
            ca = CiscoItem(item.sku, item.serv_lev, '', '', '', '')
            tabla_datos_cisco.append(ca)

        # Pero es muy posible que algunas combinaciones SKU/SLA no aparezcan en los catálogos de PSS/Smartnet, por lo
        # los retiraremos de la tabla_datos_cisco. Para ello, verificamos cada ítem en la base de datos cisco.db, donde
        # figuran los catálogos de PSS y Smartnet.

        lista_desechables = []  # Listado de SKU/sla_excel que no están en la base de datos

        for item in tabla_datos_cisco:

            # Ahora buscamos si los items están en la base de datos de cisco
            padre.signals.informacion.emit('Buscando códigos en base de datos')

            lista_busca_pss = upt_pss_codes.get(item.serv_lev, None)  # Posibles PSS asociados al servicio Uptime
            lista_busca_smartnet = upt_smartnet_codes.get(item.serv_lev, None)  # Posibles Smartnet asociados al
            # servicio Uptime

            found, back_out, list_price, end_of_support = look_for_cisco_list(item.sku, lista_busca_pss, db_file,
                                                                              smartnet=False)
            found_smt, smt, smt_list_price, smt_eos = look_for_cisco_list(item.sku, lista_busca_smartnet, db_file,
                                                                          smartnet=True)
            if found or found_smt:  # El ítem figura en la tabla de PSS o en la de Smartnet. Rellenamos datos
                item.backout = back_out
                item.eos = end_of_support
                item.list_price = list_price
                item.smartnet_sku = smt
                item.smartnet_list = smt_list_price
                print(item)
                if smt:
                    item.service_price_list = round(float(smt_list_price) *
                                                    float(coef_servicio.get(item.serv_lev.lower())), 2)
                else:
                    item.service_price_list = 0.0

            else:  # El ítem no está en la base de datos. Lo metemos en la lista de desechables.
                lista_desechables.append(item)

        # Ahora eliminamos de la tabla_datos_cisco los ítems de la lista de desechables
        if lista_desechables:
            for item in lista_desechables:
                tabla_datos_cisco.remove(item)

        # Finalmente, completamos los datos de la tabla_datos_cisco consultando al API de Didata los costes del GDC
        padre.signals.informacion.emit('Consultando costes de GDC al API')
        mensaje_api = request_gdc_cost_list(tabla_datos_cisco)  # Este procedimiento escribe sobre la propia tabla los precios GDC

        if mensaje_api != 'OK':  # La consulta con el API no ha resultado correcta
            # Notificamos el error. El coste del GDC queda a cero
            padre.signals.warning.emit(mensaje_api)

    else:  # El formato de la oferta no es bueno
        text = 'El formato de la oferta no es correcto\n El nombre de algún campo clave es incorrecto o no existe'
        padre.signals.error_fichero.emit(text)
        return

    print('comienzo códigos ', datetime.datetime.now())
    aux_file_list = []  # Lista de artículos Cisco encontrados para colocar en fichero auxiliar
    not_found_codes = []  # Códigos Cisco que no aparecen en los catálogos

    for k in range(len(codes_excel)):
        codigo = codes_excel[k][0].value
        fabricante = manufacturer[k][0].value
        serv_level = sla_excel[k][0].value.lower()

        if codigo and (fabricante.strip().lower() == 'cisco'):

            # Buscamos ahora si el ítem en curso de la oferta figura en la tabla_datos_cisco. Si es así, apuntamos
            # en la copia Excel de la oferta los precios de lista de backout, eos date, código del backout, coste
            # interno del servicio y coste del GDC. Además, listamos en aux_file el SKU, PSS, smartnet y eos para
            # pasarlos luego al fichero auxiliar que contendrá estos datos. Es un fichero de consulta realmente.

            encontrado, back_out, list_price, end_of_support, coste_interno, smartnet, coste_gdc = \
                buscar_en_tabla_cisco(codigo, serv_level, tabla_datos_cisco)

            if encontrado:  # El código está en el catálogo estándar de Cisco
                end_date_excel[k][0].value = end_of_support
                backout_excel[k][0].value = back_out
                if list_price:
                    coste = float(list_price)
                else:
                    coste = 0.0  # No hay backout para este seervicio
                price_excel[k][0].value = coste
                internal_spain_cost[k][0].value = round(float(coste_interno) * coef_coste_interno.get(serv_level, 0), 2)
                gdc_cost[k][0].value = float(coste_gdc)

                if light:  # En la plantilla Light el coste neto de backout debe ponerlo el programa, no la hoja Excel
                    net_cost[k][0].value = coste * (1 - descuento)
                aux_file_list.append([codigo, coste, back_out, end_of_support, smartnet])

            else:
                not_found = codigo + ' - ' + serv_level
                not_found_codes.append(not_found)

    libro_auxiliar = Workbook()
    hoja_aux = libro_auxiliar.active

    if aux_file_list:
        # Creamos un fichero Excel que guardará los datos de SKU, PSS, Smartnet y precios de lista que encontraremos en
        # las posteriores búsquedas en la base de datos

        fill_aux(aux_file_list, hoja_aux)  # Rellenamos el fichero auxiliar con los códigos encontrados

    print('fin codigos ', datetime.datetime.now())
    libro_oferta.close()

    padre.signals.fin_OK_backouts.emit(libro_oferta, not_found_codes, libro_auxiliar)
