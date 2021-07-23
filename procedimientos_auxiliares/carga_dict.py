import os
from os.path import dirname

import openpyxl

from .rutinas_busqueda import get_ultima_fila

SERV = 'A'
PSS1 = 'B'
PSS2 = 'C'
PSS3 = 'D'
PSS4 = 'E'
SMT1 = 'G'
SMT2 = 'H'
SMT3 = 'I'
SMT4 = 'J'
COEF_INT = 'L'
COEF_LIST = 'N'
FIRST_ROW = str(2)


def formar_diccionarios():
    """
    Este procedimiento lee el fichero listas.xlsx y extrae las listas ordenadas de servicios, PSSs, Smartnets y
    coeficientes de cálculo, devolviendo cuatro diccionarios:
    dict_pss: Relaciona el servicio requerido con una lista de pss posibles (dependen de la tecnología)
    dict_smt: Relaciona el servicio requerido con una lista de smartnet posibles (dependen de la tecnología)
    dict_coef_interno: Coeficiente que multiplicado por el Service List Price da el coste interno
    dict_coef_list: Coeficiente que multiplicado por el smartnet apropiado da el Service List Price
    :return: Los diccionarios que acabamos de citar
    """

    direct = dirname(os.path.dirname(__file__))
    print(direct)
    filename = os.path.join(direct, 'listas.xlsx')

    libro = openpyxl.load_workbook(filename)
    hoja = libro.active

    last_row = str(get_ultima_fila(hoja, SERV))

    # Extraemos las columnas que nos interesan en forma de lista de celdas openpyxl
    servicio = hoja[SERV + FIRST_ROW: SERV + last_row]
    pss1 = hoja[PSS1 + FIRST_ROW: PSS1 + last_row]
    pss2 = hoja[PSS2 + FIRST_ROW: PSS2 + last_row]
    pss3 = hoja[PSS3 + FIRST_ROW: PSS3 + last_row]
    pss4 = hoja[PSS4 + FIRST_ROW: PSS4 + last_row]
    smt1 = hoja[SMT1 + FIRST_ROW: SMT1 + last_row]
    smt2 = hoja[SMT2 + FIRST_ROW: SMT2 + last_row]
    smt3 = hoja[SMT3 + FIRST_ROW: SMT3 + last_row]
    smt4 = hoja[SMT4 + FIRST_ROW: SMT4 + last_row]
    cf_int = hoja[COEF_INT + FIRST_ROW: COEF_INT + last_row]
    cf_list = hoja[COEF_LIST + FIRST_ROW: COEF_LIST + last_row]

    pss = []  # Formamos una lista de listas de posibles PSS para cada servicio Uptime
    for item1, item2, item3, item4 in zip(pss1, pss2, pss3, pss4):
        fila = [item1[0].value, item2[0].value, item3[0].value, item4[0].value]
        fila_limpia = [x
                       for x in fila
                       if x]
        pss.append(fila_limpia)

    smt = []  # Formamos una lista de listas de posibles smartnet para cada servicio Uptime

    for item1, item2, item3, item4 in zip(smt1, smt2, smt3, smt4):
        fila = [item1[0].value, item2[0].value, item3[0].value, item4[0].value]
        fila_limpia = [x
                       for x in fila
                       if x]
        smt.append(fila_limpia)

    service = [x[0].value.lower()
               for x in servicio] # Lista de servicios Uptima

    coef_list = [x[0].value
                 for x in cf_list]  # Lista de coeficientes para cálculo del Service List Price

    coef_int = [x[0].value
                for x in cf_int]  # Lista de coeficientes para cálculo de costes interno

    # Partiendo de las listas formadas, componemos los diccionarios que vamos a
    # devolver para facilitar el cálculo de los costes del servicio

    dict_pss = dict((x, y) for (x, y) in zip(service, pss))
    dict_smt = dict((x, y) for (x, y) in zip(service, smt))
    dict_coef_list = dict((x, y) for (x, y) in zip(service, coef_list))
    dict_coef_int = dict((x, y) for (x, y) in zip(service, coef_int))

    libro.close()

    return dict_pss, dict_smt, dict_coef_int, dict_coef_list

