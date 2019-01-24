import quart.flask_patch

from datetime import timedelta

from quart import current_app, request
from quart_openapi import Pint, Resource, PintBlueprint
from flask_jwt_extended import jwt_required

from http import HTTPStatus

import walkoff.config
from walkoff.helpers import format_exception_message, load_yaml
from walkoff.security import permissions_accepted_for_resources, ResourcePermissions
from walkoff.server.problem import Problem
from walkoff.server.returncodes import *

config_bp = PintBlueprint(__name__, 'configuration',
                          base_model_schema=load_yaml(walkoff.config.Config.API_PATH, "configuration.yaml"))


@config_bp.route('/configuration')
class ReadConfigValues(Resource):

    def __get_current_configuration(self):
        return {'db_path': walkoff.config.Config.DB_PATH,
                'logging_config_path': walkoff.config.Config.LOGGING_CONFIG_PATH,
                'host': walkoff.config.Config.HOST,
                'port': int(walkoff.config.Config.PORT),
                'walkoff_db_type': walkoff.config.Config.WALKOFF_DB_TYPE,
                'access_token_duration': int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].seconds / 60),
                'refresh_token_duration': int(current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].days),
                'zmq_results_address': walkoff.config.Config.ZMQ_RESULTS_ADDRESS,
                'zmq_communication_address': walkoff.config.Config.ZMQ_COMMUNICATION_ADDRESS,
                'number_processes': int(walkoff.config.Config.NUMBER_PROCESSES),
                'number_threads_per_process': int(walkoff.config.Config.NUMBER_THREADS_PER_PROCESS),
                'cache': walkoff.config.Config.CACHE}

    def _reset_token_durations(self, access_token_duration=None, refresh_token_duration=None):
        access_token_duration = (timedelta(minutes=access_token_duration) if access_token_duration is not None
                                 else current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
        refresh_token_duration = (timedelta(days=refresh_token_duration) if refresh_token_duration is not None
                                  else current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
        if access_token_duration < refresh_token_duration:
            current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = access_token_duration
            current_app.config['JWT_REFRESH_TOKEN_EXPIRES'] = refresh_token_duration
            return True
        return False

    @jwt_required
    @permissions_accepted_for_resources(ResourcePermissions('configuration', ['read']))
    @config_bp.response(HTTPStatus.OK, "Success", config_bp.create_ref_validator("Configuration", "schemas"))
    @config_bp.response(HTTPStatus.UNAUTHORIZED, "Unauthorized", config_bp.create_ref_validator("Error", "schemas"))
    def get(self):
        return self.__get_current_configuration(), SUCCESS

    @jwt_required
    @permissions_accepted_for_resources(ResourcePermissions('configuration', ['update']))
    @config_bp.expect(config_bp.create_ref_validator("Configuration", "schemas"))
    @config_bp.response(HTTPStatus.OK, "Success", config_bp.create_ref_validator("Configuration", "schemas"))
    @config_bp.response(HTTPStatus.UNAUTHORIZED, "Unauthorized", config_bp.create_ref_validator("Error", "schemas"))
    @config_bp.response(HTTPStatus.INTERNAL_SERVER_ERROR, "Could not write configuration to file",
                        config_bp.create_ref_validator("Error", "schemas"))
    def put(self):
        config_in = request.get_json()
        if not self._reset_token_durations(access_token_duration=config_in.get('access_token_duration', None),
                                           refresh_token_duration=config_in.get('refresh_token_duration', None)):
            return Problem.from_crud_resource(
                BAD_REQUEST,
                'configuration',
                'update',
                'Access token duration must be less than refresh token duration.')

        for config, config_value in config_in.items():
            if hasattr(walkoff.config.Config, config.upper()):
                setattr(walkoff.config.Config, config.upper(), config_value)
            elif hasattr(current_app.config, config.upper()):
                setattr(current_app.config, config.upper(), config_value)

        current_app.logger.info('Changed configuration')
        try:
            walkoff.config.Config.write_values_to_file()
            return self.__get_current_configuration(), SUCCESS
        except (IOError, OSError) as e:
            current_app.logger.error('Could not write changes to configuration to file')
            return Problem(
                SERVER_ERROR,
                'Could not write changes to file.',
                'Could not write configuration changes to file. Problem: {}'.format(format_exception_message(e)))

    @jwt_required
    @permissions_accepted_for_resources(ResourcePermissions('configuration', ['update']))
    @config_bp.expect(config_bp.create_ref_validator("Configuration", "schemas"))
    @config_bp.response(HTTPStatus.OK, "Success", config_bp.create_ref_validator("Configuration", "schemas"))
    @config_bp.response(HTTPStatus.UNAUTHORIZED, "Unauthorized", config_bp.create_ref_validator("Error", "schemas"))
    @config_bp.response(HTTPStatus.INTERNAL_SERVER_ERROR, "Could not write configuration to file",
                        config_bp.create_ref_validator("Error", "schemas"))
    def patch(self):
        return self.put()



