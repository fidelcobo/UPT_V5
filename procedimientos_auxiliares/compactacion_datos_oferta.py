from aux_class import FullElementosOferta


def compactar_datos_oferta(*args):
    """
    Convertimos las diversas listas con los datos de los ítems de la oferta a una única lista de elementos
    FullElementosOferta
    :param args: Las diversas listas que contienen los datos de la oferta: código, fabricante, backout, etc.
    :return: Una única lista compuesta por elementos de la clase FullElementosOferta
    """
    lista_items = []
    for i in range(len(args[0])):
        item = FullElementosOferta(code=args[0][i], uptime=args[1][i], uptime_descr=args[2][i],
                                   tech=args[3][i], manufacturer=args[4][i], init_date=args[5][i],
                                   end_date=args[6][i], duration=args[7][i], gpl=args[8][i], cost_backout=args[9][i],
                                   venta_backout=args[10][i], total_cost=args[11][i], total_sell_price=args[12][i],
                                   backout_name=args[13][i], qty=args[14][i], serial_no=args[15][i],
                                   currency=args[16][i], in_csv=args[17][i], total_price=0)
        if item.in_csv == 'Yes':  # Corrección de error 25/1/2021
            lista_items.append(item)

    return lista_items
