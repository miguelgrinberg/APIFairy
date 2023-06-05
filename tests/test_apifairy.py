from io import BytesIO
import sys
try:
    from typing import Annotated
except ImportError:
    Annotated = None
import unittest
import pytest

from flask import Flask, Blueprint, request, session, abort
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE
from openapi_spec_validator import validate_spec

from apifairy import APIFairy, body, arguments, response, authenticate, \
    other_responses, webhook, FileField

ma = Marshmallow()


class Schema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    id = ma.Integer(default=123)
    name = ma.Str(required=True)


class Schema2(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    id2 = ma.Integer(default=123)
    name2 = ma.Str(required=True)


class FooSchema(ma.Schema):
    id = ma.Integer(default=123)
    name = ma.Str()


class QuerySchema(ma.Schema):
    id = ma.Integer(missing=1)


class FormSchema(ma.Schema):
    csrf = ma.Str(required=True)
    name = ma.Str(required=True)
    age = ma.Int()


class FormUploadSchema(ma.Schema):
    name = ma.Str()
    file = FileField(required=True)


class FormUploadSchema2(ma.Schema):
    name = ma.Str()
    files = ma.List(FileField(), required=True)


class HeaderSchema(ma.Schema):
    x_token = ma.Str(data_key='X-Token', required=True)


class TestAPIFairy(unittest.TestCase):
    def create_app(self, config=None):
        app = Flask(__name__)
        app.config['APIFAIRY_TITLE'] = 'Foo'
        app.config['APIFAIRY_VERSION'] = '1.0'
        if config:
            app.config.update(config)
        ma.init_app(app)
        apifairy = APIFairy(app)
        return app, apifairy

    def test_apispec(self):
        app, apifairy = self.create_app()
        auth = HTTPBasicAuth()

        @apifairy.process_apispec
        def edit_apispec(apispec):
            assert apispec['openapi'] == '3.0.3'
            apispec['openapi'] = '3.0.2'
            return apispec

        @auth.verify_password
        def verify_password(username, password):
            if username == 'foo' and password == 'bar':
                return {'user': 'foo'}
            elif username == 'bar' and password == 'foo':
                return {'user': 'bar'}

        @auth.get_user_roles
        def get_roles(user):
            if user['user'] == 'bar':
                return 'admin'
            return 'normal'

        @app.route('/foo')
        @authenticate(auth)
        @arguments(QuerySchema)
        @body(Schema)
        @response(Schema)
        @other_responses({404: 'foo not found'})
        def foo():
            return {'id': 123, 'name': auth.current_user()['user']}

        client = app.test_client()

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['openapi'] == '3.0.2'
        assert rv.json['info']['title'] == 'Foo'
        assert rv.json['info']['version'] == '1.0'

        assert apifairy.apispec is apifairy.apispec

        rv = client.get('/docs')
        assert rv.status_code == 200
        assert b'redoc.standalone.js' in rv.data

    def test_custom_apispec_path(self):
        app, _ = self.create_app(config={'APIFAIRY_APISPEC_PATH': '/foo'})

        client = app.test_client()
        rv = client.get('/apispec.json')
        assert rv.status_code == 404
        rv = client.get('/foo')
        assert rv.status_code == 200
        assert set(rv.json.keys()) == {
            'openapi', 'info', 'servers', 'paths', 'tags'}

    def test_no_apispec_path(self):
        app, _ = self.create_app(config={'APIFAIRY_APISPEC_PATH': None})

        client = app.test_client()
        rv = client.get('/apispec.json')
        assert rv.status_code == 404

    def test_ui(self):
        app, _ = self.create_app(config={'APIFAIRY_UI': 'swagger_ui'})

        client = app.test_client()
        rv = client.get('/docs')
        assert rv.status_code == 200
        assert b'redoc.standalone.js' not in rv.data
        assert b'swagger-ui-bundle.js' in rv.data

    def test_custom_ui_path(self):
        app, _ = self.create_app(config={'APIFAIRY_UI_PATH': '/foo'})

        client = app.test_client()
        rv = client.get('/docs')
        assert rv.status_code == 404
        rv = client.get('/foo')
        assert rv.status_code == 200
        assert b'redoc.standalone.js' in rv.data

    def test_no_ui_path(self):
        app, _ = self.create_app(config={'APIFAIRY_UI_PATH': None})

        client = app.test_client()
        rv = client.get('/docs')
        assert rv.status_code == 404

    def test_apispec_ui_decorators(self):
        def auth(f):
            def wrapper(*args, **kwargs):
                if request.headers.get('X-Token') != 'foo' and \
                        session.get('X-Token') != 'foo':
                    abort(401)
                return f(*args, **kwargs)
            return wrapper

        def more_auth(f):
            def wrapper(*args, **kwargs):
                if request.headers.get('X-Key') != 'bar':
                    abort(401)
                session['X-Token'] = 'foo'
                return f(*args, **kwargs)
            return wrapper

        app, apifairy = self.create_app(config={
            'APIFAIRY_APISPEC_DECORATORS': [auth],
            'APIFAIRY_UI_DECORATORS': [auth, more_auth]})
        app.secret_key = 'secret'

        client = app.test_client()
        rv = client.get('/apispec.json')
        assert rv.status_code == 401
        rv = client.get('/docs')
        assert rv.status_code == 401
        rv = client.get('/apispec.json', headers={'X-Token': 'foo'})
        assert rv.status_code == 200
        rv = client.get('/docs', headers={'X-Key': 'bar'})
        assert rv.status_code == 200

    def test_body(self):
        app, _ = self.create_app()

        @app.route('/foo', methods=['POST'])
        @body(Schema())
        def foo(schema):
            return schema

        client = app.test_client()

        rv = client.post('/foo')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'json': {'name': ['Missing data for required field.']}
            }
        }

        rv = client.post('/foo', json={'id': 1})
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'json': {'name': ['Missing data for required field.']}
            }
        }

        rv = client.post('/foo', json={'id': 1, 'name': 'bar'})
        assert rv.status_code == 200
        assert rv.json == {'id': 1, 'name': 'bar'}

        rv = client.post('/foo', json={'name': 'bar'})
        assert rv.status_code == 200
        assert rv.json == {'name': 'bar'}

    def test_body_form(self):
        app, _ = self.create_app()

        @app.route('/form', methods=['POST'])
        @body(FormSchema(), location='form')
        def foo(schema):
            return schema

        client = app.test_client()

        rv = client.post('/form')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'form': {
                    'csrf': ['Missing data for required field.'],
                    'name': ['Missing data for required field.'],
                }
            }
        }

        rv = client.post('/form', data={'csrf': 'foo', 'age': '12'})
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'form': {'name': ['Missing data for required field.']}
            }
        }

        rv = client.post('/form', data={'csrf': 'foo', 'name': 'bar'})
        assert rv.status_code == 200
        assert rv.json == {'csrf': 'foo', 'name': 'bar'}

        rv = client.post('/form', data={'csrf': 'foo', 'name': 'bar',
                                        'age': '12'})
        assert rv.status_code == 200
        assert rv.json == {'csrf': 'foo', 'name': 'bar', 'age': 12}

    def test_body_form_upload(self):
        app, _ = self.create_app()

        @app.route('/form', methods=['POST'])
        @body(FormUploadSchema(), location='form')
        def foo(schema):
            return {'name': schema.get('name'),
                    'len': len(schema['file'].read())}

        client = app.test_client()

        rv = client.post('/form')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'form': {'file': ['Missing data for required field.']}
            }
        }

        rv = client.post('/form', data={'name': 'foo'},
                         content_type='multipart/form-data')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'form': {'file': ['Missing data for required field.']}
            }
        }

        rv = client.post('/form', data={'file': 'foo'},
                         content_type='multipart/form-data')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'form': {'file': ['Not a file.']}
            }
        }

        rv = client.post('/form', data={'name': 'foo',
                                        'file': (BytesIO(b'bar'), 'test.txt')})
        assert rv.status_code == 200
        assert rv.json == {'name': 'foo', 'len': 3}

        rv = client.post('/form', data={'file': (BytesIO(b'bar'), 'test.txt')})
        assert rv.status_code == 200
        assert rv.json == {'name': None, 'len': 3}

    def test_body_custom_error_handler(self):
        app, apifairy = self.create_app()

        @apifairy.error_handler
        def error_handler(status_code, messages):
            return {'errors': messages}, status_code

        @app.route('/foo', methods=['POST'])
        @body(Schema())
        def foo(schema):
            return schema

        client = app.test_client()

        rv = client.post('/foo')
        assert rv.status_code == 400
        assert rv.json == {
            'errors': {
                'json': {'name': ['Missing data for required field.']}
            }
        }

    def test_query(self):
        app, _ = self.create_app()

        @app.route('/foo', methods=['POST'])
        @arguments(Schema())
        @arguments(Schema2())
        def foo(schema, schema2):
            return {'name': schema['name'], 'name2': schema2['name2']}

        client = app.test_client()

        rv = client.post('/foo')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'query': {'name': ['Missing data for required field.']}
            }
        }

        rv = client.post('/foo?id=1&name=bar')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'query': {'name2': ['Missing data for required field.']}
            }
        }

        rv = client.post('/foo?id=1&name=bar&id2=2&name2=baz')
        assert rv.status_code == 200
        assert rv.json == {'name': 'bar', 'name2': 'baz'}

        rv = client.post('/foo?name=bar&name2=baz')
        assert rv.status_code == 200
        assert rv.json == {'name': 'bar', 'name2': 'baz'}

    def test_response(self):
        app, _ = self.create_app()

        @app.route('/foo')
        @response(Schema())
        def foo():
            return {'name': 'bar'}

        @app.route('/bar')
        @response(Schema(), status_code=201)
        def bar():
            return {'name': 'foo'}

        @app.route('/baz')
        @arguments(QuerySchema)
        @response(Schema(), status_code=201)
        def baz(query):
            if query['id'] == 1:
                return {'name': 'foo'}, 202
            elif query['id'] == 2:
                return {'name': 'foo'}, {'Location': '/baz'}
            elif query['id'] == 3:
                return {'name': 'foo'}, 202, {'Location': '/baz'}
            return ({'name': 'foo'},)

        client = app.test_client()

        rv = client.get('/foo')
        assert rv.status_code == 200
        assert rv.json == {'id': 123, 'name': 'bar'}

        rv = client.get('/bar')
        assert rv.status_code == 201
        assert rv.json == {'id': 123, 'name': 'foo'}

        rv = client.get('/baz')
        assert rv.status_code == 202
        assert rv.json == {'id': 123, 'name': 'foo'}
        assert 'Location' not in rv.headers

        rv = client.get('/baz?id=2')
        assert rv.status_code == 201
        assert rv.json == {'id': 123, 'name': 'foo'}
        assert rv.headers['Location'] in ['http://localhost/baz', '/baz']

        rv = client.get('/baz?id=3')
        assert rv.status_code == 202
        assert rv.json == {'id': 123, 'name': 'foo'}
        assert rv.headers['Location'] in ['http://localhost/baz', '/baz']

        rv = client.get('/baz?id=4')
        assert rv.status_code == 201
        assert rv.json == {'id': 123, 'name': 'foo'}
        assert 'Location' not in rv.headers

    def test_basic_auth(self):
        app, _ = self.create_app()
        auth = HTTPBasicAuth()

        @auth.verify_password
        def verify_password(username, password):
            if username == 'foo' and password == 'bar':
                return {'user': 'foo'}
            elif username == 'bar' and password == 'foo':
                return {'user': 'bar'}

        @auth.get_user_roles
        def get_roles(user):
            if user['user'] == 'bar':
                return 'admin'
            return 'normal'

        @app.route('/foo')
        @authenticate(auth)
        def foo():
            return auth.current_user()

        @app.route('/bar')
        @authenticate(auth, role='admin')
        def bar():
            return auth.current_user()

        client = app.test_client()

        rv = client.get('/foo')
        assert rv.status_code == 401

        rv = client.get('/foo',
                        headers={'Authorization': 'Basic Zm9vOmJhcg=='})
        assert rv.status_code == 200
        assert rv.json == {'user': 'foo'}

        rv = client.get('/bar',
                        headers={'Authorization': 'Basic Zm9vOmJhcg=='})
        assert rv.status_code == 403

        rv = client.get('/foo',
                        headers={'Authorization': 'Basic YmFyOmZvbw=='})
        assert rv.status_code == 200
        assert rv.json == {'user': 'bar'}

        rv = client.get('/bar',
                        headers={'Authorization': 'Basic YmFyOmZvbw=='})
        assert rv.status_code == 200
        assert rv.json == {'user': 'bar'}

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        assert rv.json['components']['securitySchemes'] == {
            'basic_auth': {'scheme': 'basic', 'type': 'http'},
        }
        assert rv.json['paths']['/foo']['get']['security'] == [
            {'basic_auth': []}]
        assert rv.json['paths']['/bar']['get']['security'] == [
            {'basic_auth': ['admin']}]

    def test_token_auth(self):
        app, _ = self.create_app()
        auth = HTTPTokenAuth()

        @auth.verify_token
        def verify_token(token):
            if token == 'foo':
                return {'user': 'foo'}
            elif token == 'bar':
                return {'user': 'bar'}

        @auth.get_user_roles
        def get_roles(user):
            if user['user'] == 'bar':
                return 'admin'
            return 'normal'

        @app.route('/foo')
        @authenticate(auth)
        def foo():
            return auth.current_user()

        @app.route('/bar')
        @authenticate(auth, role='admin')
        def bar():
            return auth.current_user()

        client = app.test_client()

        rv = client.get('/foo')
        assert rv.status_code == 401

        rv = client.get('/foo',
                        headers={'Authorization': 'Bearer foo'})
        assert rv.status_code == 200
        assert rv.json == {'user': 'foo'}

        rv = client.get('/bar',
                        headers={'Authorization': 'Bearer foo'})
        assert rv.status_code == 403

        rv = client.get('/foo',
                        headers={'Authorization': 'Bearer bar'})
        assert rv.status_code == 200
        assert rv.json == {'user': 'bar'}

        rv = client.get('/bar',
                        headers={'Authorization': 'Bearer bar'})
        assert rv.status_code == 200
        assert rv.json == {'user': 'bar'}

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        assert rv.json['components']['securitySchemes'] == {
            'token_auth': {'scheme': 'bearer', 'type': 'http'},
        }
        assert rv.json['paths']['/foo']['get']['security'] == [
            {'token_auth': []}]
        assert rv.json['paths']['/bar']['get']['security'] == [
            {'token_auth': ['admin']}]

    def test_multiple_auth(self):
        app, _ = self.create_app()
        auth = HTTPTokenAuth()
        auth.__doc__ = 'auth documentation'
        auth2 = HTTPTokenAuth(header='X-Token')

        class MyHTTPTokenAuth(HTTPTokenAuth):
            """custom auth documentation"""
            pass

        auth3 = MyHTTPTokenAuth()

        @app.route('/foo')
        @authenticate(auth)
        def foo():
            return auth.current_user()

        @app.route('/bar')
        @authenticate(auth2)
        def bar():
            return auth.current_user()

        @app.route('/baz')
        @authenticate(auth3)
        def baz():
            return auth.current_user()

        client = app.test_client()

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        assert rv.json['components']['securitySchemes'] == {
            'token_auth': {'scheme': 'bearer', 'type': 'http',
                           'description': 'auth documentation'},
            'token_auth_2': {'scheme': 'bearer', 'type': 'http',
                             'description': 'custom auth documentation'},
            'api_key': {'type': 'apiKey', 'name': 'X-Token', 'in': 'header'},
        }
        assert rv.json['paths']['/foo']['get']['security'] == [
            {'token_auth': []}]
        assert rv.json['paths']['/bar']['get']['security'] == [
            {'api_key': []}]
        assert rv.json['paths']['/baz']['get']['security'] == [
            {'token_auth_2': []}]

    def test_apispec_schemas(self):
        app, apifairy = self.create_app()

        @app.route('/foo')
        @response(Schema(partial=True))
        def foo():
            pass

        @app.route('/bar')
        @response(Schema2(many=True))
        def bar():
            pass

        @app.route('/baz')
        @response(FooSchema)
        def baz():
            pass

        with app.test_request_context():
            apispec = apifairy.apispec
        assert len(apispec['components']['schemas']) == 3
        assert 'SchemaUpdate' in apispec['components']['schemas']
        assert 'Schema2' in apispec['components']['schemas']
        assert 'Foo' in apispec['components']['schemas']

    def test_endpoints(self):
        app, apifairy = self.create_app()

        @app.route('/users')
        @response(Schema)
        def get_users():
            """get users."""
            pass

        @app.route('/users', methods=['POST', 'PUT'])
        @body(FormSchema, location='form')
        @response(Schema, status_code=201)
        @other_responses({400: (Schema2, 'bad request'),
                          401: ('unauthorized', FooSchema()),
                          403: 'forbidden',
                          404: Schema2(many=True)})
        def new_user():
            """new user.
            modify user.
            """
            pass

        @app.route('/upload', methods=['POST'])
        @body(FormUploadSchema, location='form')
        def upload():
            """upload file."""
            pass

        @app.route('/uploads', methods=['POST'])
        @body(FormUploadSchema2, location='form',
              media_type='multipart/form-data')
        def uploads():
            """upload files."""
            pass

        @app.route('/tokens', methods=['POST'])
        @response(Schema, headers=HeaderSchema)
        def token():
            """get a token."""
            pass

        client = app.test_client()

        rv = client.get('/apispec.json')
        assert rv.status_code == 200

        assert rv.json['paths']['/users']['get']['operationId'] == 'get_users'
        assert list(rv.json['paths']['/users']['get']['responses']) == ['200']
        assert rv.json['paths']['/users']['get']['summary'] == 'get users.'
        assert 'description' not in rv.json['paths']['/users']['get']

        assert rv.json['paths']['/users']['post']['operationId'] == \
            'post_new_user'
        assert list(rv.json['paths']['/users']['post']['responses']) == \
            ['201', '400', '401', '403', '404']
        assert rv.json['paths']['/users']['post']['summary'] == 'new user.'
        assert rv.json['paths']['/users']['post']['description'] == \
            'modify user.'
        assert 'application/x-www-form-urlencoded' in \
            rv.json['paths']['/users']['post']['requestBody']['content']

        assert rv.json['paths']['/users']['put']['operationId'] == \
            'put_new_user'
        assert list(rv.json['paths']['/users']['put']['responses']) == \
            ['201', '400', '401', '403', '404']
        assert rv.json['paths']['/users']['put']['summary'] == 'new user.'
        assert rv.json['paths']['/users']['put']['description'] == \
            'modify user.'

        assert rv.json['paths']['/upload']['post']['operationId'] == 'upload'
        assert list(rv.json['paths']['/upload']['post']['responses']) == \
            ['204']
        assert rv.json['paths']['/upload']['post']['summary'] == 'upload file.'
        assert 'description' not in rv.json['paths']['/upload']['post']
        assert 'multipart/form-data' in \
            rv.json['paths']['/upload']['post']['requestBody']['content']

        assert rv.json['paths']['/uploads']['post']['operationId'] == 'uploads'
        assert list(rv.json['paths']['/uploads']['post']['responses']) == \
            ['204']
        assert rv.json['paths']['/uploads']['post']['summary'] == \
            'upload files.'
        assert 'description' not in rv.json['paths']['/uploads']['post']
        assert 'multipart/form-data' in \
            rv.json['paths']['/uploads']['post']['requestBody']['content']

        assert rv.json['paths']['/tokens']['post']['operationId'] == 'token'
        assert list(rv.json['paths']['/tokens']['post']['responses']) == \
            ['200']
        assert rv.json['paths']['/tokens']['post']['summary'] == 'get a token.'
        assert 'description' not in rv.json['paths']['/tokens']['post']
        assert 'headers' in \
            rv.json['paths']['/tokens']['post']['responses']['200']
        assert 'X-Token' in \
            rv.json['paths']['/tokens']['post']['responses']['200']['headers']

        r201 = {
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/Schema'}
                }
            },
            'description': 'Created'
        }
        assert rv.json['paths']['/users']['post']['responses']['201'] == r201
        assert rv.json['paths']['/users']['put']['responses']['201'] == r201

        r400 = {
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/Schema2'}
                }
            },
            'description': 'bad request'
        }
        assert rv.json['paths']['/users']['post']['responses']['400'] == r400
        assert rv.json['paths']['/users']['put']['responses']['400'] == r400

        r401 = {
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/Foo'}
                }
            },
            'description': 'unauthorized'
        }
        assert rv.json['paths']['/users']['post']['responses']['401'] == r401
        assert rv.json['paths']['/users']['put']['responses']['401'] == r401

        r403 = {'description': 'forbidden'}
        assert rv.json['paths']['/users']['post']['responses']['403'] == r403
        assert rv.json['paths']['/users']['put']['responses']['403'] == r403

        r404 = {
            'content': {
                'application/json': {
                    'schema': {
                        'items': {'$ref': '#/components/schemas/Schema2'},
                        'type': 'array'
                    }
                }
            },
            'description': 'Not Found'
        }
        assert rv.json['paths']['/users']['post']['responses']['404'] == r404
        assert rv.json['paths']['/users']['put']['responses']['404'] == r404

    def test_apispec_path_parameters(self):
        app, apifairy = self.create_app()

        @app.route('/strings/<some_string>')
        @response(Schema)
        def get_string(some_string: 'some_string docs'):  # noqa: F722
            pass

        @app.route('/floats/<float:some_float>', methods=['POST'])
        @response(Schema)
        def get_float(some_float: float):
            pass

        if Annotated:
            @app.route('/integers/<int:some_integer>', methods=['PUT'])
            @response(Schema)
            def get_integer(some_integer: Annotated[int, 1,
                                                    'some_integer docs']):
                pass

            @app.route('/users/<int:user_id>/articles/<int:article_id>')
            @response(Schema)
            def get_article(user_id: Annotated[int, 1], article_id):
                pass
        else:
            @app.route('/integers/<int:some_integer>', methods=['PUT'])
            @response(Schema)
            def get_integer(some_integer: 'some_integer docs'):  # noqa: F722
                pass

            @app.route('/users/<int:user_id>/articles/<int:article_id>')
            @response(Schema)
            def get_article(user_id, article_id):
                pass

        client = app.test_client()

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        validate_spec(rv.json)

        assert rv.json['paths']['/strings/{some_string}'][
            'get']['parameters'][0]['in'] == 'path'
        assert rv.json['paths']['/strings/{some_string}'][
            'get']['parameters'][0]['description'] == 'some_string docs'
        assert rv.json['paths']['/strings/{some_string}'][
            'get']['parameters'][0]['name'] == 'some_string'
        assert rv.json['paths']['/strings/{some_string}'][
            'get']['parameters'][0]['schema']['type'] == 'string'

        assert rv.json['paths']['/floats/{some_float}'][
            'post']['parameters'][0]['in'] == 'path'
        assert 'description' not in rv.json['paths']['/floats/{some_float}'][
            'post']['parameters'][0]
        assert rv.json['paths']['/floats/{some_float}'][
            'post']['parameters'][0]['schema']['type'] == 'number'
        assert rv.json['paths']['/floats/{some_float}'][
            'post']['parameters'][0]['schema']['type'] == 'number'

        assert rv.json['paths']['/integers/{some_integer}'][
            'put']['parameters'][0]['in'] == 'path'
        assert rv.json['paths']['/integers/{some_integer}'][
            'put']['parameters'][0]['description'] == 'some_integer docs'
        assert rv.json['paths']['/integers/{some_integer}'][
            'put']['parameters'][0]['schema']['type'] == 'integer'

        assert rv.json['paths']['/users/{user_id}/articles/{article_id}'][
            'get']['parameters'][0]['in'] == 'path'
        assert rv.json['paths']['/users/{user_id}/articles/{article_id}'][
            'get']['parameters'][0]['name'] == 'user_id'
        assert 'description' not in rv.json['paths'][
            '/users/{user_id}/articles/{article_id}']['get']['parameters'][0]
        assert rv.json['paths']['/users/{user_id}/articles/{article_id}'][
            'get']['parameters'][1]['in'] == 'path'
        assert rv.json['paths']['/users/{user_id}/articles/{article_id}'][
            'get']['parameters'][1]['name'] == 'article_id'
        assert 'description' not in rv.json['paths'][
            '/users/{user_id}/articles/{article_id}']['get']['parameters'][1]

    def test_path_arguments_detection(self):
        app, apifairy = self.create_app()

        @app.route('/<foo>')
        @response(Schema)
        def pattern1():
            pass

        @app.route('/foo/<bar>')
        @response(Schema)
        def pattern2():
            pass

        @app.route('/<foo>/bar')
        @response(Schema)
        def pattern3():
            pass

        @app.route('/<int:foo>/<bar>/baz')
        @response(Schema)
        def pattern4():
            pass

        @app.route('/foo/<int:bar>/<int:baz>')
        @response(Schema)
        def pattern5():
            pass

        @app.route('/<int:foo>/<bar>/<float:baz>')
        @response(Schema)
        def pattern6():
            pass

        client = app.test_client()

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert '/{foo}' in rv.json['paths']
        assert '/foo/{bar}' in rv.json['paths']
        assert '/{foo}/bar' in rv.json['paths']
        assert '/{foo}/{bar}/baz' in rv.json['paths']
        assert '/foo/{bar}/{baz}' in rv.json['paths']
        assert '/{foo}/{bar}/{baz}' in rv.json['paths']
        assert rv.json['paths']['/{foo}/{bar}/{baz}']['get'][
            'parameters'][0]['schema']['type'] == 'integer'
        assert rv.json['paths']['/{foo}/{bar}/{baz}']['get'][
            'parameters'][1]['schema']['type'] == 'string'
        assert rv.json['paths']['/{foo}/{bar}/{baz}']['get'][
            'parameters'][2]['schema']['type'] == 'number'

    def test_path_tags_with_nesting_blueprints(self):
        if not hasattr(Blueprint, 'register_blueprint'):
            pytest.skip('This test requires Flask 2.0 or higher.')

        app, apifairy = self.create_app()

        parent_bp = Blueprint('parent', __name__, url_prefix='/parent')
        child_bp = Blueprint('child', __name__, url_prefix='/child')

        @parent_bp.route('/')
        @response(Schema)
        def foo():
            pass

        @child_bp.route('/')
        @response(Schema)
        def bar():
            pass

        parent_bp.register_blueprint(child_bp)
        app.register_blueprint(parent_bp)

        client = app.test_client()

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert {'name': 'Parent'} in rv.json['tags']
        assert {'name': 'Parent.Child'} in rv.json['tags']
        assert rv.json['paths']['/parent/']['get']['tags'] == ['Parent']
        assert rv.json['paths']['/parent/child/']['get'][
            'tags'] == ['Parent.Child']

    def test_async_views(self):
        if not sys.version_info >= (3, 7):
            pytest.skip('This test requires Python 3.7 or higher.')

        app, apifairy = self.create_app()
        auth = HTTPBasicAuth()

        @auth.verify_password
        def verify_password(username, password):
            if username == 'foo' and password == 'bar':
                return {'user': 'foo'}
            elif username == 'bar' and password == 'foo':
                return {'user': 'bar'}

        @auth.get_user_roles
        def get_roles(user):
            if user['user'] == 'bar':
                return 'admin'
            return 'normal'

        @app.route('/foo', methods=['POST'])
        @authenticate(auth)
        @arguments(QuerySchema)
        @body(Schema)
        @response(Schema)
        @other_responses({404: 'foo not found'})
        async def foo(query, body):
            return {'id': query['id'], 'name': auth.current_user()['user']}

        client = app.test_client()

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['openapi'] == '3.0.3'
        assert rv.json['info']['title'] == 'Foo'
        assert rv.json['info']['version'] == '1.0'

        assert apifairy.apispec is apifairy.apispec

        rv = client.get('/docs')
        assert rv.status_code == 200
        assert b'redoc.standalone.js' in rv.data

        rv = client.post('/foo')
        assert rv.status_code == 401

        rv = client.post(
            '/foo', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
        assert rv.json['messages']['json']['name'] == \
            ['Missing data for required field.']
        assert rv.status_code == 400

        rv = client.post('/foo', json={'name': 'john'},
                         headers={'Authorization': 'Basic Zm9vOmJhcg=='})
        assert rv.status_code == 200
        assert rv.json == {'id': 1, 'name': 'foo'}

        rv = client.post('/foo?id=2', json={'name': 'john'},
                         headers={'Authorization': 'Basic Zm9vOmJhcg=='})
        assert rv.status_code == 200
        assert rv.json == {'id': 2, 'name': 'foo'}

    def test_webhook(self):
        app, apifairy = self.create_app()
        bp = Blueprint('bp', __name__)

        @webhook
        @body(Schema)
        def default_webhook():
            pass

        @webhook(endpoint='my-endpoint')
        @body(Schema)
        def custom_endpoint():
            pass

        @webhook(method='POST')
        @body(Schema)
        def post_webhook():
            pass

        @webhook(endpoint='tag.tagged-webhook')
        @body(Schema)
        def tagged_webhook():
            pass

        @webhook(blueprint=bp)
        @body(Schema)
        def blueprint_webhook():
            pass

        app.register_blueprint(bp)
        client = app.test_client()

        rv = client.get('/apispec.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['openapi'] == '3.1.0'
        assert 'default_webhook' in rv.json['webhooks']
        assert 'get' in rv.json['webhooks']['default_webhook']
        assert 'my-endpoint' in rv.json['webhooks']
        assert 'get' in rv.json['webhooks']['my-endpoint']
        assert 'post_webhook' in rv.json['webhooks']
        assert 'post' in rv.json['webhooks']['post_webhook']
        assert 'tagged-webhook' in rv.json['webhooks']
        assert 'get' in rv.json['webhooks']['tagged-webhook']
        assert 'blueprint_webhook' in rv.json['webhooks']
        assert 'get' in rv.json['webhooks']['blueprint_webhook']

    def test_webhook_duplicate(self):
        app, apifairy = self.create_app()

        def add_webhooks():
            @webhook
            @body(Schema)
            def default_webhook():
                pass

            @webhook(endpoint='default_webhook')
            @body(Schema)
            def another_webhook():
                pass

        with pytest.raises(ValueError):
            add_webhooks()
