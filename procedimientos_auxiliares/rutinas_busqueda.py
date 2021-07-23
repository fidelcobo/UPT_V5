import requests

from aux_class import Cisco_Articles


def busca_codigos_cisco(code, sla, manufacturer) -> set:
    """
    Este procedimiento recibe tres listas sacadas directamente de la plantilla Excel: la de SKUs,
    la de SLAs correspondientes y la de fabricantes. Las filtra y entrega un set de combinaciones
    únicas cisco/SKU/SLA
    :param code: la lista de SKUs de la oferta
    :param sla: El SLA (servicio Uptime) de los backouts de los SKUs
    :param manufacturer: El fabricante
    :return: Set de parejas únicas SKU/SLA de Cisco
    """

    set_valores = set()

    for i in range(len(code)):
        fabricante = manufacturer[i][0].value
        serv_lev = sla[i][0].value.lower()
        codigo = code[i][0].value

        if fabricante.strip().lower() == 'cisco':
            item = Cisco_Articles(sku=codigo, serv_lev=serv_lev)
            if item in set_valores:
                pass
            else:
                set_valores.add(item)

    return set_valores


def get_ultima_fila(hoja, col_code):
    fila = 11
    fin = False
    while not fin:
        cell = col_code + str(fila)
        if not hoja[cell].value:
            fin = True
        else:
            fila += 1
            fin = False
    return fila - 1


def busca_columnas(sheet, lista_busca: list, fila_busca: str) -> object:
    columnas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM',
                'AN', 'AO', 'AP', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE',
                'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV',
                'BW', 'BX', 'BY', 'BZ', 'CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL']

    result_busca = []

    for items in lista_busca:
        for col in columnas:
            cell = col + fila_busca

            if sheet[cell].value == items:
                result_busca.append(col)
                break

    if len(result_busca) == len(lista_busca):  # Se han encontrado todos los campos relevantes
        ok = True
    else:
        ok = False

    return ok, result_busca


def fill_aux(lista, hoja):
    row = 2

    for item in lista:
        hoja['A' + str(row)].value = item[0]
        hoja['C' + str(row)].value = round(float(item[1]), 2)
        hoja['B' + str(row)].value = item[2]
        hoja['D' + str(row)].value = item[3]
        hoja['E' + str(row)].value = item[4]
        row += 1


def buscar_en_tabla_cisco(codigo, sla, tabla_datos_cisco):
    """
    :Este procedimeinto devuelve los datos significativos de la combinación SKU-SLA si existen en catálogo.
    :Si no, devuelve el parámetro 'encontrado' a False. Se consulta la tabla que guarda los datos significativos
    :extraídos de la base de datos.
    :param codigo: El SKU del artículo cuyo backout se busca
    :param sla: el SLA del backuot (PSRN, PSUP, etc.)
    :param tabla_datos_cisco: La tabla de datos de los diversos artículos de la oferta que aparecen en el
    :catálogo oficial del fabricante
    :return: 7 parámetros: encontrado (bool), código del backout, list price, end of supprt date, precio de lista del
    : servicio y coste del GDC (Dimension Data)
    """
    encontrado, backout, price, eos, coste_interno, smt, coste_gdc = False, '', '', '', '', '', 0
    for item in tabla_datos_cisco:
        if (item.sku == codigo) and (item.serv_lev == sla):
            encontrado = True
            backout = item.backout
            price = item.list_price
            eos = item.eos
            coste_interno = item.service_price_list
            smt = item.smartnet_sku
            coste_gdc = item.gdc_cost
            break
    return encontrado, backout, price, eos, coste_interno, smt, coste_gdc


def fraccionar_lista(lista_entrada: list, size: int):
    """
    Este procedimiento toma una lista_entrada, la fracciona en sublistas de longitud size (excepto la última) y genera otra
    lista_entrada compuesta por dichas sublistas. Se usa para evitar consultas demasiado largas al API
    :param lista_entrada: list
    :param size: int
    :return: lista_listas: list
    """
    lista_listas = []
    repet = len(lista_entrada) // size

    for x in range(repet):
        lista_cortada = lista_entrada[x * size: (size * (x + 1))]
        lista_listas.append(lista_cortada)

    lista_cortada = lista_entrada[repet * size:]  # Es el último trozo, que puede tener cualquier longitud 1-10
    lista_listas.append(lista_cortada)

    return lista_listas


