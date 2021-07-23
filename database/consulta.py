from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .declaracion import Catalogo, CatalogoSmartnet


def look_for_cisco_list(sku: str, serv_list: list, db, smartnet: bool):
    """
    Este procedimiento se conecta a la base de datos de catálogo Cisco. Busca el artículo con el SKU y la lista de
    posibles PSSs o Smartnets(serv_list). Si lo encuentra, devuelve el código de servicios, el precio
    de lista y la fecha de fin de soporte
    :param sku: El código del artículo en cuestión
    :param serv_list: Lista de posibles PSSs o Smarnet
    :param db: Fichero de la base de datos de catálogo Cisco
    :param smartnet: Indica si hay que buscar en la tabla de PSSs o de Smartnet de la base de datos

    :return: 4 parámetros
        encontrado (bool): si la búsqueda ha sido exitosa o no
        serv_code = el código del PSS/Smartnet buscado
        price: precio de lista anual del backout (USD)
        eos = fecha de fin de soporte
    """
    engine = create_engine('sqlite:///' + db, echo=False)
    found = False

    if smartnet:
        tabla = CatalogoSmartnet  # Buscamos en la tabla de smartnets

    else:
        tabla = Catalogo # Buscamos en la tabla de PSS/UCS

    if not serv_list:
        return found, None, None, None  # La lista está vacía. Decimos que no se ha encontrado nada

    # Abrimos sesión en la base de datos
    Session = sessionmaker(bind=engine)
    session = Session()

    for sla in serv_list:
        articulo = session.query(tabla).filter((tabla.sku == sku), (tabla.serv_lev == sla)).first()

        if articulo:
            found = True
            session.close()
            engine.dispose()
            return found, articulo.serv_code, articulo.price, articulo.eos

    session.close()
    engine.dispose()
    return found, None, None, None  # No figura en el catálogo
