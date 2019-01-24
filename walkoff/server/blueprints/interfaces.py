from quart import jsonify, request
from quart_openapi import PintBlueprint, Resource, Swagger
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import walkoff.config as config
from flask_swagger_ui import get_swaggerui_blueprint
from http import HTTPStatus
from walkoff.helpers import load_yaml
from walkoff.extensions import db

# from .helper import load_yaml
# from .auth import blueprint as auth_bp

from ruamel.yaml import YAML

app = PintBlueprint(__name__, "interfaces", base_model_schema=load_yaml(config.Config.API_PATH, 'interfaces.yaml'))


# @app.param("test_path", ref=app.create_ref_validator("test_path", "parameters"))
# @app.param("test_query", ref=app.create_ref_validator("test_query", "parameters"))
#@jwt_required
@app.route('/interfaces/<uuid>')
class Interface(Resource):

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
class Interfaces(Resource):

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
    @app.response(HTTPStatus.OK, "Success", app.create_ref_validator("test_response", "responses"))
    async def post(self, query_params):
        """
        Interface Post
        This is a route that creates a new Interface
        """
        #interface_id = request.args.get('id')
        interface_name = request.args.get('name')
        interface_widgets = request.args.get('widgets')
        interface = Interface(interface_name, interface_widgets)
        db.session.add(interface)
        db.session.commit()
        return jsonify(["Success", "Object, {} , created".format(interface_name)])


