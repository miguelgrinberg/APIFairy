from functools import wraps

from flask import current_app, Response
from webargs.flaskparser import FlaskParser as BaseFlaskParser

from apifairy.exceptions import ValidationError


class FlaskParser(BaseFlaskParser):
    USE_ARGS_POSITIONAL = False
    DEFAULT_VALIDATION_STATUS = 400

    def load_form(self, req, schema):
        return {**self.load_files(req, schema),
                **super().load_form(req, schema)}

    def handle_error(self, error, req, schema, *, error_status_code,
                     error_headers):
        raise ValidationError(
            error_status_code or self.DEFAULT_VALIDATION_STATUS,
            error.messages)


parser = FlaskParser()
use_args = parser.use_args
_webhooks = {}


def _ensure_sync(f):
    if hasattr(f, '_sync_ensured'):
        return f

    @wraps(f)
    def wrapper(*args, **kwargs):
        if hasattr(current_app, 'ensure_sync'):
            return current_app.ensure_sync(f)(*args, **kwargs)
        else:  # pragma: no cover
            return f(*args, **kwargs)

    wrapper._sync_ensured = True
    return wrapper


def _annotate(f, **kwargs):
    if not hasattr(f, '_spec'):
        f._spec = {}
    for key, value in kwargs.items():
        f._spec[key] = value


def authenticate(auth, **kwargs):
    def decorator(f):
        roles = kwargs.get('role')
        if not isinstance(roles, list):  # pragma: no cover
            roles = [roles] if roles is not None else []
        f = _ensure_sync(f)
        _annotate(f, auth=auth, roles=roles)
        return auth.login_required(**kwargs)(f)
    return decorator


def arguments(schema, location='query', **kwargs):
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        f = _ensure_sync(f)
        if not hasattr(f, '_spec') or f._spec.get('args') is None:
            _annotate(f, args=[])
        f._spec['args'].append((schema, location))
        arg_name = f'{location}_{schema.__class__.__name__}_args'

        @wraps(f)
        def _f(*args, **kwargs):
            location_args = kwargs.pop(arg_name, {})
            return f(*args, location_args, **kwargs)

        return use_args(schema, location=location, arg_name=arg_name,
                        **kwargs)(_f)
    return decorator


def body(schema, location='json', media_type=None, **kwargs):
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        f = _ensure_sync(f)
        _annotate(f, body=(schema, location, media_type))
        arg_name = f'{location}_{schema.__class__.__name__}_args'

        @wraps(f)
        def _f(*args, **kwargs):
            location_args = kwargs.pop(arg_name, {})
            return f(*args, location_args, **kwargs)

        return use_args(schema, location=location, arg_name=arg_name,
                        **kwargs)(_f)
    return decorator


def response(schema, status_code=200, description=None, headers=None):
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        f = _ensure_sync(f)
        _annotate(f, response=schema, status_code=status_code,
                  description=description, response_headers=headers)

        @wraps(f)
        def _response(*args, **kwargs):
            rv = f(*args, **kwargs)
            if isinstance(rv, Response):  # pragma: no cover
                raise RuntimeError(
                    'The @response decorator cannot handle Response objects.')
            if isinstance(rv, tuple):
                json = schema.jsonify(rv[0])
                if len(rv) == 2:
                    if not isinstance(rv[1], int):
                        rv = (json, status_code, rv[1])
                    else:
                        rv = (json, rv[1])
                elif len(rv) >= 3:
                    rv = (json, rv[1], rv[2])
                else:
                    rv = (json, status_code)
                return rv
            else:
                return schema.jsonify(rv), status_code
        return _response
    return decorator


def other_responses(responses):
    def decorator(f):
        f = _ensure_sync(f)
        _annotate(f, other_responses=responses)
        return f
    return decorator


def webhook(method='GET', blueprint=None, endpoint=None):
    def decorator(f):
        class WebhookRule:
            def __init__(self, view_func, endpoint, methods):
                self.view_func = view_func
                self.endpoint = endpoint
                self.methods = methods

        nonlocal endpoint
        endpoint = endpoint or f.__name__
        if blueprint is not None:
            endpoint = blueprint.name + '.' + endpoint
        if endpoint not in _webhooks:
            _webhooks[endpoint] = WebhookRule(f, endpoint, methods=[method])
        else:
            raise ValueError(f'Webhook {endpoint} has been defined twice')
        return f

    if callable(method) and blueprint is None and endpoint is None:
        # invoked as a decorator without arguments
        f = method
        method = 'GET'
        return decorator(f)
    else:
        # invoked as a decorator with arguments
        return decorator
