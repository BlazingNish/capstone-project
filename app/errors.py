from flask import jsonify

def notFoundError(message):
    response = jsonify({'error':'Not Found', 'message': message})
    response.status_code = 404
    return response

def badRequestError(message):
    response = jsonify({'error':'Bad Request', 'message': message})
    response.status_code = 400
    return response