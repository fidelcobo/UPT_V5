
from sqlalchemy import (Column, Integer, String)
from sqlalchemy.ext.declarative import declarative_base

# Estos son los módulos que hay que importar para declarar la DB

# engine = create_engine('sqlite:///cisco.db', echo=False)
Base = declarative_base()

class Catalogo(Base):  # Ésta es la tabla de catálogo para PSSs
    __tablename__ = 'cisco'
    id = Column(Integer, primary_key=True)
    sku = Column(String, nullable=False)
    serv_lev = Column(String, nullable=False)
    serv_code = Column(String, nullable=False)
    price = Column(String, nullable=False)
    eos = Column(String, nullable=False)

    def __init__(self, sku, serv_lev, serv_code, price, eos):
        self.sku = sku
        self.serv_lev = serv_lev
        self.serv_code = serv_code
        self.price = price
        self.eos = eos

    def __repr__(self):
        return str(self.titulo)


class CatalogoSmartnet(Base):  # Ésta es la tabla de catálogo para Smartnet
    __tablename__ = 'cisco_smartnet'
    id = Column(Integer, primary_key=True)
    sku = Column(String, nullable=False)
    serv_lev = Column(String, nullable=False)
    serv_code = Column(String, nullable=False)
    price = Column(String, nullable=False)
    eos = Column(String, nullable=False)

    def __init__(self, sku, serv_lev, serv_code, price, eos):
        self.sku = sku
        self.serv_lev = serv_lev
        self.serv_code = serv_code
        self.price = price
        self.eos = eos

    def __repr__(self):
        return str(self.titulo)


# Base.metadata.create_all(engine)
