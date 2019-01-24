import logging
import sys

import nacl.secret
import nacl.utils
from sqlalchemy import JSON, Column, Integer, ForeignKey, String, orm, and_
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from uuid import uuid4

import walkoff.config
from walkoff.appgateway.validator import convert_primitive_type
from walkoff.executiondb import Execution_Base, ExecutionDatabase

logger = logging.getLogger(__name__)


class UnknownDeviceField(Exception):
    pass


class Interface(Execution_Base):
    """SqlAlchemy ORM class for Apps

    Attributes:
        id (int): Integer Column which is the primary key
        name (str): String Column which is the name of the interface
        widgets(obj): An array of Interface Widget(s) belonging to an Interface.
                      Supplied by the foreign key from Interface_widget
    Args:
        name (str): Name
    """
    __tablename__ = 'interface'

    id = Column(Integer, primary_key=True, autoincrement=True, default=uuid4)
    name = Column('name', String, nullable=False)
    widgets = relationship('InterfaceWidget')

    def __init__(self, name, widgets=None):

        self.name = name
        if widgets is not None:
            for widget in widgets:
                self.add_widget(widget)

    def add_widget(self, widget):
        """Adds a widget to this Interface. If the name of the device to add to this app already exists, then
            no device will be added

        Args:
            widget (widget): The widget to add
        """
        if not any(widget.name == widget.name for widget in self.widgets):
            self.widgets.append(widget)
