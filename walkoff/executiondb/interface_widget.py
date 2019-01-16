import logging
import sys

import nacl.secret
import nacl.utils
from sqlalchemy import JSON, Column, Integer, ForeignKey, String, LargeBinary, Enum, DateTime, func, orm, and_
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import walkoff.config
from walkoff.appgateway.validator import convert_primitive_type
from walkoff.executiondb import Execution_Base, ExecutionDatabase

logger = logging.getLogger(__name__)


class UnknownDeviceField(Exception):
    pass


class InterfaceWidget(Execution_Base):
    """SqlAlchemy ORM class for Apps

    Attributes:
        id (int): Integer Column, which is the primary key
        title (str): String Column, which is the name of the interface
        type (str): String Column, which is the type of interface
        x(int): Integer Column which is the x coordinate in a point pair (x,y) format
        y(int): Integer Column, which is the y coordinate in a point pair (x,y) format
        cols(int): Integer Column, which is the number of columns in widget
        rows(int): Integer Column, which is the number of rows in the widget
        options(str): String Column, which are the different details about the widget
        interface_id(int): Integer Column, the foreign key related to Interface

    Args:
        name (str): Name
    """
    __tablename__ = 'interface_widget'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column('title', String, nullable=False)
    type = Column('type', String, nullable=False)
    x = Column('x', Integer, nullable=False)
    y = Column('y', Integer, nullable=False)
    cols = Column('cols', Integer, nullable=False)
    rows = Column('rows', Integer, nullable=False)
    options = Column('options', String, nullable=False)
    interface_id = Column(Integer, ForeignKey('interface.id'))


