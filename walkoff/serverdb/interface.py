import logging
import sys

import nacl.secret
import nacl.utils
from uuid import uuid4
from walkoff.serverdb.interface_widget import Widget
from walkoff.extensions import db
from sqlalchemy_utils import UUIDType
from walkoff.appgateway.validator import convert_primitive_type
#from walkoff.executiondb import Execution_Base

logger = logging.getLogger(__name__)


class UnknownDeviceField(Exception):
    pass


class Interface(db.Model):
    """SqlAlchemy ORM class for Apps

    Attributes:
        id (int): Integer Column which is the primary key
        name (str): String Column which is the name of the interface
        widgets(obj): An array of Interface Widget(s) belonging to an Interface.
                      Supplied by the foreign key from Interface_widget
    """
    __tablename__ = 'interface'

    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    name = db.Column(db.String, nullable=False)
    widgets = db.relationship('Widget', backref=db.backref('interface', lazy=True))

    def __init__(self, name, widgets=None):
        self.name = name
        for widget in widgets:
            w = Widget(widget)
            self.add_widget(w)

    # def __repr__(self):
    #     return "<Interface(id={}, name={}, widgets={}>"\
    #             .format(self.id, self.name, self.widgets)

    def add_widget(self, widget):
        """Adds a widget to this Interface. If the name of the device to add to this app already exists, then
            no device will be added

        Args:
            widget (widget): The widget to add
        """
        if not any(widget.name == widget.name for widget in self.widgets):
            self.widgets.append(widget)

    def as_json(self):
        """Returns the dictionary representation of an Interface object.

        Args:
            None

        Returns:
            (out): The dictionary representation of an Interface object.
        """
        out = {"id": self.id,
               "name": self.name,
               "widgets": [widget.as_json() for widget in self.widgets]
               }
        return out
