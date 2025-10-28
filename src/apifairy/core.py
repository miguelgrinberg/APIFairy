from json import dumps
import re
import sys
try:
    from typing import _AnnotatedAlias
except ImportError:  # pragma: no cover
    _AnnotatedAlias = None

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import current_app, Blueprint, render_template, request
from flask_marshmallow import fields
try:
    from flask_marshmallow import sqla
except ImportError:
    sqla = None
try:
    from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
except ImportError:  # pragma: no cover
    HTTPBasicAuth = None
    HTTPTokenAuth = None
from packaging.version import Version
from werkzeug.http import HTTP_STATUS_CODES

from apifairy.decorators import _webhooks
from apifairy.exceptions import ValidationError
from apifairy import fields as apifairy_fields


class APIFairy:
    def __init__(self, app=None):
        self.title = None
        self.version = None
        self.apispec_path = None
        self.ui = None
        self.ui_path = None
        self.tags = None

        self.apispec_callback = None
        self.error_handler_callback = self.default_error_handler
        self._apispec = None
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        self.title = app.config.get('APIFAIRY_TITLE', 'No title')
        self.version = app.config.get('APIFAIRY_VERSION', 'No version')
        self.apispec_path = app.config.get('APIFAIRY_APISPEC_PATH',
                                           '/apispec.json')
        self.apispec_version = app.config.get('APIFAIRY_APISPEC_VERSION', None)
        self.apispec_decorators = app.config.get(
            'APIFAIRY_APISPEC_DECORATORS', [])
        self.ui = app.config.get('APIFAIRY_UI', 'redoc')
        self.ui_path = app.config.get('APIFAIRY_UI_PATH', '/docs')
        self.ui_decorators = app.config.get('APIFAIRY_UI_DECORATORS', [])
        self.tags = app.config.get('APIFAIRY_TAGS')

        bp = Blueprint('apifairy', __name__, template_folder='templates')

        if self.apispec_path:
            def json():
                return dumps(self.apispec), 200, \
                    {'Content-Type': 'application/json'}

            for decorator in self.apispec_decorators:
                json = decorator(json)
            bp.add_url_rule(self.apispec_path, 'json', json)

        if self.ui_path:
            def docs():
                return render_template(f'apifairy/{self.ui}.html',
                                       title=self.title, version=self.version)

            for decorator in self.ui_decorators:
                docs = decorator(docs)
            bp.add_url_rule(self.ui_path, 'docs', docs)

        if self.apispec_path or self.ui_path:  # pragma: no cover
            app.register_blueprint(bp)

        @app.errorhandler(ValidationError)
        def http_error(error):
            return self.error_handler_callback(error.status_code,
                                               error.messages)

    def process_apispec(self, f):
        self.apispec_callback = f
        return f

    def error_handler(self, f):
        self.error_handler_callback = f
        return f

    def default_error_handler(self, status_code, messages):
        return {'messages': messages}, status_code

    @property
    def apispec(self):
        if self._apispec is None:
            self._apispec = self._generate_apispec()
            if self.apispec_callback:
                self._apispec = self.apispec_callback(self._apispec)
        return self._apispec

    def _generate_apispec(self):
        def resolver(schema):
            name = schema.__class__.__name__
            if name.endswith("Schema"):
                name = name[:-6] or name
            if schema.partial:
                name += 'Update'
            return name

        # info object
        info = {}
        module_name = current_app.import_name
        while module_name:
            module = sys.modules[module_name]
            if module.__doc__:  # pragma: no cover
                info['description'] = module.__doc__.strip()
                break
            if '.' not in module_name:
                module_name = '.' + module_name
            module_name = module_name.rsplit('.', 1)[0]

        # servers
        servers = [{'url': request.url_root}]

        # tags
        tag_names = self.tags
        if tag_names is None:  # pragma: no branch
            # auto-generate tags from blueprints
            tag_names = []
            for rule in current_app.url_map.iter_rules():
                view_func = current_app.view_functions[rule.endpoint]
                if hasattr(view_func, '_spec'):
                    if '.' in rule.endpoint:
                        blueprint = rule.endpoint.rsplit('.', 1)[0]
                        if blueprint not in tag_names:  # pragma: no branch
                            tag_names.append(blueprint)
        tags = {}
        for name, blueprint in current_app.blueprints.items():
            if name not in tag_names:
                continue
            module = sys.modules[blueprint.import_name]
            tag = {'name': name.title()}
            if module.__doc__:  # pragma: no cover
                tag['description'] = module.__doc__.strip()
            tags[name] = tag
        tag_list = [tags[name] for name in tag_names]
        ma_plugin = MarshmallowPlugin(schema_name_resolver=resolver)
        apispec_version = self.apispec_version
        if apispec_version is None:
            apispec_version = '3.1.0' if _webhooks else '3.0.3'
        version = Version(apispec_version)
        if version < Version('3.0.3'):
            raise RuntimeError("Must use at openapi version '3.0.3' or newer")
        elif version < Version('3.1.0') and _webhooks:
            raise RuntimeError("Must use at least openapi version '3.1.0' "
                               'when using the @webhook decorator')
        spec = APISpec(
            title=self.title,
            version=self.version,
            openapi_version=apispec_version,
            plugins=[ma_plugin],
            info=info,
            servers=servers,
            tags=tag_list,
        )

        # configure flask-marshmallow URL types
        ma_plugin.converter.field_mapping[fields.URLFor] = ('string', 'url')
        ma_plugin.converter.field_mapping[fields.AbsoluteURLFor] = \
            ('string', 'url')
        if sqla is not None:  # pragma: no cover
            ma_plugin.converter.field_mapping[sqla.HyperlinkRelated] = \
                ('string', 'url')

        # configure FileField
        ma_plugin.converter.field_mapping[apifairy_fields.FileField] = \
            ('string', 'binary')

        # security schemes
        auth_schemes = []
        auth_names = []
        for rule in current_app.url_map.iter_rules():
            view_func = current_app.view_functions[rule.endpoint]
            if hasattr(view_func, '_spec'):
                auth = view_func._spec.get('auth')
                if auth is not None and auth not in auth_schemes:
                    auth_schemes.append(auth)
                    if isinstance(auth, HTTPBasicAuth):
                        name = 'basic_auth'
                    elif isinstance(auth, HTTPTokenAuth):
                        if auth.scheme == 'Bearer' and auth.header is None:
                            name = 'token_auth'
                        else:
                            name = 'api_key'
                    else:  # pragma: no cover
                        raise RuntimeError('Unknown authentication scheme')
                    if name in auth_names:
                        apispec_version = 2
                        new_name = f'{name}_{apispec_version}'
                        while new_name in auth_names:  # pragma: no cover
                            apispec_version += 1
                            new_name = f'{name}_{apispec_version}'
                        name = new_name
                    auth_names.append(name)
        security = {}
        security_schemes = {}
        for name, auth in zip(auth_names, auth_schemes):
            security[auth] = name
            if isinstance(auth, HTTPTokenAuth):
                if auth.scheme == 'Bearer' and auth.header is None:
                    security_schemes[name] = {
                        'type': 'http',
                        'scheme': 'bearer',
                    }
                else:
                    security_schemes[name] = {
                        'type': 'apiKey',
                        'name': auth.header,
                        'in': 'header',
                    }
            else:
                security_schemes[name] = {
                    'type': 'http',
                    'scheme': 'basic',
                }
            if auth.__doc__:
                security_schemes[name]['description'] = auth.__doc__.strip()
        for prefix in ['basic_auth', 'token_auth', 'api_key']:
            for name, scheme in security_schemes.items():
                if name.startswith(prefix):
                    spec.components.security_scheme(name, scheme)

        # paths
        paths = {}
        rules = list(current_app.url_map.iter_rules())
        rules = sorted(rules, key=lambda rule: len(rule.rule))
        rules += _webhooks.values()
        for rule in rules:
            operations = {}
            is_endpoint = True  # False for webhooks
            view_func = current_app.view_functions.get(rule.endpoint)
            if view_func is None:
                is_endpoint = False
                view_func = rule.view_func
            if not hasattr(view_func, '_spec'):
                continue
            if '.' in rule.endpoint:
                tag, endpoint = rule.endpoint.rsplit('.', 1)
                tag = tag.title()
            else:
                tag = None
                endpoint = rule.endpoint
            methods = [method for method in rule.methods
                       if method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']]
            for method in methods:
                operation_id = rule.endpoint.replace('.', '_')
                if len(methods) > 1:
                    operation_id = method.lower() + '_' + operation_id
                operation = {
                    'operationId': operation_id,
                    'parameters': [
                        {'in': location, 'schema': schema}
                        for schema, location in view_func._spec.get('args', [])
                        if location != 'body'
                    ],
                }
                if tag:
                    operation['tags'] = [tag]
                docs = [line.strip() for line in (
                    view_func.__doc__ or '').strip().split('\n')]
                if docs[0]:
                    operation['summary'] = docs[0]
                if len(docs) > 1:
                    operation['description'] = '\n'.join(docs[1:]).strip()
                if view_func._spec.get('response'):
                    code = str(view_func._spec['status_code'])
                    operation['responses'] = {
                        code: {
                            'content': {
                                'application/json': {
                                    'schema': view_func._spec.get('response')
                                }
                            }
                        }
                    }
                    operation['responses'][code]['description'] = \
                        view_func._spec['description'] or HTTP_STATUS_CODES[
                            int(code)]
                    if view_func._spec.get('response_headers'):
                        schema = view_func._spec.get('response_headers')
                        if isinstance(schema, type):  # pragma: no branch
                            schema = schema()
                        headers = ma_plugin.converter.schema2parameters(
                            schema, location='headers')
                        operation['responses'][code]['headers'] = {
                            header['name']: header for header in headers}
                else:
                    operation['responses'] = {
                        '204': {'description': HTTP_STATUS_CODES[204]}}

                if view_func._spec.get('other_responses'):
                    for status_code, response in view_func._spec.get(
                            'other_responses').items():
                        if not isinstance(response, (tuple, list)):
                            response = (response,)
                        operation['responses'][status_code] = {}
                        for r in response:
                            if isinstance(r, str):
                                operation['responses'][status_code][
                                    'description'] = r
                            else:
                                if isinstance(r, type):
                                    r = r()  # instantiate the schema
                                operation['responses'][status_code][
                                    'content'] = {
                                        'application/json': {
                                            'schema': r
                                        }
                                    }
                        if 'description' not in operation['responses'][
                                status_code]:
                            operation['responses'][status_code][
                                'description'] = HTTP_STATUS_CODES[
                                    int(status_code)]

                if view_func._spec.get('body'):
                    schema = view_func._spec.get('body')[0]
                    location = view_func._spec.get('body')[1]
                    media_type = view_func._spec.get('body')[2]
                    if media_type is None and location == 'form':
                        has_file = False
                        for field in schema.dump_fields.values():
                            if isinstance(field, apifairy_fields.FileField):
                                has_file = True
                                break
                        media_type = 'application/x-www-form-urlencoded' \
                            if not has_file else 'multipart/form-data'
                    if media_type is None:
                        media_type = 'application/json'
                    operation['requestBody'] = {
                        'content': {
                            media_type: {
                                'schema': schema,
                            }
                        },
                        'required': True,
                    }

                if view_func._spec.get('auth'):
                    operation['security'] = [{
                        security[view_func._spec['auth']]: view_func._spec[
                            'roles']
                    }]
                operations[method.lower()] = operation

            if is_endpoint:
                path_arguments = re.findall(r'<(([^<:]+:)?([^>]+))>',
                                            rule.rule)
                if path_arguments:
                    annotations = view_func.__annotations__ or {}
                    arguments = []
                    for _, type_, name in path_arguments:
                        argument = {
                            'in': 'path',
                            'name': name,
                        }
                        if type_ == 'int:':
                            argument['schema'] = {'type': 'integer'}
                        elif type_ == 'float:':
                            argument['schema'] = {'type': 'number'}
                        else:
                            argument['schema'] = {'type': 'string'}
                        if isinstance(annotations.get(name), str):
                            argument['description'] = annotations[name]
                        elif _AnnotatedAlias and isinstance(
                                annotations.get(name), _AnnotatedAlias):
                            for annotation in annotations[name].__metadata__:
                                if isinstance(annotation, str):
                                    argument['description'] = annotation
                                    break
                        arguments.append(argument)

                    for method, operation in operations.items():
                        operation['parameters'] = arguments + \
                            operation['parameters']

                path = re.sub(r'<([^<:]+:)?', '{', rule.rule).replace('>', '}')
                if path not in paths:
                    paths[path] = operations
                else:
                    paths[path].update(operations)
            else:
                # apispec does not support webhooks, so here they are added as
                # paths, and later they are moved to their own section after
                # the spec is generated
                paths['webhook:' + endpoint] = operations
        for path, operations in paths.items():
            # sort by method before adding them to the spec
            sorted_operations = {}
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in operations:
                    sorted_operations[method] = operations[method]
            spec.path(path=path, operations=sorted_operations)

        spec = spec.to_dict()

        # extract webhooks from paths and add them to the webhooks section
        webhooks = {
            path[8:]: operations for path, operations in spec['paths'].items()
            if path.startswith('webhook:')
        }
        if webhooks:
            paths = {
                path: operations for path, operations in spec['paths'].items()
                if not path.startswith('webhook:')
            }
            spec['paths'] = paths
            spec['webhooks'] = webhooks
        return spec
