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
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("test_response", "responses"))
    async def get(self, uuid):
        """
        Interface Get
        This route returns the specified  interface and attached widgets
        """
        query = request.args.get('uuid')
        return jsonify(uuid, query)

    # [PUT] /interfaces/[uuid] - Create an interface
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("test_response", "responses"))
    async def put(self, query_params):
        """
        Interface Put
        This is a route that updates an existing Interface
        """
        return jsonify(["Success", "Hi"])

    # [DELETE] /interfaces/[uuid] - Delete a specific interface
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("test_response", "responses"))
    async def delete(self, query_params):
        """
        Interface Delete
        This is a route that deletes an existing Interface
        """
        return jsonify(["Success", "Hi"])


@app.route('/interfaces')
class InterfacesEndpoint(Resource):

    # [GET] /interfaces - List all interfaces
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("test_response", "responses"))
    async def get(self):
        """
        Interface Get
        This route returns all objects
        """
        query = request.args.get('uuid')
        return jsonify(query)

    # [POST] /interfaces - Create an interface
    #@app.expect(app.create_ref_validator("interface_name", "parameters"))
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("create_interface_201", "responses"))
    async def post(self):
        """
        Interface Post
        This is a route that creates a new Interface
        """
        data = await request.get_json()
        #print("data", data)
        name = data['interface_name']
        if not Interface.query.filter_by(name=name).first():
            interface = add_interface(name=name, widgets=data['widgets'])
            db.session.commit()
            current_app.logger.info('Interface added: {0}'.format(interface.as_json()))
            return jsonify(interface.as_json()), OBJECT_CREATED
        else:
            current_app.logger.warning('Cannot create Interface {0}. Interface already exists.'.format(name))
            return Problem.from_crud_resource(
                OBJECT_EXISTS_ERROR,
                'interface',
                'create',
                'Interface with name, {}, already exists'.format(name))


