"""Welcome to the APIFairy Simple Example project!

## Overview

This is a short and simple example that demonstrates many of the features of
APIFairy.
"""
from typing import Annotated
from uuid import uuid4
from flask import Flask, abort
from flask_marshmallow import Marshmallow
from apifairy import APIFairy, body, response, other_responses

app = Flask(__name__)
app.config['APIFAIRY_TITLE'] = 'APIFairy Simple Example'
app.config['APIFAIRY_VERSION'] = '1.0'
app.config['APIFAIRY_UI'] = 'swagger_ui'
ma = Marshmallow(app)
apifairy = APIFairy(app)
users = []


class UserSchema(ma.Schema):
    class Meta:
        description = 'This schema represents a user'

    id = ma.String(dump_only=True, metadata={"description": "The user's id"})
    username = ma.String(required=True, metadata={"description": "The user's username"})
    first_name = ma.String(metadata={"description": "The user's first name"})
    last_name = ma.String(metadata={"description": "The user's last name"})
    age = ma.Integer(metadata={"description": "The user's age"})
    password = ma.String(load_only=True, metadata={"description": "The user's password"})


@app.get('/users')
@response(UserSchema(many=True), description="The users", examples={
    "main": {
        "summary": "All users",
        "value": [
            {
                "username": "user1",
                "first_name": "john",
                "last_name": "smith",
                "age": 34,
            },
            {
                "username": "user2",
                "first_name": "elena",
                "last_name": "McGee",
                "age": 44,
            },
        ],
    },
})
def get_users():
    """Return all the users."""
    return users


@app.post('/users')
@body(UserSchema, description="The user.", examples={
    "main": {
        "summary": "Create a new user",
        "value": {
            "username": "smith34",
            "first_name": "john",
            "last_name": "smith",
            "age": 34,
        },
    },
})
@response(UserSchema, description="The new user")
@other_responses({400: 'Duplicate username or validation error'})
def new_user(user):
    """Create a new user."""
    if any([u['username'] == user['username'] for u in users]):
        abort(400)
    new_id = uuid4().hex
    user['id'] = new_id
    users.append(user)
    return user


@app.get('/users/<id>')
@response(UserSchema, description="The requested user")
@other_responses({404: 'User not found'})
def get_user(id: Annotated[str, 'The id of the user']):
    """Return a user."""
    user = [u for u in users if u['id'] == id]
    if not user:
        abort(404)
    return user[0]


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
