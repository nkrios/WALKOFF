import quart.flask_patch

import json
from walkoff.helpers import load_yaml
import walkoff.config as config

from quart import jsonify, request, Response
from quart_openapi import Pint, Resource, Swagger
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
# from flask_sqlalchemy import SQLAlchemy

from flask_swagger_ui import get_swaggerui_blueprint
from http import HTTPStatus

from jinja2 import FileSystemLoader

from walkoff.server.context import Context

from walkoff.server.blueprints import root
from walkoff.server.blueprints import interfaces

from walkoff.extensions import db, jwt


def register_blueprints(app_):
    app_.register_blueprint(root.root_page)
    app_.register_blueprint(auth.blueprint)
    app_.register_blueprint(interfaces.app)
    swaggerui_blueprint = get_swaggerui_blueprint("/api/docs", "/openapi.json")
    app_.register_blueprint(swaggerui_blueprint, url_prefix="/api/docs")


def create_app():
    config.initialize()

    app_ = Pint(__name__, base_model_schema=load_yaml(config.Config.API_PATH, "interfaces.yaml"),
                template_folder="walkoff/templates")
    app_.config["JWT_SECRET_KEY"] = 'changethis'
    app_.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
    app_.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app_)
    jwt.init_app(app_)

    # app_.jinja_loader = FileSystemLoader(['walkoff/templates'])
    app_.config.from_object(config.Config)
    app_.running_context = Context(executor=False)

    register_blueprints(app_)

    return app_


app = create_app()
app.run(host="0.0.0.0", port=5001)