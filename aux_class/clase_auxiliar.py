from collections import namedtuple
from dataclasses import dataclass

Cisco_Articles = namedtuple('Cisco_Articles', 'sku serv_lev')
DatosGenerales = namedtuple('DatosGenerales', 'nombre_oferta cliente bid version am')  # V4


@dataclass()
class CiscoItem:
    sku: str
    serv_lev: str
    backout: str = ''
    list_price: float = 0
    eos: str = ''
    smartnet_list: str = ''

    def __post_init__(self):
        self.smartnet_sku = ''
        self.service_price_list = ''
        self.gdc_cost = 0.0

    def __repr__(self):
        return ('sku: {}, sla: {}, back: {}, precio: {}, eos: {}, smartnet: {} {}'.format(self.sku, self.serv_lev,
                                                                                          self.backout, self.list_price,
                                                                                          self.eos,
                                                                                          self.smartnet_sku,
                                                                                          self.smartnet_list))


@dataclass()
class ElementosOferta:
    """
    Esta clase se utilizará para manejar los elementos no repetidos de la quote, de forma que pueda hacerse una
    oferta económica resumida para el cliente. V4
    """

    in_csv: str
    manufacturer: str
    code: str
    qty: int
    init_date: str
    end_date: str
    uptime: str
    total_price: float = 0.0


class FullElementosOferta(ElementosOferta):

    def __init__(self, uptime_descr, tech, gpl, cost_backout, venta_backout, total_cost,
                 total_sell_price, backout_name, serial_no, duration, currency,
                 in_csv, manufacturer, code, qty, init_date, end_date, uptime, total_price):
        super().__init__(in_csv, manufacturer, code, qty, init_date, end_date, uptime, total_price)

        self.uptime_descr = uptime_descr
        self.tech = tech
        self.duration = duration
        self.gpl = gpl
        self.cost_backout = cost_backout
        self.venta_backout = venta_backout
        self.total_cost = total_cost
        self.total_sell_price = total_sell_price
        self.backout_name = backout_name
        self.serial_no = serial_no
        self.currency = currency

    def igual_a(self, otro_elemento):
        if ((self.manufacturer == otro_elemento.manufacturer) and (self.code == otro_elemento.code) and
                (self.init_date == otro_elemento.init_date) and (self.end_date == otro_elemento.end_date) and
                (self.uptime == otro_elemento.uptime)):
            return True
        else:
            return False