def request_gdc_cost_list_old(tabla_articulos: list):
    """
    Este procedimiento consulta al API de Didata y rellena el coste del GDC para los artículos listados en la
    tabla recibida como parámetro. Si falla la conexión o tarda mucho devuelve mensaje de error y rellena el coste a 0
    :param tabla_articulos: La tabla en la que ha de rellenarse el coste del GDC. El procedimiento escribe los
    :resultados directamente en esta tabla.
    :return: OK si bien; mensaje de error si ha habido problemas
    """
    # Primeramente componemos la lista de diccionarios que entregamos al API para consultar

    url_base = 'http://apps.eu.dimensiondata.com:5866'
    offset = '/product/uptime'
    # offset = '/product/endOfLife'
    url = url_base + offset

    headers = {
        'Authorization': 'appId:cffd3376-2122-4bad-bb7b-510a6a888129, secret: 1f007b7d-b1fb-4954-8ee2-276de4066167',
        'Content-type': 'application/json'
    }

    lista_consulta = []
    lista_items = []
    for item in tabla_articulos:
        lista_items.append(item.sku)

    set_items = set(lista_items)  # Se eliminan aquí los elemntos repetidos

    for item in set_items:  # Aquí es donde se forma la lista de diccionarios de consulta
        req_dict = {'Manufacturer': 'Cisco', 'ManufacturerPartNumber': item}
        lista_consulta.append(req_dict)

    # El problema es que el API no admite más de 10 artículos en cada consulta, por lo que en algunos casos es
    # necesario fraccionar la lista de consultas. Es lo que hacfemos a continuación

    lista_fraccionada_consultas = fraccionar_lista(lista_consulta, 8)

    # Ahora hacemos las consultas al API. En bloques de 8 (los artículos que contiene cada sublista

    for sublista in lista_fraccionada_consultas:

        try:
            resp = requests.post(url, headers=headers, json=sublista, timeout=100)
            if resp.status_code == 200:  # Resultado OK
                respuesta = resp.json()

                # Ahora vamos pasando por cada uno de los componentes de la respuesta y lo comparamos con la tabla de
                # artículos. En la entrada de la tabla coincidente escribimos el coste del GDC

                for articulo in respuesta:
                    key = articulo['PartNumber']
                    lista_servicios = articulo['RemoteServiceCatalog']

                    for item in tabla_articulos:  # Buscamos en la tabla la entrada coincidente con "articulo"
                        if item.sku == key:
                            service = item.serv_lev
                            gdc = 'GDC 2'
                            for serv in lista_servicios:
                                if (serv['ServicePartNumber'].lower() == service) and (serv['DeliveryOwner'] == gdc):
                                    print(serv['CombinedPrice'], item)
                                    item.gdc_cost = 12 * float(serv['CombinedPrice'])

            else:
                print(resp.status_code)
                return 'Error {}. El coste del GDC no ha podido consultarse en el API'.format(resp.status_code)

        except requests.exceptions.ReadTimeout:
            print('Esto va muy lento. E bazura')
            return 'El API tarda mucho en responder. El coste del GDC se deja a cero'

        except:
            print('Error de conexión. E bazura')
            return 'No se ha podido establecer conexión con el API. Verifique su configuración de red.' \
                   ' El coste del GDC se deja a cero'

    return 'OK'


def request_gdc_cost_list(tabla_articulos: list):
    """
    Este procedimiento consulta al API /product/uptimeSearch de Didata y rellena el coste del GDC para los artículos listados en la
    tabla recibida como parámetro. Si falla la conexión o tarda mucho devuelve mensaje de error y rellena el coste a 0
    :param tabla_articulos: La tabla en la que ha de rellenarse el coste del GDC. El procedimiento escribe los
    :resultados directamente en esta tabla.
    :return: OK si bien; mensaje de error si ha habido problemas
    """
    # Primeramente componemos la lista de diccionarios que entregamos al API para consultar

    url_base = 'http://apps.eu.dimensiondata.com:5866'
    offset = '/product/uptimeSearch'
    # offset = '/product/endOfLife'
    url = url_base + offset

    headers = {
        'Authorization': 'appId:cffd3376-2122-4bad-bb7b-510a6a888129, secret: 1f007b7d-b1fb-4954-8ee2-276de4066167',
        'Content-type': 'application/json'
    }

    lista_consulta = []
    lista_items = []
    for item in tabla_articulos:
        lista_items.append(item.sku)

    set_items = set(lista_items)  # Se eliminan aquí los elemntos repetidos

    for item in set_items:  # Aquí es donde se forma la lista de diccionarios de consulta
        aux_dict = {'Manufacturer': 'Cisco', 'ManufacturerPartNumber': item}
        lista_consulta.append(aux_dict)

    # El problema es que el API no admite más de 10 artículos en cada consulta, por lo que en algunos casos es
    # necesario fraccionar la lista de consultas. Es lo que hacfemos a continuación

    lista_fraccionada_consultas = fraccionar_lista(lista_consulta, 8)

    # Ahora hacemos las consultas al API. En bloques de 8 (los artículos que contiene cada sublista

    DeliveryOwner = 'GDC 2'

    for sublista in lista_fraccionada_consultas:

        try:
            req_dict_API = {"ProductKey": sublista, "DeliveryOwner": DeliveryOwner,
                            "PartNumberWildcard": "False"}
            resp = requests.post(url, headers=headers, json=req_dict_API, timeout=100)
            if resp.status_code == 200:  # Resultado OK
                respuesta = resp.json()

                # Ahora vamos pasando por cada uno de los componentes de la respuesta y lo comparamos con la tabla de
                # artículos. En la entrada de la tabla coincidente escribimos el coste del GDC

                for articulo in respuesta:
                    key = articulo['PartNumber']
                    lista_servicios = articulo['RemoteServiceCatalog']

                    for item in tabla_articulos:  # Buscamos en la tabla la entrada coincidente con "articulo"
                        if item.sku == key:
                            service = item.serv_lev
                            gdc = 'GDC 2'
                            for serv in lista_servicios:
                                if (serv['ServicePartNumber'].lower() == service) and (serv['DeliveryOwner'] == gdc):
                                    print(serv['CombinedPrice'], item)
                                    item.gdc_cost = 12 * float(serv['CombinedPrice'])

            else:
                print(resp.status_code)
                return 'Error {}. El coste del GDC no ha podido consultarse en el API'.format(resp.status_code)

        except requests.exceptions.ReadTimeout:
            print('Esto va muy lento. E bazura')
            return 'El API tarda mucho en responder. El coste del GDC se deja a cero'

        except:
            print('Error de conexión. E bazura')
            return 'No se ha podido establecer conexión con el API. Verifique su configuración de red.' \
                   ' El coste del GDC se deja a cero'

    return 'OK'
