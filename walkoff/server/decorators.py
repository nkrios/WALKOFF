from uuid import UUID

from quart import current_app

from walkoff.server.problem import Problem
from walkoff.server.returncodes import OBJECT_DNE_ERROR, BAD_REQUEST


def get_id_str(ids):
    return '-'.join([str(id_) for id_ in ids])


def resource_not_found_problem(resource, operation, id_):
    return Problem.from_crud_resource(
        OBJECT_DNE_ERROR,
        resource,
        operation,
        '{} {} does not exist.'.format(resource.title(), id_))


def log_operation_error(resource, operation, id_):
    current_app.logger.error('Could not {} {} {}. {} does not exist'.format(operation, resource, id_, resource))


async def dne_error(resource, operation, ids):
    id_str = get_id_str(ids)
    log_operation_error(resource, operation, id_str)
    return lambda: (resource_not_found_problem(resource, operation, id_str))


def validate_resource_exists_factory(resource_name, existence_func):
    def validate_resource_exists(operation, *ids):

        def wrapper(func):
            if existence_func(*ids):
                return func
            else:
                return dne_error(resource_name, operation, ids)

        return wrapper

    return validate_resource_exists


def invalid_id_problem(resource, operation):
    return Problem.from_crud_resource(BAD_REQUEST, resource, operation, 'Invalid ID format.')


def with_resource_factory(resource_name, getter_func, validator=None):
    """Factory pattern which takes in resource name and resource specific functions, returns a validator decorator"""
    print("validator factory")

    def arg_wrapper(operation, id_param):
        """This decorator serves to take in the args to the decorator call and make it available below"""
        print("arg wrapper")

        def func_wrapper(func):
            """This decorator serves to wrap the actual decorated function and return the replacement function below"""
            print("func wrapper")

            async def func_caller(*args, **kwargs):
                """This decorator is the actual replacement function for the decorated function"""
                print("func caller")
                print(func, operation, id_param, args, kwargs)
                if validator and not validator(id_param):
                    return await invalid_id_problem(resource_name, operation)

                kwargs[id_param] = getter_func(kwargs[id_param])
                if kwargs[id_param]:
                    return await func(*args, **kwargs)
                else:
                    return await dne_error(resource_name, operation, kwargs[id_param])

            return func_caller

        return func_wrapper

    return arg_wrapper


def is_valid_uid(*ids):
    try:
        for id_ in ids:
            UUID(id_)
        return True
    except ValueError:
        return False
