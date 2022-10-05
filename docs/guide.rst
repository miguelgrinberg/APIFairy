Documenting your API with APIFairy
==================================

APIFairy can discover and document your API through its
:ref:`decorators <Decorator Reference>`, but in most cases you'll want to
complement automatically generated documentation with manually written notes.
The following sections describe all the places where APIFairy looks for text to
attach to your project's documentation.

Project Title and Version
-------------------------

The title and version of your project are defined in the Flask configuration
object::

    app = Flask(__name__)
    app.config['APIFAIRY_TITLE'] = 'My API Project'
    app.config['APIFAIRY_VERSION'] = '1.0'

Project Overview
----------------

Most API documentation sites include one or more sections that provide general
project information for developers, such as how to authenticate, how
pagination works, or what is the structure of error responses. APIFairy looks
for project description text to attach to the documentation in module-level
docstrings in all the packages and modules referenced in the Flask
application's import name, starting from the right side.

While different OpenAPI documentation renderers may have different expectations
for the formatting of this text, it is fairly common for documentation to be
written in Markdown format, with support for long, multi-line text.

To help clarify how this works, consider a project with the following
structure:

- my_api_project/
   - api/
      - __init__.py
      - app.py
      - routes.py
   - project.py

The contents of *project.py* are::

    from api.app import create_app

    app = create_app()

The contents of *api/app.py* are::

    from flask import Flask
    from apifairy import APIFairy

    apifairy = APIFairy()

    def create_app():
        app = Flask(__name__)
        app.config['APIFAIRY_TITLE'] = 'My API Project'
        app.config['APIFAIRY_VERSION'] = '1.0'
        apifairy.init_app(app)
        return app

With this project structure, the import name of the Flask application is
``api.app``. In general, the import name of the application is the value that
is passed as first argument to the ``Flask`` class. In most cases this is the
``__name__`` Python global variable, which represents the fully qualified
package name of the module in which the application is defined.

Following this example, APIFairy will first look for project-level
documentation in the ``api.app`` module, which maps to the *api/app.py* file.
Documentation can then be added at the top of this file, as follows::

    """Welcome to My API Project!

    ## Project Overview

    This is the project overview.

    ## Authentication

    This is how authentication works.
    """
    from flask import Flask
    from apifairy import APIFairy

    apifairy = APIFairy()

    def create_app():
        app = Flask(__name__)
        app.config['APIFAIRY_TITLE'] = 'My API Project'
        app.config['APIFAIRY_VERSION'] = '1.0'
        apifairy.init_app(app)
        return app

If APIFairy does not find a module docstring in ``api.app``, it will remove the
last component of the import name and try again. Following this example, this
would be ``api``, which is a package, so its docstring can be found in
*api/__init__.py*.

So the alternative to putting the documentation in *api/app.py* is to leave
this file without a docstring, and instead add the documentation in
*api/__init__.py*.

Endpoints
---------

To document an endpoint, add a docstring to its view function. The first line
of the docstring should be a short summary of the endpoint's purpose. A longer
description can be included starting from the second line.

Example with just a summary::

    @users.route('/users', methods=['POST'])
    @body(user_schema)
    @response(user_schema, 201)
    def new(args):
        """Register a new user"""
        user = User(**args)
        db.session.add(user)
        db.session.commit()
        return user

Example with summary and longer description::

    @users.route('/users', methods=['POST'])
    @body(user_schema)
    @response(user_schema, 201)
    def new(args):
        """Register a new user
        Clients can use this endpoint when they need to register a new user
        in the system.
        """
        user = User(**args)
        db.session.add(user)
        db.session.commit()
        return user

As with the project overview, these docstrings can also be written in Markdown.

Path parameters
---------------

For endpoints that have dynamic components in their path, APIFairy will
automatically extract their type directly from the Flask route specification.
A text description of a parameter can be included by adding a string as an
annotation.

Annotations have been evolving in recent releasees of Python, so the best
format to provide documentation for endpoint parameters depends on which
version of Python you are using.

The basic method, which works with any recent version of Python, involves
simply adding the documentation as a string annotation to the parameter::

    @users.route('/users/<int:id>', methods=['GET'])
    @authenticate(token_auth)
    @response(user_schema)
    def get(id: 'The id of the user to retrieve.'):  # noqa: F722
        """Retrieve a user by id"""
        return db.session.get(User, id) or abort(404)

While this method works, Python code linters and type checkers will flag the
annotation as invalid, because they expect annotations to be used for type
hints and not for documentation, so it may be necessary to add a ``noqa`` or
similar comment for these errors to be ignored.

If using Python 3.9 or newer, luckily there is a better option. The
`typing.Annotated <https://docs.python.org/3/library/typing.html#typing.Annotated>`_
type can be used to provide a type hint for the parameter along with additional
metadata such as a documentation string::

    from typing import Annotated

    @users.route('/users/<int:id>', methods=['GET'])
    @authenticate(token_auth)
    @response(user_schema)
    def get(id: Annotated[int, 'The id of the user to retrieve.']):
        """Retrieve a user by id"""
        return db.session.get(User, id) or abort(404)

Even if the project does not use type hints, using this format will prevent
linting and typing errors, so it is the preferred way to document a parameter.

Documentation for parameters can include multiple lines and paragraphs, if
desired. Markdown formatting is also supported by most OpenAPI renderers.

Schemas
-------

Many of the :ref:`APIFairy decorators <Decorator Reference>` accept Marshmallow
schemas as arguments. These schemas are automatically documented, including
their field types and validation requirements.

