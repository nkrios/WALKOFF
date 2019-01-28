import quart.flask_patch

from quart import jsonify, request, current_app
from quart_openapi import Pint, Resource, PintBlueprint

from flask_jwt_extended import (jwt_refresh_token_required, create_access_token, create_refresh_token, get_jwt_identity,
                                get_raw_jwt, jwt_required, decode_token)

from http import HTTPStatus

from walkoff.config import Config
from walkoff.helpers import load_yaml
from walkoff.server.problem import Problem
from walkoff.server.returncodes import *
from walkoff.serverdb import User, db
from walkoff.serverdb.tokens import revoke_token

token_problem_title = 'Could not grant access token.'
invalid_username_password_problem = Problem(
    UNAUTHORIZED_ERROR, token_problem_title, 'Invalid username or password.')
user_deactivated_problem = Problem(UNAUTHORIZED_ERROR, token_problem_title, 'User is deactivated.')

blueprint = PintBlueprint(__name__, 'auth',
                          base_model_schema=load_yaml(Config.API_PATH, "composed_api.yaml"))


async def _authenticate_and_grant_tokens(json_in, with_refresh=False):
    username = json_in.get('username', None)
    password = json_in.get('password', None)
    if not (username and password):
        return invalid_username_password_problem

    user = User.query.filter_by(username=username).first()
    if user is None:
        return invalid_username_password_problem
    try:
        password = password.encode('utf-8')
    except UnicodeEncodeError:
        return invalid_username_password_problem
    if not user.active:
        return user_deactivated_problem
    if user.verify_password(password):
        response = {'access_token': create_access_token(identity=user.id, fresh=True)}
        if with_refresh:
            user.login(request.remote_addr)
            db.session.commit()
            response['refresh_token'] = create_refresh_token(identity=user.id)
        return jsonify(response), OBJECT_CREATED
    else:
        return invalid_username_password_problem


@blueprint.route('/auth')
class Login(Resource):
    @blueprint.expect(blueprint.create_ref_validator("Authentication", "schemas"))
    @blueprint.response(HTTPStatus.OK, "Success", blueprint.create_ref_validator("Token", "schemas"))
    @blueprint.response(HTTPStatus.UNAUTHORIZED, "Unauthorized", blueprint.create_ref_validator("Error", "schemas"))
    async def post(self):
        return await _authenticate_and_grant_tokens(await request.get_json(), with_refresh=True)


async def fresh_login():
    return await _authenticate_and_grant_tokens(await request.get_json(), with_refresh=False)


@blueprint.route('/auth/refresh')
class Refresh(Resource):
    @jwt_refresh_token_required
    @blueprint.response(HTTPStatus.OK, "Success", blueprint.create_ref_validator("Token", "schemas"))
    @blueprint.response(HTTPStatus.UNAUTHORIZED, "Unauthorized", blueprint.create_ref_validator("Error", "schemas"))
    async def post(self, body=None, token_info=None, user=None):
        current_user_id = get_jwt_identity()
        user = User.query.filter(User.id == current_user_id).first()
        if user is None:
            revoke_token(get_raw_jwt())
            return Problem(
                UNAUTHORIZED_ERROR,
                'Could not grant access token.',
                'User {} from refresh JWT identity could not be found.'.format(current_user_id))
        if user.active:
            return {'access_token': create_access_token(identity=current_user_id, fresh=False)}, OBJECT_CREATED
        else:
            return user_deactivated_problem


@blueprint.route('/auth/logout')
class Logout(Resource):
    from walkoff.serverdb.tokens import revoke_token

    @jwt_required
    @blueprint.expect(blueprint.create_ref_validator("RevokeToken", "schemas"))
    @blueprint.response(HTTPStatus.NO_CONTENT, "Success")
    @blueprint.response(HTTPStatus.BAD_REQUEST, "Invalid Refresh Token", blueprint.create_ref_validator("Error", "schemas"))
    def post(self):
        data = request.get_json()
        refresh_token = data.get('refresh_token', None) if data else None
        if refresh_token is None:
            return Problem(BAD_REQUEST, 'Could not logout.', 'A refresh token is required to logout.')
        decoded_refresh_token = decode_token(refresh_token)
        refresh_token_identity = decoded_refresh_token[current_app.config['JWT_IDENTITY_CLAIM']]
        user_id = get_jwt_identity()
        if user_id == refresh_token_identity:
            user = User.query.filter(User.id == user_id).first()
            if user is not None:
                user.logout()
            revoke_token(decode_token(refresh_token))
            return None, NO_CONTENT
        else:
            return Problem(
                BAD_REQUEST,
                'Could not logout.',
                'The identity of the refresh token does not match the identity of the authentication token.')
