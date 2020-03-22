import os
from flask import Flask, request, jsonify, abort
from sqlalchemy.exc import SQLAlchemyError
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# NOTE: THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
db_drop_and_create_all()


# ##--------------------------------------------------## #
# ##--------------------- Routes ---------------------## #
# ##--------------------------------------------------## #


# ##----------------- get all drinks -----------------## #
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks_query = Drink.query.all()

    drinks = []
    for drink in drinks_query:
        drinks.append(drink.short())

    if not drinks:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


# ##----------- get all drinks in details ------------## #
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks_query = Drink.query.all()

    drinks = []
    for drink in drinks_query:
        drinks.append(drink.long())

    if not drinks:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


# ##------------------ create drink ------------------## #
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    title = request.get_json()['title']
    recipe = request.get_json()['recipe']

    if not (title or recipe):
        abort(404)

    try:
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()

    except SQLAlchemyError as error:
        print(error)
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    }), 200


# ##------------------ update drink ------------------## #
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not drink:
        abort(404)

    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)

    if not (title or recipe):
        abort(404)

    if title:
        drink.title = title

    if recipe:
        drink.recipe = json.dumps(recipe)

    try:
        drink.update()

    except SQLAlchemyError:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


# ##------------------ delete drink ------------------## #
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not drink:
        abort(404)

    try:
        drink.delete()

    except SQLAlchemyError:
        abort(422)

    return jsonify({
        'success': True,
        'delete': drink_id
    }), 200


# ##--------------------------------------------------## #
# ##---------------- Error Handling ------------------## #
# ##--------------------------------------------------## #

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


# error handler for AuthError
@app.errorhandler(AuthError)
def authentication_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "authentication error"
    }), error.status_code
