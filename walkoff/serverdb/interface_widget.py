import logging
import sys

import nacl.secret
import nacl.utils

import walkoff.config
from walkoff.appgateway.validator import convert_primitive_type
#from walkoff.executiondb import Execution_Base, ExecutionDatabase
from walkoff.extensions import db
from uuid import uuid4
logger = logging.getLogger(__name__)


class UnknownDeviceField(Exception):
    pass


class Widget(db.Model):
    """SqlAlchemy ORM class for Apps

    Attributes:
        id (int): db.Integer db.Column, which is the primary key
        title (str): db.String db.Column, which is the name of the interface
        type (str): db.String db.Column, which is the type of interface
        x(int): db.Integer db.Column which is the x coordinate in a point pair (x,y) format
        y(int): db.Integer db.Column, which is the y coordinate in a point pair (x,y) format
        cols(int): db.Integer db.Column, which is the number of db.Columns in widget
        rows(int): db.Integer db.Column, which is the number of rows in the widget
        options(str): db.String db.Column, which are the different details about the widget
        interface_id(int): db.Integer db.Column, the foreign key related to Interface

    Args:
        name (str): Name
    """
    __tablename__ = 'interface_widget'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, default=uuid4)
    title = db.Column('title', db.String, nullable=False)
    x = db.Column('x', db.Integer, nullable=False)
    y = db.Column('y', db.Integer, nullable=False)
    cols = db.Column('cols', db.Integer, nullable=False)
    rows = db.Column('rows', db.Integer, nullable=False)

    # This json string is arbitrary and will not be the same format for each widget
    options = db.Column('options', db.String, nullable=True)

    interface_id = db.Column(db.Integer, db.ForeignKey('interface.id'))

    # def __init__(self, title, x, y, cols, rows, options):
    #     self.title = title
    #     self.x = x
    #     self.y = y
    #     self.cols = cols
    #     self.rows = rows
    #     self.options = options

    def __init__(self, widget):
        self.title = widget['title']
        self.x = widget['x']
        self.y = widget['y']
        self.cols = widget['cols']
        self.rows = widget['rows']
        self.options = widget['options']

    def as_json(self):
        """Returns the dictionary representation of an Interface_Widget object.

        Args:
            None

        Returns:
            (out): The dictionary representation of an Interface_Widget object.
        """
        out = {"id": self.id,
                "title": self.tlte,
                "type": self.type,
                "x": self.x,
                "y": self.y,
                "cols": self.cols,
                "rows": self.rows,
                "options": self.options,
                "interface_id": self.interface_id
               }
        return out
