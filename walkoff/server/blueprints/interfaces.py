from quart import jsonify, request
from quart_openapi import PintBlueprint, Resource, Swagger
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import walkoff.config as config
from flask_swagger_ui import get_swaggerui_blueprint
from http import HTTPStatus
from walkoff.helpers import load_yaml
from walkoff.extensions import db
from walkoff.serverdb import add_interface
from walkoff.serverdb import Interface
from walkoff.serverdb.interface_widget import Widget
from walkoff.server.returncodes import *
from quart import request, current_app
from walkoff.server.problem import Problem

import json

from ruamel.yaml import YAML

app = PintBlueprint(__name__, "interfaces", base_model_schema=load_yaml(config.Config.API_PATH, 'interfaces.yaml'))


# @app.param("test_path", ref=app.create_ref_validator("test_path", "parameters"))
# @app.param("test_query", ref=app.create_ref_validator("test_query", "parameters"))
#@jwt_required
@app.route('/interfaces/<uuid>')
class InterfaceEndpoint(Resource):

    # [GET] /interfaces/[uuid] - Get specific interface
    # @interface_validator("blah")
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("get_single_interface_200", "responses"))
    async def get(self, uuid):
        """
        Interface Get
        This route returns the specified  interface and attached widgets
        """

        interface = Interface.query.filter_by(id=uuid).first()
        if interface:
            return jsonify(interface.as_json()), SUCCESS
        else:
            current_app.logger.warning('Interface with id, {}, not found.'.format(uuid))
            return Problem.from_crud_resource(
                OBJECT_EXISTS_ERROR,
                'interface',
                'get',
                'Interface with id, {}, not found'.format(uuid))

    # [PUT] /interfaces/<uuid> - Create an interface
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("test_response", "responses"))
    async def put(self, uuid):
        """
        Interface Put
        This is a route that updates an existing Interface
        """

        data = await request.get_json()
        interface = Interface.query.filter_by(id=uuid).first()
        print("data", data)
        print("interface", interface.as_json())

        if interface:
            if data['interface_name']:
                interface.name = data['interface_name']

            incoming_widgets = []
            for w in data['widgets']:
                new_widget = Widget(w)
                incoming_widgets.append(new_widget)
            print("incoming widgets", incoming_widgets)

            if len(interface.widgets) == 0:
                for incoming_widget in incoming_widgets:
                    interface.add_widget(incoming_widget)

            else:
                for index, incoming_widget in enumerate(incoming_widgets):
                    for interface_widget in interface.widgets:
                        if incoming_widget.title == interface_widget.title:
                            interface.widgets[index] = incoming_widget
                        else:
                            interface.add_widget(incoming_widget)
            print("updated interface", interface.as_json())
            db.session.commit()
            return jsonify("Interface {} updated".format(interface.name)), SUCCESS

        else:
            current_app.logger.warning('Interface with id, {}, not found.'.format(uuid))
            return Problem.from_crud_resource(
                    OBJECT_EXISTS_ERROR,
                    'interface',
                    'update',
                    'Interface with id, {}, not found'.format(uuid))

    # [DELETE] /interfaces/[uuid] - Delete a specific interface
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("test_response", "responses"))
    async def delete(self, uuid):
        """
        Interface Delete
        This is a route that deletes an existing Interface
        """
        interface = Interface.query.filter_by(id=uuid).first()
        if interface:
            db.session.delete(interface)
            db.session.commit()
            return jsonify("Interface {} deleted.".format(interface.name)), SUCCESS
        else:
            current_app.logger.warning('Interface with id, {}, not found.'.format(uuid))
            return Problem.from_crud_resource(
                OBJECT_EXISTS_ERROR,
                'interface',
                'get',
                'Interface with id, {}, not found'.format(uuid))


@app.route('/interfaces')
class InterfacesEndpoint(Resource):

    # [GET] /interfaces - List all interfaces
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("get_all_interfaces_200", "responses"))
    async def get(self):
        """
        Interface Get
        This route returns all objects
        """
        interfaces = Interface.query.all()
        result = []
        for interface in interfaces:
            result.append(interface.as_json())
        return jsonify(result), SUCCESS

    # [POST] /interfaces - Create an interface
    #@app.expect(app.create_ref_validator("interface_name", "parameters"))
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("create_interface_201", "responses"))
    async def post(self):
        """
        Interface Post
        This is a route that creates a new Interface
        """
        data = await request.get_json()
        name = data['interface_name']
        if not Interface.query.filter_by(name=name).first():
            interface = add_interface(name=name, widgets=data['widgets'])
            current_app.logger.info('Interface added: {0}'.format(interface.as_json()))
            return jsonify("Interface {} created".format(interface.name)), OBJECT_CREATED
        else:
            current_app.logger.warning('Cannot create Interface {0}. Interface already exists.'.format(name))
            return Problem.from_crud_resource(
                OBJECT_EXISTS_ERROR,
                'interface',
                'create',
                'Interface with name, {}, already exists'.format(name))


