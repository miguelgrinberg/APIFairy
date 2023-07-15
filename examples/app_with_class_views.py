"""Welcome to the APIFairy Simple Example project!

## Overview

This is a short and simple example that demonstrates many of the features of
APIFairy. The difference between this version of the example and `app.py` is
that in this example class-based views are used.
"""
from typing import Annotated
from uuid import uuid4
from flask import Flask, abort
from flask.views import MethodView
from flask_marshmallow import Marshmallow
from apifairy import APIFairy, body, response, other_responses

app = Flask(__name__)
app.config['APIFAIRY_TITLE'] = 'APIFairy Simple Example'
app.config['APIFAIRY_VERSION'] = '1.0'
ma = Marshmallow(app)
apifairy = APIFairy(app)
users = []


class UserSchema(ma.Schema):
    class Meta:
        description = 'This schema represents a user'

    id = ma.String(dump_only=True, description="The user's id")
    username = ma.String(required=True, description="The user's username")
    first_name = ma.String(description="The user's first name")
    last_name = ma.String(description="The user's last name")
    age = ma.Integer(description="The user's age")
    password = ma.String(load_only=True, description="The user's password")


class GetUsersEndpoint(MethodView):
    decorators= [
        response(UserSchema(many=True), description="The users"),
    ]

    def get(self):
        """Return all the users."""
        return users
     

class NewUserEndpoint(MethodView):
    decorators = [
        other_responses({400: 'Duplicate username or validation error'}),
        response(UserSchema, description="The new user"),
        body(UserSchema),
    ]

    # important note: endpoints like this one that take arguments from APIFairy
    # are currently broken, due to a bug in Flask
    # see https://github.com/pallets/flask/issues/5199 
    def post(self, user):
        """Create a new user."""
        if any([u['username'] == user['username'] for u in users]):
            abort(400)
        new_id = uuid4().hex
        user['id'] = new_id
        users.append(user)
        return user


class UserEndpoint(MethodView):
    decorators = [
        response(UserSchema, description="The requested user"),
        other_responses({404: 'User not found'}),
    ]

    def get(self, id: Annotated[str, 'The id of the user']):
        """Return a user."""
        user = [u for u in users if u['id'] == id]
        if not user:
            abort(404)
        return user[0]


app.add_url_rule("/users", view_func=GetUsersEndpoint.as_view("get_users"))
app.add_url_rule("/users", view_func=NewUserEndpoint.as_view("new_user"))
app.add_url_rule("/user/<id>", view_func=UserEndpoint.as_view("get_user"))


@app.errorhandler(400)
def bad_request(e):
    return {'code': 400, 'error': 'bad request'}


@app.errorhandler(404)
def not_found(e):
    return {'code': 404, 'error': 'not found'}


@apifairy.error_handler
def validation_error(status_code, messages):
    return {'code': status_code, 'error': 'validation error',
            'messages': messages['json']}