If the application wants to provide additional information, a schema
description can be provided in the ``description`` field of the schema's
metaclass::

    class UserSchema(ma.SQLAlchemySchema):
        class Meta:
            model = User
            ordered = True
            description = 'This schema represents a user.'

        id = ma.auto_field(dump_only=True)
        url = ma.String(dump_only=True)
        username = ma.auto_field(required=True,
                                 validate=validate.Length(min=3, max=64))

Documentation that is specific to a schema field can be added in a
``description`` argument when the field is declared::

    class UserSchema(ma.SQLAlchemySchema):
        class Meta:
            model = User
            ordered = True

        id = ma.auto_field(dump_only=True, description="The user's id.")
        url = ma.String(dump_only=True, description="The user's unique URL.")
        username = ma.auto_field(required=True,
                                 validate=validate.Length(min=3, max=64),
                                 description="The user's username.")

Query String
------------

APIFairy will automatically document query string parameters for endpoints that
use the :ref:`@arguments` decorator::

    @users.route('/users', methods=['GET'])
    @arguments(pagination_schema)
    @response(users_schema)
    def get_users(pagination):
        """Retrieve all users"""
        # ...

Request Headers
---------------

APIFairy also documents request headers that are declared with the
:ref:`@arguments` decorator. Note that this decorator defaults to the query
string, but the `location` argument can be set to `headers` when needed.

Example::

    class HeadersSchema(ma.Schema):
        x_token = ma.String(data_key='X-Token', required=True)

    @users.route('/users', methods=['GET'])
    @arguments(HeadersSchema, location='headers')
    @response(users_schema)
    def get_users(headers):
        """Retrieve all users"""
        # ...

The ``@arguments`` decorator can be given twice when an endpoint needs query
string and header arguments both::

    @users.route('/users', methods=['GET'])
    @arguments(PaginationSchema)
    @arguments(HeadersSchema, location='headers')
    @response(users_schema)
    def all(pagination, headers):
        """Retrieve all users"""
        # ...

Responses
---------

In addition to the schema documentation, an endpoint response can be given a
text description in a ``description`` argument to the ``@response`` decorator.

Example::

    @tokens.route('/tokens', methods=['PUT'])
    @body(token_schema)
    @response(token_schema, description='Newly issued access and refresh tokens')
    def refresh(args):
        """Refresh an access token"""
        ...

For endpoints that return information in response headers, the ``headers``
argument can be used to add these to the documentation::

    class HeadersSchema(ma.Schema):
        x_token = ma.String(data_key='X-Token')

    @tokens.route('/tokens', methods=['PUT'])
    @body(token_schema)
    @response(token_schema, headers=HeadersSchema)
    def refresh(args):
        """Refresh an access token"""
        ...

Error Responses
---------------

The ``@other_responses`` decorator takes a dictionary argument, where the keys
are the response status codes and the values provide the documentation.

To add text descriptions to these responses, set the value for each status code
to a descrition string.

Example::

    @tokens.route('/tokens', methods=['PUT'])
    @body(token_schema)
    @response(token_schema, description='Newly issued access and refresh tokens')
    @other_responses({401: 'Invalid access or refresh token',
                      403: 'Insufficient permissions'})
    def refresh(args):
        """Refresh an access token"""
        ...


To document the error response with a schema, set the value to the schema
instance.

Example::

    @tokens.route('/tokens', methods=['PUT'])
    @body(token_schema)
    @response(token_schema, description='Newly issued access and refresh tokens')
    @other_responses({401: invalid_token_schema,
                      403: insufficient_permissions_schema})
    def refresh(args):
        """Refresh an access token"""
        ...

A schema and a description can both be given as a tuple::

    @tokens.route('/tokens', methods=['PUT'])
    @body(token_schema)
    @response(token_schema, description='Newly issued access and refresh tokens')
    @other_responses({401: (invalid_token_schema, 'Invalid access or refresh token'),
                      403: (insufficient_permissions_schema, 'Insufficient permissions')})
    def refresh(args):
        """Refresh an access token"""
        ...

Authentication
--------------

APIFairy recognizes the Flask-HTTPAuth authentication object passed to the
``@authenticate`` decorator and creates the appropriate structure according to
the OpenAPI specification. To add textual documentation, define a subclass of
the Flask-HTTPAuth authentication object and add a docstring with the
documentation to it.

Example::

    from flask_httpauth import HTTPBasicAuth

    class DocumentedAuth(HTTPBasicAuth):
        """Basic authentication scheme."""
        pass

    basic_auth = DocumentedAuth()

    @tokens.route('/tokens', methods=['POST'])
    @authenticate(basic_auth)
    @response(token_schema)
    @other_responses({401: 'Invalid username or password'})
    def new():
        """Create new access and refresh tokens"""
        ...

Tags and Blueprints
-------------------

APIFairy automatically creates OpenAPI tags for all the blueprints defined in
the application, assigns each endpoint to the corresponding tag, and generates
the OpenAPI documentation with the endpoints grouped by their tag.

The order in which the groups appear can be controlled with the
``APIFAIRY_TAGS`` configuration variable, which is a list of the blueprint
names in the desired order. Any names that are not included in this list will
exclude the associated endpoints from the documentation.

A textual description for each blueprint can be provided as a module-level
docstring in the module in which the blueprint is defined.

Anything else
-------------

For any other documentation needs that are not covered by the options listed
above, the application can manually modify the OpenAPI structure. This can be
achieved in a function decorated with the ``@process_apispec`` decorator::

    @apifairy.process_apispec
    def my_apispec_processor(spec):
        # modify spec as needed here
        return spec
