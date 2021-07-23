from collections import namedtuple

Cisco_Articles = namedtuple('Cisco_Articles', 'sku serv_lev')
DatosGenerales = namedtuple('DatosGenerales', 'nombre_oferta cliente bid version am')  # V4


class CiscoItem:

    def __init__(self, sku, serv_lev, backout='', list_price=0, eos='', smartnet_list=''):
        self.sku = sku
        self.serv_lev = serv_lev
        self.backout = backout
        self.list_price = list_price
        self.eos = eos
        self.smartnet_list = smartnet_list
        self.smartnet_sku = ''
        self.service_price_list = ''
        self.gdc_cost = 0.0

    def __repr__(self):
        return ('sku: {}, sla: {}, back: {}, precio: {}, eos: {}, smartnet: {} {}'.format(self.sku, self.serv_lev,
                                                                                          self.backout, self.list_price,
                                                                                          self.eos,
                                                                                          self.smartnet_sku,
                                                                                          self.smartnet_list))


class ElementosOferta:
    """
    Esta clase se utilizará para manejar los elementos no repetidos de la quote, de forma que pueda hacerse una
    oferta económica resumida para el cliente. V4
    """

    def __init__(self, in_csv, manufacturer, code, qty, init_date, end_date, uptime, total_price=0):
        self.in_csv = in_csv
        self.manufacturer = manufacturer
        self.code = code
        self.qty = qty
        self.init_date = init_date
        self.end_date = end_date
        self.uptime = uptime
        self.total_price = total_price


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


