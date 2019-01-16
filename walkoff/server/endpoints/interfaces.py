import json

from flask import current_app, request, send_file
from flask_jwt_extended import jwt_required

from walkoff.appgateway.apiutil import get_app_device_api, UnknownApp, UnknownDevice, InvalidArgument
from walkoff.appgateway.validator import validate_device_fields
from walkoff.executiondb.device import Device, App
from walkoff.security import permissions_accepted_for_resources, ResourcePermissions
from walkoff.server.decorators import with_resource_factory
from walkoff.server.problem import Problem
from walkoff.server.returncodes import *

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


