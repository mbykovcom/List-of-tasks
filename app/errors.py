from flask import make_response, jsonify
from app import app, auth


@app.errorhandler(400)
def bad_request(error: str = None) -> object:
    response = {'error': 'bad request',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 400)


@auth.error_handler
def unauthorized(error: str = 'unauthorized access') -> object:
    response = {'error': 'unauthorized',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 401)


@app.errorhandler(404)
def not_found(error: str = None) -> object:
    response = {'error': 'not found',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 404)


@app.errorhandler(405)
def method_not_allowed(error: str = None) -> object:
    response = {'error': 'method not allowed',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 405)


@app.errorhandler(500)
def server_error(error: str = None) -> object:
    response = {'error': 'internal server error',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 500)
