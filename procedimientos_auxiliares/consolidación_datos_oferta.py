from typing import List

from aux_class import FullElementosOferta


def consolidar_datos(datos: List[FullElementosOferta]):
    """
    Este procedimiento recibe una lista compuesta de las diversas entradas del fichero de oferta. Consolida los
    elementos repetidos, entregando así una lista consolidada de menor longitud
    :param datos: Lista de entradas de la oferta
    :return: Lista consolidada de entradas
    """

    lista_consolidada = [datos[0]]  # Lista de elementos ya consolidados
    lista_consolidada[0].serial_no = str(lista_consolidada[0].serial_no)  # Por si el serial no. es todo cifras

    for i in range(1, len(datos)):
        item = datos[i]

        encontrado = False  # Parámetro auxiliar
        for item_consolidado in lista_consolidada:  # Comprobamos si la entrada ya estaba en lista_consolidada
            if ((item.manufacturer == item_consolidado.manufacturer) and (item.code == item_consolidado.code) and
                    (item.init_date == item_consolidado.init_date) and (item.end_date == item_consolidado.end_date) and
                    (item.uptime == item_consolidado.uptime)):
                item_consolidado.qty += item.qty
                no_serie = str(item.serial_no)
                item_consolidado.serial_no = item_consolidado.serial_no + (', ' + no_serie)
                encontrado = True
                break

        if not encontrado:  # Si no está, lo añadimos
            item.serial_no = str(item.serial_no)  # Convertir en str por si es todo cifras
            lista_consolidada.append(item)

    return lista_consolidada
